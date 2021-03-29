from pygame import Rect
import logging
import sprite
from pathlib import Path
from pygame.sprite import Group
import pygame
import time
class GameInput:
    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.keymaps = {}
        self.should_quit = False

    def bind_keys(self, new_keymaps):
        for keycode in new_keymaps:
            if keycode in self.keymaps:
                raise Exception('Key already bound to a function')
            self.keymaps[keycode] = new_keymaps[keycode]

    def handle_inputs(self):
        self.should_quit = False
        for event in self.event_handler.get_events():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.should_quit = True

        pressed = self.event_handler.get_pressed()

        for keycode in self.keymaps:
            if pressed[keycode]:
                self.keymaps[keycode]()

class GameState:
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def run_tick(self, delta_time):
        self._update_objects(delta_time)

    def _update_objects(self, delta_time):
        for game_object in self.game_objects:
            game_object.update(delta_time)

def sleep_until(until):
    if time.time() > until:
        Exception("Too slow computer, skipping frames")

    while time.time() < until:
        pass

class GameLoop:
    def __init__(self, game_input, game_state, game_renderer):
        self.game_input = game_input
        self.game_state = game_state
        self.game_renderer = game_renderer

    def run(self):
        previous_time = time.time()
        clock = pygame.time.Clock()
        while True:
            self.game_input.handle_inputs()
            if self.game_input.should_quit:
                return

            self.game_state.run_tick(1/60)
            self.game_renderer.render(self.game_state.game_objects)
            sleep_until(previous_time + 1/60)
            curr_time = time.time()
            logging.debug(f'fps: {1/(curr_time - previous_time)}')
            previous_time = curr_time


class GameRenderer:
    def __init__(self, screen, game_view):
        self._screen = screen
        self._game_view = game_view
        self._screen.fill((50, 50, 255))
        self._previous_dirty_rects = []
        pygame.display.update()

    def add_game_view(self, tracked_object):
        resolution = self.screen.get_window_size()
        size = self._screen.get_window_size()
        self.game_view = GameView(tracked_object, size, resolution)

    def render(self, game_objects):
        self._screen.fill((50, 50, 255))
        dirty_rects = self._game_view.render(self._screen, game_objects)
        #pygame.display.update()
        pygame.display.update(self._previous_dirty_rects)
        pygame.display.update(dirty_rects)
        self._previous_dirty_rects = dirty_rects

def constant_view_locator(x, y):
    def _inner():
        return (x, y)
    return _inner

class GameView:
    def __init__(self, view_locator, size):
        self.view_locator = view_locator
        self.size = size

    def render(self, surface, game_objects):
        rendering_region = self._rendering_region()
        visible_group = Group()

        for game_object in game_objects:
            if not game_object.sprite.overlaps(rendering_region):
                continue
            visible_group.add(game_object.sprite)

        self._translate_group(visible_group, (-rendering_region.x, -rendering_region.y))
        dirty_rects = [x.rect.copy() for x in visible_group]
        visible_group.draw(surface)
        self._translate_group(visible_group, (rendering_region.x, rendering_region.y))
        return dirty_rects

    def _rendering_region(self):
        center = self.view_locator()
        left_top = (center[0] - self.size[0]/2, center[1] - self.size[1]/2)
        return Rect(left_top, self.size)

    def _translate_group(self, group, movement):
        for sprite in group:
            sprite.rect.move_ip(movement[0], movement[1])

