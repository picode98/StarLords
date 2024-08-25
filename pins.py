""" 
pins.py
Raspberry Pi 3B+ pinouts 
GPIO.setmode(GPIO.BCM) broadcom chip pin numbers
as labeled on xikentech breakout board with screw terminals
note idsc is gpio 0 and idsd is gpio 1
note that pin logic levels are at 3.3 volts not 5 volts
that should be okay for all inputs; rotary encoder, PIR and cap touch sensors
however the five addressable LED data lines need level shifted to 5 volts, 
possibly with a 33 ohm resistor in series to compensate for the two meter transmision line
pin numbering scheme is to make wiring on the breakout board consistent as possible
Five rotary encoders with pushbutton; four control towers and a fifth one for 
control box (audio volume control towers, audio volume sub woofers, bigpixel display brightness and game speed)
"""

"""
5 volt level shifted outputs
"""
LED_BIGPIXEL_PIN = const(17)
LED_C1_PIN = const(7)
LED_C2_PIN = const(16)
LED_C3_PIN = const(19)
LED_C4_PIN = const(26)

"""
3.3 volt sensor inputs
"""
BUTTON_C1_PIN = const(8)
BUTTON_C2_PIN = const(6)
BUTTON_C3_PIN = const(20)
BUTTON_C4_PIN = const(13)
BUTTON_C5_PIN = const(2)

CLICK_C1_PIN = const(11)
CLICK_C2_PIN = const(5)
CLICK_C3_PIN = const(12)
CLICK_C4_PIN = const(21)
CLICK_C5_PIN = const(3)

DIR_C1_PIN = const(9)
DIR_C2_PIN = const(25)
DIR_C3_PIN = const(0)
DIR_C4_PIN = const(27)
DIR_C5_PIN = const(23)

PRESENCE_C1_PIN = const(10)
PRESENCE_C2_PIN = const(24)
PRESENCE_C3_PIN = const(1)
PRESENCE_C4_PIN = const(4)

