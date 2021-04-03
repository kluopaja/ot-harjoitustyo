class DrawingSurface:
    """A wrapper around the pygame.Surface"""
    def __init__(self, surface):
        self.surface = surface

    def subsurface(self, area):
        return DrawingSurface(self.surface.subsurface(area))

    def blit(self, source, dest=None):
        """Draws `source` to `self.surface`. Optionally at pygame.Rect `dest`

        Returns:
            A pygame.Rect corresponding to the changed area.
        """
        return self.surface.blit(source, dest)

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

    def fill(self, color):
        """Fills `self.surface` with `color`

        Args:
            `color` a tuple of length 3 or 4"""
        self.surface.fill(color)

    def get_rect(self):
        """Returns a Rect of the screen area"""
        return self.surface.get_rect()
