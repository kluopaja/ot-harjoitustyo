class MenuItem:
    """Base class for menu items."""
    # TODO make abstract
    def text(self):
        """Returns the text for the menu item"""
        return "0"

    def bind(self, menu_input):
        pass

    def release(self, menu_input):
        pass

    def update(self):
        """Updates the menu item state.

        Returns: a boolean
            True if the state of the menu item was changed
            False otherwise
        """
        pass

class ValueBrowserMenuItem(MenuItem):
    def __init__(self, decrease_function, increase_function, value_function, description):
        self.decrease_function = decrease_function
        self.increase_function = increase_function
        self.value_function = value_function
        self.description = description

    def text(self):
        return self.description + str(self.value_function())

    def bind(self, menu_input):
        menu_input.bind_increase(self.increase_function)
        menu_input.bind_decrease(self.decrease_function)

    def update(self, menu_input):
        return True

class ButtonMenuItem(MenuItem):
    def __init__(self, button_function, text):
        self.button_function = button_function
        self._text = text

    def text(self):
        return self._text

    def bind(self, menu_input):
        menu_input.bind_accept(self.button_function)

    def update(self, menu_input):
        return True
