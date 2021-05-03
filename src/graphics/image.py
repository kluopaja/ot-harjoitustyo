import pygame
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
