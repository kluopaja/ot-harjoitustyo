import pytest
from unittest.mock import Mock, ANY

from game import GameState

class TestGameState:
    def game_object_mock(self):
        mock = Mock()
        mock.new_objects.side_effect = lambda : []
        mock.shape.intersects.side_effect = lambda x: False
        return mock

    def player_mock(self):
        mock = Mock()
        mock.new_objects.side_effect = lambda : []
        return mock

    @pytest.fixture
    def game_state(self):
        return GameState([self.game_object_mock(), self.game_object_mock()],
                         [self.player_mock(), self.player_mock()])

    def test_run_tick_updates_newly_created_objects(self, game_state):
        newly_created = Mock()
        game_state.game_objects[0].new_objects.side_effect = lambda : [newly_created]
        game_state.run_tick(1)
        newly_created.update.assert_called_with(ANY)
