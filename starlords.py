import enum

from display import Display


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


class BallColliderType(enum.Enum):
    WALL = 0
    CASTLE_BRICK = 1
    POWER_CORE = 2


class StarlordsGame:
    BALL_COLOR = (255, 255, 255)
    BRICK_COLOR = (0, 0, 255)
    BALL_SIZE = (1.0, 1.0)

    def __init__(self, display: Display):
        self._state = GameState((display.width, display.height))
        self._display = display

    def _get_ball_collision(self):
        if (self._state.ball_position[0] + self.BALL_SIZE[0] / 2.0) >= self._state.field_size[0]:
            return BallColliderType.WALL, (-1.0, 0.0)
        elif (self._state.ball_position[0] - self.BALL_SIZE[0] / 2.0) <= 0.0:
            return BallColliderType.WALL, (1.0, 0.0)
        elif (self._state.ball_position[1] + self.BALL_SIZE[1] / 2.0) >= self._state.field_size[1]:
            return BallColliderType.WALL, (0.0, -1.0)
        elif (self._state.ball_position[1] - self.BALL_SIZE[1] / 2.0) <= 0.0:
            return BallColliderType.WALL, (0.0, 1.0)
        else:
            return None, None

    def update(self, time_delta: float):
        """ update self._state with time_delta of elapsed time """
        self._state.ball_position = (self._state.ball_position[0] + self._state.ball_velocity[0] * time_delta,
                                     self._state.ball_position[1] + self._state.ball_velocity[1] * time_delta)

        coll_type, normal_vector = self._get_ball_collision()
        if coll_type is not None:
            dot_product = self._state.ball_velocity[0] * normal_vector[0] + self._state.ball_velocity[1] * normal_vector[1]
            proj_velocity = (dot_product * normal_vector[0], dot_product * normal_vector[1])
            reflected_proj_velocity = (abs(dot_product) * normal_vector[0], abs(dot_product) * normal_vector[1])
            self._state.ball_velocity = (self._state.ball_velocity[0] - proj_velocity[0] + reflected_proj_velocity[0],
                                         self._state.ball_velocity[1] - proj_velocity[1] + reflected_proj_velocity[1])

    def render(self):
        """ draw self._state to self._display """
        for x in range(self._display.width):
            for y in range(self._display.height):
                self._display[x, y] = (0, 0, 0)

        for brick_list in self._state.castle_bricks:
            for x, y in brick_list:
                self._display[round(x), round(y)] = StarlordsGame.BRICK_COLOR

        self._display[round(self._state.ball_position[0] - StarlordsGame.BALL_SIZE[0] / 2.0), round(self._state.ball_position[1] - StarlordsGame.BALL_SIZE[0] / 2.0)] = StarlordsGame.BALL_COLOR
        self._display.write()
