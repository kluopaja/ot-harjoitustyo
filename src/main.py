import game
import graphics
from pathlib import Path
import pygame
import game_objects
from pygame import Vector2
from events import EventHandler
from game import Player, GameState, GameLoop
from shapes import Polyline, Rectangle
from screen import Screen
from game_objects import PlaneFactory
from inputs import GameInput, PlayerInput
import logging

logging.basicConfig(level=logging.INFO)
pygame.init()
screen = Screen(2000, 1300)
project_root = Path(__file__).parent.parent

game_view = game.GameView(game.constant_view_locator(1000, 650), (2000, 1300))

ground_shape = Polyline.from_points([Vector2(0, 1200), Vector2(200, 1000),
                                     Vector2(500, 1250), Vector2(2000, 500)])
ground_graphics = graphics.PolylineGraphic(ground_shape, (1, 102, 26), 7)
ground = game_objects.Ground(ground_shape, ground_graphics)

event_handler = EventHandler()
game_input = GameInput(event_handler)
player_input = PlayerInput(game_input, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT,
                           pygame.K_SPACE)

player = Player(PlaneFactory(project_root / "assets/plane.png"), player_input)
game_state = GameState([ground], [player])
renderer = game.GameRenderer(screen, game_view)

game_loop = GameLoop(game_input, game_state, renderer)
game_loop.run()
