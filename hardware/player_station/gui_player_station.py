from .player_station import PlayerStation

import tkinter

class GUIPlayerStation(PlayerStation):
    def __init__(self, player_num: int, display_gui: tkinter.Widget):
        self._shield_pos = 0
        self._button_pressed = False
        self.player_num = player_num
        self.display_gui = display_gui
        display_gui.bind('<MouseWheel>', self._on_gui_scroll, add=True)
        display_gui.bind('<ButtonPress>', lambda event: self._on_gui_mousebutton(event, True), add=True)
        display_gui.bind('<ButtonRelease>', lambda event: self._on_gui_mousebutton(event, False), add=True)

    def _on_gui_scroll(self, event: tkinter.Event):
        height, width = self.display_gui.winfo_height(), self.display_gui.winfo_width()
        if (self.player_num == 1 and event.x <= width / 2 and event.y <= height / 2) or \
            (self.player_num == 2 and event.x > width / 2 and event.y <= height / 2) or \
            (self.player_num == 3 and event.x > width / 2 and event.y > height / 2) or \
            (self.player_num == 4 and event.x <= width / 2 and event.y > height / 2):
           self._shield_pos += (-1 if event.delta < 0 else 1)

    def _on_gui_mousebutton(self, event: tkinter.Event, button_pressed: bool):
        height, width = self.display_gui.winfo_height(), self.display_gui.winfo_width()
        if (self.player_num == 1 and event.x <= width / 2 and event.y <= height / 2) or \
                (self.player_num == 2 and event.x > width / 2 and event.y <= height / 2) or \
                (self.player_num == 3 and event.x > width / 2 and event.y > height / 2) or \
                (self.player_num == 4 and event.x <= width / 2 and event.y > height / 2):
            self._button_pressed = button_pressed

    def get_shield_pos(self) -> int:
        return self._shield_pos

    def get_button_pressed(self) -> bool:
        return self._button_pressed

    def get_num_ring_light_pixels(self) -> int:
        return 16
