import math

from display import Display


class GameState:
    """ information about which bricks are broken, projectile position, etc. """
    def __init__(self, field_size):
        w, h = field_size
        self.field_size = field_size
        self.ball_position = (w / 2.0, h / 2.0)
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
    BRICK_SIZE = (1.0, 1.0)
    BALL_SIZE = 1.0
    MAX_DELTA = 0.3

    def __init__(self, display: Display):
        self._state = GameState((display.width, display.height))
        self._display = display

    def _get_ball_collisions(self):
        colliders = []
        if (self._state.ball_position[0] + self.BALL_SIZE / 2.0) >= self._state.field_size[0]:
            colliders.append((BallColliderType.WALL, (-1.0, 0.0), None, None))

        if (self._state.ball_position[0] - self.BALL_SIZE / 2.0) <= 0.0:
            colliders.append((BallColliderType.WALL, (1.0, 0.0), None, None))

        if (self._state.ball_position[1] + self.BALL_SIZE / 2.0) >= self._state.field_size[1]:
            colliders.append((BallColliderType.WALL, (0.0, -1.0), None, None))

        if (self._state.ball_position[1] - self.BALL_SIZE / 2.0) <= 0.0:
            colliders.append((BallColliderType.WALL, (0.0, 1.0), None, None))

        for player_index, brick_list in enumerate(self._state.castle_bricks):
            for brick_index, (brick_x, brick_y) in enumerate(brick_list):
                corners = [(brick_x, brick_y), (brick_x + StarlordsGame.BRICK_SIZE[0], brick_y),
                           (brick_x + StarlordsGame.BRICK_SIZE[0], brick_y + StarlordsGame.BRICK_SIZE[1]),
                           (brick_x, brick_y + StarlordsGame.BRICK_SIZE[1])]
                closest_corner, dist = min(((corner, (corner[0] - self._state.ball_position[0]) ** 2 + (corner[1] - self._state.ball_position[1]) ** 2)
                    for corner in corners), key=lambda x: x[1])
                dist = math.sqrt(dist)

                if dist <= self.BALL_SIZE / 2.0:
                    abs_intersect_x = math.sqrt((StarlordsGame.BALL_SIZE / 2.0) ** 2 - (closest_corner[1] - self._state.ball_position[1]) ** 2)
                    abs_intersect_y = math.sqrt((StarlordsGame.BALL_SIZE / 2.0) ** 2 - (closest_corner[0] - self._state.ball_position[0]) ** 2)
                    ix_point = (self._state.ball_position[0] + (-abs_intersect_x if closest_corner[0] < self._state.ball_position[0] else abs_intersect_x), closest_corner[1])
                    iy_point = (closest_corner[0], self._state.ball_position[1] + (-abs_intersect_y if closest_corner[1] < self._state.ball_position[1] else abs_intersect_y))

                    normal_vector = (self._state.ball_position[0] - (ix_point[0] + iy_point[0]) / 2.0,
                                     self._state.ball_position[1] - (ix_point[1] + iy_point[1]) / 2.0)
                    # normal_vector = (self._state.ball_position[0] - closest_corner[0],
                    #                  self._state.ball_position[1] - closest_corner[1])
                    length = math.sqrt(normal_vector[0] ** 2 + normal_vector[1] ** 2)
                    unit_normal_vector = (normal_vector[0] / length, normal_vector[1] / length)
                    colliders.append((BallColliderType.CASTLE_BRICK, unit_normal_vector, player_index, brick_index))
                elif (self._state.ball_position[0] + StarlordsGame.BALL_SIZE / 2.0 >= brick_x and
                         self._state.ball_position[0] - StarlordsGame.BALL_SIZE / 2.0 <= brick_x + StarlordsGame.BRICK_SIZE[0] and
                         self._state.ball_position[1] >= brick_y and
                         self._state.ball_position[1] <= brick_y + StarlordsGame.BRICK_SIZE[1]
                    ) or (
                        self._state.ball_position[0] >= brick_x and
                        self._state.ball_position[0] <= brick_x + StarlordsGame.BRICK_SIZE[0] and
                        self._state.ball_position[1] + StarlordsGame.BALL_SIZE / 2.0 >= brick_y and
                        self._state.ball_position[1] - StarlordsGame.BALL_SIZE / 2.0 <= brick_y + StarlordsGame.BRICK_SIZE[1]
                    ):
                    delta = (self._state.ball_position[0] - (brick_x + StarlordsGame.BRICK_SIZE[0] / 2.0),
                             self._state.ball_position[1] - (brick_y + StarlordsGame.BRICK_SIZE[1] / 2.0))
                    if abs(delta[0]) >= abs(delta[1]):
                        normal_vector = (-1.0 if delta[0] < 0.0 else 1.0, 0.0)
                    else:
                        normal_vector = (0.0, -1.0 if delta[1] < 0.0 else 1.0)

                    colliders.append((BallColliderType.CASTLE_BRICK, normal_vector, player_index, brick_index))

        return colliders

    def update(self, time_delta: float):
        """ update self._state with time_delta of elapsed time """
        mag_delta_sqr = (self._state.ball_velocity[0] * time_delta) ** 2 + (self._state.ball_velocity[1] * time_delta) ** 2
        if mag_delta_sqr >= StarlordsGame.MAX_DELTA ** 2:
            time_delta /= (mag_delta_sqr / (StarlordsGame.MAX_DELTA ** 2))

        collisions = self._get_ball_collisions()
        avg_normal_vector = (0.0, 0.0)
        for _, normal_vector, _, _ in collisions:
            avg_normal_vector = (avg_normal_vector[0] + normal_vector[0], avg_normal_vector[1] + normal_vector[1])

        if len(collisions) > 0:
            len_avg_normal_vector = math.sqrt(avg_normal_vector[0] ** 2 + avg_normal_vector[1] ** 2)
            avg_normal_vector = (avg_normal_vector[0] / len_avg_normal_vector, avg_normal_vector[1] / len_avg_normal_vector)

            # for coll_type, normal_vector, player_index, brick_index in self._get_ball_collisions():
            dot_product = self._state.ball_velocity[0] * avg_normal_vector[0] + self._state.ball_velocity[1] * avg_normal_vector[1]
            proj_velocity = (dot_product * avg_normal_vector[0], dot_product * avg_normal_vector[1])
            reflected_proj_velocity = (abs(dot_product) * avg_normal_vector[0], abs(dot_product) * avg_normal_vector[1])
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
        self._display[round(self._state.ball_position[0] - StarlordsGame.BALL_SIZE / 2.0), round(self._state.ball_position[1] - StarlordsGame.BALL_SIZE / 2.0)] = StarlordsGame.BALL_COLOR
        self._display.write()
