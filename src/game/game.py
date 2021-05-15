import sys
import logging
import itertools

from pygame import Vector2

from game.game_stats import RoundStats
from database_connection import DatabaseError

class GameNotification:
    """Class storing and modifying messages shown to players."""

    def __init__(self, press_key_to_start_msg, until_spawn_msg):
        """Initializes GameNotification.

        Arguments:
            `press_key_to_start_msg`: A string
                The message shown to user when the plane is ready
                to spawn when the user presses some key.

            `until_spawn_msg`: A string
                The message shown to the user after the spawn timer
                (in seconds). Will be attached directly to the
                time left without an extra whitespace.
            """
        self._message = ""
        self._press_key_to_start_msg = press_key_to_start_msg
        self._until_spawn_msg = until_spawn_msg

    def press_key_to_start(self):
        """Set the message to the instructions to start the game"""
        self._message = self._press_key_to_start_msg

    def until_spawn(self, seconds_left):
        """Set the message to the remaining time until spawn"""
        self._message = f"{seconds_left:.1f}" + self._until_spawn_msg

    def clear(self):
        """Don't show any message to the player"""
        self._message = ""

    def get_message(self):
        """Get the message that should be shown to the player"""
        return self._message


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
        if self._plane is None:
            self.notification.until_spawn(self._spawn_timer.time_left())
            if self._spawn_timer.expired():
                self.notification.press_key_to_start()
                self._player_input.bind_shoot(self._start_new_flight)
            return

        if not self._plane.alive():
            self.user_recorder.add_death()
            self.user_recorder.add_score(-self._plane_factory.get_plane_cost())
            self._plane = None
            self._spawn_timer.start()

    def new_objects(self):
        tmp = self._new_objects
        self._new_objects = []
        return tmp

    def view_location(self):
        if self._plane is None:
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
    def __init__(self, game_objects, players, level_name, timer):
        self.game_objects = game_objects
        self.players = players
        self.level_name = level_name
        self.timer = timer

    def run_tick(self, delta_time):
        self.timer.update(delta_time)
        self._update_players(delta_time)
        # update the game object list _before_ game object update so that
        # the newly created bullets will be moved with the plane (otherwise
        # the plane might hit the bullets at high speeds)
        self._update_game_object_list()
        self._update_game_objects(delta_time)
        self._handle_collisions()

    def game_over(self):
        return self.timer.expired()

    def _update_players(self, delta_time):
        for player in self.players:
            player.update(delta_time)

    def _update_game_objects(self, delta_time):
        for game_object in self.game_objects:
            game_object.update(delta_time)

    def _handle_collisions(self):
        for object_1, object_2 in itertools.combinations(self.game_objects, 2):
            if object_1.shape.intersects(object_2.shape):
                object_1.collide(object_2)
                object_2.collide(object_1)

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
        self._busy_frac_history = []

    def run(self):
        self._paused = False
        self.game_input.bind_pause(self._toggle_pause)
        self.clock.reset()
        self._busy_frac_history = []
        while True:
            if self._paused:
                self.game_input.handle_pause_inputs()
            else:
                self.game_input.handle_inputs()

            if self.game_input.should_quit:
                break

            if self._paused:
                self.game_renderer.render_pause(self.game_state)
            else:
                self.game_state.run_tick(self.clock.delta_time)
                self.game_renderer.render(self.game_state)

            if self.game_state.game_over():
                break

            self.clock.tick()
            self._log()

    def _log(self):
        self._busy_frac_history.append(self.clock.busy_fraction())
        logging.debug(
            f"busy frac: {self.clock.busy_fraction():5.3f}, "
            f"average(10): {self._mean(self._busy_frac_history):6.3f}"
        )
        if len(self._busy_frac_history) >= 10:
            self._busy_frac_history = self._busy_frac_history[1:]

    def _mean(self, v):
        return sum(v)/len(v)

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
    def __init__(self, results_viewer, stats_dao):
        self._results_viewer = results_viewer
        self._stats_dao = stats_dao

    def organize(self, game):
        game.run()

        round_stats = RoundStats(game.get_user_recorders())
        try:
            self._stats_dao.save_user_rounds(round_stats.get_user_rounds())
        except DatabaseError:
            logging.critical("Failed saving results to the database! "
                             "Try reinitializing the database.")
            sys.exit()

        self._results_viewer.run(round_stats)
