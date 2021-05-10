import pygame
from graphics.drawing_surface import DrawingSurface
from pygame import Vector2

class Screen:
    def __init__(self, width, height, font_size):
        pygame.init()
        self._height = height
        font_pixels = int(self.get_height() * font_size)
        self.font = pygame.font.SysFont("monospace", font_pixels)

        self.surface = DrawingSurface(
            pygame.display.set_mode((width, height), vsync=1),
            self, Vector2(0))
        self._previous_dirty_rects = []
        self._current_dirty_rects = []

    def resize(self, width, height):
        self.surface = DrawingSurface(
            pygame.display.set_mode((width, height), vsync=1), Vector2(0))
        self._previous_dirty_rects = None
        self._current_dirty_rects = []

    def update(self):
        """Updates screen."""

        pygame.display.update(self._previous_dirty_rects + self._current_dirty_rects)
        self._previous_dirty_rects = self._current_dirty_rects
        self._current_dirty_rects = []

    def add_dirty_rect(self, rect):
        """Adds a pygame.Rect to the list of dirty rects"""
        self._current_dirty_rects.append(rect)

    def get_height(self):
        return self._height
