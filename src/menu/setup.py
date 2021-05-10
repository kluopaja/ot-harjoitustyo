import pygame
from user_dao import UserDao
from game.setup import GameFactory
from graphics.menu_rendering import MenuItemRenderer, MenuListRenderer
from menu.input import MenuKeys, MenuInput
from menu.menu_list import MenuListFactory
from game.game_stats import create_results_viewer, create_high_score_viewer
from stats_dao import StatsDao
from game.game import GameOrganizer
from menu.menus import NewGameMenu, AddUserMenu, MainMenu
from user import UserFactory, User
from utils.timing import Clock, sleep_wait

def create_main_menu(screen, event_handler, assets_path, database_connection):
    user_dao = UserDao(database_connection)
    user_dao.create(User("default user"))

    game_factory = GameFactory(assets_path, user_dao, event_handler, screen)

    menu_item_renderer = MenuItemRenderer(font_color=(50, 69, 63))
    menu_list_renderer = MenuListRenderer(screen, background_color=(186, 204, 200),
                                 item_spacing=0.1, item_renderer=menu_item_renderer)
    menu_keys = MenuKeys(pygame.K_ESCAPE, pygame.K_DOWN, pygame.K_UP,
                         pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RETURN, pygame.K_BACKSPACE)
    menu_input = MenuInput(event_handler, menu_keys)

    menu_list_factory = MenuListFactory(menu_list_renderer, menu_input, Clock(20, sleep_wait))

    results_viewer = create_results_viewer(menu_input, screen)

    stats_dao = StatsDao(database_connection)
    game_organizer = GameOrganizer(results_viewer, stats_dao)

    new_game_menu = NewGameMenu(game_factory, menu_list_factory, game_organizer)
    user_factory = UserFactory(user_dao)
    add_user_menu = AddUserMenu(menu_list_factory, user_factory)
    high_score_viewer = create_high_score_viewer(stats_dao, 5,  menu_input, screen)
    return MainMenu(menu_list_factory, new_game_menu, add_user_menu, high_score_viewer)
