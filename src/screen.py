import pygame
from drawing_surface import DrawingSurface


class Screen:
    def __init__(self, width, height):
        self.surface = DrawingSurface(
            pygame.display.set_mode((width, height), vsync=1))

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
