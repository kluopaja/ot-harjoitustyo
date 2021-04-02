import pygame
class Screen:
    def __init__(self, width, height):
        self.surface = pygame.display.set_mode((width, height), vsync=1)

    def blit(self, source, dest=None):
        """Draws `source` to `self.surface`. Optionally at pygame.Rect `dest`

        Returns:
            A pygame.Rect corresponding to the changed area.
        """
        return self.surface.blit(source, dest)

    def draw_line(self, color, begin, end, width=1):
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

    def update(self, dirty_rects=None):
        """Updates screen.

        If `dirty_rects` is None, then updates the whole screen.
        Otherwise updates the screen only at `dirty_rects`
        Args:
            `dirty_rects`: None or list of Rects
        """
        if dirty_rects is None:
            pygame.display.update()
        else:
            pygame.display.update(dirty_rects)

    def get_rect(self):
        """Returns a Rect of the screen area"""
        return self.surface.get_rect()


