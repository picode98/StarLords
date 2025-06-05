def get_serpentine_index(x: int, y: int, disp_width: int, block_width: int, block_height: int):
    block_row, block_col = y // block_height, x // block_width
    block_start_index = block_row * block_height * disp_width + block_height * block_width * (
        block_col if block_row % 2 == 0 else (disp_width // block_width - 1 - block_col))
    return (block_start_index + block_width * (y % block_height if block_col % 2 == 0 else (block_height - 1) - (y % block_height))
            + (x % block_width if y % 2 == 0 else (block_width - 1) - (x % block_width)))


class Display:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.brightness = 1.0

    def __setitem__(self, indices, value):
        raise NotImplementedError()

    def write(self):
        raise NotImplementedError()

    def hardware_test(self):
        pass
