from pygame import Vector2
class MenuListRenderer:
    """A rendering class for MenuList"""
    def __init__(self, screen, background_color, item_spacing, item_renderer):
        """Initializes MenuListRenderer.

        Arguments:
            `screen`: A Screen
                The Screen to which the menu is rendered
            `background_color`: A tuple of 3
            `item_spacing`: A positive float
                The vertical distance between menu items in relative
                screen.surface coordinates.
        """
        self._screen = screen
        self._background_color = background_color
        self._item_renderer = item_renderer
        self._item_spacing = item_spacing

    def render(self, menu_items, selected_index):
        """Renders `menu_items`.

        Arguments:
            `menu_items`: A list of MenuItem objects
            `selected_index`: A non-negative integer or None
                The index of the selected MenuItem
                None if none of the items is selected
        """
        self._screen.surface.fill(self._background_color, update=True)
        for i in range(len(menu_items)):
            item_center = self._item_center(i, len(menu_items))
            is_active = False
            if i == selected_index:
                is_active = True
            self._item_renderer.render(self._screen.surface, menu_items[i],
                                       item_center, is_active)
        self._screen.update()

    def _item_center(self, item_index, total_items):
        """Returns a Vector2 corresponding to the item center"""
        screen_center = Vector2(self._screen.surface.get_rect().center)
        menu_height = self._item_spacing * total_items
        menu_start = screen_center - Vector2(0, menu_height)/2
        return menu_start + Vector2(0, self._item_spacing) * item_index


class MenuItemRenderer:
    def __init__(self, font_color):
        self.font_color = font_color

    def render(self, surface, menu_item, center, is_active):
        text = menu_item.text()
        if is_active:
            text = "-> " + text + " <-"

        surface.centered_text(text, center, self.font_color)
