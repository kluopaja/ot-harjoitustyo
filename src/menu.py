from pygame import Vector2
from menu_item import ButtonMenuItem
import pygame
class MenuKeys:
    def __init__(self, quit_menu, next_item, prev_item, increase, decrease, accept):
        self.quit = quit_menu
        self.next_item = next_item
        self.prev_item = prev_item
        self.increase = increase
        self.decrease = decrease
        self.accept = accept

class MenuInput:
    def __init__(self, event_handler, menu_keys):
        self.event_handler = event_handler
        self.keys = menu_keys
        self.keymaps = {}
        self.should_quit = False
        self._text_input = []

    def bind_next_item(self, func):
        self.keymaps[self.keys.next_item] = func

    def bind_previous_item(self, func):
        self.keymaps[self.keys.prev_item] = func

    def bind_quit(self, func):
        self.keymaps[self.keys.quit] = func

    def bind_increase(self, func):
        self.keymaps[self.keys.increase] = func

    def bind_decrease(self, func):
        self.keymaps[self.keys.decrease] = func

    def bind_accept(self, func):
        self.keymaps[self.keys.accept] = func
    
    def clear_item_bindings(self):
        if self.keys.increase in self.keymaps:
            del self.keymaps[self.keys.increase]

        if self.keys.decrease in self.keymaps:
            del self.keymaps[self.keys.decrease]

        if self.keys.accept in self.keymaps:
            del self.keymaps[self.keys.accept]

    def clear_bindings(self):
        self.keymaps.clear()

    def handle_inputs(self):
        self.should_quit = False
        self._text_input = []
        callbacks = []
        for event in self.event_handler.get_events():
            if event.type == pygame.KEYDOWN:
                if event.key == self.keys.quit:
                    self.should_quit = True
                elif event.key in self.keymaps:
                    callbacks.append(self.keymaps[event.key])
                else:
                    self._text_input.append(event.unicode)

        for f in callbacks:
            f()

class NewGameMenu:
    def __init__(self, menu_renderer, menu_input, game_factory):
        self.menu_renderer = menu_renderer
        self.menu_input = menu_input
        self.game_factory = game_factory
        self.items = game_factory.menu_item_modifiers() \
                     + [ButtonMenuItem(self._start_game, "start game")]
        self.selected_item = 0
        self._should_start_game = False

    def run(self, screen):
        while True:
           self._prepare_menu_input()
           self.menu_input.handle_inputs()
           if self.menu_input.should_quit:
               return None
           if self._should_start_game:
               self._should_start_game = False
               self.game_factory.game(screen).run()
           if self.items[self.selected_item].update(self.menu_input):
               self.menu_renderer.render(self)
    
    def _prepare_menu_input(self):
        self.menu_input.clear_bindings()
        self.menu_input.bind_next_item(self._activate_next_item)
        self.menu_input.bind_previous_item(self._activate_previous_item)
        self.items[self.selected_item].bind(self.menu_input)

    def _start_game(self):
        self._should_start_game = True

    def _activate_next_item(self):
        self._activate_item((self.selected_item - 1) % len(self.items))

    def _activate_previous_item(self):
        self._activate_item((self.selected_item + 1) % len(self.items))

    def _activate_item(self, item_index):
        self.selected_item = item_index

class MenuRenderer:
    def __init__(self, screen, background_color, item_spacing, item_renderer):
        self.screen = screen
        self.background_color = background_color
        self.item_renderer = item_renderer
        self.item_spacing = item_spacing
        self.screen.surface.fill(background_color)
        self.screen.update()

    def render(self, menu):
        self.screen.surface.fill(self.background_color)
        for i in range(len(menu.items)):
            item_center = self._item_center(i, len(menu.items))
            is_active = False
            if i == menu.selected_item:
                is_active = True
            self.item_renderer.render(self.screen.surface, menu.items[i],
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
