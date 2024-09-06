from RPi import GPIO
import digitalio

class IncrementalEncoder:
    def _pin_a_interrupt(self, pin_id):
        # print('A ' + ('falling' if self._prev_value_a else 'rising'))
        self._count += 1 if self._prev_value_a == self._prev_value_b else -1
        self._prev_value_a = not self._prev_value_a

    def _pin_b_interrupt(self, pin_id):
        # print('B ' + ('falling' if self._prev_value_b else 'rising'))
        self._count += -1 if self._prev_value_a == self._prev_value_b else 1
        self._prev_value_b = not self._prev_value_b

    # def _pin_a_falling(self, pin_id):
    #     print('A falling')
    #     self._count += -1 if self._prev_value_b else 1
    #     self._prev_value_a = False

    # def _pin_b_rising(self, pin_id):
    #     print('B rising')
    #     self._count += -1 if self._prev_value_a else 1
    #     self._prev_value_b = True

    # def _pin_b_falling(self, pin_id):
    #     print('B falling')
    #     self._count += 1 if self._prev_value_a else -1
    #     self._prev_value_b = False
    

    # def _pin_interrupt(self, pin_id):
    #     new_value_a = GPIO.input(self.pin_a.id)
    #     new_value_b = GPIO.input(self.pin_b.id)

    #     print((self._prev_value_a, self._prev_value_b, new_value_a, new_value_b))

    #     if self._prev_value_a == self._prev_value_b:
    #         self._count += 1 if self._prev_value_a == new_value_a else -1
    #     else:
    #         self._count += 1 if self._prev_value_a != new_value_a else -1

    #     self._prev_value_a = new_value_a
    #     self._prev_value_b = new_value_b


    def __init__(self, pin_a: digitalio.Pin, pin_b: digitalio.Pin, divisor: int = 4):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.divisor = divisor
        self._count = 0

        GPIO.setup(pin_a.id, GPIO.IN)
        GPIO.setup(pin_b.id, GPIO.IN)

        GPIO.add_event_detect(pin_a.id, GPIO.BOTH, callback=self._pin_a_interrupt, bouncetime=20)
        GPIO.add_event_detect(pin_b.id, GPIO.BOTH, callback=self._pin_b_interrupt, bouncetime=20)

        self._prev_value_a = bool(GPIO.input(self.pin_a.id))
        self._prev_value_b = bool(GPIO.input(self.pin_b.id))

    @property
    def position(self):
        return self._count // self.divisor

    