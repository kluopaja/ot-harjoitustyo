import math
from pathlib import Path

import pytest
import pygame
from pygame import Rect, Vector2

from graphics import Image, ImageGraphic, PolylineGraphic
from shapes import Rectangle, Polyline

from tests.screen_test import ScreenStub
from screen import Screen

@pytest.fixture
def screen_stub():
    return ScreenStub(10, 10)

@pytest.fixture
def image():
    tests_path = Path(__file__).parent
    return Image(Path(tests_path / "assets/test_image_1.png"))

class TestPolylineGraphics:
    @pytest.fixture
    def polyline_graphic(self):
        polyline = Polyline.from_points([Vector2(0, 0), Vector2(1, 2), Vector2(5, 4)])
        return PolylineGraphic(polyline, (1, 2, 3), 2)

    def test_constructor_sets_color_correctly(self, polyline_graphic):
        assert polyline_graphic.color == (1, 2, 3)

    def test_constructor_sets_width_correctly(self, polyline_graphic):
        assert polyline_graphic.width == 2

    def test_draw_no_offset(self, polyline_graphic, screen_stub):
        polyline_graphic.draw(screen_stub)
        assert screen_stub.draw_line_calls[0] == {'color': (1, 2, 3),
                                                  'begin': Vector2(0, 0),
                                                  'end': Vector2(1, 2),
                                                  'width': 2}
        assert screen_stub.draw_line_calls[1] == {'color': (1, 2, 3),
                                                  'begin': Vector2(1, 2),
                                                  'end': Vector2(5, 4),
                                                  'width': 2}

    def test_draw_with_offset(self, polyline_graphic, screen_stub):
        polyline_graphic.draw(screen_stub, Vector2(5, 3))
        assert screen_stub.draw_line_calls[0] == {'color': (1, 2, 3),
                                                  'begin': -Vector2(5, 3),
                                                  'end': Vector2(1, 2) - Vector2(5, 3),
                                                  'width': 2}
        assert screen_stub.draw_line_calls[1] == {'color': (1, 2, 3),
                                                  'begin': Vector2(1, 2) - Vector2(5, 3),
                                                  'end': Vector2(5, 4) - Vector2(5, 3),
                                                  'width': 2}

    def test_location_sets_location_correctly(self, polyline_graphic):
        polyline_graphic.location = Vector2(1, 2)
        assert polyline_graphic.location == Vector2(1, 2)

    def test_rotation_sets_rotation_correctly(self, polyline_graphic):
        polyline_graphic.rotation = 1.2
        assert polyline_graphic.rotation == 1.2

    def test_location_and_draw(self, polyline_graphic, screen_stub):
        polyline_graphic.location = Vector2(1, 2)
        polyline_graphic.draw(screen_stub)
        assert screen_stub.draw_line_calls[0] == {'color': (1, 2, 3),
                                                  'begin': Vector2(1, 2),
                                                  'end': Vector2(1, 2) + Vector2(1, 2),
                                                  'width': 2}

        assert screen_stub.draw_line_calls[1] == {'color': (1, 2, 3),
                                                  'begin': Vector2(1, 2) + Vector2(1, 2),
                                                  'end': Vector2(5, 4) + Vector2(1, 2),
                                                  'width': 2}

    def test_rotation_and_draw(self, polyline_graphic, screen_stub):
        polyline_graphic.rotation = math.pi/2
        polyline_graphic.draw(screen_stub)
        assert screen_stub.draw_line_calls[0] == {'color': (1, 2, 3),
                                                  'begin': Vector2(0, 0),
                                                  'end': Vector2(2, -1),
                                                  'width': 2}

        assert screen_stub.draw_line_calls[1] == {'color': (1, 2, 3),
                                                  'begin': Vector2(2, -1),
                                                  'end': Vector2(4, -5),
                                                  'width': 2}


class TestImageGraphics:
    @pytest.fixture
    def image_graphic(self, image):
        rectangle = Rectangle(Vector2(0, 0), Vector2(3, 0), Vector2(0, 2))
        return ImageGraphic(rectangle, image)

    def test_location_initialized_to_zero(self, image_graphic):
        assert image_graphic.location == Vector2(0)

    def test_rotation_initialized_to_zero(self, image_graphic):
        assert image_graphic.rotation == 0.0

    def test_image_resized_to_match_rectangle(self, image):
        rectangle = Rectangle(Vector2(0, 0), Vector2(10, 0), Vector2(0, 10))
        image_graphic = ImageGraphic(rectangle, image)
        assert image.image.get_rect() == Rect(0, 0, 10, 10)

    def test_from_image_path_with_offset(self, screen_stub):
        tests_path = Path(__file__).parent
        image_graphic = ImageGraphic.from_image_path(
            Path(tests_path / "assets/test_image_1.png"),
            Vector2(1, 1), Vector2(3, 2))

        image_graphic.draw(screen_stub)
        assert screen_stub.blit_calls[0]['dest'] == Rect(0, 0, 3, 2)
        assert screen_stub.surface.get_at((1, 0)) == (0, 0, 0, 255)
        assert screen_stub.surface.get_at((0, 1)) == (255, 255, 255, 255)
        assert screen_stub.surface.get_at((2, 0)) == (255, 255, 255, 255)

    def test_draw(self, image_graphic, screen_stub):
        image_graphic.draw(screen_stub)
        assert screen_stub.blit_calls[0]['dest'] == Rect(0, 0, 3, 2)
        assert screen_stub.surface.get_at((1, 0)) == (0, 0, 0, 255)
        assert screen_stub.surface.get_at((0, 1)) == (255, 255, 255, 255)
        assert screen_stub.surface.get_at((2, 0)) == (255, 255, 255, 255)

    def test_draw_positive_offset(self, image_graphic, screen_stub):
        screen_stub.fill((1, 2, 3))
        image_graphic.draw(screen_stub, Vector2(1, 0))
        assert screen_stub.blit_calls[0]['dest'] == Rect(-1, 0, 3, 2)
        assert screen_stub.surface.get_at((0, 0)) == (0, 0, 0, 255)
        assert screen_stub.surface.get_at((1, 0)) == (255, 255, 255, 255)
        assert screen_stub.surface.get_at((2, 0)) == (1, 2, 3, 255)

    def test_draw_negative_offset(self, image_graphic, screen_stub):
        screen_stub.fill((1, 2, 3))
        image_graphic.draw(screen_stub, Vector2(-1, 0))
        assert screen_stub.blit_calls[0]['dest'] == Rect(1, 0, 3, 2)
        assert screen_stub.surface.get_at((0, 0)) == (1, 2, 3, 255)
        assert screen_stub.surface.get_at((1, 0)) == (0, 0, 0, 255)
        assert screen_stub.surface.get_at((2, 0)) == (0, 0, 0, 255)
        assert screen_stub.surface.get_at((3, 0)) == (255, 255, 255, 255)

    def test_location_sets_location(self, image_graphic):
        image_graphic.location = Vector2(13, 37)
        assert image_graphic.location == Vector2(13, 37)

    def test_location_moves_drawn_image(self, image_graphic, screen_stub):
        image_graphic.location = Vector2(0, 1)
        screen_stub.fill((1, 2, 3))
        image_graphic.draw(screen_stub)
        assert screen_stub.blit_calls[0]['dest'] == Rect(0, 1, 3, 2)
        assert screen_stub.surface.get_at((0, 0)) == (1, 2, 3, 255)
        assert screen_stub.surface.get_at((0, 1)) == (0, 0, 0, 255)
        assert screen_stub.surface.get_at((0, 2)) == (255, 255, 255, 255)

    def test_rotation_sets_location(self, image_graphic):
        image_graphic.location = Vector2(13, 37)
        assert image_graphic.location == Vector2(13, 37)

    def test_rotation_rotates_drawn_image(self, image_graphic, screen_stub):
        screen_stub.fill((1, 2, 3))
        image_graphic.rotation = math.pi/2
        image_graphic.draw(screen_stub)
        assert screen_stub.blit_calls[0]['dest'] == Rect(0, -3, 2, 3)
        assert screen_stub.surface.get_at((0, 0)) == (1, 2, 3, 255)
        assert screen_stub.surface.get_at((0, 1)) == (1, 2, 3, 255)
        assert screen_stub.surface.get_at((0, 2)) == (1, 2, 3, 255)

    def test_location_plus_rotation(self, image_graphic, screen_stub):
        screen_stub.fill((1, 2, 3))
        image_graphic.location = Vector2(0, 3)
        image_graphic.rotation = math.pi/2
        image_graphic.draw(screen_stub)
        assert screen_stub.blit_calls[0]['dest'] == Rect(0, 0, 2, 3)
        assert screen_stub.surface.get_at((0, 0)) == (255, 255, 255, 255)
        assert screen_stub.surface.get_at((0, 1)) == (0, 0, 0, 255)
        assert screen_stub.surface.get_at((0, 2)) == (0, 0, 0, 255)

class TestImage:
    def test_constructor_loads_correctly_shaped_image(self, image):
        assert image.image.get_rect() == Rect(0, 0, 3, 2)

    def test_draw_only_draws_to_image_area(self, image, screen_stub):
        image.draw(screen_stub)
        assert screen_stub.blit_calls[0]['dest'] == Rect(0, 0, 3, 2)

    def test_draw_only_draws_to_image_area(self, image, screen_stub):
        image.draw(screen_stub, Vector2(1, 1))
        assert screen_stub.blit_calls[0]['dest'] == Rect(0, 0, 3, 2)

    def test_draw_correct_image(self, image, screen_stub):
        image.draw(screen_stub, Vector2(1, 1))
        assert screen_stub.surface.get_at((1, 0)) == (0, 0, 0, 255)
        assert screen_stub.surface.get_at((0, 1)) == (255, 255, 255, 255)
        assert screen_stub.surface.get_at((2, 0)) == (255, 255, 255, 255)

    def test_rotate_and_draw(self, image, screen_stub):
        image.rotate_to(math.pi/2)
        image.draw(screen_stub, Vector2(1, 1))
        assert screen_stub.blit_calls[0]['dest'] == Rect(0, 0, 2, 3)
        assert screen_stub.surface.get_at((0, 0)) == (255, 255, 255, 255)
        assert screen_stub.surface.get_at((0, 1)) == (0, 0, 0, 255)
        assert screen_stub.surface.get_at((0, 2)) == (0, 0, 0, 255)

    def test_resize_draws_correct_size(self, image, screen_stub):
        image.resize(Vector2(6, 4))
        image.draw(screen_stub, Vector2(3, 2))
        assert screen_stub.blit_calls[0]['dest'] == Rect(0, 0, 6, 4)

    def test_resize_with_zero_dimensions(self, image, screen_stub):
        image.resize(Vector2(0, 0))
        image.draw(screen_stub, Vector2(3, 2))
        assert screen_stub.blit_calls[0]['dest'] == Rect(3, 2, 0, 0)

    def test_resize_with_negative_dimension(self, image, screen_stub):
        with pytest.raises(ValueError) as e:
            image.resize(Vector2(-1, 0))

        assert str(e.value) == "The resize dimensions cannot be negative"

        with pytest.raises(ValueError) as e:
            image.resize(Vector2(0, -1))

        assert str(e.value) == "The resize dimensions cannot be negative"
