import math
import random
from typing import List

from hardware.display.display import Display
from hardware.player_station.player_station import PlayerStation
from hardware.sound import SamplePlayer, GameSample

def _add_colors(*args):
    return tuple(min(sum(arg[i] for arg in args), 255) for i in range(len(args[0])))

class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def length2(self):
        return self.x ** 2 + self.y ** 2

    def length(self):
        return math.sqrt(self.length2())

    def __add__(self, other):
        if hasattr(other, 'x'):
            return Vector2(self.x + other.x, self.y + other.y)
        else:
            return Vector2(self.x + other[0], self.y + other[1])

    def __radd__(self, other): return self + other

    def __sub__(self, other):
        if hasattr(other, 'x'):
            return Vector2(self.x - other.x, self.y - other.y)
        else:
            return Vector2(self.x - other[0], self.y - other[1])

    def __rsub__(self, other): return self - other

    def __mul__(self, other):
        if hasattr(other, 'x'):
            return Vector2(self.x * other.x, self.y * other.y)
        elif hasattr(other, '__len__'):
            return Vector2(self.x * other[0], self.y * other[1])
        else:
            return Vector2(self.x * other, self.y * other)

    def __rmul__(self, other): return self * other

    def dot(self, other: 'Vector2'):
        return self.x * other.x + self.y * other.y

    def __truediv__(self, other):
        if hasattr(other, 'x'):
            return Vector2(self.x / other.x, self.y / other.y)
        elif hasattr(other, '__len__'):
            return Vector2(self.x / other[0], self.y / other[1])
        else:
            return Vector2(self.x / other, self.y / other)

    def __rtruediv__(self, other): return self / other

    def __repr__(self):
        return f'<{self.x}, {self.y}>'


v2 = Vector2


def _circle_rectangle_collision(circle_pos: v2, circle_radius: float, rectangle_pos: v2, rectangle_size: v2):
    corners = [rectangle_pos, v2(rectangle_pos.x + rectangle_size.x, rectangle_pos.y),
               rectangle_pos + rectangle_size,
               v2(rectangle_pos.x, rectangle_pos.y + rectangle_size.y)]
    closest_corner, dist = min(((corner, (corner - circle_pos).length2())
                                for corner in corners), key=lambda x: x[1])
    dist = math.sqrt(dist)

    if dist <= circle_radius:
        abs_intersect_x = math.sqrt(
            circle_radius ** 2 - (closest_corner.y - circle_pos.y) ** 2)
        abs_intersect_y = math.sqrt(
            circle_radius ** 2 - (closest_corner.x - circle_pos.x) ** 2)
        ix_point = v2(circle_pos.x + (
            -abs_intersect_x if closest_corner.x < circle_pos.x else abs_intersect_x), closest_corner.y)
        iy_point = v2(closest_corner.x, circle_pos.y + (
            -abs_intersect_y if closest_corner.y < circle_pos.y else abs_intersect_y))

        normal_vector = circle_pos - (ix_point + iy_point) / 2.0
        # normal_vector = (self._state.ball_position[0] - closest_corner[0],
        #                  self._state.ball_position[1] - closest_corner[1])
        unit_normal_vector: Vector2 = normal_vector / normal_vector.length()
        return unit_normal_vector
    elif (circle_pos.x + circle_radius >= rectangle_pos.x and
          circle_pos.x - circle_radius <= rectangle_pos.x + rectangle_size.x and
          circle_pos.y >= rectangle_pos.y and
          circle_pos.y <= rectangle_pos.y + rectangle_size.y
    ) or (
            circle_pos.x >= rectangle_pos.x and
            circle_pos.x <= rectangle_pos.x + rectangle_size.x and
            circle_pos.y + circle_radius >= rectangle_pos.y and
            circle_pos.y - circle_radius <= rectangle_pos.y + rectangle_size.y
    ):
        delta = circle_pos - (rectangle_pos + rectangle_size / 2.0)

        if abs(delta.x) >= abs(delta.y):
            normal_vector = v2(-1.0 if delta.x < 0.0 else 1.0, 0.0)
        else:
            normal_vector = v2(0.0, -1.0 if delta.y < 0.0 else 1.0)

        return normal_vector
    else:
        return None



class GameState:
    """ information about which bricks are broken, projectile position, etc. """
    def __init__(self, field_size: Vector2, initial_ball_speed: float):
        w, h = field_size.x, field_size.y
        self.field_size: Vector2 = field_size
        self.ready_players = set()
        self.ready_player_wait_time = 0.0
        self.active_players = {0, 1, 2, 3}
        self.ball_position = v2(w / 2.0, h / 2.0)

        while True:
            ball_angle = random.random() * 2.0 * math.pi
            multiples_of_pi_4 = ball_angle / (math.pi / 4.0)
            if abs(round(multiples_of_pi_4) - multiples_of_pi_4) >= 0.05:
                break

        self.ball_velocity = v2(initial_ball_speed * math.cos(ball_angle), initial_ball_speed * math.sin(ball_angle))
        self.ball_captured_by = None
        self.ball_releasing_from = None
        self.ball_capture_speed = None
        self.castle_bricks = [[v2(3.0, 0.0), v2(3.0, 1.0), v2(3.0, 2.0), v2(3.0, 3.0), v2(2.0, 3.0), v2(1.0, 3.0), v2(0.0, 3.0)],
                              [v2(w - 4.0, 0.0), v2(w - 4.0, 1.0), v2(w - 4.0, 2.0), v2(w - 4.0, 3.0), v2(w - 3.0, 3.0), v2(w - 2.0, 3.0), v2(w - 1.0, 3.0)],
                              [v2(w - 4.0, h - 1.0), v2(w - 4.0, h - 2.0), v2(w - 4.0, h - 3.0), v2(w - 4.0, h - 4.0), v2(w - 3.0, h - 4.0), v2(w - 2.0, h - 4.0), v2(w - 1.0, h - 4.0)],
                              [v2(3.0, h - 1.0), v2(3.0, h - 2.0), v2(3.0, h - 3.0), v2(3.0, h - 4.0), v2(2.0, h - 4.0), v2(1.0, h - 4.0), v2(0.0, h - 4.0)]
        ]
        self.shield_position_maps = [lambda x: v2(5.0, x) if x <= 5.0 else v2(10.0 - x, 5.0), #  [v2(5.0, 0.0), v2(5.0, 1.0), v2(5.0, 2.0), v2(5.0, 3.0), v2(5.0, 4.0), v2(5.0, 5.0), v2(4.0, 5.0), v2(3.0, 5.0), v2(2.0, 5.0), v2(1.0, 5.0), v2(0.0, 5.0)],
                                     lambda x: v2(w - 6.0, x) if x <= 5.0 else v2(w - 6.0 + (x - 5.0), 5.0),  # [v2(w - 6.0, 0.0), v2(w - 6.0, 1.0), v2(w - 6.0, 2.0), v2(w - 6.0, 3.0), v2(w - 6.0, 4.0), v2(w - 6.0, 5.0), v2(w - 5.0, 5.0), v2(w - 4.0, 5.0), v2(w - 3.0, 5.0), v2(w - 2.0, 5.0), v2(w - 1.0, 5.0)],
                                     lambda x: v2(w - 6.0, h - 1.0 - x) if x <= 5.0 else v2(w - 6.0 + (x - 5.0), h - 6.0), # [v2(w - 6.0, h - 1.0), v2(w - 6.0, h - 2.0), v2(w - 6.0, h - 3.0), v2(w - 6.0, h - 4.0), v2(w - 6.0, h - 5.0), v2(w - 6.0, h - 6.0), v2(w - 5.0, h - 6.0), v2(w - 4.0, h - 6.0), v2(w - 3.0, h - 6.0), v2(w - 2.0, h - 6.0), v2(w - 1.0, h - 6.0)],
                                     lambda x: v2(5.0, h - 1.0 - x) if x <= 5.0 else v2(10.0 - x, h - 6.0)  # [v2(5.0, h - 1.0), v2(5.0, h - 2.0), v2(5.0, h - 3.0), v2(5.0, h - 4.0), v2(5.0, h - 5.0), v2(5.0, h - 6.0), v2(4.0, h - 6.0), v2(3.0, h - 6.0), v2(2.0, h - 6.0), v2(1.0, h - 6.0), v2(0.0, h - 6.0)]
        ]
        self.shield_positions = [0.0, 0.0, 0.0, 0.0]
        self.shield_position_biases = [0.0, 0.0, 0.0, 0.0]
        self.power_core_positions = [v2(1, 1), v2(w - 2, 1), v2(w - 2, h - 2), v2(1, h - 2)]
        self.explosions = []
        self.game_started = False
        self.game_start_time_remaining = None
        self.game_complete = False


class BallColliderType:
    WALL = 0
    CASTLE_BRICK = 1
    SHIELD = 2
    POWER_CORE = 3

COUNTDOWN_DIGITS = [
'''
   -
  --
   -
   -
   -
   -
 -----
''',
'''
----- 
     -
     -
 ----
-
-
 -----
''',
'''
------
     -
     -
  ----
     -
     -
------
''',
'''
-    -
-    -
-    -
 -----
     -
     -
     -
''',
'''
------
-
-
------
     -
-    -
 ----
'''
]
COUNTDOWN_DIGITS = [[[char != ' ' for char in line] for line in digit.strip('\n').split('\n')] for digit in COUNTDOWN_DIGITS]



class StarlordsGame:
    BALL_COLOR = (200, 0, 0)
    BRICK_COLOR = (0, 0, 200)
    SHIELD_COLOR = (0, 200, 0)
    WINNER_BRICK_COLOR = (0xd5, 0x8f, 0)
    POWER_CORE_COLOR = (100, 200, 100)
    EXPLOSION_COLOR = (200, 200, 200)
    COUNTDOWN_DIGIT_COLOR = (200, 200, 200)
    BRICK_SIZE = v2(1.0, 1.0)
    SHIELD_SIZE = v2(1.0, 1.0)
    POWER_CORE_SIZE = v2(1.0, 1.0)
    BALL_SIZE = 1.0
    BALL_MIN_SPEED = 8.0
    BALL_MAX_SPEED = 30.0
    MAX_DELTA = 0.3
    MINIMUM_EXPLOSION_BRIGHTNESS = 0.05
    EXPLOSION_SHOCKWAVE_VELOCITY = 8.0
    START_COUNTDOWN_LENGTH = 12.0
    PLAYER_START_TIMEOUT = 30.0
    MAX_SHIELD_SPEED = 8.0
    MAX_SHIELD_POSITION = 10.0

    def __init__(self, display: Display, player_stations: List[PlayerStation], sample_player: SamplePlayer):
        self._state = GameState(v2(display.width, display.height), initial_ball_speed=self.BALL_MIN_SPEED)
        self._ready_players_since_last_render = []
        self._new_game_since_last_render = True
        self._ball_bounce_since_last_render = False
        self._brick_bounce_since_last_render = False
        self._player_eliminated_since_last_render = False
        self._display = display
        self._sample_player = sample_player

        assert len(player_stations) == 4
        self._player_stations = player_stations

    def _get_ball_collisions(self):
        colliders = []
        if (self._state.ball_position.x + self.BALL_SIZE / 2.0) >= self._state.field_size.x:
            colliders.append((BallColliderType.WALL, v2(-1.0, 0.0), None, None))

        if (self._state.ball_position.x - self.BALL_SIZE / 2.0) <= 0.0:
            colliders.append((BallColliderType.WALL, v2(1.0, 0.0), None, None))

        if (self._state.ball_position.y + self.BALL_SIZE / 2.0) >= self._state.field_size.y:
            colliders.append((BallColliderType.WALL, v2(0.0, -1.0), None, None))

        if (self._state.ball_position.y - self.BALL_SIZE / 2.0) <= 0.0:
            colliders.append((BallColliderType.WALL, v2(0.0, 1.0), None, None))

        for player_index, brick_list in enumerate(self._state.castle_bricks):
            for brick_index, brick_pos in enumerate(brick_list):
                collision_normal_vector = _circle_rectangle_collision(self._state.ball_position, self.BALL_SIZE / 2.0, brick_pos, self.BRICK_SIZE)
                if collision_normal_vector is not None:
                    colliders.append((BallColliderType.CASTLE_BRICK, collision_normal_vector, player_index, brick_index))

        for player_index in self._state.active_players:
            collision_normal_vector = _circle_rectangle_collision(self._state.ball_position, self.BALL_SIZE / 2.0, self._state.shield_position_maps[player_index](self._state.shield_positions[player_index]), self.BRICK_SIZE)
            if collision_normal_vector is not None:
                colliders.append((BallColliderType.SHIELD, collision_normal_vector, player_index, None))

            collision_normal_vector = _circle_rectangle_collision(self._state.ball_position, self.BALL_SIZE / 2.0,
                                                                  self._state.power_core_positions[player_index],
                                                                  self.POWER_CORE_SIZE)
            if collision_normal_vector is not None:
                colliders.append((BallColliderType.POWER_CORE, collision_normal_vector, player_index, None))

        return colliders

    def update(self, time_delta: float):
        """ update self._state with time_delta of elapsed time """
        mag_delta_sqr = (self._state.ball_velocity * time_delta).length2()
        if mag_delta_sqr >= StarlordsGame.MAX_DELTA ** 2:
            time_delta /= (mag_delta_sqr / (StarlordsGame.MAX_DELTA ** 2))

        time_delta = min(time_delta, self.MAX_DELTA / self.MAX_SHIELD_SPEED)

        shield_velocities: List[Vector2] = []
        for i, station in enumerate(self._player_stations):
            unbiased_position = station.get_shield_pos()
            if unbiased_position - self._state.shield_position_biases[i] > self.MAX_SHIELD_POSITION:
                self._state.shield_position_biases[i] = unbiased_position - self.MAX_SHIELD_POSITION
            elif unbiased_position - self._state.shield_position_biases[i] < 0:
                self._state.shield_position_biases[i] = unbiased_position

            shield_offset = (unbiased_position - self._state.shield_position_biases[i]) - self._state.shield_positions[i]
            shield_delta = (1.0 if shield_offset >= 0.0 else -1.0) * min(abs(shield_offset), self.MAX_SHIELD_SPEED * time_delta)
            pos_map = self._state.shield_position_maps[i]
            shield_velocities.append((pos_map(self._state.shield_positions[i] + shield_delta) - pos_map(self._state.shield_positions[i])) / time_delta)
            self._state.shield_positions[i] += shield_delta

        radius_delta = StarlordsGame.EXPLOSION_SHOCKWAVE_VELOCITY * time_delta
        new_explosions = []
        for position, radius, brightness in self._state.explosions:
            new_explosion = (position, radius + radius_delta, brightness * ((radius / (radius + radius_delta)) ** 2))
            if new_explosion[2] >= StarlordsGame.MINIMUM_EXPLOSION_BRIGHTNESS:
                new_explosions.append(new_explosion)

        self._state.explosions = new_explosions


        if self._state.game_start_time_remaining is not None:
            self._state.game_start_time_remaining -= time_delta
            if self._state.game_start_time_remaining <= 0.0:
                self._state.game_start_time_remaining = None
                self._state.game_started = True
        elif not self._state.game_started:
            self._state.ready_player_wait_time += time_delta
            for player_index, player_station in enumerate(self._player_stations):
                if player_station.get_button_pressed() and player_index not in self._state.ready_players:
                    self._state.ready_players.add(player_index)
                    self._ready_players_since_last_render.append(player_index)
                    self._state.ready_player_wait_time = 0.0

            if len(self._state.ready_players) == len(self._player_stations):
                self._state.game_start_time_remaining = self.START_COUNTDOWN_LENGTH
            elif self._state.ready_player_wait_time >= self.PLAYER_START_TIMEOUT:
                self.reset_game()
        elif not self._state.game_complete:
            collisions = self._get_ball_collisions()
            filtered_collisions = [collision for collision in collisions if collision[0] != BallColliderType.SHIELD or collision[2] != self._state.ball_releasing_from]

            if len(filtered_collisions) == len(collisions):
                self._state.ball_releasing_from = None
            # for _, normal_vector, _, _ in collisions:
            #     avg_normal_vector = (avg_normal_vector[0] + normal_vector[0], avg_normal_vector[1] + normal_vector[1])

            if self._state.ball_captured_by is not None:
                captured_shield_position = self._state.shield_position_maps[self._state.ball_captured_by](self._state.shield_positions[self._state.ball_captured_by])
                self._state.ball_position = captured_shield_position + v2(self.BALL_SIZE / 2, self.BALL_SIZE / 2)

                if self._player_stations[self._state.ball_captured_by].get_button_pressed():
                    self._state.ball_velocity = v2(0.0, 0.0)
                else:
                    corner_position = [v2(0.0, 0.0), v2(self._display.width, 0.0), v2(self._display.width, self._display.height),
                                   v2(0.0, self._display.height)][self._state.ball_captured_by]

                    new_velocity = captured_shield_position - corner_position
                    scaled_new_velocity = new_velocity * (self._state.ball_capture_speed / new_velocity.length())

                    self._state.ball_velocity = scaled_new_velocity
                    self._state.ball_releasing_from = self._state.ball_captured_by
                    self._state.ball_captured_by = None
                    self._state.ball_capture_speed = None
            elif len(filtered_collisions) > 0:
                brick_removals = set()
                current_speed = self._state.ball_velocity.length()
                for coll_type, normal_vector, player_index, brick_index in filtered_collisions:
                    if coll_type == BallColliderType.WALL:
                        self._ball_bounce_since_last_render = True
                    elif coll_type == BallColliderType.CASTLE_BRICK:
                        brick_pos = self._state.castle_bricks[player_index][brick_index]
                        brick_removals.add((player_index, brick_index))
                        self._state.ball_velocity *= (self.BALL_MIN_SPEED / current_speed)
                        self._state.explosions.append((brick_pos + StarlordsGame.BRICK_SIZE / 2, 1.0, 5.0))
                        self._brick_bounce_since_last_render = True
                    elif coll_type == BallColliderType.SHIELD:
                        if self._player_stations[player_index].get_button_pressed():
                            self._state.ball_captured_by = player_index
                            self._state.ball_capture_speed = current_speed
                        else:
                            self._state.ball_velocity *= (min(current_speed * 1.1, self.BALL_MAX_SPEED) / current_speed)
                            self._ball_bounce_since_last_render = True
                    elif coll_type == BallColliderType.POWER_CORE:
                        self._state.explosions.append((self._state.power_core_positions[player_index] + StarlordsGame.POWER_CORE_SIZE / 2, 1.0, 100.0))
                        self._state.active_players.remove(player_index)
                        self._player_eliminated_since_last_render = True

                        if len(self._state.active_players) == 1:
                            self._state.game_complete = True

                self._state.castle_bricks = [[brick_pos for brick_index, brick_pos in enumerate(brick_list) if not (player_index, brick_index) in brick_removals]
                                             for player_index, brick_list in enumerate(self._state.castle_bricks)]

                # avg_normal_vector = sum((normal_vector for _, normal_vector, _, _ in filtered_collisions), v2(0.0, 0.0))
                #
                # normal_length = avg_normal_vector.length()
                # if normal_length > 0.0:
                #     avg_normal_vector = avg_normal_vector / avg_normal_vector.length()

                for coll_type, normal_vector, player_index, brick_index in self._get_ball_collisions():
                    collider_velocity = shield_velocities[player_index] if coll_type == BallColliderType.SHIELD else v2(0.0, 0.0)
                    dot_product = (self._state.ball_velocity - collider_velocity).dot(normal_vector)
                    proj_velocity = dot_product * normal_vector
                    reflected_proj_velocity = abs(dot_product) * normal_vector
                    self._state.ball_velocity = self._state.ball_velocity - proj_velocity + reflected_proj_velocity + collider_velocity

            self._state.ball_position = self._state.ball_position + self._state.ball_velocity * time_delta

        return time_delta

    #   File "/home/pi/StarLords/main.py", line 31, in <module>
    #     frame_time -= game.update(frame_time)
    #                   ^^^^^^^^^^^^^^^^^^^^^^^
    #   File "/home/pi/StarLords/starlords.py", line 266, in update
    #     avg_normal_vector = avg_normal_vector / avg_normal_vector.length()
    #                         ~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #   File "/home/pi/StarLords/starlords.py", line 56, in __truediv__
    #     return Vector2(self.x / other, self.y / other)
    #                    ~~~~~~~^~~~~~~
    # ZeroDivisionError: float division by zero

    def render(self):
        """ draw self._state to self._display """
        display_buf = [[(0, 0, 0) for _ in range(self._display.height)] for _ in range(self._display.width)]

        if self._state.game_start_time_remaining is not None and int(self._state.game_start_time_remaining) < len(COUNTDOWN_DIGITS):
            digit = COUNTDOWN_DIGITS[int(self._state.game_start_time_remaining)]
            center_pos_x = (self._display.width - max(len(line) for line in digit)) // 2
            center_pos_y = (self._display.height - len(digit)) // 2
            for y, line in enumerate(digit):
                for x, char in enumerate(line):
                    if char:
                        display_buf[center_pos_x + x][center_pos_y + y] = self.COUNTDOWN_DIGIT_COLOR

        for player_index in (self._state.active_players if self._state.game_started else self._state.ready_players):
            brick_list = self._state.castle_bricks[player_index]
            for brick_pos in brick_list:
                display_buf[round(brick_pos.x)][round(brick_pos.y)] = StarlordsGame.WINNER_BRICK_COLOR if self._state.game_complete else StarlordsGame.BRICK_COLOR

            shield_pos = self._state.shield_position_maps[player_index](self._state.shield_positions[player_index])
            display_buf[round(shield_pos.x)][round(shield_pos.y)] = _add_colors(display_buf[round(shield_pos.x)][round(shield_pos.y)], StarlordsGame.SHIELD_COLOR)

            power_core_pos = self._state.power_core_positions[player_index]
            display_buf[power_core_pos.x][power_core_pos.y] = _add_colors(display_buf[power_core_pos.x][power_core_pos.y], (StarlordsGame.WINNER_BRICK_COLOR if self._state.game_complete else self.POWER_CORE_COLOR))

        for position, radius, brightness in self._state.explosions:
            for block_x in range(max(int(position.x - radius), 0), min(math.ceil(position.x + radius), self._display.width - 1) + 1):
                for block_y in range(max(int(position.y - radius), 0), min(math.ceil(position.y + radius), self._display.height - 1) + 1):
                    if (position.x - (block_x + 0.5)) ** 2 + (position.y - (block_y + 0.5)) ** 2 <= radius:
                        display_buf[block_x][block_y] = _add_colors(display_buf[block_x][block_y], (round(StarlordsGame.EXPLOSION_COLOR[0] * brightness),
                                                           round(StarlordsGame.EXPLOSION_COLOR[1] * brightness),
                                                           round(StarlordsGame.EXPLOSION_COLOR[2] * brightness)))

        # print(f'Position: {self._state.ball_position} Velocity: {self._state.ball_velocity}')
        if self._state.game_started and not self._state.game_complete:
            ball_draw_x, ball_draw_y = round(self._state.ball_position.x - StarlordsGame.BALL_SIZE / 2.0), round(self._state.ball_position.y - StarlordsGame.BALL_SIZE / 2.0)
            display_buf[ball_draw_x][ball_draw_y] = _add_colors(display_buf[ball_draw_x][ball_draw_y], StarlordsGame.BALL_COLOR)
        
        for y in range(self._display.height):
            for x in range(self._display.width):
                self._display[x, y] = display_buf[x][y]
        self._display.write()

        if not self._state.game_started:
            for player_index, player_station in enumerate(self._player_stations):
                for pxl in range(player_station.get_num_ring_light_pixels()):
                    player_station.set_ring_light_value(pxl, (255, 255, 255) if player_index in self._state.ready_players else (50, 50, 50))
        elif not self._state.game_complete:
            for player_index, player_station in enumerate(self._player_stations):
                for pxl in range(player_station.get_num_ring_light_pixels()):
                    player_station.set_ring_light_value(pxl, (0, 255, 0) if player_index in self._state.active_players else (255, 0, 0))
        else:
            for player_index, player_station in enumerate(self._player_stations):
                for pxl in range(player_station.get_num_ring_light_pixels()):
                    player_station.set_ring_light_value(pxl, (0xd5, 0x8f, 0) if player_index in self._state.active_players else (255, 0, 0))

#        for player_station in self._player_stations:
#            player_station.write_ring_light()

        if self._brick_bounce_since_last_render:
            self._sample_player.play_sample(GameSample.BREAK, cancel_existing=True)
        elif self._ball_bounce_since_last_render:
            self._sample_player.play_sample(GameSample.BOUNCE, cancel_existing=True)
        elif self._player_eliminated_since_last_render:
            self._sample_player.play_sample(GameSample.PLAYER_DEATH, cancel_existing=True)

            if len(self._state.active_players) == 1:
                self._sample_player.play_sample(GameSample.PLAYER_WIN)

        for i, player_index in enumerate(self._ready_players_since_last_render):
            sample = [GameSample.READY_PLAYER_ONE, GameSample.READY_PLAYER_TWO, GameSample.READY_PLAYER_THREE,
                      GameSample.READY_PLAYER_FOUR][player_index]
            self._sample_player.play_sample(sample, cancel_existing=(i == 0 and len(self._state.ready_players) - len(self._ready_players_since_last_render) == 0))

        if len(self._ready_players_since_last_render) > 0 and len(self._state.ready_players) == len(self._player_stations):
            self._sample_player.play_sample(GameSample.GAME_START)
        elif len(self._state.ready_players) == 0 and self._new_game_since_last_render:
            self._sample_player.play_sample(GameSample.IDLE_LOOP, cancel_existing=True)
            self._sample_player.loop = True

        self._new_game_since_last_render = False
        self._ball_bounce_since_last_render = False
        self._brick_bounce_since_last_render = False
        self._player_eliminated_since_last_render = False
        self._ready_players_since_last_render.clear()

    @property
    def game_complete(self):
        return self._state.game_complete

    def reset_game(self):
        self._state = GameState(v2(self._display.width, self._display.height), initial_ball_speed=self.BALL_MIN_SPEED)
        self._new_game_since_last_render = True
