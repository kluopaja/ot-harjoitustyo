import math

import pytest
from pygame import Vector2

from game.shapes import Circle, Line, Rectangle, Polyline
from constants import EPS


def vec_eq(v1, v2):
    return (v1-v2).magnitude() < EPS


def line_eq(l1, l2):
    return vec_eq(l1.begin, l2.begin) and vec_eq(l1.end, l2.end)


def rect_eq(r1, r2):
    return all([line_eq(x, y) for x, y in zip(r1.sides, r2.sides)])


def polyline_eq(p1, p2):
    return all([line_eq(x, y) for x, y in zip(p1.lines, p2.lines)])


class TestCircle:
    @pytest.fixture
    def circle1(self):
        return Circle(Vector2(1, 2), 3)

    def test_contructor_sets_data_members_correctly(self):
        circle = Circle(Vector2(12, 13), 1)
        assert circle.center == Vector2(12, 13)
        assert circle.radius == 1

    def test_constructor_fails_with_negative_radius(self):
        with pytest.raises(ValueError) as e:
            Circle(Vector2(12, 13), -1)

        assert "The radius should be nonnegative" == str(e.value)

    def test_setting_location_changes_location_correctly(self, circle1):
        circle1.location = Vector2(1, 3)
        assert vec_eq(circle1.location, Vector2(1, 3))

    def test_setting_location_changes_center_correctly(self, circle1):
        circle1.location = Vector2(1, 3)
        assert vec_eq(circle1.center, Vector2(1+1, 2+3))

    def test_setting_rotation_changes_rotation_correctly(self, circle1):
        circle1.rotation = 1
        assert circle1.rotation == 1

    def test_setting_rotation_changes_center_correctly(self, circle1):
        circle1.rotation = math.pi / 2
        assert vec_eq(circle1.center, Vector2(2, -1))

    def test_location_plus_rotation_change_center_correctly(self, circle1):
        circle1.location = Vector2(1, 3)
        circle1.rotation = math.pi / 2
        assert vec_eq(circle1.center, Vector2(2 + 1, -1 + 3))

    def test_repr(self, circle1):
        assert "Circle(center = [1, 2], radius = 3, location = [0, 0], rotation = 0.0)" \
            == repr(circle1)


class TestLine:
    @pytest.fixture
    def line1(self):
        return Line(Vector2(1, 2), Vector2(3, 1))

    @pytest.fixture
    def line_45_degrees(self):
        return Line(Vector2(1, 2), Vector2(2, 3))

    def test_contructor_sets_data_members_correctly(self, line1):
        assert line1.begin == Vector2(1, 2)
        assert line1.end == Vector2(3, 1)

    def test_constructor_fails_when_line_length_is_zero(self):
        with pytest.raises(ValueError) as e:
            Line(Vector2(12, 13), Vector2(12, 13))

        assert "The Line must have a positive length" == str(e.value)

    def test_setting_location_changes_location_correctly(self, line1):
        line1.location = Vector2(1, 3)
        assert vec_eq(line1.location, Vector2(1, 3))

    def test_setting_location_changes_endpoints_correctly(self, line1):
        line1.location = Vector2(1, 3)
        assert vec_eq(line1.begin, Vector2(1+1, 2+3))
        assert vec_eq(line1.end, Vector2(3+1, 1+3))

    def test_setting_rotation_changes_rotation_correctly(self, line1):
        line1.rotation = 1
        assert line1.rotation == 1

    def test_setting_rotation_changes_endpoints_correctly(self, line1):
        line1.rotation = math.pi / 2
        assert vec_eq(line1.begin, Vector2(2, -1))
        assert vec_eq(line1.end, Vector2(1, -3))

    def test_location_plus_rotation_change_endpoints_correctly(self, line1):
        line1.location = Vector2(1, 3)
        line1.rotation = math.pi / 2
        assert vec_eq(line1.begin, Vector2(2 + 1, -1 + 3))
        assert vec_eq(line1.end, Vector2(1 + 1, -3 + 3))

    def test_projection_param_point_already_on_line(self, line1):
        position = line1.projection_param(
            Vector2(1, 2) * 0.8 + Vector2(3, 1) * 0.2)
        assert pytest.approx(position, EPS) == 0.2

    def test_projection_param_point_projection_on_line(self, line1):
        # (3, 1) - (1, 2) = (2, -1) --> (1, 2) is perpendicular
        point = Vector2(1, 2) * 0.8 + Vector2(3, 1) * 0.2 + Vector2(1, 2)
        assert pytest.approx(line1.projection_param(point), EPS) == 0.2

    def test_projection_param_point_projection_outside_line(self, line1):
        # (3, 1) - (1, 2) = (2, -1) --> (1, 2) is perpendicular
        point = Vector2(1, 2) + (Vector2(3, 1) -
                                 Vector2(1, 2)) * 3 + Vector2(1, 2)
        assert pytest.approx(line1.projection_param(point), EPS) == 3

    def test_distance_to_closest_at_begin(self, line_45_degrees):
        assert pytest.approx(line_45_degrees.distance_to(
            Vector2(0.5, 2)), EPS) == 0.5

    def test_distance_to_closest_at_end(self, line_45_degrees):
        assert pytest.approx(line_45_degrees.distance_to(
            Vector2(2, 3.5)), EPS) == 0.5

    def test_distance_to_point_on_line(self, line_45_degrees):
        point = Vector2(1, 2) + 0.5 * Vector2(1, 1)
        assert pytest.approx(line_45_degrees.distance_to(point), EPS) == 0.0

    def test_distance_to_closest_at_projection(self, line_45_degrees):
        point = Vector2(1, 2) + 0.5 * Vector2(1, 1) + Vector2(1, -1)
        assert pytest.approx(line_45_degrees.distance_to(
            point), EPS) == math.sqrt(2)

    def test_repr(self, line1):
        assert "Line(begin = [1, 2], end = [3, 1], location = [0, 0], rotation = 0.0)" \
            == repr(line1)


class TestRectangle:
    @pytest.fixture
    def rect1(self):
        return Rectangle(Vector2(0, 0), Vector2(2, 0), Vector2(0, 1))

    def test_contructor_sets_data_members_correctly(self, rect1):
        assert line_eq(rect1.sides[0], Line(Vector2(0, 0), Vector2(0, 1)))
        assert line_eq(rect1.sides[1], Line(Vector2(0, 1), Vector2(2, 1)))
        assert line_eq(rect1.sides[2], Line(Vector2(2, 1), Vector2(2, 0)))
        assert line_eq(rect1.sides[3], Line(Vector2(2, 0), Vector2(0, 0)))

    def test_constructor_fails_when_degenerate(self):
        with pytest.raises(ValueError) as e:
            Rectangle(Vector2(0, 0), Vector2(0, 0), Vector2(1, 0))

        assert "Degenerate Rectangles are not allowed" == str(e.value)

    def test_constructor_fails_when_not_rectangular(self):
        with pytest.raises(ValueError) as e:
            Rectangle(Vector2(0, 0), Vector2(1, 0), Vector2(1, 1))

        assert "Arguments do not form a rectangle" == str(e.value)

    def test_setting_location_changes_location_correctly(self, rect1):
        rect1.location = Vector2(1, 3)
        assert vec_eq(rect1.location, Vector2(1, 3))

    def test_setting_location_moves_sides_correctly(self, rect1):
        rect1.location = Vector2(1, 3)
        assert rect_eq(rect1, Rectangle(
            Vector2(1, 3), Vector2(3, 3), Vector2(1, 4)))

    def test_setting_rotation_changes_rotation_correctly(self, rect1):
        rect1.rotation = 1
        assert rect1.rotation == 1

    def test_setting_rotation_moves_sides_correctly(self, rect1):
        rect1.rotation = math.pi / 2
        assert rect_eq(rect1, Rectangle(
            Vector2(0, 0), Vector2(0, -2), Vector2(1, 0)))

    def test_location_plus_rotation_change_endpoints_correctly(self, rect1):
        rect1.location = Vector2(1, 3)
        rect1.rotation = math.pi / 2
        assert rect_eq(rect1, Rectangle(Vector2(1, 3), Vector2(0 + 1, -2 + 3),
                                        Vector2(1 + 1, 0 + 3)))

    def test_repr(self, rect1):
        assert "Rectangle(topleft = [0, 0], topright = [2, 0], bottomleft = [0, 1], location = [0, 0], rotation = 0.0)" \
            == repr(rect1)


class TestPolyline:
    @pytest.fixture
    def polyline1(self):
        return Polyline([Line(Vector2(0, 0), Vector2(2, 0)),
                         Line(Vector2(0, 1), Vector2(2, 2))])

    def test_contructor_sets_data_members_correctly(self, polyline1):
        assert line_eq(polyline1.lines[0], Line(Vector2(0, 0), Vector2(2, 0)))
        assert line_eq(polyline1.lines[1], Line(Vector2(0, 1), Vector2(2, 2)))

    def test_from_points_sets_data_members_correctly(self):
        polyline = Polyline.from_points(
            [Vector2(0, 0), Vector2(0, 1), Vector2(1, 3)])
        assert line_eq(polyline.lines[0], Line(Vector2(0, 0), Vector2(0, 1)))
        assert line_eq(polyline.lines[1], Line(Vector2(0, 1), Vector2(1, 3)))

    def test_from_points_fails_when_degenerate_lines(self):
        with pytest.raises(ValueError) as e:
            Polyline.from_points([Vector2(0, 0), Vector2(0, 0), Vector2(1, 3)])

        assert "The Line must have a positive length" == str(e.value)

    def test_setting_location_changes_location_correctly(self, polyline1):
        polyline1.location = Vector2(1, 3)
        assert vec_eq(polyline1.location, Vector2(1, 3))

    def test_setting_location_moves_sides_correctly(self, polyline1):
        polyline1.location = Vector2(1, 3)
        assert polyline_eq(polyline1, Polyline([Line(Vector2(0+1, 0+3), Vector2(2+1, 0+3)),
                                                Line(Vector2(0+1, 1+3), Vector2(2+1, 2+3))]))

    def test_setting_rotation_changes_rotation_correctly(self, polyline1):
        polyline1.rotation = 1
        assert polyline1.rotation == 1

    def test_setting_rotation_moves_sides_correctly(self, polyline1):
        polyline1.rotation = math.pi / 2
        assert polyline_eq(polyline1, Polyline([Line(Vector2(0, 0), Vector2(0, -2)),
                                                Line(Vector2(1, 0), Vector2(2, -2))]))

    def test_location_plus_rotation_change_endpoints_correctly(self, polyline1):
        polyline1.location = Vector2(1, 3)
        polyline1.rotation = math.pi / 2
        assert polyline_eq(polyline1, Polyline([Line(Vector2(0+1, 0+3), Vector2(0+1, -2+3)),
                                                Line(Vector2(1+1, 0+3), Vector2(2+1, -2+3))]))

    def test_repr(self, polyline1):
        assert """Polyline([
[[0, 0], [2, 0]],
[[0, 1], [2, 2]]],
location = [0, 0], rotation = 0.0)""" \
                == repr(polyline1)


class TestCollisions:
    @pytest.fixture
    def unit_circle(self):
        return Circle(Vector2(0, 0), 1)

    @pytest.fixture
    def polyline1(self):
        return Polyline([Line(Vector2(2, 3), Vector2(3, 4)),
                         Line(Vector2(4, 5), Vector2(5, 6))])

    def test_circle_circle_no_intersection(self, unit_circle):
        circle2 = Circle(Vector2(3, 0), 1)
        assert not unit_circle.intersects(circle2)
        assert not circle2.intersects(unit_circle)

    def test_circle_circle_intersection(self, unit_circle):
        circle2 = Circle(Vector2(1, 0), 1)
        assert unit_circle.intersects(circle2)
        assert circle2.intersects(unit_circle)

    def test_line_circle_no_intersection(self, unit_circle):
        line = Line(Vector2(1, 1), Vector2(1, 2))
        assert not unit_circle.intersects(line)
        assert not line.intersects(unit_circle)

    def test_line_circle_intersection(self, unit_circle):
        line = Line(Vector2(0, 0.8), Vector2(1, 2))
        assert unit_circle.intersects(line)
        assert line.intersects(unit_circle)

    def test_line_line_no_intersection(self):
        line1 = Line(Vector2(1, 1), Vector2(1, 2))
        line2 = Line(Vector2(1+1, 1+1), Vector2(1+1, 2+1))
        assert not line1.intersects(line2)
        assert not line2.intersects(line1)

    def test_line_line_intersection_with_itself(self):
        line1 = Line(Vector2(1, 1), Vector2(1, 2))
        line2 = Line(Vector2(1, 1), Vector2(1, 2))
        assert line1.intersects(line2)
        assert line2.intersects(line1)

    def test_line_line_intersection(self):
        line1 = Line(Vector2(-1, -1), Vector2(1, 1))
        line2 = Line(Vector2(-1, 1), Vector2(1, -1))
        assert line1.intersects(line2)
        assert line2.intersects(line1)

    def test_rectangle_circle_no_intersection(self, unit_circle):
        rect = Rectangle(Vector2(1.1, 0), Vector2(2, 0), Vector2(1.1, 1))
        assert not unit_circle.intersects(rect)
        assert not rect.intersects(unit_circle)

    def test_rectangle_circle_intersection_center_inside_rect(self, unit_circle):
        rect = Rectangle(Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1))
        assert unit_circle.intersects(rect)
        assert rect.intersects(unit_circle)

    def test_rectangle_circle_intersection_center_not_inside_rect(self, unit_circle):
        rect = Rectangle(Vector2(0.8, 0), Vector2(2, 0), Vector2(0.8, 1))
        assert unit_circle.intersects(rect)
        assert rect.intersects(unit_circle)

    def test_rectangle_rectangle_no_intersection(self):
        rect1 = Rectangle(Vector2(1, 0), Vector2(2, 0), Vector2(1, 1))
        rect2 = Rectangle(Vector2(2.5, 0), Vector2(3, 0), Vector2(2.5, 1))
        assert not rect1.intersects(rect2)
        assert not rect2.intersects(rect1)

    def test_rectangle_rectangle_intersection(self):
        rect1 = Rectangle(Vector2(1, 0), Vector2(2, 0), Vector2(1, 1))
        rect2 = Rectangle(Vector2(0.5, 0), Vector2(3, 0), Vector2(0.5, 1))
        assert rect1.intersects(rect2)
        assert rect2.intersects(rect1)

    def test_rectangle_rectangle_intersection_fully_inside_other(self):
        rect1 = Rectangle(Vector2(1, 0), Vector2(2, 0), Vector2(1, 1))
        rect2 = Rectangle(Vector2(1.1, 0.1), Vector2(
            1.2, 0.1), Vector2(1.1, 0.3))
        assert rect1.intersects(rect2)
        assert rect2.intersects(rect1)

    def test_polyline_circle_no_intersection(self, unit_circle, polyline1):
        assert not polyline1.intersects(unit_circle)
        assert not unit_circle.intersects(polyline1)

    def test_polyline_circle_intersection(self, unit_circle):
        polyline = Polyline([Line(Vector2(0, 0), Vector2(3, 4)),
                             Line(Vector2(4, 5), Vector2(5, 6))])
        assert polyline.intersects(unit_circle)
        assert unit_circle.intersects(polyline)

    def test_polyline_line_no_intersection(self, polyline1):
        line = Line(Vector2(10, 12), Vector2(13, 14))
        assert not polyline1.intersects(line)
        assert not line.intersects(polyline1)

    def test_polyline_line_intersection(self, polyline1):
        line = Line(Vector2(3, 4), Vector2(4.5, 5.5))
        assert polyline1.intersects(line)
        assert line.intersects(polyline1)

    def test_polyline_rectangle_no_intersection(self, polyline1):
        rectangle = Rectangle(Vector2(0, 0), Vector2(1, 0), Vector2(0, 1))
        assert not polyline1.intersects(rectangle)
        assert not rectangle.intersects(polyline1)

    def test_polyline_rectangle_intersection(self, polyline1):
        rectangle = Rectangle(Vector2(2, 3), Vector2(2.2, 3), Vector2(2, 3.3))
        assert polyline1.intersects(rectangle)
        assert rectangle.intersects(polyline1)

    def test_polyline_rectangle_intersection_polyline_inside_rectangle(self, polyline1):
        rectangle = Rectangle(Vector2(0, 0), Vector2(10, 0), Vector2(0, 10))
        assert polyline1.intersects(rectangle)
        assert rectangle.intersects(polyline1)

    def test_polyline_polyline_no_intersection(self, polyline1):
        polyline2 = Polyline([Line(Vector2(10, 23), Vector2(23, 42)),
                             Line(Vector2(12, 10), Vector2(33, 44))])
        assert not polyline1.intersects(polyline2)
        assert not polyline2.intersects(polyline1)

    def test_polyline_polyline_intersection(self, polyline1):
        polyline2 = Polyline(
            [Line(Vector2(2.5 + 1, 3.5 - 1), Vector2(3 - 1, 4 + 1))])
        assert polyline1.intersects(polyline2)
        assert polyline2.intersects(polyline1)
