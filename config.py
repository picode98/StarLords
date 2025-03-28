"""
General configuration variables for game setup
"""
import enum


class DisplayMode(enum.StrEnum):
    PRINT = 'print'
    GUI = 'gui'
    NEOPIXEL = 'neopixel'
    ARTNET = 'artnet'


DISPLAY_MODE = DisplayMode.NEOPIXEL
DISPLAY_SIZE = (18, 18)
DISPLAY_NEOPIXEL_BPP = 4
DISPLAY_NEOPIXEL_PIXEL_ORDER = 'RGBW'
DISPLAY_NEOPIXEL_EXTRA_PIXELS_END = 16
SIMULATE_PLAYER_STATIONS = False
ARTNET_IP = '10.0.0.3'
ARTNET_PORT = 6454
TARGET_FRAME_RATE = 30.0
GAME_COMPLETE_PAUSE = 10.0
PLAYER_STATION_RING_LIGHT_LENGTH = 16

""" 
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
LED_BIGPIXEL_PIN = 21
LED_C1_PIN = 12
# LED_C2_PIN = 16
# LED_C3_PIN = 19
# LED_C4_PIN = 26

"""
3.3 volt sensor inputs
"""
BUTTON_C1_PIN = 8
BUTTON_C2_PIN = 6
BUTTON_C3_PIN = 20
BUTTON_C4_PIN = 13
BUTTON_C5_PIN = 2

# TODO: CLICK and DIR pin numbers are reversed as a means of temporarily reversing
# the encoder directions, which were found to be backward. Further investigation is required
# to determine the root cause.
CLICK_C1_PIN = 9
CLICK_C2_PIN = 5
CLICK_C3_PIN = 23
CLICK_C4_PIN = 7
CLICK_C5_PIN = 0

DIR_C1_PIN = 11
DIR_C2_PIN = 25
DIR_C3_PIN = 19
DIR_C4_PIN = 27
DIR_C5_PIN = 3

PRESENCE_C1_PIN = 10
PRESENCE_C2_PIN = 24
PRESENCE_C3_PIN = 1
PRESENCE_C4_PIN = 4

