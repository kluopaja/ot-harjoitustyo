from game import Player, GameState, Game, GameNotification, GameBackground
from game import GameRenderer, GameView
from timing import Timer, Clock, busy_wait
from graphics import ImageGraphic, PolylineGraphic
from shapes import Polyline, Rectangle
from screen import Screen
from game_objects import PlaneFactory, Ground
from inputs import GameInput, PlayerInput
import pygame
from pygame import Vector2
from menu_item import ValueBrowserMenuItem, ButtonMenuItem, TextInputMenuItem
from level_config import LevelConfigSelector
import json


class PlayerInputLoader:
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


class PlayerPreferences:
    def __init__(self, name):
        self.name = name


class PlayerPreferencesSelector:
    def __init__(self, n_players, default_name):
        self._check_n_players(n_players)
        self.n_players = n_players
        self.default_name = default_name
        self.preferences = []
        self.selected_idx = 0
        self._update()

    def set_players(self, n_players):
        self._check_n_players(n_players)
        self.n_players = n_players
        self._update()

    def next(self):
        if self.selected_idx + 1 < self.n_players:
            self.selected_idx += 1
        self._update()

    def previous(self):
        if self.selected_idx > 0:
            self.selected_idx -= 1
        self._update()

    def get_current(self):
        return self.preferences[self.selected_idx]

    def _update(self):
        if self.selected_idx >= self.n_players:
            self.selected_idx = self.n_players - 1

        for i in range(len(self.preferences), self.n_players):
            name = self.default_name + " " + str(i+1)
            self.preferences.append(PlayerPreferences(name))

    def _check_n_players(self, n_players):
        if n_players < 1:
            raise ValueError("`n_players` must be at least 1")


class GameFactory:
    def __init__(self, assets_path, event_handler, screen, n_players=2):
        self.n_players = n_players
        self.assets_path = assets_path
        if event_handler is None:
            event_handler = EventHandler()
        self.event_handler = event_handler
        self.screen = screen
        self.level_config_selector = LevelConfigSelector(
            self.assets_path / "levels")
        self.player_input_loader = PlayerInputLoader(
            self.assets_path / "keys.json")
        self.player_preferences_selector = PlayerPreferencesSelector(self.n_players,
                                                                     "Player")

    def game(self):
        level_config = self.level_config_selector.get_selected()
        game_input = GameInput(self.event_handler)
        player_inputs = self.player_input_loader.get_player_inputs(game_input)

        game_notifications = []
        plane_factories = []

        start_positions = level_config.starting_locations()

        for i in range(self.n_players):
            game_notifications.append(
                GameNotification("press `shoot` to start flying", "seconds to go"))
            plane_factories.append(
                PlaneFactory(self.assets_path / "plane.png",
                             self.assets_path / "bullet.png"))
            plane_factories[i].start_position = start_positions[i]

        players = []
        game_views = []
        for i in range(self.n_players):
            players.append(Player(plane_factories[i], player_inputs[i],
                                  game_notifications[i], Timer(0.5)))
            player_preferences = self.player_preferences_selector.preferences[i]
            players[-1].name = player_preferences.name
            game_views.append(GameView(players[-1], (30, 72, 102)))

        game_state = GameState(level_config.game_objects(), players)

        cloud_graphic = ImageGraphic.from_image_path(self.assets_path / "cloud.png",
                                                     Vector2(0, 0), Vector2(119, 81))
        background = GameBackground(cloud_graphic, n_clouds=10,
                                    repeat_area=Vector2(3000, 2000),
                                    fill_color=(180, 213, 224))
        renderer = GameRenderer(self.screen, game_views, background)

        game = Game(game_input, game_state, renderer, Clock(60, busy_wait))
        return game

    def add_player(self):
        self.n_players += 1
        self._update_players()

    def remove_player(self):
        self.n_players -= 1
        self._update_players()

    def next_level(self):
        self.level_config_selector.next_level()
        self._update_players()

    def previous_level(self):
        self.level_config_selector.previous_level()
        self._update_players()

    def activate_previous_player(self):
        self.player_preferences_selector.previous()

    def activate_next_player(self):
        self.player_preferences_selector.next()

    def active_player_name(self):
        return self.player_preferences_selector.get_current().name

    def active_player_preferences(self):
        return self.player_preferences_selector.get_current()

    def _update_players(self):
        self._clamp_n_players()
        self.player_preferences_selector.set_players(self.n_players)

    def _clamp_n_players(self):
        self.n_players = max(1, self.n_players)
        self.n_players = min(
            self.n_players, self.level_config_selector.max_players())
        self.n_players = min(
            self.n_players, self.player_input_loader.max_players())


def player_preferences_menu_items(preferences):
    out = []
    # callback function for the menu item

    def set_name(name):
        preferences.name = name

    def get_name():
        return preferences.name
    out.append(TextInputMenuItem("Name: ", get_name, set_name))
    return out


def new_game_menu_items(game_factory, menu_factory):
    """Returns a list of MenuItem objects that modifies `game_factory`"""
    items = []
    level_selector = game_factory.level_config_selector
    items.append(ValueBrowserMenuItem(game_factory.previous_level, game_factory.next_level,
                                      level_selector.level_name, "Level: "))
    items.append(ValueBrowserMenuItem(game_factory.remove_player, game_factory.add_player,
                                      lambda: game_factory.n_players, "Number of players: "))

    def preferences_menu_runner():
        active_player_preferences = game_factory.active_player_preferences()
        menu_items = player_preferences_menu_items(active_player_preferences)
        menu_factory.menu(menu_items).run()

    items.append(ValueBrowserMenuItem(game_factory.activate_previous_player,
                                      game_factory.activate_next_player,
                                      game_factory.active_player_name,
                                      "Edit preferences: ", preferences_menu_runner))

    def game_runner():
        game_factory.game().run()

    items.append(ButtonMenuItem(game_runner, "start game"))
    return items
