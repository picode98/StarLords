import time

import pins
from hardware import display, player_station, sound
import starlords

sleep = time.sleep_us if hasattr(time, 'sleep_us') else lambda us: time.sleep(us / 1e6)

DISPLAY_SIZE = (16, 16)
TARGET_FRAME_RATE = 30.0
GAME_COMPLETE_PAUSE = 10.0


if display.NeopixelDisplay is None:
    game_disp = display.PrintDisplay(DISPLAY_SIZE[0], DISPLAY_SIZE[1])
else:
    from board.pin import Pin
    game_disp = display.NeopixelDisplay(Pin(pins.LED_BIGPIXEL_PIN), DISPLAY_SIZE[0], DISPLAY_SIZE[1])

if player_station.IOPlayerStation is None:
    p1_station, p2_station, p3_station, p4_station = player_station.FilePlayerStation('./p1_station.txt'), player_station.FilePlayerStation('./p2_station.txt'), player_station.FilePlayerStation('./p3_station.txt'), player_station.FilePlayerStation('./p4_station.txt')
else:
    from board.pin import Pin
    p1_station = player_station.IOPlayerStation(Pin(pins.CLICK_C1_PIN), Pin(pins.DIR_C1_PIN), Pin(pins.BUTTON_C1_PIN), 0, 10)
    p2_station = player_station.IOPlayerStation(Pin(pins.CLICK_C2_PIN), Pin(pins.DIR_C2_PIN), Pin(pins.BUTTON_C2_PIN), 0, 10)
    p3_station = player_station.IOPlayerStation(Pin(pins.CLICK_C3_PIN), Pin(pins.DIR_C3_PIN), Pin(pins.BUTTON_C3_PIN), 0, 10)
    p4_station = player_station.IOPlayerStation(Pin(pins.CLICK_C4_PIN), Pin(pins.DIR_C4_PIN), Pin(pins.BUTTON_C4_PIN), 0, 10)

sample_player = sound.SamplePlayer()

# sample_player.play_sample(sound.GameSample.IDLE_LOOP, cancel_existing=True)
# sample_player.loop = True
# sleep(10000000000000)

game = starlords.StarlordsGame(game_disp, [p1_station, p2_station, p3_station, p4_station], sample_player)

target_ticks = 1000000000 / TARGET_FRAME_RATE
frame = 0
ticks = time.time_ns()
game_completed_time = None
while True:
    frame_time = target_ticks / 1.0e9
    while frame_time > 0.0:
        frame_time -= game.update(frame_time)

    if game_completed_time is None and game.game_complete:
        game_completed_time = ticks

    if game_completed_time is not None and (ticks - game_completed_time) >= GAME_COMPLETE_PAUSE * 1.0e9:
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
