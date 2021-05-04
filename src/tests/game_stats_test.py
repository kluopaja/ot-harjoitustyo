import pytest
import unittest
import numpy as np
from unittest.mock import Mock, create_autospec

from utils.timing import Timer

from game.game_stats import UserRecorder, UserRecorderAnalyzer

class TestUserRecorder(unittest.TestCase):
    def setUp(self):
        self.timer = create_autospec(Timer)
        self.timer.current_time.return_value = 1
        self.user = Mock()
        self.recorder = UserRecorder(self.user, self.timer)

    def test_add_score(self):
        self.recorder.add_score(10)
        assert len(self.recorder.scores) == 1
        assert self.recorder.scores[0] == (1, 10)

    def test_add_shot(self):
        self.recorder.add_shot()
        assert len(self.recorder.shots_fired) == 1
        assert self.recorder.shots_fired[0] == 1

    def test_add_kill(self):
        self.recorder.add_kill()
        assert len(self.recorder.shots_fired) == 0
        assert len(self.recorder.kills) == 1
        assert self.recorder.kills[0] == 1

    def test_add_death(self):
        self.recorder.add_death()
        assert len(self.recorder.deaths) == 1
        assert self.recorder.deaths[0] == 1

    def test_record_end_time(self):
        assert self.recorder.record_end_time() == 1

    def test_update(self):
        self.recorder.update(10)
        self.timer.update.assert_called_with(10)

    def test_total_score(self):
        self.recorder.add_score(10)
        self.recorder.add_score(15)
        assert self.recorder.total_score() == 25

class TestUserRecorderAnalyzer(unittest.TestCase):
    def setUp(self):
        self.timer = create_autospec(Timer)
        self.timer.current_time.return_value = 1
        self.user_1 = Mock()
        self.user_1.name = "a"
        self.recorder_1 = UserRecorder(self.user_1, self.timer)
        self.recorder_1.add_score(100)
        self.recorder_1.add_shot()
        self.recorder_1.add_kill()
        self.recorder_1.add_kill()
        self.recorder_1.add_death()
        self.recorder_1.add_death()
        self.recorder_1.add_death()

        self.user_2 = Mock()
        self.user_2.name = "b"
        self.recorder_2 = UserRecorder(self.user_2, self.timer)
        self.recorder_2.add_score(50)
        self.recorder_2.add_shot()
        self.recorder_2.add_kill()
        self.recorder_2.add_death()

        self.analyzer = UserRecorderAnalyzer()

    def test_get_sorted_summary_table(self):
        result = self.analyzer.get_sorted_summary_table([self.recorder_1, self.recorder_2])
        assert list(result['name'].values) == ['a', 'b']
        assert list(result['score'].values) == [100, 50]
        assert list(result['shots_fired'].values) == [1, 1]
        assert list(result['kills'].values) == [2, 1]
        assert list(result['deaths'].values) == [3, 1]
        np.testing.assert_almost_equal(result['k/d'], [2/3, 1])
        np.testing.assert_almost_equal(result['shots/kills'], [0.5, 1])

