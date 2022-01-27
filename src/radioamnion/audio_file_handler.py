import os
import warnings

import librosa
import scipy.io.wavfile
import numpy as np


class AudioFileHandler:
    def __init__(self, file_name):
        self.file_name = os.path.abspath(os.path.expanduser(file_name))
        self.sample_rate = None
        self.data = None  # [left, right, mono]; mono=(left+right)/2

        self.time = None

        try:
            self.read_file_scipy()
        except ValueError:  # ValueError will come up for mp3 files
            self.read_file_librosa()

    def read_file_scipy(self):
        """Read the audio file with scipy.io.wavfile.read. Faster but onyl supports `.wav` files."""
        # load the data
        self.sample_rate, self.data = scipy.io.wavfile.read(self.file_name)
        self.data = self.data.T  # self.data[0] is selected_channel 0

        self.__time_and_mono_ch__()

    def read_file_librosa(self):
        """Read the audio file with librosa.load. Slower but supports more file typs  e.g. `.mp3`."""
        # load the data
        with warnings.catch_warnings():
            self.data, self.sample_rate = librosa.load(
                self.file_name, sr=None, mono=False
            )

        # librosa exports the data as float in the range [-1,1[ -> *2**15 will give the int16 format.
        self.data = (self.data * 2 * 15).astype(
            np.int16
        )  # self.data[0] is selected_channel 0

        self.__time_and_mono_ch__()

    def __time_and_mono_ch__(self):
        """Calculate the timestamps and adds the mono channel as data[2]"""
        self.time = np.arange(self.data.shape[-1], dtype=float) / self.sample_rate
        self.data = np.append(self.data, [self.data.sum(axis=0) // 2], axis=0)
