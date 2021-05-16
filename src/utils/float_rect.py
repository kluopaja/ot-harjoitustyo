class FloatRect:
    """Similar class to pygame.Rect but with floats"""

    def __init__(self, x, y, width, height):
        """Initializes FloatRect

        Arguments:
            `x`: float
                x coordinate of the top left corner
            `y`: float
                y coordinate of the top left corner
            `width`: float
            `height`: float
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def top(self):
        return self._y

    @top.setter
    def top(self, value):
        self._y = value

    @property
    def bottom(self):
        return self._y + self._height

    @bottom.setter
    def bottom(self, value):
        self._y = value - self._height

    @property
    def left(self):
        return self._x

    @left.setter
    def left(self, value):
        self._x = value

    @property
    def right(self):
        return self._x + self.width

    @right.setter
    def right(self, value):
        self._x = value - self._width

    @property
    def center(self):
        return (self._x + self._width / 2, self._y + self._height / 2)

    @center.setter
    def center(self, value):
        self._x = value[0] - self._width / 2
        self._y = value[1] - self._height / 2

    @property
    def topleft(self):
        return (self._x, self._y)

    @topleft.setter
    def topleft(self, value):
        self._x = value[0]
        self._y = value[1]

    @property
    def size(self):
        return (self._width, self._height)

    @size.setter
    def size(self, value):
        self._width = value[0]
        self._height = value[1]

    @property
    def midtop(self):
        return (self._x + self._width / 2, self._y)

    @midtop.setter
    def midtop(self, value):
        self._x = value[0] - self._width / 2
        self._y = value[1]

    @property
    def topright(self):
        return (self._x + self._width, self._y)

    @topright.setter
    def topright(self, value):
        self._x = value[0] - self._width
        self._y = value[1]

    @property
    def bottomleft(self):
        return (self._x, self._y + self._height)

    @topright.setter
    def topright(self, value):
        self._x = value[0]
        self._y = value[1] - self._height

    def copy(self):
        """Creates a copy of `self`"""
        return FloatRect(self._x, self._y, self._width, self._height)

    def __repr__(self):
        return f"FloatRect({self._x}, {self._y}, {self._width}, {self._height})"
