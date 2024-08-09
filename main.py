import time

import display
import starlords

sleep = time.sleep_us if hasattr(time, 'sleep_us') else lambda us: time.sleep(us / 1e6)

import machine
# game_disp = display.PrintDisplay(20, 20)
game_disp = display.NeopixelDisplay(machine.Pin(16), 16, 16)
game = starlords.StarlordsGame(game_disp)
game._state.ball_velocity = (1.01, 1.0)

target_ticks = 100000000
ticks = time.time_ns()
frame = 0
while True:
    frame_time = target_ticks / 1.0e9
    while frame_time > 0.0:
        frame_time -= game.update(0.1)

    frame += 1
