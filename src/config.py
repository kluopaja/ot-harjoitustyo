import logging
import sys
import traceback
from pathlib import Path
import os
import json
# hide the pygame start message
# has to be placed before any of the pygame the imports!
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
from pygame import Vector2
import pygame

import jsonschema

from graphics.graphics import PolylineGraphic
from game.shapes import Polyline
from game.game_objects import Ground


project_root = Path(__file__).parent.parent
SCHEMAS_PATH = project_root / "assets/schemas"
CONFIG_PATH = project_root / "assets/config.json"
DEFAULT_DATABASE_PATH = project_root / "data/database.sqlite"

class ValidationError(Exception):
    pass


def validate_keys_config(keys_config_path):
    schema = json.load(open(SCHEMAS_PATH / "keys_schema.json"))
    data = json.load(open(keys_config_path, "r"))
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as ex:
        msg = str(ex)
        raise ValidationError("Error parsing keys config:\n" + msg)

class Config:
    """A class for storing all of the configs."""
    def __init__(self, file_path):
        try:
            file_dir = file_path.parent
            schema = json.load(open(SCHEMAS_PATH / "config_schema.json"))
            data = json.load(open(file_path, "r"))
            try:
                jsonschema.validate(instance=data, schema=schema)
            except jsonschema.exceptions.ValidationError as ex:
                msg = str(ex)
                raise ValidationError("Error parsing main config:\n" + msg)

            self.level_config_selector = LevelConfigSelector(file_dir / data["level_dir"])
            self.plane_config = PlaneConfig(file_dir / data["plane_config_path"])
            self.background_config = BackgroundConfig(file_dir / data["background_config_path"])

            keys_config_path = file_dir / data["keys_config_path"]
            validate_keys_config(keys_config_path)
            self.player_input_configs = player_input_configs_loader(keys_config_path)
            self.game_input_config = GameInputConfig.from_file(keys_config_path)
            self.menu_input_config = MenuInputConfig.from_file(keys_config_path)

            self.database_path = file_dir / data["database_path"]

            self.window_width = data["window_width"]
            self.window_height = data["window_height"]

            self.font_size = data["font_size"]

            self.menu_font_color = tuple(data["menu_font_color"])
            self.menu_background_color = tuple(data["menu_background_color"])
            self.menu_item_spacing = data["menu_item_spacing"]

            self.game_camera_height = data["camera_height"]
            self.press_key_to_start_message = data["press_key_to_start_message"]
            self.until_spawn_message = data["until_spawn_message"]

            self.game_view_font_color = data["game_view_font_color"]
            self.player_spawn_time = data["player_spawn_time"]
            self.game_length = data["game_length"]

            self.info_bar_level_message = data["info_bar_level_message"]
            self.info_bar_time_left_message = data["info_bar_time_left_message"]
            self.info_bar_font_color = data["info_bar_font_color"]
            self.info_bar_background_color = data["info_bar_background_color"]

            self.pause_message = data["pause_message"]
            self.pause_font_color = tuple(data["pause_font_color"])
            self.pause_blur_radius = data["pause_blur_radius"]

            self.game_fps = data["game_fps"]

        except ValidationError as ex:
            logging.critical(ex)
            sys.exit()
        except Exception:
            logging.critical(traceback.format_exc())
            logging.critical("Failed parsing configuration files")
            sys.exit()

class LevelConfig:
    """A class for storing the properties of a level."""

    def __init__(self, file_path):
        schema = json.load(open(SCHEMAS_PATH / "level_schema.json"))
        self._data = json.load(open(file_path, "r"))

        try:
            jsonschema.validate(instance=self._data, schema=schema)
        except jsonschema.exceptions.ValidationError as ex:
            msg = str(ex)
            raise ValidationError(
                f"Error parsing level config {file_path}:\n" + msg)

        background_path = file_path.parent / self._data["background_config_path"]
        self.background_config = BackgroundConfig(background_path)

    def name(self):
        return self._data["name"]

    def max_players(self):
        """Returns the maximum number of players supported by the level"""
        return len(self._data["starting_locations"])

    def starting_locations(self):
        """Returns the starting locations for the players' planes"""
        return self._data["starting_locations"][:]

    def game_objects(self):
        result = []
        for ground_line_config in self._data["ground_lines"]:
            result.append(self._read_ground_line_config(ground_line_config))
        return result

    def _read_ground_line_config(self, ground_line_config):
        points = [Vector2(x) for x in ground_line_config["points"]]
        shape = Polyline.from_points(points)
        color = tuple(ground_line_config["color"])
        width = ground_line_config["width"]
        graphic = PolylineGraphic(shape, color, width)
        return Ground(shape, graphic)


class LevelConfigSelector:
    """A class for selecting a level config file"""

    def __init__(self, level_path):
        """Inits LevelConfigSelctor with level config files in `level_path`"""
        self.level_configs = []
        self.selected_idx = 0
        for child in sorted(level_path.iterdir()):
            if child.suffix == ".json":
                self.level_configs.append(LevelConfig(child))

        if len(self.level_configs) == 0:
            raise ValueError("No level configs could be found!")


    def get_selected(self):
        """Returns a LevelConfig object for the currently selected level"""
        return self.level_configs[self.selected_idx]

    def next_level(self):
        """Moves selection to the next level on the list.

            Does nothing if already at the last level."""
        if self.selected_idx+1 < len(self.level_configs):
            self.selected_idx += 1

    def previous_level(self):
        """Moves selection to the previous level on the list.

            Does nothing if already at the first level."""
        if self.selected_idx > 0:
            self.selected_idx -= 1

    def level_name(self):
        """Returns the name of the selected level"""
        return self.level_configs[self.selected_idx].name()

    def max_players(self):
        """Returns the maximum number of players for selected level"""
        return self.level_configs[self.selected_idx].max_players()

class BackgroundConfig:
    def __init__(self, config_path):
        schema = json.load(open(SCHEMAS_PATH / "background_schema.json"))
        data = json.load(open(config_path, "r"))
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.exceptions.ValidationError as ex:
            msg = str(ex)
            raise ValidationError("Error parsing background config:\n" + msg)

        self.image_file_path = config_path.parent / data["image_file_path"]
        self.image_size = (data["image_size"]["width"], data["image_size"]["height"])
        self.n_images = data["n_images"]
        self.repeat_area = (data["repeat_area"]["width"], data["repeat_area"]["height"])
        self.fill_color = tuple(data["fill_color"])

def pygame_key_code(description):
    """A function to map `description` into a pygame key code"""
    try:
        return pygame.key.key_code(description)
    except ValueError:
        raise ValueError(
            f"Failed to map key description "
            f"'{description}' into a pygame keycode")

class MenuInputConfig:
    def __init__(self, quit_key, next_item, prev_item, increase, decrease, accept,
                 erase):
        self.quit = quit_key
        self.next_item = next_item
        self.prev_item = prev_item
        self.increase = increase
        self.decrease = decrease
        self.accept = accept
        self.erase = erase

    @classmethod
    def from_file(cls, keymaps_file_path):
        data = json.load(open(keymaps_file_path, "r"))
        keys = data["menu_keys"]

        return cls(
            pygame_key_code(keys["quit"]),
            pygame_key_code(keys["next_item"]),
            pygame_key_code(keys["previous_item"]),
            pygame_key_code(keys["increase"]),
            pygame_key_code(keys["decrease"]),
            pygame_key_code(keys["accept"]),
            pygame_key_code(keys["erase"]))

class PlayerInputConfig:
    """A class for storing the keys for a single player.

    Stores keys as pygame keycodes."""

    def __init__(self, accelerate, up, down, shoot):
        self.accelerate = accelerate
        self.up = up
        self.down = down
        self.shoot = shoot

class GameInputConfig:
    """A class for storing game keys common to all players"""
    def __init__(self, quit_key, pause):
        self.quit = quit_key
        self.pause = pause

    @classmethod
    def from_file(cls, keymaps_file_path):
        data = json.load(open(keymaps_file_path, "r"))
        return cls(pygame_key_code(data["game_keys"]["quit"]),
                   pygame_key_code(data["game_keys"]["pause"]))


def player_input_configs_loader(keymaps_file_path):
    """Reads a list of PlayerInputConfig objects from a keymap file."""
    data = json.load(open(keymaps_file_path, "r"))
    player_input_configs = []

    for keys in data["game_keys"]["player_keys"]:
        player_input_configs.append(PlayerInputConfig(
            pygame_key_code(keys["accelerate"]), pygame_key_code(keys["up"]),
            pygame_key_code(keys["down"]), pygame_key_code(keys["shoot"])))

    return player_input_configs

class PlaneConfig:
    """A class for reading and storing the properties of a plane."""
    def __init__(self, plane_config_path):
        schema = json.load(open(SCHEMAS_PATH / "plane_schema.json"))
        data = json.load(open(plane_config_path, "r"))
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.exceptions.ValidationError as ex:
            msg = str(ex)
            raise ValidationError("Error parsing plane config:\n" + msg)
        self.image_file_path = plane_config_path.parent / data["image_file_path"]
        self.gun_config = GunConfig(plane_config_path.parent / data["gun_config_path"])
        self.size = Vector2(data["size"]["width"], data["size"]["height"])
        self.acceleration = data["acceleration"]
        self.rotation = data["rotation"]
        self.body_drag = data["body_drag"]
        self.wing_size = data["wing_size"]
        self.gravity = data["gravity"]
        self.health = data["health"]
        self.collision_damage = data["collision_damage"]
        self.score_per_damage = data["score_per_damage"]
        self.score_when_destroyed = data["score_when_destroyed"]
        self.cost = data["cost"]

class GunConfig:
    """A class for reading and storing the properties of a gun."""
    def __init__(self, gun_config_path):
        schema = json.load(open(SCHEMAS_PATH / "gun_schema.json"))
        data = json.load(open(gun_config_path, "r"))
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.exceptions.ValidationError as ex:
            msg = str(ex)
            raise ValidationError("Error parsing gun config:\n" + msg)
        self.bullet_config = BulletConfig(
            gun_config_path.parent / data["bullet_config_path"])
        self.bullet_spawn_time = data["bullet_spawn_time"]
        self.bullet_spawn_offset = data["bullet_spawn_offset"]
        self.bullet_speed = data["bullet_speed"]


class BulletConfig:
    """A class for reading and storing the properties of a bullet."""
    def __init__(self, bullet_config_path):
        schema = json.load(open(SCHEMAS_PATH / "bullet_schema.json"))
        data = json.load(open(bullet_config_path, "r"))
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.exceptions.ValidationError as ex:
            msg = str(ex)
            raise ValidationError("Error parsing bullet config:\n" + msg)
        self.image_file_path = bullet_config_path.parent / data["image_file_path"]
        self.diameter = data["diameter"]
        self.gravity = data["gravity"]
        self.body_drag = data["body_drag"]
        self.health = data["health"]
        self.collision_damage = data["collision_damage"]
        self.timeout = data["timeout"]
