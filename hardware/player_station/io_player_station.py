from hardware import rotary_encoder
from .player_station import PlayerStation

import digitalio
import neopixel

from typing import Tuple

PinType = digitalio.Pin


class IOPlayerStation(PlayerStation):
    def __init__(self, rotary_enc_pin_a: PinType, rotary_enc_pin_b: PinType, button_pin: PinType,
                 ring_light_pin: PinType, min_position: int, max_position: int, ring_light_num_leds: int):
        self.rotary_enc = rotary_encoder.IncrementalEncoder(rotary_enc_pin_a, rotary_enc_pin_b, divisor=2)
        self.min_position = min_position
        self.max_position = max_position
        self.rotary_enc_bias = 0
        self.button_pin = digitalio.DigitalInOut(button_pin)
        # self.ring_light = neopixel.NeoPixel(ring_light_pin, ring_light_num_leds)

    def get_shield_pos(self) -> int:
        if self.rotary_enc.position - self.rotary_enc_bias > self.max_position:
            self.rotary_enc_bias = self.rotary_enc.position - self.max_position
        elif self.rotary_enc.position - self.rotary_enc_bias < self.min_position:
            self.rotary_enc_bias = self.rotary_enc.position - self.min_position

        return self.rotary_enc.position - self.rotary_enc_bias

    def get_button_pressed(self) -> bool:
        return not self.button_pin.value

    def set_ring_light_value(self, idx: int, value: Tuple[int, int, int]):
        self.ring_light[idx] = value

    def write_ring_light(self):
        self.ring_light.write()
