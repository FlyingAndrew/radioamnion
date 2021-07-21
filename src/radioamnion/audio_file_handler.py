import os
import scipy.io.wavfile
import numpy as np


class AudioFileHandler:
    def __init__(self, file_name):
        self.file_name = os.path.abspath(os.path.expanduser(file_name))
        self.sample_rate = None
        self.data = None  # [left, right, mono]; mono=(left+right)/2

        self.time = None

        self.read_file()

    def read_file(self):
        # load the data
        self.sample_rate, self.data = scipy.io.wavfile.read(self.file_name)
        self.time = np.arange(self.data.shape[0], dtype=float) / self.sample_rate

        self.data = self.data.T  # self.data[0] is selected_channel 0
        self.data = np.append(self.data, [self.data.sum(axis=0) // 2], axis=0)
