from game import Player, GameState, Game, GameNotification, GameBackground
from game import GameRenderer, GameView, PauseOverlay
from timing import Timer, Clock, busy_wait
from graphics import ImageGraphic, PolylineGraphic
from shapes import Polyline, Rectangle
from screen import Screen
from game_objects import PlaneFactory, Ground
from inputs import GameKeys, GameInput, PlayerInput
import pygame
from pygame import Vector2
from menu_item import ValueBrowserMenuItem, ButtonMenuItem, TextInputMenuItem
from level_config import LevelConfigSelector
from user import UserSelector
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

class GameFactory:
    def __init__(self, assets_path, user_dao, event_handler, screen, n_players=2):
        self.n_players = n_players
        self.assets_path = assets_path
        self.user_dao = user_dao
        if event_handler is None:
            event_handler = EventHandler()
        self.event_handler = event_handler
        self.screen = screen
        self.level_config_selector = LevelConfigSelector(
            self.assets_path / "levels")
        self.player_input_loader = PlayerInputLoader(
            self.assets_path / "keys.json")
        self.user_selectors = []
        self._update_players()

    def game(self):
        level_config = self.level_config_selector.get_selected()
        game_keys = GameKeys(quit_game = pygame.K_ESCAPE,
                             pause_game = pygame.key.key_code("p"))
        game_input = GameInput(self.event_handler, game_keys)
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
            user = self.user_selectors[i].get_current()
            players[-1].name = user.name
            game_views.append(GameView(players[-1], (30, 72, 102)))

        game_state = GameState(level_config.game_objects(), players)

        cloud_graphic = ImageGraphic.from_image_path(self.assets_path / "cloud.png",
                                                     Vector2(0, 0), Vector2(119, 81))
        background = GameBackground(cloud_graphic, n_clouds=10,
                                    repeat_area=Vector2(3000, 2000),
                                    fill_color=(180, 213, 224))
        pause_overlay = PauseOverlay("PAUSE", (107, 88, 110))
        renderer = GameRenderer(self.screen, game_views, background, pause_overlay)

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

    def _update_players(self):
        self._clamp_n_players()
        for i in range(len(self.user_selectors), self.n_players):
            self.user_selectors.append(UserSelector(self.user_dao))

        self.user_selectors = self.user_selectors[0:self.n_players]

    def _clamp_n_players(self):
        self.n_players = max(1, self.n_players)
        self.n_players = min(
            self.n_players, self.level_config_selector.max_players())
        self.n_players = min(
            self.n_players, self.player_input_loader.max_players())
