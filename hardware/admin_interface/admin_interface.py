import enum
from typing import Iterable


class AdminInterfaceCommand(enum.Enum):
    RESTART_GAME = 'restart_game'
    BRIGHTNESS_UP = 'brightness_up'
    BRIGHTNESS_DOWN = 'brightness_down'
    GAME_SPEED_UP = 'game_speed_up'
    GAME_SPEED_DOWN = 'game_speed_down'
    HARDWARE_TEST = 'hardware_test'
    INVERT_DISPLAY_X = 'invert_display_x'
    INVERT_DISPLAY_Y = 'invert_display_y'


class AdminInterface:
    def get_commands(self) -> Iterable[AdminInterfaceCommand]:
        raise NotImplementedError()
