import pygame
import logging
from pygame import Vector2, Rect
import math
from abc import ABC, abstractmethod
from shapes import Rectangle
class Graphic(ABC):
    @abstractmethod
    def draw(self, surface, offset=(0, 0)):
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

    def draw(self, surface, offset=None):
        """Draws image on `surface`.

        Arguments:
            `surface`: DrawingSurface
                The target of drawing
            `offset`: Vector2 or None
                Sets the coordinates of `surface` that are used as an origo
                for the drawing.
                If None, then Vector2(0, 0) is used as an origo

        Returns:
            `dirty_rects`: a list of Rect
                contains the changed pixels"""

        if offset is None:
            offset = Vector2(0)

        dirty_rects = []
        # TODO draw only visible if necessary
        for line in self._polyline.lines:
            begin = line.begin - offset
            end = line.end - offset
            dirty_rects.append(surface.draw_line(begin, end, self.color, self.width))
        return dirty_rects

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
        self._rectangle = rectangle
        self._image = image
        self._image.resize(self._rectangle.size())

    @classmethod
    def from_image_path(cls, image_path, center_offset, size):
        """Creates ImageGraphic from an image file.

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
        helper_rect = Rect(0, 0, size[0], size[1])
        helper_rect.center = (math.floor(center_offset[0]), math.floor(center_offset[1]))
        rectangle = Rectangle.from_rect(helper_rect)
        image = Image(image_path)
        return ImageGraphic(rectangle, image)

    def draw(self, surface, offset=None):
        '''Draws image on `surface`.

        Returns a list of Rects containing the changed pixels'''

        if offset is None:
            offset = Vector2(0)

        target_rectangle = Rectangle.from_rect(surface.get_rect().move(offset))
        if not self._rectangle.intersects(target_rectangle):
            return []

        return self._image.draw(surface, self._rectangle.center() - Vector2(offset))

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
        self._image.rotate_to(self._rectangle.rotation)

class Image:
    """Class for storing and drawing an image.

    """
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path)
        self._image_not_rotated = self.image

    def rotate_to(self, radians):
        """Changes the image rotation to `radians`.

        Arguments:
            `radians` the amount of rotation.
        """
        degrees = math.degrees(radians)
        self.image = pygame.transform.rotate(self._image_not_rotated, degrees)

    def resize(self, size):
        if size[0] < 0 or size[1] < 0:
            raise ValueError("The resize dimensions cannot be negative")

        size_tuple = (int(size[0]), int(size[1]))
        self.image = pygame.transform.scale(self.image, size_tuple)
        self._image_not_rotated = pygame.transform.scale(self._image_not_rotated, size_tuple)

    def draw(self, surface, center):
        rect = self.image.get_rect()
        rect.center = (math.floor(center[0]), math.floor(center[1]))
        return [surface.blit(self.image, rect)]
