import pygame
class Image:
    """Class for storing and drawing an image.

    Attributes:
        `image`: A pygame.Surface
            contains the image pixels
    """

    def __init__(self, image_path):
        """Initializes Image.

        Arguments:
            `image_path`: A Path
        """
        self.image = pygame.image.load(image_path).convert_alpha()

    def set_aspect_ratio(self, width, height):
        """Changes the aspect ratio.

        Changes the aspect ratio to match the aspect ratio
        of (`width`, `height`) by only stretching but not shrinking the image.

        Arguments:
            `width`: a positive float
            `height`: a positive foat
        """
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
