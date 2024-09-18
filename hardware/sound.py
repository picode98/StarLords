import sounddevice as sd

import queue
import wave
import cffi
import enum


class GameSample(enum.Enum):
    READY_PLAYER_ONE = 'ready-player-one.wav'
    READY_PLAYER_TWO = 'ready-player-two.wav'
    READY_PLAYER_THREE = 'ready-player-three.wav'
    READY_PLAYER_FOUR = 'ready-player-four.wav'
    GAME_START = 'it-begins.wav'
    BOUNCE = 'bounce.wav'
    BREAK = 'break.wav'
    PLAYER_DEATH = 'death.wav'
    PLAYER_WIN = 'you-are-starlord.wav'


class SamplePlayer:
    def __init__(self):
        self._sample_cache = dict()
        for sample in GameSample:
            with wave.open(sample.value, 'rb') as in_file:
                self._sample_cache[sample.value] = (in_file.readframes(in_file.getnframes()), in_file.getnchannels(), in_file.getframerate())

        self._samples_to_play = queue.SimpleQueue()
        self._curr_sample = None
        self._curr_sample_offset = None
        self._output_device = sd.RawOutputStream(channels=1, dtype='int16', callback=self._stream_callback)
        self._output_device.start()

    def _stream_callback(self, output: 'cffi.FFI.buffer', num_frames: int, time: 'cffi.FFI.CData', status: sd.CallbackFlags):
        output_start = 0
        while output_start < len(output):
            if self._curr_sample is None:
                try:
                    self._curr_sample = self._samples_to_play.get_nowait()
                    self._curr_sample_offset = 0
                except queue.Empty:
                    output[output_start:] = b'\0' * (len(output) - output_start)
                    return

            sample_data = self._sample_cache[self._curr_sample.value][0]
            bytes_to_write = min(len(sample_data) - self._curr_sample_offset, len(output) - output_start)
            output[output_start:output_start + bytes_to_write] = sample_data[self._curr_sample_offset:self._curr_sample_offset + bytes_to_write]
            output_start += bytes_to_write
            self._curr_sample_offset += output_start

            if self._curr_sample_offset >= len(sample_data):
                self._curr_sample = None
                self._curr_sample_offset = None

        return

    def play_sample(self, sample: GameSample, cancel_existing: bool = False):
        if cancel_existing:
            try:
                while True:
                    self._samples_to_play.get_nowait()
            except queue.Empty:
                pass

            self._curr_sample = sample
            self._curr_sample_offset = 0
        else:
            self._samples_to_play.put_nowait(sample)
