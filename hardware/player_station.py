from os.path import isfile

class PlayerStation:
    def get_shield_pos(self) -> int:
        raise NotImplementedError()
    
    def get_button_pressed(self) -> bool:
        raise NotImplementedError()

try:
    from . import rotary_encoder
    
    try:
        import machine
        PinType = machine.Pin
    except ImportError:
        import digitalio
        PinType = digitalio.Pin
    
    class IOPlayerStation(PlayerStation):
        def __init__(self, rotary_enc_pin_a: PinType, rotary_enc_pin_b: PinType, button_pin: PinType, min_position: int, max_position: int):
            self.rotary_enc = rotary_encoder.IncrementalEncoder(rotary_enc_pin_a, rotary_enc_pin_b, divisor=2)
            self.min_position = min_position
            self.max_position = max_position
            self.rotary_enc_bias = 0
            self.button_pin = digitalio.DigitalInOut(button_pin)
            
        def get_shield_pos(self) -> int:
            if self.rotary_enc.position - self.rotary_enc_bias > self.max_position:
                self.rotary_enc_bias = self.rotary_enc.position - self.max_position
            elif self.rotary_enc.position - self.rotary_enc_bias < self.min_position:
                self.rotary_enc_bias = self.rotary_enc.position - self.min_position
                
            return self.rotary_enc.position - self.rotary_enc_bias
    
        def get_button_pressed(self) -> bool:
            return not self.button_pin.value

except ImportError:
    IOPlayerStation = None
    

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
