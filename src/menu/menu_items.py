class MenuItem:
    """Base class for menu items."""

    def text(self):
        """Returns the text for the menu item"""
        return "0"

    def bind(self, menu_input):
        """Binds the MenuItem to a MenuInput `menu_input`"""
        pass

class ValueBrowserMenuItem(MenuItem):
    """A MenuItem supporting browsing through a list of values"""
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
    """A MenuItem supporting "press" operation"""
    def __init__(self, button_function, description):
        self.button_function = button_function
        self.description = description

    def text(self):
        return self.description

    def bind(self, menu_input):
        menu_input.bind_accept(self.button_function)


class TextInputMenuItem(MenuItem):
    """A MenuItem with a text input box"""
    def __init__(self, description, get_text, set_text):
        self.description = description
        self.get_text = get_text
        self.set_text = set_text

    def text(self):
        return self.description + self.get_text()

    def bind(self, menu_input):
        menu_input.bind_text(self.get_text, self.set_text)

class MenuItemCollection:
    """A class for organizing the MenuItems.

    Holds either other MenuItemCollection or single items.

    Useful for having a list of MenuItems that has to support
    adding and deleting MenuItems at some positions in the middle
    of the list.
    """
    def __init__(self):
        """Initializes an empty MenuItemsCollection"""
        self._subcollections = []

    def add_item(self, item):
        """Adds a single MenuItem `item` to the end of `self`"""
        self._subcollections.append(_SingleMenuItemCollection(item))

    def add_collection(self, collection):
        """Adds another MenuItemCollection to the end of `self`"""
        self._subcollections.append(collection)

    def clear(self):
        """Empties `self`"""
        self._subcollections = []

    def get_item_list(self):
        """Transforms `self` into a list of MenuItems"""
        result = []
        for subcollection in self._subcollections:
            result.extend(subcollection.get_item_list())
        return result

class _SingleMenuItemCollection:
    """A helper class to store a single MenuItem"""
    def __init__(self, item):
        self._item = item

    def get_item_list(self):
        return [self._item]
