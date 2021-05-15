from pygame import Vector2
class Camera:
    """Camera class.

    The class for transforming drawing commands from world space
    to the relative DrawingSurface space.

    Attributes:
        `location`: A pygame.Vector2
            The location the camera is pointing at.
    """
    def __init__(self, view_height):
        self.location = Vector2(0, 0)
        self._drawing_surface = None
        self._view_height = view_height
        self._surface_center = Vector2(0, 0)

    def set_drawing_surface(self, surface):
        self._drawing_surface = surface
        self._surface_center = self._drawing_surface.get_size() / 2

    def draw_line(self, begin, end, color, width):

        """
        Args:
            `begin` a Vector2
            `end` a Vector2
            `color` a tuple of length 3 or 4
            `width` a scalar

            All coordinate values are in world coordinates
        """

        if self._drawing_surface is None:
            return

        _begin = self._to_drawing_surface_coords(begin)
        _end = self._to_drawing_surface_coords(end)

        _width = width / self._view_height

        self._drawing_surface.draw_line(_begin, _end, color, _width, scaled=True)

    def draw_image(self, image, location, rotation, height):
        """Draws image on Camera.

        Arguments:
            `image`: A Image
            `location`: A pygame.Vector2
                The center of the image in game world coordinates.
            `rotation`: Radians (a float)
                Positive rotation mean counter-clockwise
            `height`: A float
                The height of the image in the game world units.
        """
        if self._drawing_surface is None:
            return

        _location = self._to_drawing_surface_coords(location)
        _height = height / self._view_height
        self._drawing_surface.draw_image(image, _location, rotation, _height)

    def _to_drawing_surface_coords(self, world_coords):
        return (world_coords - self.location) / self._view_height + self._surface_center
