import numpy as np
import soundfile as sf
# import pyloudnorm as pyln


class WavInfo(object):

    MIN_VOLUME_DB = -120.0
    eps = 10 ** (MIN_VOLUME_DB / 20.0)

    # Load wav from path by soundfile
    def __init__(self, path: str = ""):
        self.path = path
        self.available = True
        self.rev_id = -1
        self.depot_path = ""
        if len(path) > 0:
            self.data, self.sr = sf.read(path, always_2d=True)
            if self.data.shape[0] == 0:
                raise Exception("Wav data is empty.")
        else:
            self.create_failed_data()
        self.duration = len(self.data) / self.sr
        # self.lufs_meter = pyln.Meter(self.sr)

    def create_failed_data(self):
        self.available = False
        self.data = np.zeros((1, 1))
        self.sr = 44100

    @property
    def channels(self) -> int:
        # return self.sound.channels
        return self.data.shape[1]

    # avg volume of all channels
    @property
    def RMS(self) -> np.array:
        return np.clip(np.sqrt(np.mean(np.square(self.data), axis=0)), self.eps, None)

    # avg volume of all channels in dB
    @property
    def dBFS(self) -> np.array:
        return 20 * np.log10(self.RMS / 1.0)

    # max dBFS of all channels
    @property
    def max_dBFS(self) -> np.array:
        return 20 * np.log10(np.clip(np.max(np.abs(self.data), axis=0), self.eps, None) / 1.0)

    # LUFS, another avg volume meter
    # @property
    # def LUFS(self) -> float:
    #     return self.lufs_meter.integrated_loudness(self.data)

    # dB diff between channels
    @property
    def channels_dBFS_diff(self) -> float:
        dBFS = self.dBFS
        return np.max(dBFS) - np.min(dBFS)
