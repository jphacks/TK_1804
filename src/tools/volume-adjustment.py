import audioop
import numpy as np
import pyaudio
import wave

CHUNK_SIZE = 1024

class Music:

    def __init__(self, path = "./stereo.wav"):
        self.path = path
        self.wf = wave.open(path, 'rb')
        self.width = self.wf.getsampwidth()
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format = self.pa.get_format_from_width(self.width),
                                   channels = 6,
                                   rate = self.wf.getframerate(),
                                   output = True)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def replay(self):
        # バイト列を取得
        # [L0, R0, L1, R1, L2, R2, ...]
        src_frames = self.wf.readframes(CHUNK_SIZE)

        while src_frames != '':
            # バイト列を取得
            # [L0, R0, L1, R1, L2, R2, ...]
            src_frames = self.wf.readframes(CHUNK_SIZE)

            # L, Rに分割
            l_frames = audioop.tomono(src_frames, self.width, 1, 0)
            r_frames = audioop.tomono(src_frames, self.width, 0, 1)

            # 各chに流す音量を調整
            # L, FL, FR, R, Bの順
            volumes = [[1, 1, 1, 1, 1], [0, 0, 0, 0, 0]]
            six_ch_frames = self.set_6ch_audio(l_frames, r_frames, volumes)

            # 6chオーディオをstreamに渡す
            # [FL0, FR0, CT0, BA0, RL0, RR0, ...]
            self.stream.write(six_ch_frames)

        self.stop()

    def set_6ch_audio(self, l_frames, r_frames, volumes):
        all_frame = [ [np.fromstring(audioop.mul(l_frames, self.width, volumes[0][i]), dtype=np.int16)]
                      if volumes[0][i] != 0
                      else [np.fromstring(audioop.mul(r_frames, self.width, volumes[1][i]), dtype=np.int16)]
                      for i in range(5)]
        audio = np.concatenate(all_frame, axis=0)
        # insertの第2引数がミュートするチャンネル
        audio = np.insert(audio, 4, 0, axis=0).T.astype(np.int16).tostring()

        return audio

if __name__ == '__main__':
    music = Music()
    music.replay()
