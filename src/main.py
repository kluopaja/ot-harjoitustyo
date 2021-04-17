from pathlib import Path
import pygame
from pygame import Vector2
from events import EventHandler
from screen import Screen
import logging
from game_setup import GameFactory
from menu import MenuRenderer, MenuItemRenderer, MenuInput, NewGameMenu, MenuKeys
from timing import Clock, sleep_wait
import sys


logging.basicConfig(level=logging.INFO)
pygame.init()
screen = Screen(2000, 1300)
project_root = Path(__file__).parent.parent

event_handler = EventHandler()

game_factory = GameFactory(project_root / "assets", event_handler)
game_factory.remove_player()

menu_item_renderer = MenuItemRenderer(font_color=(50, 69, 63))
menu_renderer = MenuRenderer(screen, background_color=(186, 204, 200),
                             item_spacing=100, item_renderer=menu_item_renderer)
menu_keys = MenuKeys(pygame.K_ESCAPE, pygame.K_UP, pygame.K_DOWN,
                     pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RETURN)
menu_input = MenuInput(event_handler, menu_keys)
menu = NewGameMenu(menu_renderer, menu_input, game_factory, Clock(20, sleep_wait))
menu.run(screen)
