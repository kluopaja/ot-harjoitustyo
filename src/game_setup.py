from game import Player, Timer, GameState, Game, GameNotification, GameBackground
from game import Clock, GameRenderer, GameView
from graphics import ImageGraphic, PolylineGraphic
from shapes import Polyline, Rectangle
from screen import Screen
from game_objects import PlaneFactory, Ground
from inputs import GameInput, PlayerInput
import pygame
from pygame import Vector2
from menu_item import PlayerNumberMenuItem
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

    def game(self, screen):
        game_input = GameInput(self.event_handler)
        # TODO read from config file
        player_inputs = []
        player_inputs.append(PlayerInput(game_input, pygame.K_w, pygame.K_a,
                                         pygame.K_d, pygame.K_LSHIFT))
        player_inputs.append(PlayerInput(game_input, pygame.K_UP, pygame.K_LEFT,
                                         pygame.K_RIGHT, pygame.K_SPACE))
        game_notifications = []
        plane_factories = []
        for i in range(self.max_players):
            game_notifications.append(
                GameNotification("press `shoot` to start flying", "seconds to go"))
            plane_factories.append(
                PlaneFactory(self.assets_path / "plane.png",
                             self.assets_path / "bullet.png"))
        plane_factories[0].start_position = Vector2(400, 400)
        plane_factories[1].start_position = Vector2(1000, 200)

        players = []
        game_views = []
        for i in range(self.n_players):
            players.append(Player(plane_factories[i], player_inputs[i],
                                  game_notifications[i], Timer(0.5)))
            game_views.append(GameView(players[-1], (30, 72, 102)))


        ground_shape = Polyline.from_points([Vector2(0, 1200), Vector2(200, 1000),
                                             Vector2(500, 1250), Vector2(2000, 500)])
        ground_graphic = PolylineGraphic(ground_shape, (1, 102, 26), 7)
        ground = Ground(ground_shape, ground_graphic)
        game_state = GameState([ground], players)

        cloud_graphic = ImageGraphic.from_image_path(self.assets_path / "cloud.png",
                                                     Vector2(0, 0), Vector2(119, 81))
        background = GameBackground(cloud_graphic, n_clouds=10,
                                    repeat_area=Vector2(3000, 2000),
                                    fill_color = (180, 213, 224))
        renderer = GameRenderer(screen, game_views, background)

        game = Game(game_input, game_state, renderer, Clock(60))
        return game

    def add_player(self):
        if self.n_players < self.max_players:
            self.n_players += 1

    def remove_player(self):
        if self.n_players > 0:
            self.n_players -= 1

    def menu_item_modifiers(self):
        return [PlayerNumberMenuItem(self, "Number of players: ")]
