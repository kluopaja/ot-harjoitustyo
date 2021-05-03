import pygame
import math
from pygame import Vector2
from pygame import Rect

class FloatRect:
    """Similar class to pygame.Rect except also with floats"""

    # TODO use Vector2?

    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def top(self):
        return self._y

    @top.setter
    def top(self, value):
        self._y = value

    @property
    def bottom(self):
        return self._y + self._height

    @bottom.setter
    def bottom(self, value):
        self._y = value - self._height

    @property
    def left(self):
        return self._x

    @left.setter
    def left(self, value):
        self._x = value

    @property
    def right(self):
        return self._x + self.width

    @right.setter
    def right(self, value):
        self._x = value - self._width

    @property
    def center(self):
        return (self._x + self._width / 2, self._y + self._height / 2)

    @center.setter
    def center(self, value):
        self._x = value[0] - self._width / 2
        self._y = value[1] - self._height / 2

    @property
    def topleft(self):
        return (self._x, self._y)

    @topleft.setter
    def topleft(self, value):
        self._x = value[0]
        self._y = value[1]

    @property
    def size(self):
        return (self._width, self._height)

    @size.setter
    def size(self, value):
        self._width = value[0]
        self._height = value[1]

    @property
    def midtop(self):
        return (self._x + self._width / 2, self._y)

    @midtop.setter
    def midtop(self, value):
        self._x = value[0] - self._width / 2
        self._y = value[1]

    @property
    def topright(self):
        return (self._x + self._width, self._y)

    @topright.setter
    def topright(self, value):
        self._x = value[0] - self._width
        self._y = value[1]

    @property
    def bottomleft(self):
        return (self._x, self._y + self._height)

    @topright.setter
    def topright(self, value):
        self._x = value[0]
        self._y = value[1] - self._height

    def copy(self):
        return FloatRect(self._x, self._y, self._width, self._height)

    def __repr__(self):
        return f"FloatRect({self._x}, {self._y}, {self._width}, {self._height})"

# NOTE the window resizing hasn't been implemented yet
# but should work as long as we always create a new DrawingSurface
# at each rendering
class DrawingSurface:
    def __init__(self, surface, screen, absolute_topleft):
        """Initializes a DrawingSurface.

        Args:
            `surface`: A pygame.Surface
            `screen`: A Screen object
            `absolute_topleft`: Vector2
                The absolute pixel coordinates of the top left corner
        """

        self._surface = surface
        self._screen = screen
        self._absolute_topleft = absolute_topleft

    def subsurface(self, area):
        rect_topleft = self._to_pixel_coordinates(area.topleft)
        size = self._to_pixel_coordinates(area.size)
        _area = Rect(rect_topleft[0], rect_topleft[1], size[0], size[1])
        new_absolute_topleft = rect_topleft + self._absolute_topleft
        return DrawingSurface(self._surface.subsurface(_area), self._screen,
                              new_absolute_topleft)

    def get_relative_width(self):
        """The width of the drawing surface relative to the height.

        """
        return self._surface.get_width() / self._surface.get_height()

    def blur(self, radius):
        size = self._surface.get_size()
        tmp = pygame.transform.smoothscale(self._surface, (size[0]//radius, size[1]//radius))
        dirty_rect = self._surface.blit(
            pygame.transform.scale(tmp, self._surface.get_size()),
            (0, 0)
        )
        self._add_dirty_rect(dirty_rect)

    def draw_line(self, begin, end, color, width=1, scaled=True):
        """Draws a line to `self._surface`

        Args:
            `color` a tuple of length 3 or 4
            `begin` a Vector2
            `end` a Vector2
            `width` a positive number
                If scaled == False:
                    the fraction of the self._screen's height
                If scaled == True:
                    the fraction of the self's height
        """

        _begin = self._to_pixel_coordinates(begin)
        _end = self._to_pixel_coordinates(end)
        if not scaled:
            _width = max(1, int(self._screen.get_height() * width))
        else:
            _width = max(1, int(self._surface.get_height() * width))

        dirty_rect = pygame.draw.line(self._surface, color, _begin, _end, _width)
        self._add_dirty_rect(dirty_rect)

    def draw_image(self, image, position, rotation, height):
        """Draws image

        Args:
            `image`
            `position` Vector2
                The position of the center of the image
            `rotation`: radians
                The rotation, positive is to the ccw
            `height`: a positive number
                height of the image as the fraction of self's height
        """
        _position = self._to_pixel_coordinates(position)
        _height = height * self._surface.get_height()
        degrees_rotation = math.degrees(rotation)
        zoom_factor = _height / image.get_height_pixels()
        final_image = pygame.transform.rotozoom(image.image, degrees_rotation,
                                                zoom_factor)
        area = final_image.get_rect()
        area.center = _position
        dirty_rect = self._surface.blit(final_image, area.topleft)
        self._add_dirty_rect(dirty_rect)

    def draw_image_from_array(self, array, position, height):
        """Draws image from a numpy array.

        Args:
            `array` a numpy array of shape (?, ?, 4) (ARGB)
            `position` Vector2
                The position of the top left corner.

        """
        _position = self._to_pixel_coordinates(position)
        _height = height * self._surface.get_height()
        image_surface = pygame.surfarray.make_surface(array[:, :, 1:]).convert_alpha()
        _width = _height * image_surface.get_width() / image_surface.get_height()
        _height = int(_height)
        _width = int(_width)
        pygame.surfarray.pixels_alpha(image_surface)[:, :] = array[:, :, 0]
        final_surface = pygame.transform.smoothscale(image_surface, (_width, _height))
        dirty_rect = self._surface.blit(final_surface, _position)
        self._add_dirty_rect(dirty_rect)

    def fill(self, color, update=False):
        """Fills `self._surface` with `color`

        Args:
            `color` a tuple of length 3 or 4
            `update` a boolean
                True: the screen will be forced to update
                False: Only the previous location of drawn elements will
                be updated
        """
        if update:
            self._screen.add_dirty_rect(self._surface.fill(color))
        else:
            self._surface.fill(color)


    def get_rect(self):
        """Returns a FloatRect of the relative screen area"""

        return FloatRect(0, 0, self.get_relative_width(), 1)

    def get_size(self):
        """Returns a Vector2 of the screen relative area"""

        return Vector2(self.get_relative_width(), 1)

    def centered_text(self, text, position, color):
        """Draws `text` centered at `position`
        """
        _position = self._to_pixel_coordinates(position)
        text_surface = self._screen.font.render(text, True, color)
        dest = text_surface.get_rect()
        dest.center = (_position[0], _position[1])
        dirty_rect = self._surface.blit(text_surface, dest.topleft)
        self._add_dirty_rect(dirty_rect)

    def midtop_text(self, text, position, color):
        """Draws `text` with top middle at `position`
        """
        _position = self._to_pixel_coordinates(position)
        text_surface = self._screen.font.render(text, True, color)
        dest = text_surface.get_rect()
        dest.midtop = (_position[0], _position[1])
        dirty_rect = self._surface.blit(text_surface, dest.topleft)
        self._add_dirty_rect(dirty_rect)

    def topleft_text(self, text, position, color):
        """Draws `text` with top left edge at `position`
        """
        _position = self._to_pixel_coordinates(position)
        text_surface = self._screen.font.render(text, True, color)
        dest = text_surface.get_rect()
        dest.topleft = (_position[0], _position[1])
        dirty_rect = self._surface.blit(text_surface, dest.topleft)
        self._add_dirty_rect(dirty_rect)

    def _to_pixel_coordinates(self, relative_coords):
        tmp = Vector2(relative_coords) * self._surface.get_size()[1]
        # reduces jitter in the rendering
        tmp[0] = round(tmp[0])
        tmp[1] = round(tmp[1])
        return tmp

    def _add_dirty_rect(self, dirty_rect):
        """Add `dirty_rect` to `self._screen`.

        Transforms coordinates from `self._surface` space to
        the absolute screen coordinates and adds the transformed
        rect to `self._screen`.

        NOTE: modifies `dirty_rect`!

        Args:
            `dirty_rect`: A pygame.Rect
                The pixel coordinates of the rect with respect to
                `self._surface`
        """
        dirty_rect.topleft += self._absolute_topleft
        self._screen.add_dirty_rect(dirty_rect)


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

class Image:
    """Class for storing and drawing an image.

    """

    def __init__(self, image_path):
        self.image = pygame.image.load(image_path).convert_alpha()

    def set_aspect_ratio(self, width, height):
        """Changes the aspect ratio."""
        new_ratio = width / height
        current_ratio = self.get_width_pixels() / self.get_height_pixels()
        new_width = self.get_width_pixels()
        new_height = self.get_height_pixels()
        if new_ratio > current_ratio:
            new_width = int(new_ratio * new_height)
        else:
            new_height = int(new_width / new_ratio)

        self.image = pygame.transform.scale(self.image,
                                            (new_width, new_height)).convert_alpha()

    def get_height_pixels(self):
        return self.image.get_height()

    def get_width_pixels(self):
        return self.image.get_width()
