import board
import neopixel

from .display import Display

from typing import Optional

PinType = type(board.D0)


class NeopixelDisplay(Display):
    def __init__(self, pin: PinType, height: int, width: int, bpp: int = 3, pixel_order: Optional[str] = None):
        super().__init__(height, width)
        self.bpp = bpp
        try:
            self._leds = neopixel.NeoPixel(pin, height * width, bpp=bpp, pixel_order=pixel_order, auto_write=False)
        except TypeError:
            self._leds = neopixel.NeoPixel(pin, height * width, bpp=bpp, pixel_order=pixel_order)

    def __setitem__(self, indices, value):
        x, y = indices
        if len(value) < self.bpp:
            value = (*value, *((0,) * (self.bpp - len(value))))
        
        try:
            self._leds[y * self.width + ((self.width - 1 - x) if y % 2 == 0 else x)] = value
        except IndexError:
            print(f'WARNING: Out of bounds display access: {x}, {y}')

    def write(self):
        self._leds.write()
