def rect_horizontal_split(rect):
    """Splits `rect` along the horizontal axis`

    Arguments:
        `rect`: a FloatRect

    Returns:
        (r1, r2) : a tuple of FloatRects
            r1 is the upper FloatRect and r2 is the lower FloatRect"""

    upper = rect.copy()
    upper.height /= 2

    lower = rect.copy()
    lower.height = rect.height - upper.height

    lower.top = upper.bottom
    return (upper, lower)


def rect_vertical_split(rect):
    """Splits `rect` along the vertical axis`

    Arguments:
        `rect`: a FloatRect

    Returns:
        (r1, r2) : a tuple of FloatRects
            r1 is the left FloatRect and r2 is the right FloatRect"""

    left = rect.copy()
    left.width /= 2

    right = rect.copy()
    right.width = rect.width - left.width

    right.left = left.right
    return (left, right)


def rect_splitter(split_depth, rect, start_dimension='vertical'):
    """Recursively splits `rect`.

    Alternates between horizontal and vertical splits

    Arguments:
        `split_depth`: a non-negative integer
            The number of recursive splits
        `rect`: a FloatRect
        `start_dimension`: `vertical` or `horizontal`
            The direction of the first split

    Returns:
        a list of FloatRects
            The final results of the splits"""

    splitters = (rect_vertical_split, rect_horizontal_split)
    if start_dimension == 'vertical':
        pass
    elif start_dimension == 'horizontal':
        splitters = splitters[1], splitters[0]
    else:
        raise ValueError("Invalid `start_dimension`")

    split_results = [rect.copy()]

    for i in range(split_depth):
        new_split_results = []
        for x in split_results:
            new_split_results.extend(splitters[i % 2](x))
        split_results = new_split_results

    return split_results
