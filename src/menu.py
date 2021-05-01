from pygame import Vector2
from menu_item import ButtonMenuItem
import pygame
import string


class MenuKeys:
    def __init__(self, quit_menu, next_item, prev_item, increase, decrease,
                 accept, erase):
        self.quit = quit_menu
        self.next_item = next_item
        self.prev_item = prev_item
        self.increase = increase
        self.decrease = decrease
        self.accept = accept
        self.erase = erase


class MenuInput:
    def __init__(self, event_handler, menu_keys):
        self.event_handler = event_handler
        self.keys = menu_keys
        self.keymaps = {}
        self.get_text_callback = None
        self.set_text_callback = None

    def bind_quit(self, func):
        self.keymaps[self.keys.quit] = func

    def bind_next_item(self, func):
        self.keymaps[self.keys.next_item] = func

    def bind_previous_item(self, func):
        self.keymaps[self.keys.prev_item] = func

    def bind_increase(self, func):
        self.keymaps[self.keys.increase] = func

    def bind_decrease(self, func):
        self.keymaps[self.keys.decrease] = func

    def bind_accept(self, func):
        self.keymaps[self.keys.accept] = func

    def bind_text(self, get_text, set_text):
        self.get_text_callback = get_text
        self.set_text_callback = set_text

    def clear_bindings(self):
        self.keymaps.clear()
        self.set_text_callback = None
        self.get_text_callback = None

    def handle_inputs(self):
        callbacks = []
        for event in self.event_handler.get_events():
            if event.type == pygame.KEYDOWN:
                if event.key in self.keymaps:
                    callbacks.append(self.keymaps[event.key])
                elif event.key == self.keys.erase:
                    callbacks.append(self._erase_text)
                else:
                    callbacks.append(lambda c=event.unicode: self._add_text(c))

        # important to call there only here to avoid the side effects
        # of the callbacks to self
        for f in callbacks:
            f()

    def _erase_text(self):
        if (self.set_text_callback is None) or (self.get_text_callback is None):
            return
        self.set_text_callback(self.get_text_callback()[0:-1])

    def _add_text(self, character):
        if character in string.whitespace:
            return
        if (self.set_text_callback is None) or (self.get_text_callback is None):
            return
        self.set_text_callback(self.get_text_callback() + character)


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
        self._items = []

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

    def _start_game(self):
        self._should_start_game = True

    def _activate_next_item(self):
        self._activate_item((self.selected_item + 1) % len(self.items))

    def _activate_previous_item(self):
        self._activate_item((self.selected_item - 1) % len(self.items))

    def _activate_item(self, item_index):
        self.selected_item = item_index


class MenuListRenderer:
    def __init__(self, screen, background_color, item_spacing, item_renderer):
        self.screen = screen
        self.background_color = background_color
        self.item_renderer = item_renderer
        self.item_spacing = item_spacing

    def render(self, menu_list):
        self.screen.surface.fill(self.background_color, update=True)
        for i in range(len(menu_list.items)):
            item_center = self._item_center(i, len(menu_list.items))
            is_active = False
            if i == menu_list.selected_item:
                is_active = True
            self.item_renderer.render(self.screen.surface, menu_list.items[i],
                                      item_center, is_active)
        self.screen.update()

    def _item_center(self, item_index, total_items):
        """Returns a Vector2 corresponding to the item center"""
        screen_center = Vector2(self.screen.surface.get_rect().center)
        menu_height = self.item_spacing * total_items
        menu_start = screen_center - Vector2(0, menu_height)/2
        return menu_start + Vector2(0, self.item_spacing) * item_index


class MenuItemRenderer:
    def __init__(self, font_color):
        self.font_color = font_color

    def render(self, surface, menu_item, center, is_active):
        text = menu_item.text()
        if is_active:
            text = "-> " + text + " <-"

        surface.centered_text(text, center, self.font_color)
