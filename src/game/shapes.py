from abc import ABC, abstractmethod
from pygame import Vector2
from constants import EPS


class Shape(ABC):
    """A base class for Shape classes.

    The final location/rotation of the Shape corresponds to the
    location/rotation as if the Shape was first rotated to
    `rotation` and then translated by the vector from origo to `location`.

    NOTE: The `location` doesn't always correspond to the intuitive location
    of the shape. For example, we might have a Shape which is a circle drawn
    around point (1, 1). The location of this might still be (0
    and changing the location to (2, 2) our circle would be around (3, 3).

    Attributes:
        `location`: A pygame.Vector2
            The location of the Shape
        `rotation`: Radians
            Positive rotation mean counter-clockwise
            (in coordinates where x grows right and y grows down)

    """
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
        """Returns True if `self` intersects `shape`, False otherwise."""
        pass


class Circle(Shape):
    """A class representing a Circle.

    Attributes:
        `center`: A pygame.Vector2 (read only)
            The center of the circle
        `radius`: A non_negative float (read only)
            The radius of the circle
        """
    def __init__(self, center, radius):
        """Initializes Circle

        NOTE: `self.location` will be initialized to Vector2(0, 0)
        and `self.rotation` will be initialized to 0!

        Arguments:
            `center`: A pygame.Vector2
                The center of the circle
            `radius`: A non_negative float
                The radius of the circle
        """
        if radius < 0:
            raise ValueError("The radius should be nonnegative")
        self._center = center
        self._radius = radius
        self._location = Vector2(0, 0)
        self._rotation = 0.0

    @property
    def center(self):
        return self._center

    @property
    def radius(self):
        return self._radius

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._center += value - self._location
        self._location = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        tmp = self._location
        self.location = Vector2(0, 0)
        self._center.rotate_ip_rad(-(value - self._rotation))
        self.location = tmp
        self._rotation = value

    def intersects(self, shape):
        """See the base class"""
        if isinstance(shape, Circle):
            return self._intersects_circle(shape)
        return shape.intersects(self)

    def _intersects_circle(self, circle):
        distance = (circle._center - self._center).magnitude()
        return distance < self._radius + circle._radius + EPS

    def __repr__(self):
        return (f"Circle(center = {self._center}, radius = {self._radius}, "
               f"location = {self.location}, rotation = {self.rotation})")


class Line(Shape):
    """A class representing a Line.

    Attributes:
        `begin`: A pygame.Vector2 (read only)
            The start point of the line
        `end`: A pygame.Vector2 (read only)
            The end point of the line
    """
    def __init__(self, begin, end):
        """Initializes Line

        NOTE: `self.location` will be initialized to Vector2(0, 0)
        and `self.rotation` will be initialized to 0!


        Arguments:
            `begin`: A pygame.Vector2
                The start point of the line
            `end`: A pygame.Vector2
                The end point of the line

            NOTE: The lenght of the line should be positive.
        """
        if (begin-end).magnitude() < EPS:
            raise ValueError("The Line must have a positive length")

        self._begin = begin
        self._end = end
        self._location = Vector2(0, 0)
        self._rotation = 0.0

    @property
    def begin(self):
        return self._begin

    @property
    def end(self):
        return self._end

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._begin += value - self._location
        self._end += value - self._location
        self._location = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        tmp = self.location
        self.location = Vector2(0, 0)
        d_rotation = value - self._rotation
        self._begin.rotate_ip_rad(-d_rotation)
        self._end.rotate_ip_rad(-d_rotation)
        self.location = tmp
        self._rotation = value

    def projection_param(self, point):
        """Projects `point` to `self` and returns the parameter of the result.

        Arguments:
            `point`: A pygame.Vector2
        """
        v = self._end - self._begin
        p = point - self._begin
        return v.dot(p) / v.dot(v)

    def distance_to(self, point):
        """Returns the distance of `point` to `self`.

        Arguments:
            `point`: A pygame.Vector2
        """
        pos = self.projection_param(point)
        v = self._end - self._begin
        p = point - self._begin
        if 0.0 <= pos <= 1.0:
            return (p - pos * v).magnitude()
        return min(p.magnitude(), (p - v).magnitude())

    def intersects(self, shape):
        """See the base class"""
        if isinstance(shape, Circle):
            return self._intersects_circle(shape)
        if isinstance(shape, Line):
            return self._intersects_line(shape)
        return shape.intersects(self)

    def _intersects_circle(self, circle):
        return self.distance_to(circle.center) < circle.radius + EPS

    def _intersects_line(self, line):
        v = self._end - self._begin
        p1 = line._begin - self._begin
        p2 = line._end - self._begin
        if v.cross(p1) * v.cross(p2) > EPS:
            return False

        v = line._end - line._begin
        p1 = self._begin - line._begin
        p2 = self._end - line._begin
        if v.cross(p1) * v.cross(p2) > EPS:
            return False

        return True

    def __repr__(self):
        return (f"Line(begin = {self._begin}, end = {self._end}, "
               f"location = {self.location}, rotation = {self.rotation})")


class Rectangle(Shape):
    """A class representing a rectangle.

    Attributes:
        `sides`: A list of Line objects
            The sides of the Rectangle.

            NOTE: Should NOT be modified!
    """

    def __init__(self, topleft, topright, bottomleft):
        """Initializes a Rectangle.

        Arguments:
            `topleft`: A pygame.Vector2
                The position of the topleft corner of the Rectangle
            `topright`: A pygame.Vector2
                The position of the topright corner of the Rectangle
            `bottomleft`: A pygame.Vector2
                The position of the bottomleft corner of the Rectangle

            NOTE: The arguments should form a rectangle.

            NOTE: The rectangle should have positive area.
        """
        top_vector = topright - topleft
        left_vector = bottomleft - topleft
        if abs(top_vector.cross(left_vector)) < EPS:
            raise ValueError("Degenerate Rectangles are not allowed")

        if abs((top_vector).dot(left_vector)) > EPS:
            raise ValueError("Arguments do not form a rectangle")

        bottomright = bottomleft + topright - topleft

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
        """See the base class"""
        if isinstance(shape, Circle):
            return self._intersects_circle(shape)
        if isinstance(shape, Line):
            return self._intersects_line(shape)
        if isinstance(shape, Rectangle):
            return self._intersects_rectangle(shape)
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

        return any(side.intersects(line) for side in self.sides)

    def _intersects_rectangle(self, rectangle):
        if any(rectangle._contains(side.begin) for side in self.sides):
            return True
        if any(self._contains(side.begin) for side in rectangle.sides):
            return True
        return False

    def center(self):
        """Returns the coordinates of the center point of the rectangle.

        Returns:
            pygame.Vector2
        """
        return Vector2(self.sides[0].begin + self.sides[2].begin)/2

    def size(self):
        """Returns width and height of the rectangle.

        Returns:
            pygame.Vector2
        """
        width = (self.sides[3].end - self.sides[3].begin).magnitude()
        height = (self.sides[0].end - self.sides[0].begin).magnitude()
        return Vector2(width, height)

    def __repr__(self):
        return f"Rectangle(topleft = {self.sides[0].begin}, topright = {self.sides[3].begin}, \
bottomleft = {self.sides[0].end}, location = {self.location}, rotation = {self.rotation})"


class Polyline(Shape):
    """A class representing a collection of Line objects.

    Attributes:
        `lines`: A list of Line objects
    """
    def __init__(self, lines):
        """Initializes a Polyline.

        Attributes:
            `lines`: A list of Line objects
        """
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
        """See the base class"""
        return any(line.intersects(shape) for line in self.lines)

    def __repr__(self):
        line_strings = [f"[{x.begin}, {x.end}]" for x in self.lines]
        line_str = ",\n".join(line_strings)
        loc_rot_str = f"location = {self.location}, rotation = {self.rotation})"
        return "Polyline([\n" + line_str + "],\n" + loc_rot_str
