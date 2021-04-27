import pygame
from pygame import Vector2
from timing import Clock, sleep_wait
from menu import MenuListRenderer, MenuItemRenderer, MenuInput, MenuKeys, MenuListFactory
from game_menus import NewGameMenu, AddUserMenu, MainMenu
from game_setup import GameFactory
from game import GameOrganizer
import logging
from screen import Screen
from events import EventHandler
from pathlib import Path
import sys
from database_connection import get_database_connection
from user import User, UserFactory
from user_dao import UserDao
from plotter import Plotter
from game_stats import create_results_viewer

logging.basicConfig(level=logging.INFO)
pygame.init()
screen = Screen(2000, 1300)
project_root = Path(__file__).parent.parent

event_handler = EventHandler()

user_dao = UserDao(get_database_connection())
user_dao.create(User("default player"))

game_factory = GameFactory(project_root / "assets", user_dao, event_handler, screen)

menu_item_renderer = MenuItemRenderer(font_color=(50, 69, 63))
menu_list_renderer = MenuListRenderer(screen, background_color=(186, 204, 200),
                             item_spacing=100, item_renderer=menu_item_renderer)
menu_keys = MenuKeys(pygame.K_ESCAPE, pygame.K_UP, pygame.K_DOWN,
                     pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RETURN, pygame.K_BACKSPACE)
menu_input = MenuInput(event_handler, menu_keys)

menu_list_factory = MenuListFactory(menu_list_renderer, menu_input, Clock(20, sleep_wait))

results_viewer = create_results_viewer(menu_input, screen)

game_organizer = GameOrganizer(results_viewer)

new_game_menu = NewGameMenu(game_factory, menu_list_factory, game_organizer)
user_factory = UserFactory(user_dao)
add_user_menu = AddUserMenu(menu_list_factory, user_factory)
main_menu = MainMenu(menu_list_factory, new_game_menu, add_user_menu)
main_menu.run()
