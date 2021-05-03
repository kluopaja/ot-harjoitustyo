import math
from pathlib import Path

import pytest
import pygame
from pygame import Rect, Vector2

from graphics.screen import Screen

from graphics.image import Image
from graphics.camera import Camera

from unittest.mock import Mock, ANY, create_autospec, call

@pytest.fixture
def image():
    pygame.init()
    pygame.display.set_mode((0, 0), flags=pygame.HIDDEN, vsync=1)
    tests_path = Path(__file__).parent
    return Image(Path(tests_path / "assets/test_image_1.png"))

class TestImage:
    def test_constructor_loads_correctly_shaped_image(self, image):
        assert image.image.get_rect() == Rect(0, 0, 3, 2)

    def test_aspect_ratio_wider_than_current(self, image):
        image.set_aspect_ratio(6, 2)
        assert image.get_width_pixels()/image.get_height_pixels() == 3

    def test_aspect_ratio_narrower_than_current(self, image):
        image.set_aspect_ratio(1, 2)
        assert image.get_width_pixels()/image.get_height_pixels() == 0.5
