import pygame
class EventHandler:
    def get_events(self):
        return pygame.event.get()

    def get_pressed(self):
        return pygame.key.get_pressed()
