import time

import config
from hardware import sound
from hardware.admin_interface.admin_interface import AdminInterfaceCommand
import starlords

sleep = time.sleep_us if hasattr(time, 'sleep_us') else lambda us: time.sleep(us / 1e6)

display_pixel_map = None
if config.DISPLAY_ENABLE_SERPENTINE:
    from hardware.display.display import get_serpentine_index
    display_pixel_map = lambda x, y: get_serpentine_index(x, y, config.DISPLAY_SIZE[1], config.DISPLAY_SERPENTINE_BLOCK_WIDTH, config.DISPLAY_SERPENTINE_BLOCK_HEIGHT)

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
    game_disp = NeopixelDisplay(Pin(config.LED_BIGPIXEL_PIN), config.DISPLAY_SIZE[0], config.DISPLAY_SIZE[1], config.DISPLAY_BPP,
                                pixel_mapping=display_pixel_map,
                                extra_pixels_end=config.DISPLAY_EXTRA_PIXELS_END,
                                pixel_order=config.DISPLAY_PIXEL_ORDER)
elif config.DISPLAY_MODE == config.DisplayMode.ARTNET:
    import pyartnet
    from hardware.display.artnet_display import ArtNetDisplay
    artnet_node = pyartnet.ArtNetNode(config.ARTNET_IP, config.ARTNET_PORT, max_fps=config.TARGET_FRAME_RATE, start_refresh_task=False)

    game_disp = ArtNetDisplay(artnet_node, config.DISPLAY_SIZE[0], config.DISPLAY_SIZE[1], config.DISPLAY_BPP,
                              pixel_mapping=display_pixel_map,
                              extra_pixels_end=config.DISPLAY_EXTRA_PIXELS_END)
else:
    raise RuntimeError('Invalid DISPLAY_MODE setting.')

game_admin_interface = None
if config.DISPLAY_MODE == config.DisplayMode.GUI:
    from hardware.admin_interface.gui_admin_interface import GUIAdminInterface
    game_admin_interface = GUIAdminInterface(root_window)
else:
    try:
        from hardware.admin_interface.hardware_keyboard_admin_interface import HWKeyboardAdminInterface
        game_admin_interface = HWKeyboardAdminInterface()
    except BaseException:
        print('WARNING: Admin interface not available')

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
frame = 0
game_completed_time = None

game_speed_count = 0

def process_frame():
    global frame, game_completed_time, game_speed_count
    ticks = time.time_ns()
    target_ticks = 1000000000 / config.TARGET_FRAME_RATE

    if game_admin_interface is not None:
        for command in game_admin_interface.get_commands():
            if command == AdminInterfaceCommand.RESTART_GAME:
                game.reset_game()
                game_completed_time = None
            elif command == AdminInterfaceCommand.BRIGHTNESS_UP:
                game_disp.brightness = min(game_disp.brightness + 0.01, 1.0)
            elif command == AdminInterfaceCommand.BRIGHTNESS_DOWN:
                game_disp.brightness = max(game_disp.brightness - 0.01, 0.0)
            elif command == AdminInterfaceCommand.GAME_SPEED_UP or command == AdminInterfaceCommand.GAME_SPEED_DOWN:
                game_speed_count = min(game_speed_count + 1, 20) if command == AdminInterfaceCommand.GAME_SPEED_UP else max(game_speed_count - 1, -20)
                game.ball_bounce_multiplier = starlords.StarlordsGame.BALL_BOUNCE_MULTIPLIER + 0.01 * game_speed_count
                game.ball_max_speed = max(starlords.StarlordsGame.BALL_MAX_SPEED + 4.0 * game_speed_count, 8.0)
            elif command == AdminInterfaceCommand.HARDWARE_TEST:
                game_disp.hardware_test()
            elif command == AdminInterfaceCommand.INVERT_DISPLAY_X:
                game.invert_display_x = not game.invert_display_x
            elif command == AdminInterfaceCommand.INVERT_DISPLAY_Y:
                game.invert_display_y = not game.invert_display_y

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
    frame += 1
    if config.DISPLAY_MODE == config.DisplayMode.GUI:
        if frame_ticks > target_ticks:
            print(f'WARNING: Below target frame rate (frame took {frame_ticks} ns).')
            root_window.after(0, process_frame)
        else:
            root_window.after(int((target_ticks - frame_ticks) // 1000000), process_frame)
    else:
        if frame_ticks > target_ticks:
            print(f'WARNING: Below target frame rate (frame took {frame_ticks} ns).')
        else:
            sleep((target_ticks - frame_ticks) // 1000)


if config.DISPLAY_MODE == config.DisplayMode.GUI:
    root_window.after(0, process_frame)
    root_window.mainloop()
else:
    while True:
        process_frame()
