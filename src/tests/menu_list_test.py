import pytest
import unittest
from unittest.mock import Mock, create_autospec

import pygame

from menu.menu_list import MenuList
from menu.input import MenuInput
from graphics.menu_rendering import MenuListRenderer
from menu.menu_items import MenuItemCollection, MenuItem
from utils.timing import Clock

from config import MenuInputConfig


class TestMenuList(unittest.TestCase):
    def setUp(self):
        self.menu_renderer = create_autospec(MenuListRenderer)
        self.menu_input = create_autospec(MenuInput)
        self.item_collection = create_autospec(MenuItemCollection)
        self.clock = create_autospec(Clock)
        self.menu_list = MenuList(self.menu_renderer, self.menu_input,
                                  self.item_collection, self.clock)

    def test_empty_item_collection(self):
        self.item_collection.get_item_list.side_effect = lambda: []
        self.menu_list.run_tick()
        self.menu_renderer.render.assert_called_with([], None)

    def test_empty_item_collection_made_non_empty(self):
        self.item_collection.get_item_list.side_effect = lambda: []
        self.menu_list.run_tick()
        menu_item = MenuItem()
        self.item_collection.get_item_list.side_effect = lambda: [menu_item]
        self.menu_list.run_tick()
        self.menu_renderer.render.assert_called_with([menu_item], 0)

    def test_select_next_item(self):
        menu_items = [MenuItem(), MenuItem()]
        self.item_collection.get_item_list.side_effect = lambda: menu_items
        self.menu_input.bind_next_item.side_effect = lambda x: x()
        self.menu_list.run_tick()
        self.menu_input.bind_next_item.assert_called()
        self.menu_renderer.render.assert_called_with(menu_items, 1)

    def test_shrink_menu_items_past_selected(self):
        menu_items = [MenuItem(), MenuItem()]
        self.item_collection.get_item_list.side_effect = lambda: menu_items
        self.menu_input.bind_next_item.side_effect = lambda x: x()
        self.menu_list.run_tick()
        menu_items.pop()
        self.menu_list.run_tick()
        self.menu_renderer.render.assert_called_with(menu_items, 0)
