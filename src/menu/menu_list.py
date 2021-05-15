class MenuListFactory:
    def __init__(self, menu_renderer, menu_input, clock):
        self.menu_renderer = menu_renderer
        self.menu_input = menu_input
        self.clock = clock

    def menu(self, menu_item_collection):
        return MenuList(self.menu_renderer, self.menu_input, menu_item_collection, self.clock)


class MenuList:
    def __init__(self, menu_renderer, menu_input, item_collection, clock):
        self.menu_renderer = menu_renderer
        self.menu_input = menu_input
        self.item_collection = item_collection
        self.selected_item = 0
        self.clock = clock
        self._should_quit = False
        self.items = []

    def run_tick(self):
        self._update_item_list()
        self._prepare_menu_input()
        self.menu_input.handle_inputs()
        self.menu_renderer.render(self)
        self.clock.tick()

    def should_quit(self):
        return self._should_quit

    def _update_item_list(self):
        self.items = self.item_collection.get_item_list()

    def _prepare_menu_input(self):
        self.menu_input.clear_bindings()
        self.menu_input.bind_quit(self._quit)
        self.menu_input.bind_next_item(self._activate_next_item)
        self.menu_input.bind_previous_item(self._activate_previous_item)
        self.items[self.selected_item].bind(self.menu_input)
        self._should_quit = False

    def _quit(self):
        self._should_quit = True

    def _activate_next_item(self):
        self._activate_item((self.selected_item + 1) % len(self.items))

    def _activate_previous_item(self):
        self._activate_item((self.selected_item - 1) % len(self.items))

    def _activate_item(self, item_index):
        self.selected_item = item_index
