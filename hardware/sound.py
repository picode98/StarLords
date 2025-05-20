import sounddevice as sd
import numpy as np

import wave
import cffi
import enum
import threading
from typing import Optional


class GameSample(enum.Enum):
    IDLE_LOOP = 'spaceship-loop.wav'
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
        self._sample_rate = None
        self._num_output_channels = None

        for sample in GameSample:
            with wave.open(sample.value, 'rb') as in_file:
                data_array = np.frombuffer(in_file.readframes(in_file.getnframes()), dtype='int16').reshape((-1, in_file.getnchannels()))
                self._sample_cache[sample.value] = (data_array, in_file.getnchannels(), in_file.getframerate())
                if self._sample_rate is None:
                    self._sample_rate = in_file.getframerate()
                    self._num_output_channels = in_file.getnchannels()
                else:
                    assert self._sample_rate == in_file.getframerate()
                    assert self._num_output_channels == in_file.getnchannels()

        # self._samples_to_play = queue.SimpleQueue()
        self._curr_samples = []
        self._curr_samples_lock = threading.Lock()
        # self._curr_sample_offset = 0
        self._output_device = sd.OutputStream(channels=1, dtype='int16', callback=self._stream_callback)
        self._output_device.start()

    def _stream_callback(self, output: np.ndarray, num_frames: int, time: 'cffi.FFI.CData', status: sd.CallbackFlags):
        output[:] = np.zeros_like(output)
        new_samples = []

        with self._curr_samples_lock:
            for start_offset, sample, loop in self._curr_samples:
                if start_offset < 0:
                    if -start_offset < output.shape[0]:
                        output_start = -start_offset
                        this_sample_offset = 0
                    else:
                        new_samples.append((start_offset + output.shape[0], sample, loop))
                        continue
                else:
                    output_start = 0
                    this_sample_offset = start_offset

                while True:
                    sample_data = self._sample_cache[sample.value][0]
                    samples_to_write = min(sample_data.shape[0] - this_sample_offset, output.shape[0] - output_start)
                    output[output_start:output_start + samples_to_write] += sample_data[this_sample_offset:this_sample_offset + samples_to_write]

                    if loop:
                        if output_start + samples_to_write < output.shape[0]:
                            this_sample_offset = 0
                            output_start += samples_to_write
                        else:
                            new_samples.append((this_sample_offset + samples_to_write, sample, loop))
                            break
                    else:
                        if this_sample_offset + samples_to_write < sample_data.shape[0]:
                            new_samples.append((this_sample_offset + samples_to_write, sample, loop))
                        break


            self._curr_samples = new_samples

    @property
    def playing(self):
        with self._curr_samples_lock:
            return len(self._curr_samples) >= 1

    def clear_samples(self):
        with self._curr_samples_lock:
            self._curr_samples.clear()

    def play_sample(self, sample: GameSample, playback_start_time: Optional[float] = None, loop: bool = False):
        with self._curr_samples_lock:
            if playback_start_time is None:
                try:
                    start_offset = -max(self._sample_cache[sample.value][0].shape[0] - start_offset
                                        for start_offset, sample, loop in self._curr_samples if not loop)
                except ValueError:
                    start_offset = 0
            else:
                start_offset = -int(round(playback_start_time * self._sample_rate))

            self._curr_samples.append((start_offset, sample, loop))