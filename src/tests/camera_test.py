import pytest
from unittest.mock import Mock, ANY, create_autospec
import unittest

from pygame import Vector2

from graphics.drawing_surface import DrawingSurface
from graphics.camera import Camera


class TestCamera(unittest.TestCase):
    def setUp(self):
        self.drawing_surface = create_autospec(DrawingSurface)
        self.drawing_surface.get_size.return_value = Vector2(2, 1)
        self.camera = Camera(2)
        self.camera.set_drawing_surface(self.drawing_surface)

    def test_draw_line_does_nothing_if_no_drawing_surface(self):
        camera = Camera(2)
        camera.draw_line(Vector2(0), Vector2(1), (1, 2, 3), 4)

    def test_draw_line_draws_scaled_lines(self):
        self.camera.draw_line(Vector2(0), Vector2(1), (1, 2, 3), 4)
        self.drawing_surface.draw_line.assert_called_with(ANY, ANY, ANY, ANY, scaled=True)

    def test_draw_line_scales_width_correctly(self):
        self.camera.set_drawing_surface(self.drawing_surface)
        self.camera.draw_line(Vector2(0), Vector2(1), (1, 2, 3), 4)
        self.drawing_surface.draw_line.assert_called_with(ANY, ANY, ANY, 2, ANY)

    def test_draw_line_on_y_axis_when_camera_at_origo(self):
        self.camera.draw_line(Vector2(0, 1), Vector2(0, -1), (1, 2, 3), 4)
        self.drawing_surface.draw_line.assert_called_with(
            Vector2(1, 1), Vector2(1, 0), ANY, ANY, ANY)

    def test_draw_line_on_x_axis_when_camera_at_origo(self):
        self.camera.draw_line(Vector2(-2, 0), Vector2(2, 0), (1, 2, 3), 4)
        self.drawing_surface.draw_line.assert_called_with(
            Vector2(0, 0.5), Vector2(2, 0.5), ANY, ANY, ANY)

    def test_draw_line_general_when_camera_at_origo(self):
        self.camera.draw_line(Vector2(0), Vector2(1, 0.5), (1, 2, 3), 4)
        self.drawing_surface.draw_line.assert_called_with(
            Vector2(1, 0.5), Vector2(1.5, 0.75), ANY, ANY, ANY)

    def test_draw_line_general_when_camera_not_at_origo(self):
        self.camera.location = Vector2(1, 2)
        self.camera.draw_line(Vector2(0), Vector2(1, 0.5), (1, 2, 3), 4)
        self.drawing_surface.draw_line.assert_called_with(
            Vector2(1 - 0.5, 0.5 - 1), Vector2(1.5 - 0.5, 0.75 - 1), ANY, ANY, ANY)

    def test_draw_image_scales_height_correctly(self):
        image_mock = Mock()
        self.camera.draw_image(image_mock, Vector2(3, 4), 0.4, 10);
        self.drawing_surface.draw_image.assert_called_with(ANY, ANY, ANY, 5)

    def test_draw_image_draws_at_correct_location(self):
        image_mock = Mock()
        self.camera.location = Vector2(1, 2)
        self.camera.draw_image(image_mock, Vector2(1, 0.5), 0.4, 10);
        self.drawing_surface.draw_image.assert_called_with(
            ANY, Vector2(1.5 - 0.5, 0.75 - 1), ANY, ANY)

