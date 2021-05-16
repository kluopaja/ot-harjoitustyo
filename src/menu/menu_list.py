class MenuListFactory:
    def __init__(self, menu_renderer, menu_input, clock):
        self.menu_renderer = menu_renderer
        self.menu_input = menu_input
        self.clock = clock

    def menu(self, menu_item_collection):
        return MenuList(self.menu_renderer, self.menu_input, menu_item_collection, self.clock)


class MenuList:
    """A class for browsable list of MenuItems.

    The the MenuList has any MenuItems, then one of them will
    always be activated.

    If the MenuList first has 0 MenuItems and after that more,
    then the first of the MenuItems will be activated automatically.

    NOTE: Is not guaranteed to work if item is selected and then almost
    immediately (during the same frame) accessed. In this case, the
    affected MenuItem might also be the previously selected one.
    This shouldn't be a problem in practice.
    """

    def __init__(self, menu_renderer, menu_input, item_collection, clock):
        """Initializes MenuList.

        Arguments:
            `menu_renderer`: A MenuListRenderer
            `menu_input`: A MenuInput
            `item_collection`: A MenuItemCollection
                The MenuItems in the MenuList
            `clock`: A Clock
                The clock used to set the refreshing rate of the MenuList
        """

        self._menu_renderer = menu_renderer
        self._menu_input = menu_input
        self._item_collection = item_collection
        self._clock = clock
        self._should_quit = False
        # will be -1 if len(self._items) == 0
        self._selected_item = 0
        self._items = 0

    def run_tick(self):
        """Runs one tick of the menu.

        Limits the framerate to the one set by self._clock"""
        self._update_item_list()
        self._prepare_menu_input()
        self._menu_input.handle_inputs()
        selected_idx = self._selected_item
        if selected_idx == -1:
            selected_idx = None
        self._menu_renderer.render(self._items, selected_idx)
        self._clock.tick()

    def should_quit(self):
        """Returns True if the MenuList shouldn't be run anymore.

        Otherwise returns False"""
        return self._should_quit

    def _update_item_list(self):
        self._items = self._item_collection.get_item_list()
        self._selected_item = max(self._selected_item, 0)
        self._selected_item = min(self._selected_item, len(self._items)-1)

    def _prepare_menu_input(self):
        self._menu_input.clear_bindings()
        self._menu_input.bind_quit(self._quit)
        if len(self._items) > 0:
            self._menu_input.bind_next_item(self._activate_next_item)
            self._menu_input.bind_previous_item(self._activate_previous_item)
            self._items[self._selected_item].bind(self._menu_input)
        self._should_quit = False

    def _quit(self):
        self._should_quit = True

    def _activate_next_item(self):
        """Activates the next item.

        Should only be called if there are more than 0 items"""
        self._selected_item = (self._selected_item + 1) % len(self._items)

    def _activate_previous_item(self):
        """Activates the previous item.

        Should only be called if there are more than 0 items"""
        self._selected_item = (self._selected_item - 1) % len(self._items)
