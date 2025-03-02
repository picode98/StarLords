import time

import config
from hardware import sound
import starlords

sleep = time.sleep_us if hasattr(time, 'sleep_us') else lambda us: time.sleep(us / 1e6)

root_window = None
if config.DISPLAY_MODE == config.DisplayMode.PRINT:
    from hardware.display import print_display
    game_disp = print_display.PrintDisplay(config.DISPLAY_SIZE[0], config.DISPLAY_SIZE[1])
elif config.DISPLAY_MODE == config.DisplayMode.GUI:
    from hardware.display import gui_display
    import tkinter
    root_window = tkinter.Tk()
    root_window.title('StarLords')
    game_disp = gui_display.GUIDisplay(root_window, config.DISPLAY_SIZE[0], config.DISPLAY_SIZE[1], 500, 500)
elif config.DISPLAY_MODE == config.DisplayMode.NEOPIXEL:
    import board
    from hardware.display.neopixel_display import NeopixelDisplay
    Pin = board.pin.Pin
    game_disp = NeopixelDisplay(Pin(config.LED_BIGPIXEL_PIN), config.DISPLAY_SIZE[0], config.DISPLAY_SIZE[1], config.DISPLAY_NEOPIXEL_BPP, config.DISPLAY_NEOPIXEL_PIXEL_ORDER)
elif config.DISPLAY_MODE == config.DisplayMode.ARTNET:
    import pyartnet
    from hardware.display.artnet_display import ArtNetDisplay
    artnet_node = pyartnet.ArtNetNode(config.ARTNET_IP, config.ARTNET_PORT, max_fps=config.TARGET_FRAME_RATE, start_refresh_task=False)

    game_disp = ArtNetDisplay(artnet_node, config.DISPLAY_SIZE[0], config.DISPLAY_SIZE[1])
else:
    raise RuntimeError('Invalid DISPLAY_MODE setting.')

if config.SIMULATE_PLAYER_STATIONS:
    if config.DISPLAY_MODE == config.DisplayMode.GUI:
        from hardware.player_station.gui_player_station import GUIPlayerStation
        p1_station, p2_station, p3_station, p4_station = GUIPlayerStation(1, root_window), GUIPlayerStation(2, root_window), \
                                                         GUIPlayerStation(3, root_window), GUIPlayerStation(4, root_window)
    else:
        from hardware.player_station.file_player_station import FilePlayerStation
        p1_station, p2_station, p3_station, p4_station = FilePlayerStation('./p1_station.txt'), FilePlayerStation('./p2_station.txt'), FilePlayerStation('./p3_station.txt'), FilePlayerStation('./p4_station.txt')
else:
    import board
    import neopixel
    from hardware.player_station.io_player_station import IOPlayerStation
    Pin = board.pin.Pin
    ring_light_string = neopixel.NeoPixel(Pin(config.LED_C1_PIN), 64, auto_write=False)
    p1_station = IOPlayerStation(Pin(config.CLICK_C1_PIN), Pin(config.DIR_C1_PIN), Pin(config.BUTTON_C1_PIN), ring_light_string, 0, 10, range(0, config.PLAYER_STATION_RING_LIGHT_LENGTH))
    p2_station = IOPlayerStation(Pin(config.CLICK_C2_PIN), Pin(config.DIR_C2_PIN), Pin(config.BUTTON_C2_PIN), ring_light_string, 0, 10, range(config.PLAYER_STATION_RING_LIGHT_LENGTH, 2 * config.PLAYER_STATION_RING_LIGHT_LENGTH))
    p3_station = IOPlayerStation(Pin(config.CLICK_C3_PIN), Pin(config.DIR_C3_PIN), Pin(config.BUTTON_C3_PIN), ring_light_string, 0, 10, range(2 * config.PLAYER_STATION_RING_LIGHT_LENGTH, 3 * config.PLAYER_STATION_RING_LIGHT_LENGTH))
    p4_station = IOPlayerStation(Pin(config.CLICK_C4_PIN), Pin(config.DIR_C4_PIN), Pin(config.BUTTON_C4_PIN), ring_light_string, 0, 10, range(3 * config.PLAYER_STATION_RING_LIGHT_LENGTH, 4 * config.PLAYER_STATION_RING_LIGHT_LENGTH))

sample_player = sound.SamplePlayer()

game = starlords.StarlordsGame(game_disp, [p1_station, p2_station, p3_station, p4_station], sample_player)

cancel_game_loop = False
def game_loop():
    target_ticks = 1000000000 / config.TARGET_FRAME_RATE
    frame = 0
    ticks = time.time_ns()
    game_completed_time = None

    while not cancel_game_loop:
        frame_time = target_ticks / 1.0e9
        while frame_time > 0.0:
            frame_time -= game.update(frame_time)

        if game_completed_time is None and game.game_complete:
            game_completed_time = ticks

        if game_completed_time is not None and (ticks - game_completed_time) >= config.GAME_COMPLETE_PAUSE * 1.0e9:
            game.reset_game()
            game_completed_time = None
        # print(f'Frame {frame}:')
        game.render()
        # print()

        frame_ticks = time.time_ns() - ticks
        if frame_ticks > target_ticks:
            print(f'WARNING: Below target frame rate (frame took {frame_ticks} ns).')
        else:
            sleep((target_ticks - frame_ticks) // 1000)

        frame += 1
        ticks = time.time_ns()


if config.DISPLAY_MODE == config.DisplayMode.GUI:
    import threading
    game_thread = threading.Thread(target=game_loop)
    game_thread.start()

    try:
        root_window.mainloop()
    finally:
        cancel_game_loop = True
else:
    game_loop()
