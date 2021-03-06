import copy
from multiprocessing import Process, Array, Value
import ctypes
import sys
import numpy as np
import audioop
import cv2
import readchar
import dlib

from camera.head_degree import HeadDegree

from audio.music import Music
from camera.head_vector import HeadVector
from camera.select_speakers import SelectSpeakers

CHUNK_SIZE = 1024

def init_select_speaker():
    face_landmark_path = './src/camera/shape_predictor_68_face_landmarks.dat'

    K = [3.805259604807149003e+02,0.0,3.067605479328022398e+02,
        0.0,3.692700763302592577e+02,2.792470548132930048e+02,
        0.0, 0.0, 1.0]

    D = [-6.480026610793842012e-01,4.518886105418712940e-01,2.383686615865462672e-03,5.527650471881409219e-03,-1.457046727587593127e-01]

    object_pts = np.float32([[6.825897, 6.760612, 4.402142],
                            [1.330353, 7.122144, 6.903745],
                            [-1.330353, 7.122144, 6.903745],
                            [-6.825897, 6.760612, 4.402142],
                            [5.311432, 5.485328, 3.987654],
                            [1.789930, 5.393625, 4.413414],
                            [-1.789930, 5.393625, 4.413414],
                            [-5.311432, 5.485328, 3.987654],
                            [2.005628, 1.409845, 6.165652],
                            [-2.005628, 1.409845, 6.165652],
                            [2.774015, -2.080775, 5.048531],
                            [-2.774015, -2.080775, 5.048531],
                            [0.000000, -3.116408, 6.097667],
                            [0.000000, -7.415691, 4.070434]])

    reprojectsrc = np.float32([[10.0, 10.0, 10.0],
                            [10.0, 10.0, -10.0],
                            [10.0, -10.0, -10.0],
                            [10.0, -10.0, 10.0],
                            [-10.0, 10.0, 10.0],
                            [-10.0, 10.0, -10.0],
                            [-10.0, -10.0, -10.0],
                            [-10.0, -10.0, 10.0]])

    line_pairs = [[0, 1], [1, 2], [2, 3], [3, 0],
                [4, 5], [5, 6], [6, 7], [7, 4],
                [0, 4], [1, 5], [2, 6], [3, 7]]


    select_speaker = SelectSpeakers(K, D, object_pts, reprojectsrc, line_pairs, face_landmark_path)

    return select_speaker

def play_music(shared_music_l_volumes, shared_music_r_volumes):
    print("Run play_music")
    music = Music()
    print("END play_music")
    src_frames = music.stream_in.read(CHUNK_SIZE, exception_on_overflow=False)

    while src_frames != '':
        # バイト列を取得
        # [L0, R0, L1, R1, L2, R2, ...]
        src_frames = music.stream_in.read(CHUNK_SIZE, exception_on_overflow=False)
        # L, Rに分割
        l_frames = audioop.tomono(src_frames, music.width, 1, 0)
        r_frames = audioop.tomono(src_frames, music.width, 0, 1)
        music.volumes = [shared_music_l_volumes, shared_music_r_volumes]
        # 顔認識側から受け取る値
        six_ch_frames = music.set_6ch_audio(l_frames, r_frames, music.volumes)

        # 6chオーディオをstream_outに渡す
        # [FL0, FR0, CT0, BA0, RL0, RR0, ...]
        music.stream_out.write(six_ch_frames)

    music.stop()

def assign_speaker(shared_music_l_volumes, shared_music_r_volumes, direction):
    print("Run assign_speaker")
    select_speaker = init_select_speaker()
    # 顔認識
    head = HeadVector()
    head_degree = HeadDegree()
    while(True):
        # デバックモード
        if direction.value == 0:
            all_flames = select_speaker.estimate_head_orientation(head, head_degree)
            if all_flames is not None:
                l_volumes, r_volumes = all_flames[0], all_flames[1]

        elif direction.value == -1:
            l_volumes, r_volumes = np.array([0, 0, 0, 0, 0]), np.array([0, 0, 0, 0, 0])
        elif direction.value == 9:
            l_volumes, r_volumes = np.array([1, 1, 0, 0, 0.5]), np.array([0, 0, 1, 1, 0.5])
        elif direction.value == 1:
            l_volumes, r_volumes = np.array([0, 0, 0, 0, 1]), np.array([0, 0.5, 0.5, 0, 0])
        elif direction.value == 2:
            l_volumes, r_volumes = np.array([0.5, 0, 0, 0, 0.5]), np.array([0, 0, 0.75, 0.25, 0])
        elif direction.value == 3:
            l_volumes, r_volumes = np.array([1, 0, 0, 0, 0]), np.array([0, 0, 0, 1, 0])
        elif direction.value == 4:
            l_volumes, r_volumes = np.array([0.25, 0.75, 0, 0, 0]), np.array([0, 0, 0, 0.5, 0.5])
        elif direction.value == 5:
            l_volumes, r_volumes = np.array([0, 0.5, 0.5, 0, 0]), np.array([0, 0, 0, 0, 1])
        elif direction.value == 6:
            l_volumes, r_volumes = np.array([1, 0, 0, 0, 0]), np.array([0, 0, 0, 0, 0])
        elif direction.value == 7:
            l_volumes, r_volumes = np.array([0, 1, 0, 0, 0]), np.array([0, 0, 0, 0, 0])
        elif direction.value == 8:
            l_volumes, r_volumes = np.array([0, 0, 0, 0, 0]), np.array([0, 0, 1, 0, 0])
        elif direction.value == -2:
            l_volumes, r_volumes = np.array([0, 0, 0, 0, 0]), np.array([0, 0, 0, 1, 0])
        elif direction.value == -3:
            l_volumes, r_volumes = np.array([0, 0, 0, 0, 0]), np.array([0, 0, 0, 0, 1])


        for i in range(5):
            shared_music_l_volumes[i], shared_music_r_volumes[i] = l_volumes[i], r_volumes[i]


def start():
    l_volumes, r_volumes = np.array([1, 0, 0, 0, 0]), np.array([0, 0, 0, 1, 0])
    shared_music_l_volumes, shared_music_r_volumes = Array("f", l_volumes), Array("f", r_volumes)
    # デバックモード
    direction = Value('i', 0)

    music_process = Process(target=play_music, args=[shared_music_l_volumes, shared_music_r_volumes])
    speaker_process = Process(target=assign_speaker, args=[shared_music_l_volumes, shared_music_r_volumes, direction])
    music_process.start()
    speaker_process.start()

    while(True):
        kb = readchar.readchar()
        if kb == 'q':
            direction.value = -1
        elif kb == 's':
            direction.value = 0
        elif kb == 'a':
            direction.value = 9
        elif kb == '1':
            direction.value = 1
        elif kb == '2':
            direction.value = 2
        elif kb == '3':
            direction.value = 3
        elif kb == '4':
            direction.value = 4
        elif kb == '5':
            direction.value = 5
        elif kb == 'z':
            direction.value = 6
        elif kb == 'x':
            direction.value = 7
        elif kb == 'c':
            direction.value = 8
        elif kb == 'v':
            direction.value = -2
        elif kb == 'b':
            direction.value = -3
        
if __name__ == '__main__':
    start()
