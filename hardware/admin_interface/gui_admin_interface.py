import tkinter
import queue
from typing import Iterable

from .admin_interface import AdminInterface, AdminInterfaceCommand


class GUIAdminInterface(AdminInterface):
    def __init__(self, display_gui: tkinter.Widget):
        self._event_queue = queue.SimpleQueue()
        display_gui.bind('r', lambda evt: self._event_queue.put_nowait(AdminInterfaceCommand.RESTART_GAME), add=True)
        display_gui.bind('w', lambda evt: self._event_queue.put_nowait(AdminInterfaceCommand.BRIGHTNESS_UP), add=True)
        display_gui.bind('s', lambda evt: self._event_queue.put_nowait(AdminInterfaceCommand.BRIGHTNESS_DOWN), add=True)

    def get_commands(self) -> Iterable[AdminInterfaceCommand]:
        try:
            while True:
                yield self._event_queue.get_nowait()
        except queue.Empty:
            pass
