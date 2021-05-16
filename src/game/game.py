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
    """A class representing a player in one game round.

    The Player manages a single participant in a round.
    This is different from User who can be a Player (or many players!)
    in multiple rounds.

    Attributes:
        notification: A GameNotification
        player_recorder: A PlayerRecorder
        user: A User
            The user playing the player.
        """

    def __init__(self, plane_factory, player_input, game_notification,
                 player_recorder, user, spawn_timer):
        """Initializes the Player.

        Arguments:
            `plane_factory`: A PlaneFactory
                Used to make the Plane objects that the Player can spawn.
            `player_input`: A PlayerInput
                The inputs controlling the Player
            `game_notification`: A GameNotification
                The object used to show messages to the Player
            `player_recorder`: A PlayerRecorder
                The object recording statistics for the Player
            `user`: A user
                The user playing the Player
            `spawn_timer`: A Timer
                The timer for the time until a new plane is ready to spawn.
        """
        self.notification = game_notification
        self.player_recorder = player_recorder
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
        """Updates player.

        Arguments:
            `delta_time`: A non-negative float
                The passed time since last update.
        """
        self._spawn_timer.update(delta_time)
        self.player_recorder.update(delta_time)
        if self._plane is None:
            self.notification.until_spawn(self._spawn_timer.time_left())
            if self._spawn_timer.expired():
                self.notification.press_key_to_start()
                self._player_input.bind_shoot(self._start_new_flight)
            return

        if not self._plane.alive():
            self.player_recorder.add_death()
            self.player_recorder.add_score(-self._plane_factory.get_plane_cost())
            self._plane = None
            self._spawn_timer.start()

    def new_objects(self):
        """Returns newly created game objects.

        Returns:
            A list of GameObject objects:
                The objects created by Player since the last time this function
                was called.
        """
        tmp = self._new_objects
        self._new_objects = []
        return tmp

    def view_location(self):
        """The location in the game world that the Player is looking at.

        Returns:
            A pygame.Vector2:
                If the Player currently has a Plane, then this will be the
                location of the plane. Otherwise the spawning location
                of the new plane.
        """
        if self._plane is None:
            return Vector2(self._plane_factory.start_position)

        return Vector2(self._plane.graphic.location)

    def process_reward(self, score, issuer):
        """Gives score reward to `self` by `issuer`.

        Saves the rewarded score to the `self.player_recorder`.

        NOTE: A Player object cannot give a reward to itself!

        Arguments:
            `score`: A floating point number
                The amount of the reward.
            `issuer: A Player
                The Player giving the reward.
        """
        if issuer is self:
            return

        self.player_recorder.add_score(score)

    def add_kill(self, target_owner):
        """Informs `self` that they killed a target owner by `target_owner`

        NOTE: Targets owned by `self` are ignored!

        Arguments:
            `target_owner`: A Player
                The owner of the killed GameObject
        """
        if target_owner is self:
            return

        self.player_recorder.add_kill()

    def add_shot_fired(self):
        """Informs `self` that a Plane owned by `self` fired a shot"""
        self.player_recorder.add_shot()


class GameState:
    """A class represententing the state of a game round.

    Attributes:
       `game_objects`: A list of GameObject objects
            The GameObjects currently present in the game round
       `players`: A list of Player objects
            The Players participating the game round
       `level_name`: A string
            The name of the current level

    """
    def __init__(self, game_objects, players, level_name, timer):
        """Initializes a GameState.

        Arguments:
            `game_objects`: A list of GameObject objects
                The GameObjects present at the start of the round
            `players`: A list of Player objects
                The participants in the round
            `level_name`: A string
                The name of the current level
            `timer`: A Timer
                The timer defining the length of the round
        """
        self.game_objects = game_objects
        self.players = players
        self.level_name = level_name
        self._timer = timer

    def run_tick(self, delta_time):
        """Updates `self` to the next state.

        Arguments:
            `delta_time`: A non-negative scalar.
                The time difference between the next and current states.
        """

        self._timer.update(delta_time)
        self._update_players(delta_time)
        # update the game object list _before_ game object update so that
        # the newly created bullets will be moved with the plane (otherwise
        # the plane might hit the bullets at high speeds)
        self._update_game_object_list()
        self._update_game_objects(delta_time)
        self._handle_collisions()

    def game_over(self):
        """Returns True if the round has ended and otherwise False"""
        return self._timer.expired()

    def time_left(self):
        """Returns the time in seconds until the end of the round"""
        return self._timer.time_left()

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
    """A class representing a single game round.

    Attributes:
        `game_state`: A GameState object
            The current state of the game round.
    """
    def __init__(self, game_input, game_state, game_renderer, clock):
        self._game_input = game_input
        self.game_state = game_state
        self._game_renderer = game_renderer
        self._clock = clock
        self._paused = False
        self._busy_frac_history = []

    def run(self):
        self._paused = False
        self._game_input.bind_pause(self._toggle_pause)
        self._clock.reset()
        self._busy_frac_history = []
        while True:
            if self._paused:
                self._game_input.handle_pause_inputs()
            else:
                self._game_input.handle_inputs()

            if self._game_input.should_quit:
                break

            if self._paused:
                self._game_renderer.render_pause(self.game_state)
            else:
                self.game_state.run_tick(self._clock.delta_time)
                self._game_renderer.render(self.game_state)

            if self.game_state.game_over():
                break

            self._clock.tick()
            self._log()

    def _log(self):
        self._busy_frac_history.append(self._clock.busy_fraction())
        logging.debug(
            f"busy frac: {self._clock.busy_fraction():5.3f}, "
            f"average(10): {self._mean(self._busy_frac_history):6.3f}"
        )
        if len(self._busy_frac_history) >= 10:
            self._busy_frac_history = self._busy_frac_history[1:]

    def _mean(self, v):
        return sum(v)/len(v)

    def get_player_recorders(self):
        """Returns the information about partiticipants' game performance

        Returns:
            A list of PlayerRecorder objects."""

        return [player.player_recorder for player in self.game_state.players]


    def _toggle_pause(self):
        if self._paused:
            self._paused = False
        else:
            self._paused = True

class GameOrganizer:
    """Class for running a game round and handling the statistics."""
    def __init__(self, results_viewer, stats_dao):
        """Initializes a GameOrganizer.

        Arguments:
            `results_viewer`: A ResultsViewero
                The object used to show the game round statistics to the users.
            `stats_dao`: A StatsDao
                The object used to save the game round statistics to a database.
        """
        self._results_viewer = results_viewer
        self._stats_dao = stats_dao

    def organize(self, game):
        """Organizes `game`.

        Arguments:
            `game`: A Game
                The game that will be run and whose results will be
                saved and showed.
        """
        game.run()

        round_stats = RoundStats(game.get_player_recorders())
        try:
            self._stats_dao.save_player_rounds(round_stats.get_player_rounds())
        except DatabaseError:
            logging.critical("Failed saving results to the database! "
                             "Try reinitializing the database.")
            sys.exit()

        self._results_viewer.run(round_stats)
