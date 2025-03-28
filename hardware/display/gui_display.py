import tkinter

from .display import Display

class GUIDisplay(Display):
    def __init__(self, parent, height, width, gui_height, gui_width):
        super().__init__(height, width)
        self._canvas = tkinter.Canvas(parent, background='black', height=gui_height, width=gui_width)
        self._canvas.pack()

        self._gui_height, self._gui_width = gui_height, gui_width
        self._colors = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

        x_size, y_size = self._gui_width / self.width, self._gui_height / self.height
        self._canvas_rectangles = [[self._canvas.create_rectangle(x * x_size, y * y_size, (x + 1) * x_size, (y + 1) * y_size,
                                                                  fill=f'#000000') for x in range(width)] for y in range(height)]

    def __setitem__(self, indices, value):
        x, y = indices
        self._colors[y][x] = value

    def write(self):
        for x in range(self.width):
            for y in range(self.height):
                color_r, color_g, color_b = tuple(int(round(item * self.brightness)) for item in self._colors[y][x])
                self._canvas.itemconfig(self._canvas_rectangles[y][x], fill=f'#{color_r:02x}{color_g:02x}{color_b:02x}')
