from hardware import rotary_encoder
from .player_station import PlayerStation

import digitalio
import neopixel

from typing import Tuple, Optional

PinType = digitalio.Pin


class IOPlayerStation(PlayerStation):
    def __init__(self, rotary_enc_pin_a: PinType, rotary_enc_pin_b: PinType, button_pin: PinType,
                 ring_light: neopixel.NeoPixel, min_position: int, max_position: int, ring_light_range: Optional[range] = None):
        self.rotary_enc = rotary_encoder.IncrementalEncoder(rotary_enc_pin_a, rotary_enc_pin_b, divisor=2)
        self.min_position = min_position
        self.max_position = max_position
        self.button_pin = digitalio.DigitalInOut(button_pin)
        self.ring_light = ring_light
        self.ring_light_range = range(len(ring_light)) if ring_light_range is None else ring_light_range
        # self.ring_light = neopixel.NeoPixel(ring_light_pin, ring_light_num_leds)

    def get_shield_pos(self) -> int:
        return self.rotary_enc.position

    def get_button_pressed(self) -> bool:
        return not self.button_pin.value

    def get_num_ring_light_pixels(self) -> int:
        return self.ring_light_range.stop - self.ring_light_range.start

    def set_ring_light_value(self, idx: int, value: Tuple[int, int, int]):
        self.ring_light[self.ring_light_range.start + idx] = value

    def write_ring_light(self):
        self.ring_light.write()
