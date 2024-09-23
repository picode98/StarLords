import pyartnet

from .display import Display


class ArtNetDisplay(Display):
    def __init__(self, artnet_node: pyartnet.ArtNetNode, height: int, width: int):
        super().__init__(height, width)

        # Bit of a hack: disable the node's background refresh task to use it synchronously.
        class NoopRefreshTask:
            def start(self):
                pass
        artnet_node._process_task = NoopRefreshTask()

        self._artnet_universes = []
        self._artnet_channels = []
        total_elems = 3 * height * width
        for i in range(0, total_elems, 512):
            new_universe = artnet_node.add_universe(len(artnet_node))
            self._artnet_universes.append(new_universe)
            self._artnet_channels.append(new_universe.add_channel(start=1, width=min(512, total_elems - i)))

        self._colors = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

    def __setitem__(self, indices, value):
        x, y = indices
        self._colors[y][x] = value

    def write(self):
        color_list = []
        for y in range(self.height):
            for x in (range(self.width) if y % 2 == 0 else range(self.width - 1, -1, -1)):
                color_list += list(self._colors[y][x])

        for i, universe, channel in zip(range(0, len(color_list), 512), self._artnet_universes, self._artnet_channels, strict=True):
            channel.set_values(color_list[i:i + 512])
            universe.send_data()
