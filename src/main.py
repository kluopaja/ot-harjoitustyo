import sys

sys.path.insert(0, '/home/kalle/koodit/pygame')
from pathlib import Path
from events import EventHandler
from screen import Screen
import logging
from game_setup import GameFactory, new_game_menu_items
from menu import MenuRenderer, MenuItemRenderer, MenuInput, MenuKeys, MenuFactory
from timing import Clock, sleep_wait
from pygame import Vector2
import pygame

logging.basicConfig(level=logging.INFO)
pygame.init()
screen = Screen(2000, 1300)
project_root = Path(__file__).parent.parent

event_handler = EventHandler()

game_factory = GameFactory(project_root / "assets", event_handler, screen)

menu_item_renderer = MenuItemRenderer(font_color=(50, 69, 63))
menu_renderer = MenuRenderer(screen, background_color=(186, 204, 200),
                             item_spacing=100, item_renderer=menu_item_renderer)
menu_keys = MenuKeys(pygame.K_ESCAPE, pygame.K_UP, pygame.K_DOWN,
                     pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RETURN, pygame.K_BACKSPACE)
menu_input = MenuInput(event_handler, menu_keys)
menu_factory = MenuFactory(menu_renderer, menu_input, Clock(20, sleep_wait))
menu_items = new_game_menu_items(game_factory, menu_factory)
menu_factory.menu(menu_items).run()
