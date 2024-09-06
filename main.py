import time

from hardware import display, player_station
import starlords

sleep = time.sleep_us if hasattr(time, 'sleep_us') else lambda us: time.sleep(us / 1e6)

DISPLAY_SIZE = (16, 16)

if display.NeopixelDisplay is None:
    game_disp = display.PrintDisplay(DISPLAY_SIZE[0], DISPLAY_SIZE[1])
else:
    import board
    game_disp = display.NeopixelDisplay(board.D18, DISPLAY_SIZE[0], DISPLAY_SIZE[1])

p2_station, p3_station, p4_station = player_station.FilePlayerStation('./p2_station.txt'), player_station.FilePlayerStation('./p3_station.txt'), player_station.FilePlayerStation('./p4_station.txt')
if player_station.IOPlayerStation is None:
    p1_station = player_station.FilePlayerStation('./p1_station.txt')
else:
    p1_station = player_station.IOPlayerStation(board.D17, board.D27, board.D22, 0, 10)

game = starlords.StarlordsGame(game_disp, [p1_station, p2_station, p3_station, p4_station])
game._state.ball_velocity = starlords.Vector2(5.01, 1.0)

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
