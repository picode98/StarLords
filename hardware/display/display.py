class Display:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width

    def __setitem__(self, indices, value):
        raise NotImplementedError()

    def write(self):
        raise NotImplementedError()
