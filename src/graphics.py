import pygame
from pygame import Vector2
import math
from abc import ABC, abstractmethod
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
    def __init__(self, points, color):
        self._points = points
        self.color = color
        self._location = (0, 0)
        self._rotation = 0

    def draw(self, surface, offset=(0, 0)):
        '''Draws image on `surface`.

        Returns a list Rects containing the changed pixels'''

        dirty_rects = []
        # TODO draw only visible if necessary
        for i in range(len(self._points)-1):
            start = self._transform_point(self._points[i])
            end = self._transform_point(self._points[i+1])
            dirty_rects.append(pygame.draw.aaline(surface, self.color, start,
                                                 end))
        return dirty_rects

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value
        for i in range(len(self._points)):
            self._points[i][0] += self._location[0]
            self._points[i][1] += self._location[1]

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value

    def _transform_point(self, point):
        vec = Vector2(point)
        vec = vec.rotate_rad(self._rotation)
        vec += Vector2(self._location)
        return (vec[0], vec[1])

class ImageGraphic(Graphic):
    def __init__(self, location, image_path):
        self._sprite = Sprite(location, image_path)
        self._single_group = pygame.sprite.GroupSingle(self._sprite)

    def draw(self, surface, offset=(0, 0)):
        '''Draws image on `surface`.

        Returns a list of Rects containing the changed pixels'''

        if not self._sprite.overlaps(surface.get_rect().move(offset)):
            return []

        self._sprite.rect.move_ip(-offset[0], -offset[1])
        self._single_group.draw(surface)
        self._sprite.rect.move_ip(offset[0], offset[1])
        return [self._sprite.rect.copy()]

    @property
    def location(self):
        return self._sprite.center

    @location.setter
    def location(self, value):
        self._sprite.center = value

    @property
    def rotation(self):
        return self._sprite.rotation

    @rotation.setter
    def rotation(self, value):
        self._sprite.rotation = value

class Sprite(pygame.sprite.Sprite):
    def __init__(self, center_pos, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 40))
        self._image_original = self.image
        self.rect = self.image.get_rect()
        self.rect.center = center_pos

        self._rotation = 0

    def rotate_to(self, radians):
        degrees = math.degrees(radians)
        self.image = pygame.transform.rotate(self._image_original, degrees)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    @property
    def center(self):
        return self.rect.center

    @center.setter
    def center(self, value):
        self.rect.center = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.rotate_to(value)

    def overlaps(self, region):
        return self.rect.colliderect(region)
