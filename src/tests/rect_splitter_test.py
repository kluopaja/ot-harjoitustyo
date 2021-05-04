import unittest

from utils.rect_splitter import rect_splitter
from utils.float_rect import FloatRect

class TestRectSplitter(unittest.TestCase):
    def test_one_split_vertical(self):
        rect = FloatRect(0, 0, 1, 1)
        result = rect_splitter(1, rect, start_dimension='vertical')
        assert len(result) == 2
        result = sorted(result, key=lambda x: x.left)
        assert result[0].left == 0
        assert result[0].top == 0
        assert result[0].width == 0.5
        assert result[0].height == 1
        assert result[1].left == 0.5
        assert result[1].top == 0
        assert result[1].width == 0.5
        assert result[1].height == 1

    def test_one_split_horizontal(self):
        rect = FloatRect(0, 0, 1, 1)
        result = rect_splitter(1, rect, start_dimension='horizontal')
        assert len(result) == 2
        result = sorted(result, key=lambda x: x.top)
        assert result[0].left == 0
        assert result[0].top == 0
        assert result[0].width == 1
        assert result[0].height == 0.5
        assert result[1].left == 0
        assert result[1].top == 0.5
        assert result[1].width == 1
        assert result[1].height == 0.5

    def test_zero_splits(self):
        rect = FloatRect(0, 0, 1, 1)
        result = rect_splitter(0, rect, start_dimension='horizontal')
        assert len(result) == 1
        assert result[0].left == 0
        assert result[0].top == 0
        assert result[0].width == 1
        assert result[0].height == 1


    def test_two_splits(self):
        rect = FloatRect(0, 0, 1, 1)
        result = rect_splitter(2, rect, start_dimension='vertical')
        assert len(result) == 4
        result = sorted(result, key=lambda x: (x.left, x.top))
        assert result[0].left == 0
        assert result[0].top == 0
        assert result[0].width == 0.5
        assert result[0].height == 0.5
        assert result[3].left == 0.5
        assert result[3].top == 0.5
        assert result[3].width == 0.5
        assert result[3].height == 0.5
