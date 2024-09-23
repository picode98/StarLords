import time

import config
from hardware import sound
import starlords

sleep = time.sleep_us if hasattr(time, 'sleep_us') else lambda us: time.sleep(us / 1e6)

if config.DISPLAY_MODE == config.DisplayMode.PRINT:
    from hardware.display import print_display
    game_disp = print_display.PrintDisplay(config.DISPLAY_SIZE[0], config.DISPLAY_SIZE[1])
elif config.DISPLAY_MODE == config.DisplayMode.NEOPIXEL:
    import board
    from hardware.display.neopixel_display import NeopixelDisplay
    Pin = board.pin.Pin
    game_disp = NeopixelDisplay(Pin(config.LED_BIGPIXEL_PIN), config.DISPLAY_SIZE[0], config.DISPLAY_SIZE[1])
elif config.DISPLAY_MODE == config.DisplayMode.ARTNET:
    import pyartnet
    from hardware.display.artnet_display import ArtNetDisplay
    artnet_node = pyartnet.ArtNetNode(config.ARTNET_IP, config.ARTNET_PORT, max_fps=config.TARGET_FRAME_RATE, start_refresh_task=False)

    game_disp = ArtNetDisplay(artnet_node, config.DISPLAY_SIZE[0], config.DISPLAY_SIZE[1])
else:
    raise RuntimeError('Invalid DISPLAY_MODE setting.')

if config.SIMULATE_PLAYER_STATIONS:
    from hardware.player_station.file_player_station import FilePlayerStation
    p1_station, p2_station, p3_station, p4_station = FilePlayerStation('./p1_station.txt'), FilePlayerStation('./p2_station.txt'), FilePlayerStation('./p3_station.txt'), FilePlayerStation('./p4_station.txt')
else:
    import board
    from hardware.player_station.io_player_station import IOPlayerStation
    Pin = board.pin.Pin
    p1_station = IOPlayerStation(Pin(config.CLICK_C1_PIN), Pin(config.DIR_C1_PIN), Pin(config.BUTTON_C1_PIN), Pin(config.LED_C1_PIN), 0, 10, 16)
    p2_station = IOPlayerStation(Pin(config.CLICK_C2_PIN), Pin(config.DIR_C2_PIN), Pin(config.BUTTON_C2_PIN), Pin(config.LED_C2_PIN), 0, 10, 16)
    p3_station = IOPlayerStation(Pin(config.CLICK_C3_PIN), Pin(config.DIR_C3_PIN), Pin(config.BUTTON_C3_PIN), Pin(config.LED_C3_PIN), 0, 10, 16)
    p4_station = IOPlayerStation(Pin(config.CLICK_C4_PIN), Pin(config.DIR_C4_PIN), Pin(config.BUTTON_C4_PIN), Pin(config.LED_C4_PIN), 0, 10, 16)

sample_player = sound.SamplePlayer()

# sample_player.play_sample(sound.GameSample.IDLE_LOOP, cancel_existing=True)
# sample_player.loop = True
# sleep(10000000000000)

game = starlords.StarlordsGame(game_disp, [p1_station, p2_station, p3_station, p4_station], sample_player)

target_ticks = 1000000000 / config.TARGET_FRAME_RATE
frame = 0
ticks = time.time_ns()
game_completed_time = None
while True:
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
