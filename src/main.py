from config import ASSETS_PATH
from graphics.screen import Screen
from events import EventHandler
from database_connection import get_database_connection
from menu.setup import create_main_menu

def main():
    screen = Screen(1920, 1080, 0.02)
    event_handler = EventHandler()
    database_connection = get_database_connection()
    main_menu = create_main_menu(screen, event_handler, ASSETS_PATH,
                                 database_connection)
    main_menu.run()

if __name__ == '__main__':
    main()
