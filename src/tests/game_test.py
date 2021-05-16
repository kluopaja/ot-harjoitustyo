import pytest
from unittest.mock import Mock, ANY, create_autospec
import unittest
from pygame import Vector2

from game.game import GameState, Player, Game, GameNotification, GameOrganizer
from utils.timing import Timer, Clock

from game.inputs import GameInput
from graphics.game_rendering import GameRenderer

from game.game_stats import PlayerRecorder, ResultsViewer
from stats_dao import StatsDao
from user import User

class TestGameNotification(unittest.TestCase):
    def setUp(self):
        self.game_notification = GameNotification("press key", " until spawn")

    def test_constructor_leaves_message_clear(self):
        assert self.game_notification.get_message() == ""

    def test_press_key_to_start(self):
        self.game_notification.press_key_to_start()
        assert self.game_notification.get_message() == "press key"

    def test_until_spawn(self):
        self.game_notification.until_spawn(1.4444)
        assert self.game_notification.get_message() == "1.4 until spawn"

    def test_clear(self):
        self.game_notification.press_key_to_start()
        self.game_notification.clear()
        assert self.game_notification.get_message() == ""

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.plane_mock = Mock()
        self.plane_mock.alive.return_value = True
        self.plane_factory_mock = Mock()
        self.plane_factory_mock.plane.side_effect = lambda x, y: self.plane_mock
        self.plane_factory_mock.get_plane_cost.return_value = 123
        self.player_input_mock = Mock()
        self.game_notification = GameNotification("press key", " until spawn")
        self.spawn_timer_mock = Mock()
        self.spawn_timer_mock.time_left.return_value = 10
        self.player_recorder_mock = Mock()
        self.spawn_timer_mock.expired.return_value = False
        self.user_mock = Mock()

        self.player = Player(self.plane_factory_mock, self.player_input_mock,
                             self.game_notification,
                             self.player_recorder_mock, self.user_mock,
                             self.spawn_timer_mock)

    def test_view_location_without_plane(self):
        self.plane_factory_mock.start_position = Vector2(1, 2)
        assert self.player.view_location() == Vector2(1, 2)

    def test_user_recoder_updates(self):
        self.player.update(10)
        self.player_recorder_mock.update.assert_called_with(10)

    def test_spawn_timer_updates(self):
        self.player.update(10)
        self.spawn_timer_mock.update.assert_called_with(10)

    def _create_plane_by_shoot_key_with_timer_expired(self):
        self.spawn_timer_mock.expired.return_value = True
        self.plane_mock.graphic.location = Vector2(2, 1)

        self.player.update(1)

        assert self.player_input_mock.bind_shoot.call_args.args[0] is not None
        self.player_input_mock.bind_shoot.call_args.args[0]()

    def test_shoot_key_creates_new_plane_when_spawn_timer_expired(self):
        self._create_plane_by_shoot_key_with_timer_expired()

        new_objects = self.player.new_objects()
        assert len(new_objects) == 1
        assert new_objects[0] is self.plane_mock

    def test_view_location_with_plane(self):
        self._create_plane_by_shoot_key_with_timer_expired()
        self.plane_mock.graphic.location = Vector2(3, 3)
        assert self.player.view_location() == Vector2(3, 3)

    def test_notification_when_no_plane_and_timer_not_expired(self):
        self.player.update(1)
        assert self.game_notification.get_message() == "10.0 until spawn"

    def test_notification_after_timer_expired(self):
        self.spawn_timer_mock.expired.return_value = True
        self.player.update(1)
        assert self.game_notification.get_message() == "press key"

    def test_notification_stays_clear_when_plane_exists(self):
        self._create_plane_by_shoot_key_with_timer_expired()
        self.player.update(1)
        self.player.update(1)
        assert self.game_notification.get_message() == ""

    def test_dead_plane_starts_spawn_timer(self):
        self._create_plane_by_shoot_key_with_timer_expired()
        self.plane_mock.alive.return_value = False
        previous_call_count = self.spawn_timer_mock.start.call_count
        self.player.update(10)
        # shouldn't have an effect
        self.player.update(10)
        assert self.spawn_timer_mock.start.call_count == previous_call_count + 1

    def test_dead_plane_recorded_correctly(self):
        self._create_plane_by_shoot_key_with_timer_expired()
        self.plane_mock.alive.return_value = False
        self.player.update(10)
        # shouldn't have an effect
        self.player.update(10)
        self.player_recorder_mock.add_death.assert_called_once()
        self.player_recorder_mock.add_score.assert_called_with(-123)

    def test_process_reward_self_ignored(self):
        self.player.process_reward(10, self.player)
        self.player_recorder_mock.add_score.assert_not_called()

    def test_process_reward_other_accepted(self):
        self.player.process_reward(10, Mock())
        self.player_recorder_mock.add_score.assert_called_with(10)

    def test_add_kill_self_ignored(self):
        self.player.add_kill(self.player)
        self.player_recorder_mock.add_kill.assert_not_called()

    def test_add_kill_other_not_ignored(self):
        self.player.add_kill(Mock())
        self.player_recorder_mock.add_kill.assert_called_once()

    def test_add_shot_fired(self):
        self.player.add_shot_fired()
        self.player_recorder_mock.add_shot.assert_called_once()

class TestGameState:
    def game_object_mock(self):
        mock = Mock()
        mock.new_objects.side_effect = lambda: []
        mock.shape.intersects.return_value = True
        return mock

    def player_mock(self):
        mock = Mock()
        mock.new_objects.side_effect = lambda: []
        return mock

    @pytest.fixture
    def game_state(self):
        return GameState([self.game_object_mock(), self.game_object_mock()],
                         [self.player_mock(), self.player_mock()],
                         "level1", Timer(10))

    def test_run_tick_updates_newly_created_objects(self, game_state):
        newly_created = Mock()
        game_state.game_objects[0].new_objects.side_effect = lambda: [
            newly_created]
        game_state.run_tick(1)
        newly_created.update.assert_called_with(ANY)

    def test_game_over_returns_false_if_timer_not_expired(self, game_state):
        assert not game_state.game_over()
        game_state.run_tick(5)
        assert not game_state.game_over()

    def test_game_over_returns_true_if_timer_expired(self, game_state):
        game_state.run_tick(10)
        assert game_state.game_over

    def test_intersecting_objects_collide(self, game_state):
        new_objects = [self.game_object_mock(), self.game_object_mock(),
                       self.game_object_mock()]
        def i0(x):
            if x is new_objects[0].shape or x is new_objects[1].shape:
                return True
            return False

        def i1(x):
            if x is new_objects[0].shape or x is new_objects[1].shape:
                return True
            return False

        def i2(x):
            return False
        new_objects[0].shape.intersects.side_effect = i0
        new_objects[1].shape.intersects.side_effect = i1
        new_objects[2].shape.intersects.side_effect = i2
        game_state.game_objects[0].new_objects.side_effect = lambda : new_objects

        game_state.run_tick(5)
        new_objects[0].collide.assert_called_once_with(new_objects[1])
        new_objects[1].collide.assert_called_once_with(new_objects[0])
        new_objects[2].collide.assert_not_called()



class TestGame(unittest.TestCase):
    def setUp(self):
        self.game_input = create_autospec(GameInput)
        self.game_state = create_autospec(GameState)
        self.game_renderer = create_autospec(GameRenderer)
        self.clock = create_autospec(Clock)
        self.game = Game(self.game_input, self.game_state, self.game_renderer,
                         self.clock)
        self.game_state.game_over.side_effect = [False, True]
        self.game_input.should_quit = False
        self.clock.delta_time = 2
        self.clock.busy_fraction.return_value = 0.1

    def test_game_over_quits_game(self):
        self.game_state.game_over.side_effect = [False, False, True]
        self.game.run()
        assert self.game_state.game_over.call_count == 3

    def test_quit_input_quits_game(self):
        self.game_input.should_quit = True
        self.game.run()
        assert self.clock.tick.call_count == 0

    def test_two_pause_toggles_cancel_each_other(self):
        self.game_input.bind_pause.side_effect = lambda x: {x(), x()}
        self.game.run()
        self.game_state.run_tick.assert_called()

    def test_correct_functions_called_when_not_paused(self):
        self.game.run()
        self.game_input.handle_inputs.assert_called()
        self.game_state.run_tick.assert_called()
        self.game_renderer.render.assert_called()

        self.game_input.handle_pause_inputs.assert_not_called()
        self.game_renderer.render_pause.assert_not_called()

    def test_correct_functions_called_when_paused(self):
        # execute the pause function while binding it
        self.game_input.bind_pause.side_effect = lambda x: x()
        self.game.run()
        self.game_input.bind_pause.assert_called()
        self.game_input.handle_inputs.assert_not_called()
        self.game_state.run_tick.assert_not_called()
        self.game_renderer.render.assert_not_called()

        self.game_input.handle_pause_inputs.assert_called()
        self.game_renderer.render_pause.assert_called()

    def test_get_player_recorders(self):
        player_1 = Mock()
        player_1.player_recorder = PlayerRecorder(player_1, Timer(1))
        player_2 = Mock()
        player_2.player_recorder = PlayerRecorder(player_2, Timer(2))
        self.game_state.players = [player_1, player_2]
        assert self.game.get_player_recorders() == [player_1.player_recorder,
                                                  player_2.player_recorder]

class TestGameOrganizer(unittest.TestCase):
    def setUp(self):
        self.results_viewer = create_autospec(ResultsViewer)
        self.stats_dao = create_autospec(StatsDao)
        self.game_organizer = GameOrganizer(self.results_viewer,
                                            self.stats_dao)

    def test_organize(self):
        user = User("user")
        user.id = 123
        timer = Timer(1)
        game = create_autospec(Game)
        game.get_player_recorders.side_effect = lambda: [PlayerRecorder(user, timer)]
        self.game_organizer.organize(game)
        game.run.assert_called_once()
        assert self.stats_dao.save_player_rounds.call_args is not None
        assert self.stats_dao.save_player_rounds.call_args.args[0][0].user.name == "user"
        self.results_viewer.run.assert_called_once()
