import math

from display import Display


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


class GameState:
    """ information about which bricks are broken, projectile position, etc. """
    def __init__(self, field_size: Vector2):
        w, h = field_size.x, field_size.y
        self.field_size: Vector2 = field_size
        self.ball_position = v2(w / 2.0, h / 2.0)
        self.ball_velocity = v2(0.0, 0.0)
        self.castle_bricks = [[v2(3.0, 0.0), v2(3.0, 1.0), v2(3.0, 2.0), v2(3.0, 3.0), v2(2.0, 3.0), v2(1.0, 3.0), v2(0.0, 3.0)],
                              [v2(w - 4.0, 0.0), v2(w - 4.0, 1.0), v2(w - 4.0, 2.0), v2(w - 4.0, 3.0), v2(w - 3.0, 3.0), v2(w - 2.0, 3.0), v2(w - 1.0, 3.0)],
                              [v2(w - 4.0, h - 1.0), v2(w - 4.0, h - 2.0), v2(w - 4.0, h - 3.0), v2(w - 4.0, h - 4.0), v2(w - 3.0, h - 4.0), v2(w - 2.0, h - 4.0), v2(w - 1.0, h - 4.0)],
                              [v2(3.0, h - 1.0), v2(3.0, h - 2.0), v2(3.0, h - 3.0), v2(3.0, h - 4.0), v2(2.0, h - 4.0), v2(1.0, h - 4.0), v2(0.0, h - 4.0)]
        ]
        self.shield_positions = [v2(5.0, 5.0), v2(w - 6.0, 5.0), v2(w - 6.0, h - 6.0), v2(5.0, h - 6.0)]
        self.explosions = []


class BallColliderType:
    WALL = 0
    CASTLE_BRICK = 1
    POWER_CORE = 2


class StarlordsGame:
    BALL_COLOR = (50, 50, 50)
    BRICK_COLOR = (0, 0, 50)
    SHIELD_COLOR = (50, 0, 0)
    EXPLOSION_COLOR = (50, 50, 50)
    BRICK_SIZE = v2(1.0, 1.0)
    BALL_SIZE = 1.0
    MAX_DELTA = 0.3
    MINIMUM_EXPLOSION_BRIGHTNESS = 0.05
    EXPLOSION_SHOCKWAVE_VELOCITY = 8.0

    def __init__(self, display: Display):
        self._state = GameState(v2(display.width, display.height))
        self._display = display

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
                corners = [brick_pos, v2(brick_pos.x + StarlordsGame.BRICK_SIZE.x, brick_pos.y),
                           brick_pos + StarlordsGame.BRICK_SIZE,
                           v2(brick_pos.x, brick_pos.y + StarlordsGame.BRICK_SIZE.y)]
                closest_corner, dist = min(((corner, (corner - self._state.ball_position).length2())
                    for corner in corners), key=lambda x: x[1])
                dist = math.sqrt(dist)

                if dist <= self.BALL_SIZE / 2.0:
                    abs_intersect_x = math.sqrt((StarlordsGame.BALL_SIZE / 2.0) ** 2 - (closest_corner.y - self._state.ball_position.y) ** 2)
                    abs_intersect_y = math.sqrt((StarlordsGame.BALL_SIZE / 2.0) ** 2 - (closest_corner.x - self._state.ball_position.x) ** 2)
                    ix_point = v2(self._state.ball_position.x + (-abs_intersect_x if closest_corner.x < self._state.ball_position.x else abs_intersect_x), closest_corner.y)
                    iy_point = v2(closest_corner.x, self._state.ball_position.y + (-abs_intersect_y if closest_corner.y < self._state.ball_position.y else abs_intersect_y))

                    normal_vector = self._state.ball_position - (ix_point + iy_point) / 2.0
                    # normal_vector = (self._state.ball_position[0] - closest_corner[0],
                    #                  self._state.ball_position[1] - closest_corner[1])
                    unit_normal_vector: Vector2 = normal_vector / normal_vector.length()
                    colliders.append((BallColliderType.CASTLE_BRICK, unit_normal_vector, player_index, brick_index))
                elif (self._state.ball_position.x + StarlordsGame.BALL_SIZE / 2.0 >= brick_pos.x and
                         self._state.ball_position.x - StarlordsGame.BALL_SIZE / 2.0 <= brick_pos.x + StarlordsGame.BRICK_SIZE.x and
                         self._state.ball_position.y >= brick_pos.y and
                         self._state.ball_position.y <= brick_pos.y + StarlordsGame.BRICK_SIZE.y
                    ) or (
                        self._state.ball_position.x >= brick_pos.x and
                        self._state.ball_position.x <= brick_pos.x + StarlordsGame.BRICK_SIZE.x and
                        self._state.ball_position.y + StarlordsGame.BALL_SIZE / 2.0 >= brick_pos.y and
                        self._state.ball_position.y - StarlordsGame.BALL_SIZE / 2.0 <= brick_pos.y + StarlordsGame.BRICK_SIZE.y
                    ):
                    delta = self._state.ball_position - (brick_pos + StarlordsGame.BRICK_SIZE / 2.0)

                    if abs(delta.x) >= abs(delta.y):
                        normal_vector = v2(-1.0 if delta.x < 0.0 else 1.0, 0.0)
                    else:
                        normal_vector = v2(0.0, -1.0 if delta.y < 0.0 else 1.0)

                    colliders.append((BallColliderType.CASTLE_BRICK, normal_vector, player_index, brick_index))

        return colliders

    def update(self, time_delta: float):
        """ update self._state with time_delta of elapsed time """
        mag_delta_sqr = (self._state.ball_velocity * time_delta).length2()
        if mag_delta_sqr >= StarlordsGame.MAX_DELTA ** 2:
            time_delta /= (mag_delta_sqr / (StarlordsGame.MAX_DELTA ** 2))

        radius_delta = StarlordsGame.EXPLOSION_SHOCKWAVE_VELOCITY * time_delta
        new_explosions = []
        for position, radius, brightness in self._state.explosions:
            new_explosion = (position, radius + radius_delta, brightness * ((radius / (radius + radius_delta)) ** 2))
            if new_explosion[2] >= StarlordsGame.MINIMUM_EXPLOSION_BRIGHTNESS:
                new_explosions.append(new_explosion)

        self._state.explosions = new_explosions

        collisions = self._get_ball_collisions()
        avg_normal_vector = sum((normal_vector for _, normal_vector, _, _ in collisions), v2(0.0, 0.0))
        # for _, normal_vector, _, _ in collisions:
        #     avg_normal_vector = (avg_normal_vector[0] + normal_vector[0], avg_normal_vector[1] + normal_vector[1])

        if len(collisions) > 0:
            brick_removals = set()
            for coll_type, normal_vector, player_index, brick_index in collisions:
                if coll_type == BallColliderType.CASTLE_BRICK:
                    brick_pos = self._state.castle_bricks[player_index][brick_index]
                    brick_removals.add((player_index, brick_index))
                    self._state.explosions.append((brick_pos + StarlordsGame.BRICK_SIZE / 2, 1.0, 5.0))

            self._state.castle_bricks = [[brick_pos for brick_index, brick_pos in enumerate(brick_list) if not (player_index, brick_index) in brick_removals]
                                         for player_index, brick_list in enumerate(self._state.castle_bricks)]

            avg_normal_vector = avg_normal_vector / avg_normal_vector.length()

            # for coll_type, normal_vector, player_index, brick_index in self._get_ball_collisions():
            dot_product = self._state.ball_velocity.dot(avg_normal_vector)
            proj_velocity = dot_product * avg_normal_vector
            reflected_proj_velocity = abs(dot_product) * avg_normal_vector
            self._state.ball_velocity = self._state.ball_velocity - proj_velocity + reflected_proj_velocity

        self._state.ball_position = self._state.ball_position + self._state.ball_velocity * time_delta

        return time_delta

    def render(self):
        """ draw self._state to self._display """
        for x in range(self._display.width):
            for y in range(self._display.height):
                self._display[x, y] = (0, 0, 0)

        for brick_list in self._state.castle_bricks:
            for brick_pos in brick_list:
                self._display[round(brick_pos.x), round(brick_pos.y)] = StarlordsGame.BRICK_COLOR

        for position, radius, brightness in self._state.explosions:
            for block_x in range(max(int(position.x - radius), 0), min(math.ceil(position.x + radius) + 1, self._display.width - 1)):
                for block_y in range(max(int(position.y - radius), 0), min(math.ceil(position.y + radius) + 1, self._display.height - 1)):
                    if (position.x - (block_x + 0.5)) ** 2 + (position.y - (block_y + 0.5)) ** 2 <= radius:
                        self._display[block_x, block_y] = (round(StarlordsGame.EXPLOSION_COLOR[0] * brightness),
                                                           round(StarlordsGame.EXPLOSION_COLOR[1] * brightness),
                                                           round(StarlordsGame.EXPLOSION_COLOR[2] * brightness))

        for shield_pos in self._state.shield_positions:
            self._display[round(shield_pos.x), round(shield_pos.y)] = StarlordsGame.SHIELD_COLOR

        # print(f'Position: {self._state.ball_position} Velocity: {self._state.ball_velocity}')
        self._display[round(self._state.ball_position.x - StarlordsGame.BALL_SIZE / 2.0), round(self._state.ball_position.y - StarlordsGame.BALL_SIZE / 2.0)] = StarlordsGame.BALL_COLOR
        self._display.write()
