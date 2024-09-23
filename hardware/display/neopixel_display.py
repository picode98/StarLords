import board
import neopixel

from .display import Display

PinType = type(board.D0)


class NeopixelDisplay(Display):
    def __init__(self, pin: PinType, height: int, width: int):
        super().__init__(height, width)
        try:
            self._leds = neopixel.NeoPixel(pin, height * width, auto_write=False)
        except TypeError:
            self._leds = neopixel.NeoPixel(pin, height * width)

    def __setitem__(self, indices, value):
        x, y = indices
        try:
            self._leds[y * self.width + ((self.width - 1 - x) if y % 2 == 0 else x)] = value
        except IndexError:
            print(f'WARNING: Out of bounds display access: {x}, {y}')

    def write(self):
        self._leds.write()
