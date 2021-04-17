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
from menu_item import ValueBrowserMenuItem
from level_config import LevelConfigSelector
class GameFactory:
    def __init__(self, assets_path, event_handler, n_players=2, max_players=2):
        if max_players > 2:
            raise Exception("Maximum of 2 players currently supported")
        self.n_players = n_players
        self.max_players = max_players
        self.assets_path = assets_path
        if event_handler is None:
            event_handler = EventHandler()
        self.event_handler = event_handler
        self.level_config_selector = LevelConfigSelector(self.assets_path / "levels")

    def game(self, screen):
        level_config = self.level_config_selector.get_selected()
        game_input = GameInput(self.event_handler)
        # TODO read from config file
        player_inputs = []
        player_inputs.append(PlayerInput(game_input, pygame.K_w, pygame.K_a,
                                         pygame.K_d, pygame.K_LSHIFT))
        player_inputs.append(PlayerInput(game_input, pygame.K_UP, pygame.K_LEFT,
                                         pygame.K_RIGHT, pygame.K_SPACE))
        game_notifications = []
        plane_factories = []

        start_positions = level_config.starting_locations()

        for i in range(self.max_players):
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
            game_views.append(GameView(players[-1], (30, 72, 102)))


        game_state = GameState(level_config.game_objects(), players)

        cloud_graphic = ImageGraphic.from_image_path(self.assets_path / "cloud.png",
                                                     Vector2(0, 0), Vector2(119, 81))
        background = GameBackground(cloud_graphic, n_clouds=10,
                                    repeat_area=Vector2(3000, 2000),
                                    fill_color = (180, 213, 224))
        renderer = GameRenderer(screen, game_views, background)

        game = Game(game_input, game_state, renderer, Clock(60, busy_wait))
        return game

    def add_player(self):
        self.n_players += 1
        self._clamp_n_players()

    def remove_player(self):
        self.n_players -= 1
        self._clamp_n_players()

    def next_level(self):
        self.level_config_selector.next_level()
        self._clamp_n_players()

    def previous_level(self):
        self.level_config_selector.previous_level()
        self._clamp_n_players()

    def _clamp_n_players(self):
        self.n_players = max(1, self.n_players)
        self.n_players = min(self.n_players, self.level_config_selector.max_players())

def game_factory_menu_items(game_factory):
    """Returns a list of MenuItems that modify `game_factory`"""
    out = []
    level_selector = game_factory.level_config_selector
    out.append(ValueBrowserMenuItem(game_factory.previous_level, game_factory.next_level,
                                    level_selector.level_name, "Level: "))
    out.append(ValueBrowserMenuItem(game_factory.remove_player, game_factory.add_player,
                                    lambda : game_factory.n_players, "Number of players: "))

    return out
