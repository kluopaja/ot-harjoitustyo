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

class Player:
    def __init__(self, plane_factory, player_input, game_notification, spawn_timer):
        self.plane_factory = plane_factory
        self.player_input = player_input
        self.plane = None
        self.spawn_timer = spawn_timer
        self.score = 0

        self._new_objects = []

        self.notification = game_notification

    def _start_new_flight(self):
        self.player_input.clear_shoot()
        self.plane = self.plane_factory.plane(self.player_input, self)
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

        if not self.plane.alive():
            self.plane = None
            self.spawn_timer.start()

    def new_objects(self):
        tmp = self._new_objects
        self._new_objects = []
        return tmp

    def view_location(self):
        if self.plane == None:
            return self.plane_factory.start_position

        return self.plane.graphic.location

    def process_reward(self, score, issuer):
        if issuer is self:
            return

        self.score += score



class GameState:
    def __init__(self, game_objects, players):
        self.game_objects = game_objects
        self.players = players

    def run_tick(self, delta_time):
        self._update_players(delta_time)
        # update the game object list _before_ game object update so that
        # the newly created bullets will be moved with the plane (otherwise
        # the plane might hit the bullets at high speeds)
        self._update_game_object_list()
        self._update_game_objects(delta_time)
        self._handle_collisions()

    def _update_players(self, delta_time):
        for player in self.players:
            player.update(delta_time)

    def _update_game_objects(self, delta_time):
        for game_object in self.game_objects:
            game_object.update(delta_time)

    def _handle_collisions(self):
        for x, y in itertools.combinations(self.game_objects, 2):
            if x.shape.intersects(y.shape):
                x.collide(y)
                y.collide(x)

    def _update_game_object_list(self):
        new_game_objects = []
        for game_object in self.game_objects:
            new_game_objects.extend(game_object.new_objects())

        for player in self.players:
            new_game_objects.extend(player.new_objects())

        self.game_objects = new_game_objects

class Game:
    def __init__(self, game_input, game_state, game_renderer, clock):
        self.game_input = game_input
        self.game_state = game_state
        self.game_renderer = game_renderer
        self.clock = clock

    def run(self):
        self.clock.reset()
        while True:
            self.game_input.handle_inputs()
            if self.game_input.should_quit:
                break

            self.game_state.run_tick(self.clock.delta_time)
            self.game_renderer.render(self.game_state.game_objects)
            self.clock.tick()
            logging.debug(f'busy frac: {self.clock.busy_fraction()}')

class GameRenderer:
    def __init__(self, screen, game_views, game_background):
        self._screen = screen
        self.game_views = game_views
        self.game_background = game_background

        self._screen.surface.fill(self.game_background.fill_color)
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
        self._screen.surface.fill(self.game_background.fill_color)
        dirty_rects = []
        for game_view, area in zip(self.game_views, self.game_view_areas):
            subsurface = self._screen.surface.subsurface(area)
            dirty_subrects = game_view.render(subsurface, game_objects, self.game_background)
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

import random
class GameBackground:
    def __init__(self, cloud_graphic, n_clouds, repeat_area, fill_color=(174, 186, 232)):
        """Initializes GameBackground object.

        Arguments:
            repeat_area: Vector2 object
                The size of the repeat in background.
                NOTE: Should be large enough that at most one
                copy of each cloud can be seen in each
                `render` call!
        """
        self.cloud_graphic = cloud_graphic
        self.n_clouds = n_clouds
        # TODO rename to size or something
        self.repeat_area = repeat_area
        self.fill_color = fill_color
        self.cloud_locations = self._generate_cloud_locations()

    def _generate_cloud_locations(self):
        random.seed(1337)
        result = []
        for i in range(self.n_clouds):
            result.append(Vector2(random.randint(0, self.repeat_area[0]),
                                  random.randint(0, self.repeat_area[1])))
        return result

    def _closest_congruent(self, target, point, mod):
        """Returns the closest point to `target`.

        Considers all points congruent with `point` modulo `mod`"""

        # Note that x % mod returns non-negative values if mod > 0
        mod_distance = Vector2((point[0] - target[0]) % mod[0],
                               (point[1] - target[1]) % mod[1])
        for i in range(2):
            if mod_distance[i]*2 > mod[i]:
                mod_distance[i] -= mod[i]

        return mod_distance + target

    def render(self, surface, offset):
        center_offset = surface.get_rect().center + Vector2(offset)
        dirty_rects = []
        for location in self.cloud_locations:
            cloud_location = self._closest_congruent(center_offset, location, self.repeat_area)
            self.cloud_graphic.location = cloud_location
            dirty_rects.extend(self.cloud_graphic.draw(surface, offset))
        return dirty_rects

def constant_view_locator(x, y):
    def _inner():
        return (x, y)
    return _inner

class GameView:
    def __init__(self, player, font_color):
        self.player = player
        self.font_color = font_color

    def render(self, surface, game_objects, game_background):
        rendering_region = surface.get_rect()
        rendering_region.center = self.player.view_location()

        dirty_rects = []

        dirty_rects.extend(
            game_background.render(surface, offset=rendering_region.topleft))

        for game_object in game_objects:
            dirty_rects.extend(
                game_object.graphic.draw(surface, offset=rendering_region.topleft))


        dirty_rects.extend(self._render_notification(surface))
        dirty_rects.extend(self._render_score(surface))
        return dirty_rects

    def _render_notification(self, surface):
        text_center = Vector2(surface.get_rect().center)
        dirty_rects = []
        dirty_rects.append(
            surface.centered_text(self.player.notification.message, text_center,
                                  self.font_color))

        return dirty_rects

    def _render_score(self, surface):
        text_topleft = Vector2(surface.get_rect().topleft)
        dirty_rects = []
        dirty_rects.append(
            surface.topleft_text(str(self.player.score), text_topleft,
                                 self.font_color))

        return dirty_rects
