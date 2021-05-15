from config import CONFIG_PATH, Config
from graphics.screen import Screen
from events import EventHandler
from database_connection import get_database_connection
from menu.setup import create_main_menu

def main():
    """Function for running the application"""
    config = Config(CONFIG_PATH)

    screen = Screen(config.window_width, config.window_height, config.font_size)
    event_handler = EventHandler()
    database_connection = get_database_connection(config.database_path)
    main_menu = create_main_menu(screen, event_handler, config, database_connection)
    main_menu.run()

if __name__ == '__main__':
    main()
