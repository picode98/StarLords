import digitalio

from gpiozero import Button

class IncrementalEncoder:
    def _pin_a_rising(self):
        self._count += 1 if self._prev_value_b else -1
        self._prev_value_a = True

    def _pin_a_falling(self):
        self._count += -1 if self._prev_value_b else 1
        self._prev_value_a = False

    def _pin_b_rising(self):
        self._count += -1 if self._prev_value_a else 1
        self._prev_value_b = True

    def _pin_b_falling(self):
        self._count += 1 if self._prev_value_a else -1
        self._prev_value_b = False

    def __init__(self, pin_a: digitalio.Pin, pin_b: digitalio.Pin, divisor: int = 4):
        self.divisor = divisor
        self._count = 0
    
        self.pin_a = Button(pin_a.id, pull_up=None, active_state=True)
        self.pin_b = Button(pin_b.id, pull_up=None, active_state=True)
        self.pin_a.when_pressed = self._pin_a_rising
        self.pin_a.when_released = self._pin_a_falling
        self.pin_b.when_pressed = self._pin_b_rising
        self.pin_b.when_released = self._pin_b_falling

        self._prev_value_a = bool(self.pin_a.value)
        self._prev_value_b = bool(self.pin_b.value)

    @property
    def position(self):
        return self._count // self.divisor
