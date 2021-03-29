import game
import sprite
from pathlib import Path
import pygame
import game_objects
from pygame import Vector2
from events import EventHandler
from game import GameInput, GameState, GameLoop
import logging


logging.basicConfig(level=logging.INFO)
pygame.init()
#flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
display = pygame.display.set_mode((2000, 1300), vsync=1)

game_view = game.GameView(game.constant_view_locator(1000, 650), (2000, 1300))
project_root = Path(__file__).parent.parent

plane_image = sprite.ImageSprite((400, 400), project_root / "assets/plane.png")
plane = game_objects.Plane(plane_image)
plane.location = Vector2(400, 400)

event_handler = EventHandler()
game_input = GameInput(event_handler)
game_input.bind_keys({pygame.K_LEFT: plane.up, pygame.K_RIGHT: plane.down,
                      pygame.K_UP: plane.accelerate})
game_state = GameState([plane])
renderer = game.GameRenderer(display, game_view)

game_loop = GameLoop(game_input, game_state, renderer)
game_loop.run()
