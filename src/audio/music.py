import audioop
import numpy as np
import pyaudio
import wave
import os.path

CHUNK_SIZE = 1024

class Music:

    def __init__(self):
        self.width = 2
        self.pa = pyaudio.PyAudio()
        self.stream_in = self.pa.open(format = self.pa.get_format_from_width(self.width),
                                      channels = 2,
                                      rate = 48000,
                                      input = True)
        self.stream_out = self.pa.open(format = self.pa.get_format_from_width(self.width),
                                       channels = 6,
                                       rate = 48000,
                                       output = True)

        self.volumes = [[0, 0, 0.3, 0.7, 0], [0.7, 0.3, 0, 0, 0]]

    def stop(self):
        self.stream_out.stop_stream()
        self.stream_out.close()
        self.pa.terminate()

    def set_6ch_audio(self, l_frames, r_frames, volumes):
        all_frame = [ [np.fromstring(audioop.mul(l_frames, self.width, volumes[0][i]), dtype=np.int16)]
                      if volumes[0][i] != 0
                      else [np.fromstring(audioop.mul(r_frames, self.width, volumes[1][i]), dtype=np.int16)]
                      for i in range(5)]
        audio = np.concatenate(all_frame, axis=0)
        # insertの第2引数がミュートするチャンネル
        audio = np.insert(audio, 4, 0, axis=0).T.astype(np.int16).tostring()

        return audio
