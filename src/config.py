from pathlib import Path
from pygame import Vector2
import json
import pygame
from graphics.graphics import PolylineGraphic
from game.shapes import Polyline
from game.game_objects import Ground
from game.inputs import PlayerInput

project_root = Path(__file__).parent.parent
DATABASE_PATH = project_root / "data/database.sqlite"
ASSETS_PATH = project_root / "assets"



class LevelConfig:
    """A class for storing the properties of a level."""

    def __init__(self, file_path):
        self._data = json.load(open(file_path, "r"))
        if ("starting_locations" not in self._data) or len(self._data["starting_locations"]) == 0:
            raise ValueError(
                f"Error in loading {file_path}: no starting locations provided.")

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

class PlayerInputsConfig:
    """ A class for loading player input configs from a file"""
    def __init__(self, keymaps_file_path):
        self._data = json.load(open(keymaps_file_path, "r"))

    def max_players(self):
        return len(self._data["player_keys"])

    def get_player_inputs(self, game_input):
        """Generates a list of PlayerInput objects.

        Arguments:
            `game_input`: a GameInput object
                The object to which the PlayerInputs will be attached to."""
        player_inputs = []

        def code(description):
            return pygame.key.key_code(description)
        for keys in self._data["player_keys"]:
            player_inputs.append(PlayerInput(game_input, code(keys["accelerate"]),
                                             code(keys["up"]), code(
                                                 keys["down"]),
                                             code(keys["shoot"])))
        return player_inputs

class PlaneConfig:
    """A class for reading and storing the properties of a plane."""
    def __init__(self, plane_config_path):
        data = json.load(open(plane_config_path, "r"))
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
        data = json.load(open(gun_config_path, "r"))
        self.bullet_config = BulletConfig(
            gun_config_path.parent / data["bullet_config_path"])
        self.bullet_spawn_time = data["bullet_spawn_time"]
        self.bullet_spawn_offset = data["bullet_spawn_offset"]
        self.bullet_speed = data["bullet_speed"]


class BulletConfig:
    """A class for reading and storing the properties of a bullet."""
    def __init__(self, bullet_config_path):
        data = json.load(open(bullet_config_path, "r"))
        self.image_file_path = bullet_config_path.parent / data["image_file_path"]
        self.diameter = data["diameter"]
        self.gravity = data["gravity"]
        self.body_drag = data["body_drag"]
        self.health = data["health"]
        self.collision_damage = data["collision_damage"]
        self.timeout = data["timeout"]
