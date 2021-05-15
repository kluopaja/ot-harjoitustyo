import math
from abc import ABC, abstractmethod
from game.shapes import Rectangle
from graphics.image import Image
from utils.float_rect import FloatRect


class Graphic(ABC):
    @abstractmethod
    def draw(self, camera):
        pass

    @property
    @abstractmethod
    def location(self):
        pass

    @location.setter
    @abstractmethod
    def location(self, value):
        pass

    @property
    @abstractmethod
    def rotation(self):
        pass

    @rotation.setter
    @abstractmethod
    def rotation(self, value):
        pass


class PolylineGraphic(Graphic):
    def __init__(self, polyline, color, width):
        self._polyline = polyline
        self.color = color
        self.width = width

    def draw(self, camera):
        """Draws image on `camera`.

        Arguments:
            `camera`: Camera
                The target of drawing

        """
        for line in self._polyline.lines:
            camera.draw_line(line.begin, line.end, self.color, self.width)

    @property
    def location(self):
        return self._polyline.location

    @location.setter
    def location(self, value):
        self._polyline.location = value

    @property
    def rotation(self):
        return self._polyline.rotation

    @rotation.setter
    def rotation(self, value):
        self._polyline.rotation = value


class ImageGraphic(Graphic):
    """Class for movable and rotatable images."""

    def __init__(self, rectangle, image):
        """

        Args:
            `rectangle`: A Rectangle
            `image`: An Image

        NOTE: The drawing of the image is done by setting its height to
        match that of the `rectangle`. Therefore `rectangle` and `image`
        should have (approximately) the same aspect ratio!
        """

        rectangle_size = rectangle.size()
        rectangle_aspect_ratio = rectangle_size[0] / rectangle_size[1]
        image_aspect_ratio = image.get_width_pixels() / image.get_height_pixels()

        if abs(rectangle_aspect_ratio - image_aspect_ratio) > 0.1:
            raise ValueError("`rectangle` and `image` should have approximately \
                              the same aspect ratio!")

        self._rectangle = rectangle
        self._image = image

    @classmethod
    def from_image_path(cls, image_path, center_offset, size):
        """Creates ImageGraphic from an image file.

        Scales image to match the `size` aspect ratio.

        Arguments:
            `image_path`: pathlib.Path object
                Denotes the path to the image.
            `center_offset`: Vector2
                The position of the center of the image relative to the
                `location` of the ImageGraphic
            `size`: Vector2
                The dimensions of the image

        Returns:
            An ImageGraphic object
        """

        helper_rect = FloatRect(0, 0, size[0], size[1])
        helper_rect.center = (math.floor(
            center_offset[0]), math.floor(center_offset[1]))
        rectangle = Rectangle.from_rect(helper_rect)
        image = Image(image_path)
        image.set_aspect_ratio(helper_rect.width, helper_rect.height)
        return ImageGraphic(rectangle, image)

    def draw(self, camera):
        """Draws image on `camera`.

        """
        camera.draw_image(self._image, self._rectangle.center(),
                    self._rectangle.rotation, self._rectangle.size()[1])

    @property
    def location(self):
        return self._rectangle.location

    @location.setter
    def location(self, value):
        self._rectangle.location = value

    @property
    def rotation(self):
        return self._rectangle.rotation

    @rotation.setter
    def rotation(self, value):
        self._rectangle.rotation = value
