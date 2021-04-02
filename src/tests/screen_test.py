import pygame
class ScreenStub:
    def __init__(self, width, height):
        self.surface = pygame.Surface((width, height))
        self.blit_calls = []
        self.draw_line_calls = []
        self.fill_calls = []
        self.update_calls = []
        self.get_rect_calls = []

    def blit(self, source, dest=None):
        self.blit_calls.append({'source': source, 'dest': dest})
        return self.surface.blit(source, dest)

    def draw_line(self, begin, end, color, width=1):
        self.draw_line_calls.append({'color': color, 'begin': begin, 'end': end,
                                     'width': width})
        return pygame.draw.line(self.surface, color, begin, end, width)

    def fill(self, color):
        self.fill_calls.append({'color': color})
        self.surface.fill(color)

    def update(self, dirty_rects=None):
        self.update_calls.append({'dirty_rects': dirty_rects})

    def get_rect(self):
        self.get_rect_calls.append({})
        return self.surface.get_rect()
