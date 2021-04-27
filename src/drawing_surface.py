import pygame


class DrawingSurface:
    """A wrapper around the pygame.Surface"""

    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.SysFont("monospace", 24)

    def subsurface(self, area):
        return DrawingSurface(self.surface.subsurface(area))

    #TODO remove none?
    def blit(self, source, dest=None):
        """Draws `source` to `self.surface`.

        Args:
            `source` a pygame surface
            `dest`: A tuple of two coordinates or None
                The top left corner of the `source`

        Returns:
            A pygame.Rect corresponding to the changed area.
        """
        if dest is None:
            return self.surface.blit(source, (0, 0))

        return self.surface.blit(source, dest)

    def blur(self, radius):
        size = self.surface.get_size()
        tmp = pygame.transform.smoothscale(self.surface, (size[0]//radius, size[1]//radius))
        self.blit(pygame.transform.scale(tmp, self.surface.get_size()))

    def draw_line(self, begin, end, color, width=1):
        """Draws a line to `self.surface`

        Args:
            `color` a tuple of length 3 or 4
            `begin` a Vector2
            `end` a Vector2
            `width` an integer >= 1

        Returns:
            A pygame.Rect corresponding to the changed area.
        """
        return pygame.draw.line(self.surface, color, begin, end, width)

    def draw_image(self, image, position):
        """Draws image from a numpy array.

        Args:
            `image` a numpy array of shape (?, ?, 4) (ARGB)
            `position` Vector2
                The position of the top left corner.

        Returns:
            A pygame.Rect corresponding to the changed area.
        """
        surface = pygame.surfarray.make_surface(image[:, :, 1:]).convert_alpha()
        # TODO will locking break something if I don't unlock?
        pygame.surfarray.pixels_alpha(surface)[:, :] = image[:, :, 0]
        return self.blit(surface, position)

    def fill(self, color):
        """Fills `self.surface` with `color`

        Args:
            `color` a tuple of length 3 or 4"""
        self.surface.fill(color)

    def get_rect(self):
        """Returns a Rect of the screen area"""
        return self.surface.get_rect()

    def centered_text(self, text, position, color):
        """Draws `text` centered at `position`
        """
        # TODO read about performance issues related to this!
        text_surface = self.font.render(text, True, color)
        dest = text_surface.get_rect()
        dest.center = (position[0], position[1])
        return self.blit(text_surface, dest)

    def midtop_text(self, text, position, color):
        """Draws `text` with top middle at `position`
        """
        # TODO read about performance issues related to this!
        text_surface = self.font.render(text, True, color)
        dest = text_surface.get_rect()
        dest.midtop = (position[0], position[1])
        return self.blit(text_surface, dest)

    def topleft_text(self, text, position, color):
        """Draws `text` with top left edge at `position`
        """
        # TODO read about performance issues related to this!
        text_surface = self.font.render(text, True, color)
        dest = text_surface.get_rect()
        dest.topleft = (position[0], position[1])
        return self.blit(text_surface, dest)
