import pytest
from unittest.mock import Mock, ANY
import unittest
from pygame import Vector2

from game import GameState, Player

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.plane_mock = Mock()
        self.plane_factory_mock = Mock()
        self.plane_factory_mock.plane.side_effect = lambda x, y: self.plane_mock
        self.player_input_mock = Mock()
        self.game_notification_mock = Mock()
        self.spawn_timer_mock = Mock()

        self.player = Player(self.plane_factory_mock, self.player_input_mock,
                             self.game_notification_mock, self.spawn_timer_mock)

    def test_view_location_without_plane(self):
        self.plane_factory_mock.start_position = Vector2(1, 2)
        assert self.player.view_location() == Vector2(1, 2)

    def test_shoot_key_creates_new_plane_when_spawn_timer_expired(self):
        self.spawn_timer_mock.expired.side_effect = lambda: True
        self.plane_mock.graphic.location = Vector2(2, 1)
        new_flight_function = None

        def f(x):
            new_flight_function = x
        self.player.update(1)

        assert self.player_input_mock.bind_shoot.call_args.args[0] is not None
        self.player_input_mock.bind_shoot.call_args.args[0]()
        self.plane_mock.graphic.location = Vector2(3, 3)
        # test the view location is updated correctly
        assert self.player.view_location() == Vector2(3, 3)
        new_objects = self.player.new_objects()
        assert len(new_objects) == 1
        assert new_objects[0] is self.plane_mock

class TestGameState:
    def game_object_mock(self):
        mock = Mock()
        mock.new_objects.side_effect = lambda: []
        mock.shape.intersects.side_effect = lambda x: False
        return mock

    def player_mock(self):
        mock = Mock()
        mock.new_objects.side_effect = lambda: []
        return mock

    @pytest.fixture
    def game_state(self):
        return GameState([self.game_object_mock(), self.game_object_mock()],
                         [self.player_mock(), self.player_mock()])

    def test_run_tick_updates_newly_created_objects(self, game_state):
        newly_created = Mock()
        game_state.game_objects[0].new_objects.side_effect = lambda: [
            newly_created]
        game_state.run_tick(1)
        newly_created.update.assert_called_with(ANY)
