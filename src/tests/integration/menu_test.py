import pytest
import pygame
from unittest.mock import Mock, ANY, create_autospec
import sqlite3
import unittest

import numpy

from tests.integration.game_test import database_connection, config, screen
from tests.integration.game_test import EventHandlerMock
from tests.menu_test import MockEvent

from menu.setup import create_main_menu
from user_dao import UserDao
from stats_dao import StatsDao
from user import User

@pytest.fixture()
def main_menu_factory(config, database_connection, screen):
    user_dao = UserDao(database_connection)
    user_dao.create(User("apina"))
    user_dao.create(User("banaani"))
    user_dao.create(User("cembalo"))

    def _inner(event_handler):
        return create_main_menu(screen, event_handler, config, database_connection)

    return _inner

@pytest.fixture()
def main_menu_factory_empty_database(config, database_connection, screen):
    user_dao = UserDao(database_connection)
    def _inner(event_handler):
        return create_main_menu(screen, event_handler, config, database_connection)

    return _inner

class TestGameMenuIntegration:
    def test_creating_new_user(self, main_menu_factory, database_connection):
        events = [
            MockEvent(pygame.key.key_code("return"), "?"),
            MockEvent(pygame.key.key_code("a"), "a"),
            MockEvent(pygame.key.key_code("b"), "b"),
            MockEvent(pygame.key.key_code("c"), "c"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("return"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?")]
        event_times = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
        event_handler = EventHandlerMock(events=events, event_times=event_times)
        main_menu = main_menu_factory(event_handler)
        main_menu.run()
        user_dao = UserDao(database_connection)
        assert user_dao.get_by_name("abc") is not None

    def test_creating_erasing_new_user_text(self, main_menu_factory, database_connection):
        events = [
            MockEvent(pygame.key.key_code("return"), ""),
            MockEvent(pygame.key.key_code("a"), "a"),
            MockEvent(pygame.key.key_code("b"), "b"),
            MockEvent(pygame.key.key_code("c"), "c"),
            MockEvent(pygame.key.key_code("backspace"), "?"),
            MockEvent(pygame.key.key_code("a"), "a"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("return"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?")]
        event_times = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
        event_handler = EventHandlerMock(events=events, event_times=event_times)
        main_menu = main_menu_factory(event_handler)
        main_menu.run()
        user_dao = UserDao(database_connection)
        assert user_dao.get_by_name("aba") is not None

    def test_running_game_saves_statistics_for_correct_users(self, main_menu_factory,
                                                             database_connection):
        events = [
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("return"), ""),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("right"), "?"), # select 3 players
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("right"), "?"), # banaani
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("right"), "?"), # banaani
            MockEvent(pygame.key.key_code("right"), "?"), # cembalo
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("return"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?")]
        event_times = list(numpy.linspace(0, 12, len(events)))
        event_handler = EventHandlerMock(events=events, event_times=event_times)
        main_menu = main_menu_factory(event_handler)
        main_menu.run()
        stats_dao = StatsDao(database_connection)

        top_scorers = stats_dao.get_top_scorers(3)
        names = top_scorers.get_summary_table()["name"].values
        assert len(names) == 3
        assert "apina" in names
        assert "banaani" in names
        assert "cembalo" in names

    def test_game_works_with_empty_database_but_doesnt_save_results(self, main_menu_factory_empty_database,
                                                                    database_connection):
        events = [
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("return"), ""),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("return"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?")]
        event_times = list(numpy.linspace(0, 10, len(events)))
        event_handler = EventHandlerMock(events=events, event_times=event_times)
        main_menu = main_menu_factory_empty_database(event_handler)
        main_menu.run()
        stats_dao = StatsDao(database_connection)

        top_scorers = stats_dao.get_top_scorers(2)
        names = top_scorers.get_summary_table()["name"].values
        assert len(names) == 0

    def test_added_users_replace_default_players_when_database_starts_empty(
        self, main_menu_factory_empty_database, database_connection):
        events = [
            MockEvent(pygame.key.key_code("return"), "?"),
            MockEvent(pygame.key.key_code("a"), "a"),
            MockEvent(pygame.key.key_code("b"), "b"),
            MockEvent(pygame.key.key_code("c"), "c"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("return"), "?"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("return"), ""),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("down"), "?"),
            MockEvent(pygame.key.key_code("return"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?"),
            MockEvent(pygame.key.key_code("escape"), "?")]
        event_times = list(numpy.linspace(0, 10, len(events)))
        event_handler = EventHandlerMock(events=events, event_times=event_times)
        main_menu = main_menu_factory_empty_database(event_handler)
        main_menu.run()
        stats_dao = StatsDao(database_connection)

        top_scorers = stats_dao.get_top_scorers(2)
        names = top_scorers.get_summary_table()["name"].values
        assert len(names) == 1
        assert "abc" in names
