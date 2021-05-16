from menu.menu_items import TextInputMenuItem, ButtonMenuItem, MenuItemCollection
from menu.menu_items import ValueBrowserMenuItem
class MainMenu:
    """A class representing the main menu"""
    def __init__(self, menu_list_factory, new_game_menu, add_user_menu, high_score_view):
        """Initializes MainMenu

        Arguments:
            `menu_list_factory`: A MenuListFactory
                Used to make a runnable menu from MenuItems
            `new_game_menu`: A NewGameMenu
            `add_user_menu`: An AddUserMenu
            `high_score_view`: A HighScoreView
        """
        self.menu_list_factory = menu_list_factory
        self.item_collection = MenuItemCollection()
        self.item_collection.add_item(
            ButtonMenuItem(add_user_menu.run, "Add user")
        )
        self.item_collection.add_item(
            ButtonMenuItem(new_game_menu.run, "New game")
        )
        self.item_collection.add_item(
            ButtonMenuItem(high_score_view.run, "View high score")
        )

    def run(self):
        """Runs the menu until the user quits it"""
        menu = self.menu_list_factory.menu(self.item_collection)
        while not menu.should_quit():
            menu.run_tick()

class NewGameMenu:
    """A class representing the new game menu"""
    def __init__(self, game_factory, menu_list_factory, game_organizer):
        """Initializes NewGameMenu.

        Arguments:
            `game_factory`: A GameFactory
                The game factory modified by the menu
            `menu_list_factory`: A MenuListFactory
                Used to make a runnable menu from MenuItems
            `game_organizer`: A GameOrganizer
                Used to organize the game that has been constructed
                by `game_factory`
        """
        self.game_factory = game_factory
        self.menu_list_factory = menu_list_factory
        self.game_organizer = game_organizer
        self.item_collection = MenuItemCollection()
        self.item_collection.add_item(
            ValueBrowserMenuItem(game_factory.previous_level, game_factory.next_level,
                                 game_factory.get_level_name, "Level: ")
        )
        self.item_collection.add_item(
            ValueBrowserMenuItem(game_factory.remove_player, game_factory.add_player,
                                 game_factory.get_n_players, "Number of players: ")
        )

        self.player_selection_collection = MenuItemCollection()
        self.item_collection.add_collection(self.player_selection_collection)



        self.item_collection.add_item(ButtonMenuItem(self._game_runner, "Start game"))

    def run(self):
        menu = self.menu_list_factory.menu(self.item_collection)
        while not menu.should_quit():
            self._update_player_selection_collection()
            menu.run_tick()

    def _update_player_selection_collection(self):
        self.player_selection_collection.clear()
        for i, user_selector in enumerate(self.game_factory.user_selectors):
            self.player_selection_collection.add_item(
                ValueBrowserMenuItem(user_selector.previous,
                                     user_selector.next,
                                     lambda u=user_selector: u.get_current().name,
                                     f"Player {i+1}: ")
            )

    def _game_runner(self):
        game = self.game_factory.game()
        self.game_organizer.organize(game)



class AddUserMenu:
    """A class representing the menu for adding a new user"""
    def __init__(self, menu_list_factory, user_factory):
        """Initializes AddUserMenu

        Arguments:
            `menu_list_factory`: A MenuListFactory
                Used to make a runnable menu from MenuItems
            `user_factory`: A UserFactory
                The user factory modified by the menu
        """
        self.menu_list_factory = menu_list_factory
        self.user_factory = user_factory
        self.item_collection = MenuItemCollection()
        self.item_collection.add_item(
            TextInputMenuItem("Name: ", self.user_factory.get_name,
                              self.user_factory.set_name)
        )
        self._create_user_button = ButtonMenuItem(lambda : None, "")
        self.item_collection.add_item(self._create_user_button)
        self._should_quit = False

    def run(self):
        """Runs the menu until the user creates a new User or quits the menu."""
        self._should_quit = False
        self.user_factory.reset()
        menu = self.menu_list_factory.menu(self.item_collection)
        while (not self._should_quit) and (not menu.should_quit()):
            self._update_create_button()
            menu.run_tick()

    def _update_create_button(self):
        if self.user_factory.name_valid():
            self._activate_create_button()
        else:
            self._deactivate_create_button()

    def _activate_create_button(self):
        self._create_user_button.description = "Create user"
        def f():
            self._should_quit = True
            self.user_factory.create_user()

        self._create_user_button.button_function = f

    def _deactivate_create_button(self):
        self._create_user_button.description = "Name already in use!"
        self._create_user_button.button_function = lambda : None
