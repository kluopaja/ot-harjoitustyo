import string
import pygame

class MenuInput:
    def __init__(self, event_handler, menu_input_config):
        self.event_handler = event_handler
        self._config = menu_input_config
        self.keymaps = {}
        self.get_text_callback = None
        self.set_text_callback = None

    def bind_quit(self, func):
        self.keymaps[self._config.quit] = func

    def bind_next_item(self, func):
        self.keymaps[self._config.next_item] = func

    def bind_previous_item(self, func):
        self.keymaps[self._config.prev_item] = func

    def bind_increase(self, func):
        self.keymaps[self._config.increase] = func

    def bind_decrease(self, func):
        self.keymaps[self._config.decrease] = func

    def bind_accept(self, func):
        self.keymaps[self._config.accept] = func

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
                elif event.key == self._config.erase:
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
