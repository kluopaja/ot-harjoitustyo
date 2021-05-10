from user import UserFactory
from menu.menu_items import TextInputMenuItem, ButtonMenuItem, MenuItemCollection
from menu.menu_items import ValueBrowserMenuItem
# TODO rename menu_factory to menu_list_factory everywhere
class MainMenu:
    def __init__(self, menu_factory, new_game_menu, add_user_menu, high_score_view):
        self.menu_factory = menu_factory
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
        menu = self.menu_factory.menu(self.item_collection)
        while not menu.should_quit():
            menu.run_tick()

class NewGameMenu:
    def __init__(self, game_factory, menu_factory, game_organizer):
        self.game_factory = game_factory
        self.menu_factory = menu_factory
        self.game_organizer = game_organizer
        self.item_collection = MenuItemCollection()
        level_selector = game_factory.level_config_selector
        self.item_collection.add_item(
            ValueBrowserMenuItem(game_factory.previous_level, game_factory.next_level,
                                 level_selector.level_name, "Level: ")
        )
        self.item_collection.add_item(
            ValueBrowserMenuItem(game_factory.remove_player, game_factory.add_player,
                                 lambda: game_factory.n_players, "Number of players: ")
        )

        self.player_selection_collection = MenuItemCollection()
        self.item_collection.add_collection(self.player_selection_collection)



        self.item_collection.add_item(ButtonMenuItem(self._game_runner, "Start game"))

    def run(self):
        menu = self.menu_factory.menu(self.item_collection)
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
    def __init__(self, menu_factory, user_factory):
        self.menu_factory = menu_factory
        self.user_factory = user_factory
        self.item_collection = MenuItemCollection()
        self.item_collection.add_item(
            TextInputMenuItem("Name: ", self.user_factory.get_name,
                              self.user_factory.set_name)
        )
        self._create_user_button = ButtonMenuItem(lambda : None, "")
        self.item_collection.add_item(self._create_user_button)

    def run(self):
        self._should_quit = False
        self.user_factory.reset()
        menu = self.menu_factory.menu(self.item_collection)
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
