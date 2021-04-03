import game
import graphics
from pathlib import Path
import pygame
import game_objects
from pygame import Vector2
from events import EventHandler
from game import Player, Timer, GameState, GameLoop, GameNotification
from shapes import Polyline, Rectangle
from screen import Screen
from game_objects import PlaneFactory
from inputs import GameInput, PlayerInput
import logging

logging.basicConfig(level=logging.INFO)
pygame.init()
screen = Screen(2000, 1300)
project_root = Path(__file__).parent.parent


ground_shape = Polyline.from_points([Vector2(0, 1200), Vector2(200, 1000),
                                     Vector2(500, 1250), Vector2(2000, 500)])
ground_graphics = graphics.PolylineGraphic(ground_shape, (1, 102, 26), 7)
ground = game_objects.Ground(ground_shape, ground_graphics)

event_handler = EventHandler()
game_input = GameInput(event_handler)
player_input = PlayerInput(game_input, pygame.K_w, pygame.K_a, pygame.K_d,
                           pygame.K_LSHIFT)
player_input2 = PlayerInput(game_input, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT,
                           pygame.K_SPACE)

game_notification_1 = GameNotification("press `shoot` to start flying", "seconds to go")
game_notification_2 = GameNotification("press `shoot` to start flying", "seconds to go")
plane_factory_1 = PlaneFactory(project_root / "assets/plane.png")
plane_factory_1.start_position = Vector2(400, 400)
plane_factory_2 = PlaneFactory(project_root / "assets/plane.png")
plane_factory_2.start_position = Vector2(1000, 400)
player = Player(plane_factory_1, player_input, game_notification_1, Timer(2))
player2 = Player(plane_factory_2,  player_input2, game_notification_2, Timer(3))
game_state = GameState([ground], [player, player2])
game_view1 = game.GameView(player)
game_view2 = game.GameView(player2)
renderer = game.GameRenderer(screen, [game_view1, game_view2])

game_loop = GameLoop(game_input, game_state, renderer)
game_loop.run()
