import board
import neopixel

from .display import Display

from typing import Optional

PinType = type(board.D0)


class NeopixelDisplay(Display):
    def __init__(self, pin: PinType, height: int, width: int, bpp: int = 3,
                 serpentine_block_width: Optional[int] = None, serpentine_block_height: Optional[int] = None,
                 extra_pixels_end: int = 0, pixel_order: Optional[str] = None):
        super().__init__(height, width)
        self.bpp = bpp
        self.serpentine_block_width = serpentine_block_width or width
        self.serpentine_block_height = serpentine_block_height or height
        try:
            self._leds = neopixel.NeoPixel(pin, height * width + extra_pixels_end, bpp=bpp, pixel_order=pixel_order, auto_write=False)
        except TypeError:
            self._leds = neopixel.NeoPixel(pin, height * width + extra_pixels_end, bpp=bpp, pixel_order=pixel_order)

        for i in range(height * width, height * width + extra_pixels_end):
            self._leds[i] = ((0,) * bpp)

    def _led_index(self, x: int, y: int):
        block_row, block_col = y // self.serpentine_block_height, x // self.serpentine_block_width
        block_start_index = block_row * self.serpentine_block_height * self.width + self.serpentine_block_height * self.serpentine_block_width * (
            block_col if block_row % 2 == 0 else (self.width // self.serpentine_block_width - 1 - block_col))
        return block_start_index + self.serpentine_block_width * (
            y % self.serpentine_block_height if block_col % 2 == 0 else (self.serpentine_block_height - 1) - (y % self.serpentine_block_height)) + (
            x % self.serpentine_block_width if y % 2 == 0 else (self.serpentine_block_width - 1) - (x % self.serpentine_block_width))

    def __setitem__(self, indices, value):
        x, y = indices
        if len(value) < self.bpp:
            value = (*value, *((0,) * (self.bpp - len(value))))
        
        try:
            self._leds[self._led_index(x, y)] = value
        except IndexError:
            print(f'WARNING: Out of bounds display access: {x}, {y}')

    def write(self):
        self._leds.write()
