import math
from pathlib import Path

import pytest
import pygame
from pygame import Rect, Vector2

from graphics.graphics import ImageGraphic, PolylineGraphic
from graphics.image import Image
from game.shapes import Rectangle, Polyline

from graphics.screen import Screen

from graphics.camera import Camera

from unittest.mock import Mock, ANY, create_autospec, call

@pytest.fixture
def camera_stub():
    return create_autospec(Camera)


@pytest.fixture
def image():
    pygame.init()
    pygame.display.set_mode((0, 0), flags=pygame.HIDDEN, vsync=1)
    tests_path = Path(__file__).parent
    return Image(Path(tests_path / "assets/test_image_1.png"))


class TestPolylineGraphics:
    @pytest.fixture
    def polyline_graphic(self):
        polyline = Polyline.from_points(
            [Vector2(0, 0), Vector2(1, 2), Vector2(5, 4)])
        return PolylineGraphic(polyline, (1, 2, 3), 2)

    def test_constructor_sets_color_correctly(self, polyline_graphic):
        assert polyline_graphic.color == (1, 2, 3)

    def test_constructor_sets_width_correctly(self, polyline_graphic):
        assert polyline_graphic.width == 2

    def test_draw(self, polyline_graphic, camera_stub):
        polyline_graphic.draw(camera_stub)
        calls = [call(Vector2(0, 0), Vector2(1, 2), (1, 2, 3), 2),
                 call(Vector2(1, 2), Vector2(5, 4), (1, 2, 3), 2)]
        camera_stub.draw_line.assert_has_calls(calls, any_order=True)

    def test_location_sets_location_correctly(self, polyline_graphic):
        polyline_graphic.location = Vector2(1, 2)
        assert polyline_graphic.location == Vector2(1, 2)

    def test_rotation_sets_rotation_correctly(self, polyline_graphic):
        polyline_graphic.rotation = 1.2
        assert polyline_graphic.rotation == 1.2

    def test_location_and_draw(self, polyline_graphic, camera_stub):
        polyline_graphic.location = Vector2(1, 2)
        polyline_graphic.draw(camera_stub)
        calls = [call(Vector2(1, 2), Vector2(1, 2) + Vector2(1, 2), (1, 2, 3), 2),
                 call(Vector2(1, 2) + Vector2(1, 2), Vector2(5, 4) + Vector2(1, 2),
                      (1, 2, 3), 2)]
        camera_stub.draw_line.assert_has_calls(calls, any_order=True)

    def test_rotation_and_draw(self, polyline_graphic, camera_stub):
        polyline_graphic.rotation = math.pi/2
        polyline_graphic.draw(camera_stub)
        calls = [call(Vector2(0, 0), Vector2(2, -1), (1, 2, 3), 2),
                 call(Vector2(2, -1), Vector2(4, -5), (1, 2, 3), 2)]
        camera_stub.draw_line.assert_has_calls(calls, any_order=True)


class TestImageGraphics:
    @pytest.fixture
    def image_graphic(self, image):
        rectangle = Rectangle(Vector2(0, 0), Vector2(3, 0), Vector2(0, 2))
        return ImageGraphic(rectangle, image)

    def test_location_initialized_to_zero(self, image_graphic):
        assert image_graphic.location == Vector2(0)

    def test_rotation_initialized_to_zero(self, image_graphic):
        assert image_graphic.rotation == 0.0

    def test_from_image_path_resizes_image_to_match_aspect_ratio(self, camera_stub):
        tests_path = Path(__file__).parent
        image_graphic = ImageGraphic.from_image_path(
            Path(tests_path / "assets/test_image_1.png"),
            Vector2(0, 0), Vector2(10, 10)
        )
        image_graphic.draw(camera_stub)
        camera_stub.draw_image.assert_called()
        image = camera_stub.draw_image.call_args.args[0]
        assert image.get_height_pixels() == image.get_width_pixels()

    def test_from_image_path_with_offset(self, camera_stub):
        tests_path = Path(__file__).parent
        image_graphic = ImageGraphic.from_image_path(
            Path(tests_path / "assets/test_image_1.png"),
            Vector2(1, 1), Vector2(3, 2))

        image_graphic.draw(camera_stub)
        camera_stub.draw_image.assert_called_with(ANY, Vector2(1, 1), ANY, ANY)

    def test_draw(self, image_graphic, camera_stub):
        image_graphic.draw(camera_stub)
        camera_stub.draw_image.assert_called_with(ANY, Vector2(1.5, 1), 0, 2)

    def test_location_sets_location(self, image_graphic):
        image_graphic.location = Vector2(13, 37)
        assert image_graphic.location == Vector2(13, 37)

    def test_location_moves_drawn_image(self, image_graphic, camera_stub):
        image_graphic.location = Vector2(0, 1)
        image_graphic.draw(camera_stub)
        camera_stub.draw_image.assert_called_with(ANY, Vector2(1.5, 2), ANY, ANY)

    def test_rotation_sets_rotation(self, image_graphic):
        image_graphic.rotation = 123
        assert image_graphic.rotation == 123

    def test_rotation_rotates_drawn_image(self, image_graphic, camera_stub):
        image_graphic.rotation = math.pi/2
        image_graphic.draw(camera_stub)
        camera_stub.draw_image.assert_called_with(ANY, ANY, math.pi/2, ANY)

    def test_location_plus_rotation(self, image_graphic, camera_stub):
        print(image_graphic.location, image_graphic._rectangle.center())
        image_graphic.location = Vector2(0, 3)
        print(image_graphic.location, image_graphic._rectangle.center())
        image_graphic.rotation = math.pi/2
        print(image_graphic.location, image_graphic._rectangle.center())
        image_graphic.draw(camera_stub)
        camera_stub.draw_image.assert_called_with(ANY, Vector2(1, 1.5), math.pi/2, ANY)
