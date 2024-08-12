import time

import display
import starlords

sleep = time.sleep_us if hasattr(time, 'sleep_us') else lambda us: time.sleep(us / 1e6)

DISPLAY_SIZE = (16, 16)

if display.NeopixelDisplay is None:
    game_disp = display.PrintDisplay(DISPLAY_SIZE[0], DISPLAY_SIZE[1])
else:
    import machine
    game_disp = display.NeopixelDisplay(machine.Pin(16), DISPLAY_SIZE[0], DISPLAY_SIZE[1])

game = starlords.StarlordsGame(game_disp)
game._state.ball_velocity = (5.01, 1.0)

target_ticks = 1000000000 // 10
frame = 0
ticks = time.time_ns()
while True:
    frame_time = target_ticks / 1.0e9
    while frame_time > 0.0:
        frame_time -= game.update(frame_time)

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
