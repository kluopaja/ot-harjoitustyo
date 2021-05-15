class MenuItem:
    """Base class for menu items."""
    # TODO make abstract

    def text(self):
        """Returns the text for the menu item"""
        return "0"

    def bind(self, menu_input):
        pass

class ValueBrowserMenuItem(MenuItem):
    def __init__(self, decrease_function, increase_function, value_function,
                 description, accept_function=lambda: None):
        self.decrease_function = decrease_function
        self.increase_function = increase_function
        self.value_function = value_function
        self.accept_function = accept_function
        self.description = description

    def text(self):
        return self.description + str(self.value_function())

    def bind(self, menu_input):
        menu_input.bind_increase(self.increase_function)
        menu_input.bind_decrease(self.decrease_function)
        menu_input.bind_accept(self.accept_function)


class ButtonMenuItem(MenuItem):
    def __init__(self, button_function, description):
        self.button_function = button_function
        self.description = description

    def text(self):
        return self.description

    def bind(self, menu_input):
        menu_input.bind_accept(self.button_function)


class TextInputMenuItem(MenuItem):
    def __init__(self, description, get_text, set_text):
        self.description = description
        self.get_text = get_text
        self.set_text = set_text

    def text(self):
        return self.description + self.get_text()

    def bind(self, menu_input):
        menu_input.bind_text(self.get_text, self.set_text)

class MenuItemCollection:
    def __init__(self):
        self._subcollections = []

    def add_item(self, item):
        self._subcollections.append(SingleMenuItemCollection(item))

    def add_collection(self, collection):
        self._subcollections.append(collection)

    def clear(self):
        self._subcollections = []

    def get_item_list(self):
        result = []
        for subcollection in self._subcollections:
            result.extend(subcollection.get_item_list())
        return result

class SingleMenuItemCollection:
    def __init__(self, item):
        self._item = item

    def get_item_list(self):
        return [self._item]
