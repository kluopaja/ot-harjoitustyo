import game
import graphics
from pathlib import Path
import pygame
import game_objects
from pygame import Vector2
from events import EventHandler
from graphics import ImageGraphic
from shapes import Polyline, Rectangle
from screen import Screen
from game_objects import PlaneFactory
from inputs import GameInput, PlayerInput
import logging
from game_setup import GameFactory


logging.basicConfig(level=logging.INFO)
pygame.init()
screen = Screen(2000, 1300)
project_root = Path(__file__).parent.parent

event_handler = EventHandler()

game_factory = GameFactory(project_root / "assets", event_handler)
game_factory.remove_player()
game_factory.game(screen).run()
