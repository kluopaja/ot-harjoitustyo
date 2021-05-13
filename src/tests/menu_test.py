import pytest
import unittest
from unittest.mock import Mock

import pygame

from menu.input import MenuInput

from config import MenuInputConfig

class MockEvent:
    def __init__(self, key, unicode, event_type = pygame.KEYDOWN):
        self.key = key
        self.unicode = unicode
        self.type = event_type

class TestMenuInput(unittest.TestCase):
    def setUp(self):
        menu_keys = MenuInputConfig(pygame.K_ESCAPE, pygame.K_DOWN, pygame.K_UP,
                             pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RETURN,
                             pygame.K_BACKSPACE)

        self.event_handler = Mock()
        self.quit = Mock()
        self.next_item = Mock()
        self.previous_item = Mock()
        self.increase = Mock()
        self.decrease = Mock()
        self.accept = Mock()
        self.menu_input = MenuInput(self.event_handler, menu_keys)
        self.menu_input.bind_quit(self.quit)
        self.menu_input.bind_next_item(self.next_item)
        self.menu_input.bind_previous_item(self.previous_item)
        self.menu_input.bind_increase(self.increase)
        self.menu_input.bind_decrease(self.decrease)
        self.menu_input.bind_accept(self.accept)

        self.text = ""

        self.menu_input.bind_text(self._get_text, self._set_text)

    def _get_text(self):
        return self.text

    def _set_text(self, new_text):
        self.text = new_text

    def test_quit_key_calls_quit_function(self):
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_ESCAPE, "x")
        ]
        self.menu_input.handle_inputs()
        self.quit.assert_called()
        self.next_item.assert_not_called()

    def test_previous_item_key_calls_previous_item_function(self):
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_UP, "x")
        ]
        self.menu_input.handle_inputs()
        self.previous_item.assert_called()

    def test_next_item_key_calls_next_item_function(self):
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_DOWN, "x")
        ]
        self.menu_input.handle_inputs()
        self.next_item.assert_called()

    def test_decrease_key_calls_decrease_function(self):
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_LEFT, "x")
        ]
        self.menu_input.handle_inputs()
        self.decrease.assert_called()

    def test_increase_key_calls_increase_function(self):
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_RIGHT, "x")
        ]
        self.menu_input.handle_inputs()
        self.increase.assert_called()

    def test_clear_bindings_clear_keymaps(self):
        self.menu_input.clear_bindings()
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_RIGHT, "x")
        ]
        self.menu_input.handle_inputs()
        self.increase.assert_not_called()

    def test_clear_bindings_clear_text_input(self):
        self.menu_input.clear_bindings()
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_x, "x")
        ]
        self.menu_input.handle_inputs()
        assert self.text == ""
        self.text = "x"
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_BACKSPACE, "")
        ]
        self.menu_input.handle_inputs()
        assert self.text == "x"

    def test_text_input_add_characters_to_bound_text(self):
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_x, "x")
        ]
        self.menu_input.handle_inputs()
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_y, "y")
        ]
        self.menu_input.handle_inputs()
        assert self.text == "xy"

    def test_erase_key_erases_characters_from_the_text(self):
        self.text = "x"
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_BACKSPACE, "")
        ]
        self.menu_input.handle_inputs()
        assert self.text == ""

    def test_erase_key_doesnt_modify_empty_text(self):
        self.text = ""
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_BACKSPACE, ""),
        ]
        self.menu_input.handle_inputs()
        assert self.text == ""

    def test_two_same_events_call_the_function_twice(self):
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_RIGHT, "x"),
            MockEvent(pygame.K_RIGHT, "x")
        ]
        self.menu_input.handle_inputs()
        assert self.increase.call_count == 2

    def test_keyup_events_are_ignored(self):
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_RIGHT, "x", event_type=pygame.KEYUP),
        ]
        self.menu_input.handle_inputs()
        self.increase.assert_not_called()

    def test_whitespaces_do_not_modify_text(self):
        # clear enter from the keys
        self.menu_input.clear_bindings()
        self.menu_input.bind_text(self._get_text, self._set_text)
        self.event_handler.get_events.return_value = [
            MockEvent(pygame.K_SPACE, " "),
            MockEvent(pygame.K_RETURN, "\n"),
        ]
        self.menu_input.handle_inputs()
        # check that the enter key was cleared from the accept function
        self.accept.assert_not_called()
        assert self.text == ""
