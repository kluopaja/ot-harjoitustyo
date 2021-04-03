import pygame
class ScreenStub:
    def __init__(self, width, height):
        self.surface = pygame.Surface((width, height))
        self.update_calls = []

    def update(self, dirty_rects=None):
        self.update_calls.append({'dirty_rects': dirty_rects})

