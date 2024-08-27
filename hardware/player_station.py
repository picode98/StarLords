class PlayerStation:
    def get_shield_pos(self) -> int:
        raise NotImplementedError()
    
    def get_button_pressed(self) -> bool:
        raise NotImplementedError()

try:
    import rotaryio
    import board
    
    try:
        import machine
        PinType = machine.Pin
    except ImportError:
        import board
        PinType = type(board.D0)
    
    class IOPlayerStation(PlayerStation):
        def __init__(self, rotary_enc_pin_a: PinType, rotary_enc_pin_b: PinType, button_pin: PinType, min_position: int, max_position: int):
            self.rotary_enc = rotaryio.IncrementalEncoder(rotary_enc_pin_a, rotary_enc_pin_b, divisor=2)
            self.min_position = min_position
            self.max_position = max_position
            self.rotary_enc_bias = 0
            self.button_pin = button_pin
            
        def get_shield_pos(self) -> int:
            if self.rotary_enc.position - self.rotary_enc_bias > max_position:
                self.rotary_enc_bias = self.rotary_enc.position - max_position
            elif self.rotary_enc.position - self.rotary_enc_bias < min_position:
                self.rotary_enc_bias = self.rotary_enc.position - min_position
                
            return self.rotary_enc.position - self.rotary_enc_bias
    
        def get_button_pressed(self) -> bool:
            return not self.button_pin.value

except ImportError:
    IOPlayerStation = None
    

class FilePlayerStation(PlayerStation):
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def get_shield_pos(self) -> int:
        with open(self.file_path, 'r') as input_file:
            return int(next(iter(input_file)))
        
    def get_button_pressed(self) -> bool:
        with open(self.file_path, 'r') as input_file:
            file_iter = iter(input_file)
            next(file_iter)
            return next(file_iter) == '1'
