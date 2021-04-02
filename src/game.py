from pygame import Rect
from pygame import Vector2
import logging
import graphics
from pathlib import Path
import pygame
import time
import itertools

class Player:
    def __init__(self, plane_factory, player_input):
        self.plane_factory = plane_factory
        self.player_input = player_input
        self.plane = None

        self.since_last_plane = 0
        self.plane_interval = 2

        self._new_objects = []
        self.player_input.bind_shoot(self._start_new_flight)

    def _start_new_flight(self):
        self.player_input.clear_shoot()
        self.plane = self.plane_factory.plane(self.player_input)
        self._new_objects.append(self.plane)

    def update(self, delta_time):
        self.since_last_plane += delta_time
        if self.plane == None:
            if self.since_last_plane > self.plane_interval:
                self.player_input.bind_shoot(self._start_new_flight)
            return

        if not self.plane.alive:
            self.plane = None
            self.since_last_plane = 0

    def new_objects(self):
        tmp = self._new_objects
        self._new_objects = []
        return tmp

class GameState:
    def __init__(self, game_objects, players):
        self.game_objects = game_objects
        self.players = players
        self._update_game_object_list()

    def run_tick(self, delta_time):
        self._update_players(delta_time)
        self._update_game_objects(delta_time)
        self._handle_collisions()
        self._update_game_object_list()

    def _update_players(self, delta_time):
        for player in self.players:
            player.update(delta_time)

    def _update_game_objects(self, delta_time):
        for game_object in self.game_objects:
            game_object.update(delta_time)

    def _handle_collisions(self):
        for x, y in itertools.combinations(self.game_objects, 2):
            if x.shape.intersects(y.shape):
                x.damage(y.collision_damage)
                y.damage(x.collision_damage)

    def _update_game_object_list(self):
        new_game_objects = []
        for game_object in self.game_objects:
            new_game_objects.extend(game_object.new_objects())

        for player in self.players:
            new_game_objects.extend(player.new_objects())

        self.game_objects = new_game_objects

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

        self._screen.fill((174, 186, 232))
        self._previous_dirty_rects = []
        self._screen.update()

    def add_game_view(self, tracked_object):
        pass
        # resolution = self.screen.get_window_size()
        # size = self._screen.get_window_size()
        # self.game_view = GameView(tracked_object, size, resolution)

    def render(self, game_objects):
        self._screen.fill((174, 186, 232))
        dirty_rects = self._game_view.render(self._screen, game_objects)
        #pygame.display.update()
        self._screen.update(self._previous_dirty_rects)
        self._screen.update(dirty_rects)
        self._previous_dirty_rects = dirty_rects

def constant_view_locator(x, y):
    def _inner():
        return (x, y)
    return _inner

class GameView:
    def __init__(self, view_locator, size):
        self.view_locator = view_locator
        self.size = size

    def render(self, screen, game_objects):
        rendering_region = self._rendering_region()

        dirty_rects = []
        for game_object in game_objects:
            dirty_rects.extend(
                game_object.graphic.draw(screen, offset=rendering_region.topleft))

        return dirty_rects

    def _rendering_region(self):
        center = self.view_locator()
        left_top = (center[0] - self.size[0]/2, center[1] - self.size[1]/2)
        return Rect(left_top, self.size)

