import string
import pygame

class MenuInput:
    """A class for handling menu inputs"""
    def __init__(self, event_handler, menu_input_config):
        """Initializes MenuInput

        Arguments:
            `event_handler`: A EventHandler
            `menu_input_config`: A MenuInputConfig
                Defines the keymaps
        """
        self._event_handler = event_handler
        self._config = menu_input_config
        self._keymaps = {}
        self._get_text_callback = None
        self._set_text_callback = None

    def bind_quit(self, func):
        """Binds function `func` to the quit key"""
        self._keymaps[self._config.quit] = func

    def bind_next_item(self, func):
        """Binds function `func` to the next item key"""
        self._keymaps[self._config.next_item] = func

    def bind_previous_item(self, func):
        """Binds function `func` to the previous item key"""
        self._keymaps[self._config.prev_item] = func

    def bind_increase(self, func):
        """Binds function `func` to the increase item value key"""
        self._keymaps[self._config.increase] = func

    def bind_decrease(self, func):
        """Binds function `func` to the decrease item value key"""
        self._keymaps[self._config.decrease] = func

    def bind_accept(self, func):
        """Binds function `func` to the accept item key"""
        self._keymaps[self._config.accept] = func

    def bind_text(self, get_text, set_text):
        """Binds functions `get_text` and `set_text` to text input"""
        self._get_text_callback = get_text
        self._set_text_callback = set_text

    def clear_bindings(self):
        """Clears functions bound to keys or text input"""
        self._keymaps.clear()
        self._set_text_callback = None
        self._get_text_callback = None

    def handle_inputs(self):
        """Handles inputs in the order the key events happened"""
        callbacks = []
        for event in self._event_handler.get_events():
            if event.type == pygame.KEYDOWN:
                if event.key in self._keymaps:
                    callbacks.append(self._keymaps[event.key])
                elif event.key == self._config.erase:
                    callbacks.append(self._erase_text)
                else:
                    callbacks.append(lambda c=event.unicode: self._add_text(c))

        # important to call there only here to avoid the side effects
        # of the callbacks to self
        for f in callbacks:
            f()

    def _erase_text(self):
        if (self._set_text_callback is None) or (self._get_text_callback is None):
            return
        self._set_text_callback(self._get_text_callback()[0:-1])

    def _add_text(self, character):
        if character in string.whitespace:
            return
        if (self._set_text_callback is None) or (self._get_text_callback is None):
            return
        self._set_text_callback(self._get_text_callback() + character)
