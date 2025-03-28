import enum
from typing import Iterable


class AdminInterfaceCommand(enum.Enum):
    RESTART_GAME = 'restart_game'
    BRIGHTNESS_UP = 'brightness_up'
    BRIGHTNESS_DOWN = 'brightness_down'


class AdminInterface:
    def get_commands(self) -> Iterable[AdminInterfaceCommand]:
        raise NotImplementedError()
