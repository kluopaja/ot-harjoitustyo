from unittest.mock import Mock, ANY, create_autospec
import unittest

import pygame

from game.inputs import GameKeys, GameInput

from events import EventHandler

class MockEvent:
    def __init__(self, key, event_type = pygame.KEYDOWN):
        self.key = key
        self.type = event_type

class TestGameInput(unittest.TestCase):
    def setUp(self):
        self.event_handler = create_autospec(EventHandler)
        self.event_handler.get_pressed.return_value = [0] * 1000
        self.event_handler.get_events.return_value = []
        self.game_keys = GameKeys(pygame.K_q, pygame.K_p)
        self.game_input = GameInput(self.event_handler, self.game_keys)
        self.pause = Mock()
        self.game_input.bind_pause(self.pause)

    def test_pause_key_calls_pause_function(self):
        self.event_handler.get_events.return_value = [MockEvent(pygame.K_p)]
        self.game_input.handle_inputs()
        self.pause.assert_called()
        
    def test_no_keycode_key_doesnt_call_keycode_function(self):
        x_mock = Mock()
        self.game_input.bind_key(pygame.K_x, x_mock)
        self.game_input.handle_inputs()
        x_mock.assert_not_called()

    def test_keycode_key_calls_function(self):
        x_mock = Mock()
        self.game_input.bind_key(pygame.K_x, x_mock)
        self.event_handler.get_pressed.return_value[pygame.K_x] = True
        self.game_input.handle_inputs()
        x_mock.assert_called()
