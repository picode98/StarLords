from display import Display


class GameState:
    """ information about which bricks are broken, projectile position, etc. """
    def __init__(self):
        self.ball_position = (0.0, 0.0)
        self.ball_velocity = (0.0, 0.0)


class StarlordsGame:
    BALL_COLOR = (255, 255, 255)

    def __init__(self, display: Display):
        self._state = GameState()
        self._display = display

    def update(self, time_delta: float):
        """ update self._state with time_delta of elapsed time """
        self._state.ball_position = (self._state.ball_position[0] + self._state.ball_velocity[0] * time_delta,
                                     self._state.ball_position[1] + self._state.ball_velocity[1] * time_delta)

    def render(self):
        """ draw self._state to self._display """
        for x in range(self._display.width):
            for y in range(self._display.height):
                self._display[x, y] = (0, 0, 0)

        self._display[round(self._state.ball_position[0]), round(self._state.ball_position[1])] = StarlordsGame.BALL_COLOR
        self._display.write()
