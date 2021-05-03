import logging
from constants import EPS
from pygame import Vector2
from abc import ABC, abstractmethod


class Shape(ABC):
    @property
    @abstractmethod
    def location(self):
        pass

    @location.setter
    @abstractmethod
    def location(self, value):
        pass

    @property
    @abstractmethod
    def rotation(self):
        pass

    @rotation.setter
    @abstractmethod
    def rotation(self, value):
        pass

    @abstractmethod
    def intersects(self, shape):
        pass


class Circle(Shape):
    def __init__(self, center, radius):
        if radius < 0:
            raise ValueError("The radius should be nonnegative")
        self.center = center
        self.radius = radius
        self._location = Vector2(0, 0)
        self._rotation = 0.0

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self.center += value - self._location
        self._location = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        tmp = self._location
        self.location = Vector2(0, 0)
        self.center.rotate_ip_rad(-(value - self._rotation))
        self.location = tmp
        self._rotation = value

    def intersects(self, shape):
        if isinstance(shape, Circle):
            return self._intersects_circle(shape)
        return shape.intersects(self)

    def _intersects_circle(self, circle):
        distance = (circle.center - self.center).magnitude()
        return distance < self.radius + circle.radius + EPS

    def __repr__(self):
        return f"Circle(center = {self.center}, radius = {self.radius}, location = {self.location}, rotation = {self.rotation})"


# TODO would translate and rotate be enough for these?
class Line(Shape):
    def __init__(self, begin, end):
        if (begin-end).magnitude() < EPS:
            raise ValueError("The Line must have a positive length")

        self.begin = begin
        self.end = end
        self._location = Vector2(0, 0)
        self._rotation = 0.0

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self.begin += value - self._location
        self.end += value - self._location
        self._location = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        tmp = self.location
        self.location = Vector2(0, 0)
        d_rotation = value - self._rotation
        self.begin.rotate_ip_rad(-d_rotation)
        self.end.rotate_ip_rad(-d_rotation)
        self.location = tmp
        self._rotation = value

    def projection_param(self, point):
        '''Projects `point` to `self` and returns the parameter of the result.
        '''
        v = self.end - self.begin
        p = point - self.begin
        return v.dot(p) / v.dot(v)

    def distance_to(self, point):
        pos = self.projection_param(point)
        v = self.end - self.begin
        p = point - self.begin
        if 0.0 <= pos <= 1.0:
            return (p - pos * v).magnitude()
        return min(p.magnitude(), (p - v).magnitude())

    def intersects(self, shape):
        if isinstance(shape, Circle):
            return self._intersects_circle(shape)
        if isinstance(shape, Line):
            return self._intersects_line(shape)
        return shape.intersects(self)

    def _intersects_circle(self, circle):
        return self.distance_to(circle.center) < circle.radius + EPS

    def _intersects_line(self, line):
        v = self.end - self.begin
        p1 = line.begin - self.begin
        p2 = line.end - self.begin
        if v.cross(p1) * v.cross(p2) > EPS:
            return False

        v = line.end - line.begin
        p1 = self.begin - line.begin
        p2 = self.end - line.begin
        if v.cross(p1) * v.cross(p2) > EPS:
            return False

        return True

    def __repr__(self):
        return f"Line(begin = {self.begin}, end = {self.end}, location = {self.location}, rotation = {self.rotation})"


class Rectangle(Shape):
    def __init__(self, topleft, topright, bottomleft):
        top_vector = topright - topleft
        left_vector = bottomleft - topleft
        if abs(top_vector.cross(left_vector)) < EPS:
            raise ValueError("Degenerate Rectangles are not allowed")

        if abs((top_vector).dot(left_vector)) > EPS:
            raise ValueError("Arguments do not form a rectangle")

        bottomright = bottomleft + topright - topleft

        # TODO careful with the refernces in the list!
        # Use Vector2 to copy the arguments
        self._left = Line(Vector2(topleft), Vector2(bottomleft))
        bottom = Line(Vector2(bottomleft), Vector2(bottomright))
        right = Line(Vector2(bottomright), Vector2(topright))
        self._top = Line(Vector2(topright), Vector2(topleft))
        self.sides = [self._left, bottom, right, self._top]

        self._location = Vector2(0, 0)
        self._rotation = 0.0

    @classmethod
    def from_rect(cls, rect):
        return Rectangle(Vector2(rect.topleft), Vector2(rect.topright),
                         Vector2(rect.bottomleft))

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        for i in range(len(self.sides)):
            self.sides[i].location = value
        self._location = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        for i in range(len(self.sides)):
            self.sides[i].rotation = value
        self._rotation = value

    def intersects(self, shape):
        if isinstance(shape, Circle):
            return self._intersects_circle(shape)
        if isinstance(shape, Line):
            return self._intersects_line(shape)
        if isinstance(shape, Rectangle):
            return self._intersects_rect(shape)
        return shape.intersects(self)

    def _intersects_circle(self, circle):
        if self._contains(circle.center):
            return True
        for side in self.sides:
            if side.distance_to(circle.center) < circle.radius:
                return True
        return False

    def _contains(self, point):
        '''Returns True if `point` is inside self, otherwise False'''
        return -EPS < self._top.projection_param(point) < 1 + EPS \
            and -EPS < self._left.projection_param(point) < 1 + EPS

    def _intersects_line(self, line):
        if self._contains(line.begin) or self._contains(line.end):
            return True

        return any([side.intersects(line) for side in self.sides])

    def _intersects_rect(self, rect):
        if any([rect._contains(side.begin) for side in self.sides]):
            return True
        if any([self._contains(side.begin) for side in rect.sides]):
            return True

    def center(self):
        """Returns the coordinates of the center point of the rectangle"""
        return (self.sides[0].begin + self.sides[2].begin)/2

    def size(self):
        """Returns width and height of the rectangle"""
        width = (self.sides[3].end - self.sides[3].begin).magnitude()
        height = (self.sides[0].end - self.sides[0].begin).magnitude()
        return Vector2(width, height)

    def __repr__(self):
        return f"Rectangle(topleft = {self.sides[0].begin}, topright = {self.sides[3].begin}, \
bottomleft = {self.sides[0].end}, location = {self.location}, rotation = {self.rotation})"


class Polyline(Shape):
    def __init__(self, lines):
        self.lines = lines
        self._location = Vector2(0, 0)
        self._rotation = 0.0

    @classmethod
    def from_points(cls, points):
        lines = []
        for i in range(len(points)-1):
            lines.append(Line(Vector2(points[i]), Vector2(points[i+1])))
        return cls(lines)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        for i in range(len(self.lines)):
            self.lines[i].location = value
        self._location = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        for i in range(len(self.lines)):
            self.lines[i].rotation = value
        self._rotation = value

    def intersects(self, shape):
        return any([line.intersects(shape) for line in self.lines])

    def __repr__(self):
        line_strings = [f"[{x.begin}, {x.end}]" for x in self.lines]
        line_str = ",\n".join(line_strings)
        loc_rot_str = f"location = {self.location}, rotation = {self.rotation})"
        return "Polyline([\n" + line_str + "],\n" + loc_rot_str
