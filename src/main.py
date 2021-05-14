import logging
import sys
from config import ASSETS_PATH, Config
from graphics.screen import Screen
from events import EventHandler
from database_connection import get_database_connection
from menu.setup import create_main_menu

def main():
    config = Config(ASSETS_PATH / "general.json")

    screen = Screen(config.window_width, config.window_height, config.font_size)
    event_handler = EventHandler()
    database_connection = get_database_connection()
    main_menu = create_main_menu(screen, event_handler, ASSETS_PATH,
                                 config, database_connection)
    main_menu.run()

if __name__ == '__main__':
    main()
