from pygame import Vector2
import json
from shapes import Polyline
from graphics import PolylineGraphic
from game_objects import Ground


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
