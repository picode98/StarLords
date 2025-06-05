from .admin_interface import AdminInterface, AdminInterfaceCommand

import pathlib
import struct
import os

# Linux kernel input event constants; see https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
EV_KEY = 1
KEY_R = 19
KEY_S = 31
KEY_W = 17
KEY_I = 23
KEY_K = 37
KEY_T = 20
KEY_X = 45
KEY_Y = 21


_HW_KBD_FORMAT = struct.Struct('llHHI')
class HWKeyboardAdminInterface(AdminInterface):
    def __init__(self):
        hw_dev_file = pathlib.Path('/dev/input/by-id')
        first_kbd_file = next(pth for pth in hw_dev_file.iterdir() if pth.name.endswith('-kbd'))
        self._hw_kbd_in = open(first_kbd_file, 'rb')
        os.set_blocking(self._hw_kbd_in.fileno(), False)

    def get_commands(self):
        if self._hw_kbd_in is not None:
            while data := self._hw_kbd_in.read(_HW_KBD_FORMAT.size):
                tv_sec, tv_usec, event_type, event_code, value = _HW_KBD_FORMAT.unpack(data)
                if event_type == EV_KEY and (value == 1 or value == 2):
                    if event_code == KEY_R:
                        yield AdminInterfaceCommand.RESTART_GAME
                    elif event_code == KEY_S:
                        yield AdminInterfaceCommand.BRIGHTNESS_DOWN
                    elif event_code == KEY_W:
                        yield AdminInterfaceCommand.BRIGHTNESS_UP
                    elif event_code == KEY_I:
                        yield AdminInterfaceCommand.GAME_SPEED_UP
                    elif event_code == KEY_K:
                        yield AdminInterfaceCommand.GAME_SPEED_DOWN
                    elif event_code == KEY_T:
                        yield AdminInterfaceCommand.HARDWARE_TEST
                    elif event_code == KEY_X:
                        yield AdminInterfaceCommand.INVERT_DISPLAY_X
                    elif event_code == KEY_Y:
                        yield AdminInterfaceCommand.INVERT_DISPLAY_Y
