import board
import neopixel

from .display import Display

from math import ceil
from time import sleep
from typing import Optional

PinType = type(board.D0)


class NeopixelDisplay(Display):
    def __init__(self, pin: PinType, height: int, width: int, bpp: int = 3, pixel_mapping = None,
                 extra_pixels_end: int = 0, pixel_order: Optional[str] = None):
        super().__init__(height, width)
        self.bpp = bpp
        self.pixel_mapping = pixel_mapping or (lambda x, y: y * width + x)
        self.num_pixels = height * width + extra_pixels_end
        try:
            self._leds = neopixel.NeoPixel(pin, self.num_pixels, bpp=bpp, pixel_order=pixel_order, auto_write=False)
        except TypeError:
            self._leds = neopixel.NeoPixel(pin, self.num_pixels, bpp=bpp, pixel_order=pixel_order)

        for i in range(height * width, self.num_pixels):
            self._leds[i] = ((0,) * bpp)

    def hardware_test(self):
        for i in range(self.num_pixels):
            self._leds[i] = ((0,) * self.bpp)

        num_iter = int(ceil(self.num_pixels / 4))
        for i in range(num_iter):
            self._leds[i] = (*(255, 0, 0), *((0,) * (self.bpp - 3)))
            self._leds[num_iter + i] = (*(0, 255, 0), *((0,) * (self.bpp - 3)))
            self._leds[2 * num_iter + i] = (*(0, 0, 255), *((0,) * (self.bpp - 3)))
            if 3 * num_iter + i < self.num_pixels:
                self._leds[3 * num_iter + i] = (*(255, 255, 255), *((0,) * (self.bpp - 3)))

            self._leds.write()
            sleep(0.2)

        for i in range(self.num_pixels):
            self._leds[i] = ((0,) * self.bpp)
        self._leds.write()



    def __setitem__(self, indices, value):
        x, y = indices
        if len(value) < self.bpp:
            value = (*value, *((0,) * (self.bpp - len(value))))
        
        try:
            self._leds[self.pixel_mapping(x, y)] = tuple(int(round(item * self.brightness)) for item in value)
        except IndexError:
            print(f'WARNING: Out of bounds display access: {x}, {y}')

    def write(self):
        self._leds.write()
