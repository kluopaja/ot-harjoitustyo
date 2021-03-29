import pygame
import math
"""
class ImageObject:
    def __init__(self, center, image_path):
        self.sprite = Sprite(center, image_path)
        self.center = center
        self.rotation = 0
        self._simple_group = pygame.sprite.GroupSimple(self.sprite)

    @property
    def center(self):
        return self.sprite.rect.center

    @center.setter
    def center(self, value):
        self.sprite.rect.center = value

    @property
    def rotation(self):
        return self.rotation

    @rotation.setter
    def rotation(self, value):
        self.rotation = value
        self.sprite.rotate(value)

    def draw(self, surface):
        '''Draws image on `surface`.

        Returns a Rect containing the changed pixels'''
        self._simple_group.draw(surface)
        return self.sprite.rect

    # TODO draw_transformed(self, region, surface)

    def overlaps(self, region):
        return self.sprite.rect.colliderect(region)

"""

class ImageSprite(pygame.sprite.Sprite):
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
