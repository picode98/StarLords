import pyartnet

from .display import Display


class ArtNetDisplay(Display):
    MAX_UNIVERSE_SIZE = 512

    def __init__(self, artnet_node: pyartnet.ArtNetNode, height: int, width: int, bpp: int = 3, pixel_mapping = None,
                 extra_pixels_end: int = 0):
        super().__init__(height, width)
        self.bpp = bpp
        self.pixel_mapping = pixel_mapping or (lambda x, y: y * width + x)
        self.num_pixels = height * width + extra_pixels_end

        # Bit of a hack: disable the node's background refresh task to use it synchronously.
        class NoopRefreshTask:
            def start(self):
                pass
        artnet_node._process_task = NoopRefreshTask()

        self._artnet_universes = []
        self._artnet_channels = []
        self._max_elems_per_universe = self.MAX_UNIVERSE_SIZE - self.MAX_UNIVERSE_SIZE % self.bpp
        total_elems = self.bpp * self.num_pixels
        for i in range(0, total_elems, self._max_elems_per_universe):
            new_universe = artnet_node.add_universe(len(artnet_node))
            self._artnet_universes.append(new_universe)
            self._artnet_channels.append(new_universe.add_channel(start=1, width=min(self._max_elems_per_universe, total_elems - i)))

        self._color_list = [((0,) * self.bpp)] * self.num_pixels

    def __setitem__(self, indices, value):
        x, y = indices
        if len(value) < self.bpp:
            value = (*value, *((0,) * (self.bpp - len(value))))

        try:
            self._color_list[self.pixel_mapping(x, y)] = tuple(int(round(item * self.brightness)) for item in value)
        except IndexError:
            print(f'WARNING: Out of bounds display access: {x}, {y}')

    def write(self):
        # color_list = []
        # for y in range(self.height):
        #     for x in (range(self.width) if y % 2 == 0 else range(self.width - 1, -1, -1)):
        #         color_list += list(self._colors[y][x])
        color_list = [color for elem in self._color_list for color in elem]

        for i, universe, channel in zip(range(0, len(color_list), self._max_elems_per_universe), self._artnet_universes, self._artnet_channels, strict=True):
            channel.set_values(color_list[i:i + self._max_elems_per_universe])
            universe.send_data()
