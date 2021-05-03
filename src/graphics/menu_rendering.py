from pygame import Vector2
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
