from display import Display

from math import ceil

class GameState:
    """ information about which bricks are broken, projectile position, etc. """
    def __init__(self, field_size):
        w, h = field_size
        self.field_size = field_size
        self.ball_position = (0.0, 0.0)
        self.ball_velocity = (0.0, 0.0)
        self.castle_bricks = [[(3.0, 0.0), (3.0, 1.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0), (1.0, 3.0), (0.0, 3.0)],
                              [(w - 4.0, 0.0), (w - 4.0, 1.0), (w - 4.0, 2.0), (w - 4.0, 3.0), (w - 3.0, 3.0), (w - 2.0, 3.0), (w - 1.0, 3.0)],
                              [(w - 4.0, h - 1.0), (w - 4.0, h - 2.0), (w - 4.0, h - 3.0), (w - 4.0, h - 4.0), (w - 3.0, h - 4.0), (w - 2.0, h - 4.0), (w - 1.0, h - 4.0)],
                              [(3.0, h - 1.0), (3.0, h - 2.0), (3.0, h - 3.0), (3.0, h - 4.0), (2.0, h - 4.0), (1.0, h - 4.0), (0.0, h - 4.0)]
        ]


class BallColliderType:
    WALL = 0
    CASTLE_BRICK = 1
    POWER_CORE = 2


class StarlordsGame:
    BALL_COLOR = (50, 50, 50)
    BRICK_COLOR = (0, 0, 50)
    BALL_SIZE = (1.0, 1.0)
    MAX_DELTA = 0.3

    def __init__(self, display: Display):
        self._state = GameState((display.width, display.height))
        self._display = display

    def _get_ball_collisions(self):
        colliders = []
        if (self._state.ball_position[0] + self.BALL_SIZE[0] / 2.0) >= self._state.field_size[0]:
            colliders.append((BallColliderType.WALL, (-1.0, 0.0)))

        if (self._state.ball_position[0] - self.BALL_SIZE[0] / 2.0) <= 0.0:
            colliders.append((BallColliderType.WALL, (1.0, 0.0)))

        if (self._state.ball_position[1] + self.BALL_SIZE[1] / 2.0) >= self._state.field_size[1]:
            colliders.append((BallColliderType.WALL, (0.0, -1.0)))

        if (self._state.ball_position[1] - self.BALL_SIZE[1] / 2.0) <= 0.0:
            colliders.append((BallColliderType.WALL, (0.0, 1.0)))

        return colliders

    def update(self, time_delta: float):
        """ update self._state with time_delta of elapsed time """
        mag_delta_sqr = (self._state.ball_velocity[0] * time_delta) ** 2 + (self._state.ball_velocity[1] * time_delta) ** 2
        if mag_delta_sqr >= StarlordsGame.MAX_DELTA ** 2:
            time_delta /= (mag_delta_sqr / (StarlordsGame.MAX_DELTA ** 2))

        for coll_type, normal_vector in self._get_ball_collisions():
            dot_product = self._state.ball_velocity[0] * normal_vector[0] + self._state.ball_velocity[1] * normal_vector[1]
            proj_velocity = (dot_product * normal_vector[0], dot_product * normal_vector[1])
            reflected_proj_velocity = (abs(dot_product) * normal_vector[0], abs(dot_product) * normal_vector[1])
            self._state.ball_velocity = (self._state.ball_velocity[0] - proj_velocity[0] + reflected_proj_velocity[0],
                                         self._state.ball_velocity[1] - proj_velocity[1] + reflected_proj_velocity[1])

        self._state.ball_position = (self._state.ball_position[0] + self._state.ball_velocity[0] * time_delta,
                                     self._state.ball_position[1] + self._state.ball_velocity[1] * time_delta)

        return time_delta

    def render(self):
        """ draw self._state to self._display """
        for x in range(self._display.width):
            for y in range(self._display.height):
                self._display[x, y] = (0, 0, 0)

        for brick_list in self._state.castle_bricks:
            for x, y in brick_list:
                self._display[round(x), round(y)] = StarlordsGame.BRICK_COLOR

        # print(f'Position: {self._state.ball_position} Velocity: {self._state.ball_velocity}')
        self._display[round(self._state.ball_position[0] - StarlordsGame.BALL_SIZE[0] / 2.0), round(self._state.ball_position[1] - StarlordsGame.BALL_SIZE[0] / 2.0)] = StarlordsGame.BALL_COLOR
        self._display.write()
