from pygame import Rect
from pygame import Vector2
import logging
import graphics
from pathlib import Path
import pygame
import time
import itertools

class GameNotification:
    def __init__(self, press_key_to_start_msg, until_spawn_msg):
        self.message = ""
        self.press_key_to_start_msg = press_key_to_start_msg
        self.until_spawn_msg = until_spawn_msg

    def press_key_to_start(self):
        self.message = self.press_key_to_start_msg

    def until_spawn(self, seconds_left):
        self.message = f"{seconds_left:.1f} " + self.until_spawn_msg

    def clear(self):
        self.message = ""

class Timer:
    def __init__(self, length):
        self.time_left = length
        self.length = length

    def start(self):
        self.time_left = self.length

    def update(self, delta_time):
        self.time_left -= delta_time

    def expired(self):
        return self.time_left <= 0

class Player:
    def __init__(self, plane_factory, player_input, game_notification, spawn_timer):
        self.plane_factory = plane_factory
        self.player_input = player_input
        self.plane = None
        self.spawn_timer = spawn_timer

        self._new_objects = []

        self.notification = game_notification

    def _start_new_flight(self):
        self.player_input.clear_shoot()
        self.plane = self.plane_factory.plane(self.player_input)
        self._new_objects.append(self.plane)
        self.notification.clear()

    def update(self, delta_time):
        self.spawn_timer.update(delta_time)
        if self.plane == None:
            self.notification.until_spawn(self.spawn_timer.time_left)
            if self.spawn_timer.expired():
                self.notification.press_key_to_start()
                self.player_input.bind_shoot(self._start_new_flight)
            return

        if not self.plane.alive:
            self.plane = None
            self.spawn_timer.start()

    def new_objects(self):
        tmp = self._new_objects
        self._new_objects = []
        return tmp

    def view_location(self):
        if self.plane == None:
            return self.plane_factory.start_position

        return self.plane.location


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
    def __init__(self, screen, game_views):
        self._screen = screen
        self.game_views = game_views

        self._screen.surface.fill((174, 186, 232))
        self._previous_dirty_rects = []
        self._screen.update()

        if len(game_views) > 2:
            raise ValueError("Maximum of 2 game views supported")

        self.game_view_areas = []
        whole_area = screen.surface.get_rect()

        if len(game_views) == 1:
            self.game_view_areas = [whole_area]

        if len(game_views) == 2:
            whole_area.width = whole_area.width/2
            self.game_view_areas.append(Rect(whole_area))
            whole_area.left = whole_area.width
            self.game_view_areas.append(Rect(whole_area))



    def render(self, game_objects):
        self._screen.surface.fill((174, 186, 232))
        dirty_rects = []
        for game_view, area in zip(self.game_views, self.game_view_areas):
            subsurface = self._screen.surface.subsurface(area)
            dirty_subrects = game_view.render(subsurface, game_objects)
            dirty_rects.extend(self._subrects_to_absolute(dirty_subrects, area.topleft))

        self._screen.update(self._previous_dirty_rects)
        self._screen.update(dirty_rects)
        self._previous_dirty_rects = dirty_rects

    def _subrects_to_absolute(self, subrects, offset):
        result = []
        for rect in subrects:
            copy = Rect(rect)
            copy.left += offset[0]
            copy.top += offset[1]
            result.append(copy)

        return result


def constant_view_locator(x, y):
    def _inner():
        return (x, y)
    return _inner

class GameView:
    def __init__(self, player):
        self.player = player

    def render(self, surface, game_objects):
        rendering_region = surface.get_rect()
        rendering_region.center = self.player.view_location()

        dirty_rects = []
        for game_object in game_objects:
            dirty_rects.extend(
                game_object.graphic.draw(surface, offset=rendering_region.topleft))


        dirty_rects.extend(self._render_notification(surface))
        return dirty_rects

    def _render_notification(self, surface):
        text_center = Vector2(surface.get_rect().center)
        dirty_rects = []
        dirty_rects.append(
            surface.centered_text(self.player.notification.message, text_center,
                                  (200, 55, 55)))

        return dirty_rects
