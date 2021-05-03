from pygame import Vector2
class Camera:
    """Camera class.

    The class for transforming drawing commands from world space
    to the relative DrawingSurface space.

    """
    def __init__(self, view_height):
        self.location = Vector2(0, 0)
        self.drawing_surface = None
        self._view_height = view_height
        self._surface_center = Vector2(0, 0)

    def set_drawing_surface(self, surface):
        self.drawing_surface = surface
        self._surface_center = self.drawing_surface.get_size() / 2

    def draw_line(self, begin, end, color, width):

        """
        Args:
            `color` a tuple of length 3 or 4
            `begin` a Vector2
            `end` a Vector2
            `width` a scalar

            All coordinate values are in world coordinates
        """

        if self.drawing_surface is None:
            return

        _begin = self._to_drawing_surface_coords(begin)
        _end = self._to_drawing_surface_coords(end)

        _width = width / self._view_height

        self.drawing_surface.draw_line(_begin, _end, color, _width, scaled=True)

    def draw_image(self, image, location, rotation, height):
        if self.drawing_surface is None:
            return

        _location = self._to_drawing_surface_coords(location)
        _height = height / self._view_height
        self.drawing_surface.draw_image(image, _location, rotation, _height)

    def _to_drawing_surface_coords(self, world_coords):
        return (world_coords - self.location) / self._view_height + self._surface_center

