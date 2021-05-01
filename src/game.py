import random
from pygame import Rect
from pygame import Vector2
import logging
import graphics
from pathlib import Path
import pygame
import time
import math
import itertools

# TODO make this more general, also player name/score styles


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
    def __init__(self, plane_factory, player_input, game_notification,
                 user_recorder, user, spawn_timer):
        self.notification = game_notification
        self.user_recorder = user_recorder
        self.user = user

        self._plane_factory = plane_factory
        self._player_input = player_input
        self._plane = None
        self._spawn_timer = spawn_timer
        self._new_objects = []

    def _start_new_flight(self):
        self._player_input.clear_shoot()
        self._plane = self._plane_factory.plane(self._player_input, self)
        self._new_objects.append(self._plane)
        self.notification.clear()

    def update(self, delta_time):
        self._spawn_timer.update(delta_time)
        self.user_recorder.update(delta_time)
        if self._plane == None:
            self.notification.until_spawn(self._spawn_timer.time_left())
            if self._spawn_timer.expired():
                self.notification.press_key_to_start()
                self._player_input.bind_shoot(self._start_new_flight)
            return

        if not self._plane.alive():
            self.user_recorder.add_death()
            self._plane = None
            self._spawn_timer.start()

    def new_objects(self):
        tmp = self._new_objects
        self._new_objects = []
        return tmp

    def view_location(self):
        if self._plane == None:
            return Vector2(self._plane_factory.start_position)

        return Vector2(self._plane.graphic.location)

    def process_reward(self, score, issuer):
        if issuer is self:
            return

        self.user_recorder.add_score(score)

    def add_kill(self, target_owner):
        if target_owner is self:
            return

        self.user_recorder.add_kill()

    def add_shot_fired(self):
        self.user_recorder.add_shot()


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
        self._paused = False

    def run(self):
        self._paused = False
        self.game_input.bind_pause(self._toggle_pause)
        self.clock.reset()
        while True:
            if self._paused:
                self.game_input.handle_pause_inputs()
            else:
                self.game_input.handle_inputs()

            if self.game_input.should_quit:
                break

            if self._paused:
                self.game_renderer.render_pause(self.game_state.game_objects)
            else:
                self.game_state.run_tick(self.clock.delta_time)
                self.game_renderer.render(self.game_state.game_objects)

            self.clock.tick()
            logging.debug(f'busy frac: {self.clock.busy_fraction()}')

    def get_user_recorders(self):
        """Returns the information about partiticipants' game performance

        Returns:
            A list of UserRecorder objects."""

        return [player.user_recorder for player in self.game_state.players]


    def _toggle_pause(self):
        if self._paused:
            self._paused = False
        else:
            self._paused = True

class GameOrganizer:
    """Class for running a game and handling the statistics"""
    def __init__(self, results_viewer):
        self._results_viewer = results_viewer

    def organize(self, game):
        game.run()

        user_recorders = game.get_user_recorders()

        self._results_viewer.run(user_recorders)


def rect_horizontal_split(rect):
    """Splits `rect` along the horizontal axis`

    Arguments:
        `rect`: a FloatRect

    Returns:
        (r1, r2) : a tuple of FloatRects
            r1 is the upper FloatRect and r2 is the lower FloatRect"""

    upper = rect.copy()
    upper.height /= 2

    lower = rect.copy()
    lower.height = rect.height - upper.height

    lower.top = upper.bottom
    return (upper, lower)


def rect_vertical_split(rect):
    """Splits `rect` along the vertical axis`

    Arguments:
        `rect`: a FloatRect

    Returns:
        (r1, r2) : a tuple of FloatRects
            r1 is the left FloatRect and r2 is the right FloatRect"""

    left = rect.copy()
    left.width /= 2

    right = rect.copy()
    right.width = rect.width - left.width

    right.left = left.right
    return (left, right)


def rect_splitter(split_depth, rect, start_dimension='vertical'):
    """Recursively splits `rect`.

    Alternates between horizontal and vertical splits

    Arguments:
        `split_depth`: a non-negative integer
            The number of recursive splits
        `rect`: a FloatRect
        `start_dimension`: `vertical` or `horizontal`
            The direction of the first split

    Returns:
        a list of FloatRects
            The final results of the splits"""

    splitters = (rect_vertical_split, rect_horizontal_split)
    if start_dimension == 'vertical':
        pass
    elif start_dimension == 'horizontal':
        splitters[0], split_dimesions[1] = splitters[1], splitters[0]
    else:
        raise ValueError("Invalid `start_dimension`")

    split_results = [rect.copy()]

    for i in range(split_depth):
        new_split_results = []
        for x in split_results:
            new_split_results.extend(splitters[i % 2](x))
        split_results = new_split_results

    return split_results


class GameRenderer:
    def __init__(self, screen, game_views, game_background, pause_overlay):
        self._screen = screen
        self.game_views = game_views
        self.game_background = game_background
        self.pause_overlay = pause_overlay

        self._screen.surface.fill(self.game_background.fill_color, update=True)
        self._screen.update()

        if len(game_views) == 0:
            raise ValueError("At least 1 GameView needed")

        n_splits = math.ceil(math.log2(len(game_views)))
        whole_area = screen.surface.get_rect()
        self.game_view_areas = rect_splitter(n_splits, whole_area)

    def render(self, game_objects):
        self._render_game_objects(game_objects)
        self._screen.update()

    def render_pause(self, game_objects):
        self._render_game_objects(game_objects)
        self._screen.surface.blur(15)
        self.pause_overlay.render(self._screen.surface)
        self._screen.update()

    def _render_game_objects(self, game_objects):
        self._screen.surface.fill(self.game_background.fill_color)
        for game_view, area in zip(self.game_views, self.game_view_areas):
            subsurface = self._screen.surface.subsurface(area)
            game_view.render(subsurface, game_objects, self.game_background)

class PauseOverlay:
    def __init__(self, text, font_color):
        self.text = text
        self.font_color = font_color

    def render(self, surface):
        text_center = Vector2(surface.get_rect().center)
        surface.centered_text(self.text, text_center, self.font_color)


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

    def render(self, camera):
        center_offset = camera.location
        for location in self.cloud_locations:
            cloud_location = self._closest_congruent(
                center_offset, location, self.repeat_area)
            self.cloud_graphic.location = cloud_location
            self.cloud_graphic.draw(camera)


def constant_view_locator(x, y):
    def _inner():
        return (x, y)
    return _inner


class GameView:
    def __init__(self, player, camera, font_color):
        self.player = player
        self.camera = camera
        self.font_color = font_color

    def render(self, surface, game_objects, game_background):
        self.camera.location = self.player.view_location()
        self.camera.set_drawing_surface(surface)

        game_background.render(self.camera)

        for game_object in game_objects:
            game_object.graphic.draw(self.camera)

        self._render_notification(surface)
        self._render_score(surface)
        self._render_name(surface)

    def _render_notification(self, surface):
        text_center = Vector2(surface.get_rect().center)
        surface.centered_text(self.player.notification.message, text_center,
                              self.font_color)

    def _render_score(self, surface):
        text_topleft = Vector2(surface.get_rect().topleft)
        surface.topleft_text(str(self.player.user_recorder.total_score()), text_topleft,
                             self.font_color)

    def _render_name(self, surface):
        text_center = Vector2(surface.get_rect().midtop)
        surface.midtop_text(str(self.player.user.name), text_center,
                            self.font_color)
