from pygame import Vector2
import pygame
from graphics.drawing_surface import DrawingSurface

class Screen:
    """A class for managing the application window.

    Attributes:
        `font`: A pygame.font.Font
        `surface`: A DrawingSurface
            Corresponds to the whole Screen area

    About dirty rects:
        Due to the performance limitations of pygame, the actual
        drawing to the display must be done only at those places
        which differ from the last update.

    """
    def __init__(self, width, height, font_size):
        """Initializes Screen.

        Arguments:
            `width`: A positive integer
                The width of the window in pixels
            `height`: A positive integer
                The height of the window in pixels
            `font_size`: positive float
                Font size relative to `height`. Good values are something
                like 0.02.
        """
        pygame.init()
        self._height = height
        font_pixels = int(self.get_height() * font_size)
        self.font = pygame.font.SysFont("monospace", font_pixels)

        self.surface = DrawingSurface(
            pygame.display.set_mode((width, height), vsync=1),
            self, Vector2(0))
        self._previous_dirty_rects = []
        self._current_dirty_rects = []

    def update(self):
        """Updates screen.

        Only updates area that was either marked dirty for previous rendering
        (something that might no longer be rendered, i.e. should be cleared)
        or marked dirty for this rendering.
        """
        pygame.display.update(self._previous_dirty_rects + self._current_dirty_rects)
        self._previous_dirty_rects = self._current_dirty_rects
        self._current_dirty_rects = []

    def add_dirty_rect(self, rect):
        """Adds a pygame.Rect to the list of dirty rects"""
        self._current_dirty_rects.append(rect)

    def get_height(self):
        """Returns the height of the Screen drawing area in pixels"""
        return self._height
