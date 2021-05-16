from user_dao import UserDao
from game.setup import GameFactory
from game.game_stats import create_results_viewer, create_high_score_viewer
from game.game import GameOrganizer
from graphics.menu_rendering import MenuItemRenderer, MenuListRenderer
from menu.input import MenuInput
from menu.menu_list import MenuListFactory
from menu.menus import NewGameMenu, AddUserMenu, MainMenu
from stats_dao import StatsDao
from user import UserFactory
from utils.timing import Clock, sleep_wait

def create_main_menu(screen, event_handler, config, database_connection):
    """A Factory method for MainMenu.

    Creates a main menu and along it basically the whole application

    Arguments:
        `screen`: Screen
            The target to which the application will be rendered
        `event_handler`: An EventHandler
            The input events of the application
        `config`: Config
        `database_connection`: sqlite3.Connection
    """
    user_dao = UserDao(database_connection)

    game_factory = GameFactory(config, user_dao, event_handler, screen)

    menu_item_renderer = MenuItemRenderer(font_color=config.menu_font_color)
    menu_list_renderer = MenuListRenderer(
        screen, background_color=config.menu_background_color,
        item_spacing=config.menu_item_spacing, item_renderer=menu_item_renderer)
    menu_input = MenuInput(event_handler, config.menu_input_config)

    menu_list_factory = MenuListFactory(
        menu_list_renderer, menu_input, Clock(20, sleep_wait, False))

    results_viewer = create_results_viewer(menu_input, screen)

    stats_dao = StatsDao(database_connection)
    game_organizer = GameOrganizer(results_viewer, stats_dao)

    new_game_menu = NewGameMenu(game_factory, menu_list_factory, game_organizer)
    user_factory = UserFactory(user_dao)
    add_user_menu = AddUserMenu(menu_list_factory, user_factory)
    high_score_viewer = create_high_score_viewer(stats_dao, 5,  menu_input, screen)
    return MainMenu(menu_list_factory, new_game_menu, add_user_menu, high_score_viewer)
