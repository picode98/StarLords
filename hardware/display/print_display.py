from .display import Display


def _pixel_str(value):
    r, g, b = value
    if r >= 245 and g <= 10 and b <= 10:
        return 'r'
    elif r <= 10 and g >= 245 and b <= 10:
        return 'g'
    elif r <= 10 and g <= 10 and b >= 245:
        return 'b'
    elif r <= 10 and g <= 10 and b <= 10:
        return ' '
    else:
        return 'o'


class PrintDisplay(Display):
    def __init__(self, height: int, width: int):
        super().__init__(height, width)
        self._colors = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

    def __setitem__(self, indices, value):
        x, y = indices
        self._colors[y][x] = value

    def write(self):
        for row in self._colors:
            print(''.join(_pixel_str(color) for color in row))
