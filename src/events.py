import pygame


class EventHandler:
    """A class for event handling"""
    def get_events(self):
        """Returns the list of the events.

        Returns: A list of pygame events"""
        return pygame.event.get()

    def get_pressed(self):
        """Returns an "array" of booleans of currently pressed keys

        Returns an object indexable with [] operator.

        Keys are pygame keycodes and the value is either True
        if the key is currently pressed or False otherwise"""
        return pygame.key.get_pressed()
