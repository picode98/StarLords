from os.path import isfile

from .player_station import PlayerStation


class FilePlayerStation(PlayerStation):
    def __init__(self, file_path: str):
        self.file_path = file_path

        if not isfile(file_path):
            with open(self.file_path, 'w') as output_file:
                output_file.write('0\n0')

    def get_shield_pos(self) -> int:
        with open(self.file_path, 'r') as input_file:
            return int(next(iter(input_file)))

    def get_button_pressed(self) -> bool:
        with open(self.file_path, 'r') as input_file:
            file_iter = iter(input_file)
            next(file_iter)
            return next(file_iter) == '1'
