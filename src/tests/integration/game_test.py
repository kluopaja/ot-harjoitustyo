import pytest
import sqlite3

import time
from pathlib import Path

from unittest.mock import Mock, ANY, create_autospec
import unittest
import pygame
from pygame import Vector2

from config import Config
from user_dao import UserDao
from stats_dao import StatsDao
from user import User
from graphics.screen import Screen

from events import EventHandler

from game.setup import GameFactory
from game.game import GameOrganizer
from init_database import create_tables
from menu.input import MenuInput
from game.game_stats import create_results_viewer

from tests.menu_test import MockEvent

class PressedKeys:
    """A class for mocking the pygame.key.get_pressed() return value"""

    def __init__(self, pressed):
        """Sets values of `pressed` to pressed state, others to not pressed"""
        self._pressed = pressed

    def __getitem__(self, key):
        return key in self._pressed

class EventHandlerMock:
    def __init__(self, pressed_keys=None, pressed_times=None, events=None, event_times=None):
        """Initializes an EventHandlerMock.

        Arguments:
            `pressed_keys`: None or a list of PressedKeys objects
            `pressed_times`: None or a list of floats
                The ending time of a corresponding PressedKeys
                Should be strictly increasing

            `events`: MockEvent objects
            `event_times`: Times when the corresponding MockEvent occurs
        """
                
        if pressed_keys is None:
            pressed_keys = []
        if pressed_times is None:
            pressed_times = []
        if events is None:
            events = []
        if event_times is None:
            event_times = []

        assert len(pressed_keys) == len(pressed_times)
        assert len(events) == len(event_times)
        self.pressed_keys = pressed_keys
        self.pressed_times = pressed_times
        self.events = events
        self.event_times = event_times
        self.start_time = None

    def get_events(self):
        elapsed = self._get_elapsed()
        out = []
        while len(self.event_times) and elapsed > self.event_times[0]:
                out.append(self.events[0])
                self.events = self.events[1:]
                self.event_times = self.event_times[1:]

        return out

    def get_pressed(self):
        elapsed = self._get_elapsed()

        for i in range(len(self.pressed_times)-1, -1, -1):
            if elapsed >= self.pressed_times[i]:
                return self.pressed_keys[i]

        return PressedKeys([])

    def _get_elapsed(self):
        current_time = time.time()
        if self.start_time is None:
            self.start_time = current_time
        elapsed = current_time - self.start_time
        return elapsed

@pytest.fixture()
def database_connection():
    database_path = Path(__file__).parent / ".test.db"
    if database_path.exists():
        database_path.unlink()
    database_connection = sqlite3.connect(str(database_path))
    database_connection.row_factory = sqlite3.Row
    create_tables(database_connection)
    yield database_connection
    if database_path.exists():
        database_path.unlink()

@pytest.fixture()
def config():
    config_path = Path(__file__).parent.parent / "assets/general.json"
    return Config(config_path)

@pytest.fixture()
def screen():
    return Screen(300, 300, 0.02)

@pytest.fixture()
def game_factory_factory(config, database_connection, screen):
    user_dao = UserDao(database_connection)
    user_dao.create(User("apina"))
    user_dao.create(User("banaani"))
    user_dao.create(User("cembalo"))

    def _inner(game_length, event_handler):
        config.game_length = game_length
        return GameFactory(config, user_dao, event_handler, screen, n_players=2)

    return _inner

class TestGameFactoryIntegration:
    def test_n_players_updates_correctly(self, game_factory_factory):
        factory = game_factory_factory(0.5, EventHandlerMock([], []))
        assert factory.get_n_players() == 2
        factory.add_player()
        assert factory.get_n_players() == 3
        factory.add_player()
        assert factory.get_n_players() == 4
        factory.add_player()
        assert factory.get_n_players() == 4
        factory.remove_player()
        assert factory.get_n_players() == 3
        factory.remove_player()
        factory.remove_player()
        factory.remove_player()
        factory.remove_player()
        assert factory.get_n_players() == 1

    def test_player_selection(self, game_factory_factory):
        factory = game_factory_factory(0.5, EventHandlerMock([], []))
        factory.add_player()

        factory.user_selectors[0].next()

        factory.user_selectors[2].next()
        factory.user_selectors[2].next()
        factory.user_selectors[2].next()
        factory.user_selectors[2].next()
        game = factory.game()
        player_recorders = game.get_player_recorders()
        assert len(player_recorders) == 3
        assert player_recorders[0].user.name == "banaani"
        assert player_recorders[1].user.name == "apina"
        assert player_recorders[2].user.name == "cembalo"

    def test_level_selection(self, game_factory_factory):
        factory = game_factory_factory(0.5, EventHandlerMock([], []))
        assert factory.get_level_name() == "spring"
        factory.previous_level()
        factory.previous_level()
        assert factory.get_level_name() == "spring"
        factory.next_level()
        assert factory.get_level_name() == "small"
        factory.next_level()
        assert factory.get_level_name() == "small"


class TestGameIntegration:
    def test_game_ends_after_correct_time(self, game_factory_factory):
        factory = game_factory_factory(0.5, EventHandlerMock([], []))
        game = factory.game()
        start = time.time()
        game.run()
        length = time.time() - start
        assert abs(0.5 - length) < 0.1

    def test_planes_collide(self, game_factory_factory):

        keys = []
        times = []
        
        keys.append(PressedKeys([pygame.key.key_code("q"),
                                 pygame.key.key_code("right shift")]))
        times.append(0)

        keys.append(PressedKeys([pygame.key.key_code("w")]))
        times.append(0.7)

        factory = game_factory_factory(3, EventHandlerMock(keys, times))
        factory.user_selectors[1].next()
        game = factory.game()
        game.run()

        player_recorders = game.get_player_recorders()

        assert player_recorders[0].total_score() == 80
        assert len(player_recorders[0].kills) == 1
        assert len(player_recorders[0].deaths) == 1
        assert player_recorders[1].total_score() == 80
        assert len(player_recorders[1].kills) == 1
        assert len(player_recorders[1].deaths) == 1

    def test_shooting(self, game_factory_factory):

        keys = []
        times = []
        
        keys.append(PressedKeys([pygame.key.key_code("q"),
                                 pygame.key.key_code("right shift")]))
        times.append(0)

        keys.append(PressedKeys([]))
        times.append(0.9)

        factory = game_factory_factory(3, EventHandlerMock(keys, times))
        factory.user_selectors[1].next()

        game = factory.game()
        game.run()

        player_recorders = game.get_player_recorders()

        assert player_recorders[0].total_score() == 100
        assert len(player_recorders[0].kills) == 1
        assert len(player_recorders[0].deaths) == 0
        assert player_recorders[1].total_score() == -20
        assert len(player_recorders[1].kills) == 0
        assert len(player_recorders[1].deaths) == 1

    # used to check that the bullets are large enough to
    # not be able to pass the wall between frames
    def test_all_bullets_collide_wall(self, game_factory_factory):
        keys = []
        times = []
        
        keys.append(PressedKeys([pygame.key.key_code("q"),
                                 pygame.key.key_code("d")]))
        times.append(0)

        keys.append(PressedKeys([pygame.key.key_code("q"),
                                 pygame.key.key_code("w")]))
        times.append(1.1)

        keys.append(PressedKeys([]))
        times.append(4)

        factory = game_factory_factory(5, EventHandlerMock(keys, times))
        factory.user_selectors[1].next()

        game = factory.game()
        game.run()

        assert len(game.game_state.game_objects) == 2

    def test_planes_can_respawn(self, game_factory_factory):
        keys = []
        times = []
        
        keys.append(PressedKeys([pygame.key.key_code("q"),
                                 pygame.key.key_code("d")]))
        times.append(0)

        keys.append(PressedKeys([pygame.key.key_code("q"),
                                 pygame.key.key_code("w")]))
        times.append(0.9)

        keys.append(PressedKeys([pygame.key.key_code("q"),
                                 pygame.key.key_code("d")]))
        times.append(4)

        keys.append(PressedKeys([pygame.key.key_code("w")]))
        times.append(4.3)

        keys.append(PressedKeys([]))
        times.append(10)

        factory = game_factory_factory(6, EventHandlerMock(keys, times))
        factory.user_selectors[1].next()

        game = factory.game()
        game.run()
        player_recorders = game.get_player_recorders()

        assert player_recorders[0].total_score() == -40
        assert len(player_recorders[0].deaths) == 2

@pytest.fixture()
def stats_dao(database_connection):
    return StatsDao(database_connection)

@pytest.fixture()
def game_organizer_factory(config, stats_dao, screen):
    def _inner(event_handler):
        menu_input = MenuInput(event_handler, config.menu_input_config)
        results_viewer = create_results_viewer(menu_input, screen)
        return GameOrganizer(results_viewer, stats_dao)
    return _inner

class TestGameOrganizerIntegration:
    # allow some time to exit as the framerate is currently only 2 fps for the
    # results
    def test_game_organizer_quits_within_1s_of_esc(self, game_factory_factory,
                                                   game_organizer_factory):

        start_time = time.time()
        events = [MockEvent(pygame.key.key_code("escape"), "")]
        event_times = [2]
        event_handler = EventHandlerMock(events=events, event_times=event_times)
        game_factory = game_factory_factory(1, event_handler)
        game = game_factory.game()
        game_organizer_factory(event_handler).organize(game)

    def test_game_organizer_saves_results_to_database(self, game_factory_factory,
                                                      game_organizer_factory,
                                                      stats_dao):


        # setup player 1 shooting player 2
        keys = []
        times = []
        
        keys.append(PressedKeys([pygame.key.key_code("q"),
                                 pygame.key.key_code("right shift")]))
        times.append(0)
        keys.append(PressedKeys([]))
        times.append(0.9)

        # for quitting the results view
        events = [MockEvent(pygame.key.key_code("escape"), "")]
        event_times = [2]
        event_handler = EventHandlerMock(keys, times, events=events,
                                         event_times=event_times)
        game_factory = game_factory_factory(1, event_handler)
        game_factory.user_selectors[1].next()
        game = game_factory.game()
        game_organizer_factory(event_handler).organize(game)

        top_scorers = stats_dao.get_top_scorers(2)
        summary_table = top_scorers.get_summary_table()
        assert list(summary_table["name"].values) == ["apina", "banaani"]
        assert list(summary_table["total score"].values) == [100, -20]
        assert list(summary_table["rounds"].values) == [1, 1]
        assert list(summary_table["kills"].values) == [1, 0]
        assert list(summary_table["deaths"].values) == [0, 1]

