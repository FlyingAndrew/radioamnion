import os.path

import numpy as np
import scipy.signal
import scipy.fft
import pandas as pd

from .audio_file_handler import AudioFileHandler


class Audio2LED(AudioFileHandler):
    def __init__(self, file_name):
        AudioFileHandler.__init__(self, file_name)

        self.chunk_size = None  # size

        self.data_chunked = None
        self.time_chunked = None

        self.frequency_arr = None  # same as self.time in the frequency space
        self.f_data = None  # frequency space for each chunk -> 3D array [selected_channel, chunks, frequencies]

        self.frequency_boarder_index = None
        self.led_channel_levels = None
        self.freq_channel_amp_norm = None

        self.min_frequency = None
        self.max_frequency = None
        self.alpha_log = None
        self.index_log = None

        self.led_levels = None

        self.selected_channel = None

        self.cal_led_levels()

    def _set_fps_(self, min_fps):
        """Set the chunk size from fps, frames per second."""
        chunk_size = int(2 ** np.floor(np.log2(self.sample_rate / min_fps)))
        self._cal_data_chunked_(
            chunk_size
        )  # cal self.chunks, .chunk_size, .data_chunked

    @property
    def fps(self):
        """Get the frames per second from the chunk size"""
        if self.sample_rate is not None and self.chunk_size is not None:
            return float(self.sample_rate) / self.chunk_size
        else:
            return None

    def _cal_data_chunked_(self, chunk_size):
        """Split up the data into chunks"""
        self.chunk_size = int(chunk_size)  # chunk_size has to be int

        # modulo of array <-> cut the rest of the sound that the length is n*chunk_size
        max_n_chunk_size = int(
            np.floor(self.data.shape[-1] / self.chunk_size) * self.chunk_size
        )

        self.data_chunked = self.data[:, :max_n_chunk_size].reshape(
            self.data.shape[0], -1, int(self.chunk_size)
        )
        self.time_chunked = self.time[:max_n_chunk_size].reshape(
            -1, int(self.chunk_size)
        )

    def _cal_fft_(
        self,
    ):
        """Calculate the fft for the chunks. Chunks have to be set in advance."""
        # filter to 'subtract' baseline
        w = scipy.signal.blackman(self.chunk_size).reshape(1, -1)

        self.f_data = scipy.fft.rfft(self.data_chunked * w, axis=-1)
        self.frequency_arr = scipy.fft.rfftfreq(self.chunk_size, 1.0 / self.sample_rate)

    def _fft_(self, min_fps=15):
        """Sets up the chunks and calculate the fft."""
        self._set_fps_(min_fps)
        self._cal_fft_()

    def cal_led_levels(
        self,
        min_fps=15,
        num_index=4,
        min_frequency=40,
        max_frequency=5e3,
        index_log=True,
        alpha_log=True,
    ):
        """
        The frequencies are bundled in chunks with a log-scale width and position. The amplitudes of this chunks are
        summed up. The displayed frequency if the middle frequency (linear) of the chunks.

        PARAMETER
        ---------
        min_fps: int, optional
            minimum frames per second at which the LEDs will update. To get chunks with length 2**n,
            the resulting fps is higher.
        num_index: int, optional
            number of frequency channels
        min_frequency: float, optional
            minimum frequency of the first level
        max_frequency: float, optional
            max frequency of the last level. It will be only used for the level calculation as the upper limit
            will be set to max of the fft later.
        alpha_log: bool, optional
            Set if the alpha levels should be mapped with a linear (False) or log (True, Default) scale.
        index_log: bool, optional
            Set if the used index for the fft frequency should be mapped with a linear (False) or log (True, Default)
            scale, i.e.: FFT+chunk size -> fft frequencies -> frequencies[index]
        """
        self.min_frequency = min_frequency
        self.max_frequency = max_frequency

        self._fft_(min_fps=min_fps)

        # get the closest indexes for the given boarders
        min_index = np.argwhere(self.frequency_arr > min_frequency).flatten()[0]
        max_index = np.argwhere(self.frequency_arr < max_frequency).flatten()[-1]

        # cal. the index of the range -> 2d array: [[i_0, i_1],[i_1, i_2],...]
        if index_log:
            frequency_boarder_index = np.geomspace(
                min_index, max_index, num_index + 1, dtype=int
            )
        else:
            frequency_boarder_index = np.linspace(
                min_index, max_index, num_index + 1, dtype=int
            )
        self.index_log = index_log

        frequency_boarder_index[-1] = self.frequency_arr.shape[
            -1
        ]  # set the upper limit to max
        frequency_boarder_index = np.array(
            [frequency_boarder_index[:-1], frequency_boarder_index[1:]]
        ).T

        freq_channel_amp = []
        for i_min, i_max in frequency_boarder_index:
            # summed up the amplitude of a frequency bundle -> summed amplitude for the frequency selected_channel
            freq_channel_amp.append(
                np.sum(np.abs(self.f_data[:, :, i_min:i_max]), axis=-1)
            )

        # -> [audio selected_channel, frequency selected_channel, time]
        freq_channel_amp = np.swapaxes(freq_channel_amp, 0, 1)

        # normalize the amp. (levels should be from 0->1 and not .3->.8)
        # noinspection PyArgumentList
        max_arr = np.max(freq_channel_amp, axis=-1)
        min_arr = np.min(freq_channel_amp, axis=-1)

        # get it to the right shape
        max_arr = max_arr.reshape((*max_arr.shape, 1))
        min_arr = min_arr.reshape((*min_arr.shape, 1))

        freq_channel_amp_norm = (freq_channel_amp - min_arr) / (max_arr - min_arr)
        freq_channel_amp_norm[freq_channel_amp_norm < 1e-7] = 1e-7

        # cal. led alpha levels
        self.alpha_log = alpha_log
        if alpha_log:
            self.led_levels = np.geomspace(0.01, 1, 18)  #
        else:
            self.led_levels = np.linspace(0.01, 1, 18)
        self.led_levels = np.array([self.led_levels[:-1], self.led_levels[1:]]).T

        # led_channel_levels[selected_channel, led, chunk]; selected_channel: 0-left, 1-right; led: 0-3; chunk = time
        led_channel_levels = np.zeros_like(freq_channel_amp_norm, dtype=int)

        for i, (lim_lo, lim_hi) in enumerate(self.led_levels):
            led_channel_levels[freq_channel_amp_norm > lim_lo] = i

        self.frequency_boarder_index = frequency_boarder_index
        self.led_channel_levels = led_channel_levels
        self.freq_channel_amp_norm = freq_channel_amp_norm

    def save_to_csv(self, file_name=None, file_dir=None, selected_channel=2):
        """Create the file for the LEDs.
        PARAMETER
        ---------
        selected_channel: [0,1,2], optional
            defines the channel. 0=left, 1=right, 2=mono"""

        self.selected_channel = selected_channel

        if file_name is None:
            file_name = self.file_name.replace(" ", "_").rsplit(".", 1)[0] + ".csv"

        if file_dir is not None:
            file_name = os.path.join(file_dir, os.path.basename(file_name))

        csv_dict = {
            "time [ms]": (np.average(self.time_chunked, axis=-1) * 1000).astype(int)
        }
        csv_dict.update(
            {f"led_{i}": led_i for i, led_i in enumerate(self.led_channel_levels[2])}
        )
        csv_data = pd.DataFrame(csv_dict)
        csv_data.to_csv(file_name, index=False)

        return file_name
