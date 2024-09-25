from typing import Tuple

class PlayerStation:
    def get_shield_pos(self) -> int:
        raise NotImplementedError()
    
    def get_button_pressed(self) -> bool:
        raise NotImplementedError()

    def get_num_ring_light_pixels(self) -> int:
        raise NotImplementedError()

    def set_ring_light_value(self, idx: int, value: Tuple[int, int, int]):
        pass

    def write_ring_light(self):
        pass
