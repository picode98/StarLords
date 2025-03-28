class Display:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.brightness = 1.0

    def __setitem__(self, indices, value):
        raise NotImplementedError()

    def write(self):
        raise NotImplementedError()
