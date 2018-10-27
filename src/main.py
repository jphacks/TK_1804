import copy
from multiprocessing import Process, Array
import ctypes

import numpy as np
import audioop

from audio.music import Music
from camera.head_vector import HeadVector
from camera.select_speakers import SelectSpeakers

CHUNK_SIZE = 1024

def init_select_speaker():
    face_landmark_path = './src/camera/shape_predictor_68_face_landmarks.dat'

    K = [6.523417721418979909e+02, 0.0, 3.240992613348381610e+02,
        0.0, 6.314784883620466189e+02, 2.369864861289960629e+02,
        0.0, 0.0, 1.0]

    D = [-4.425469845416301617e-01,4.114960065684757362e-01,5.860505097580077059e-03,3.197849383691316570e-03,-3.379210829526543836e-01]

    cam_matrix = np.array(K).reshape(3, 3).astype(np.float32)
    dist_coeffs = np.array(D).reshape(5, 1).astype(np.float32)

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
    music = Music("./src/audio/wav/stereo.wav")
    src_frames = music.wf.readframes(CHUNK_SIZE)

    while src_frames != '':
        # バイト列を取得
        # [L0, R0, L1, R1, L2, R2, ...]
        src_frames = music.wf.readframes(CHUNK_SIZE)
        # L, Rに分割
        l_frames = audioop.tomono(src_frames, music.width, 1, 0)
        r_frames = audioop.tomono(src_frames, music.width, 0, 1)
        music.volumes = [shared_music_l_volumes, shared_music_r_volumes]

        # 顔認識側から受け取る値
        six_ch_frames = music.set_6ch_audio(l_frames, r_frames, music.volumes)

        # 6chオーディオをstreamに渡す
        # [FL0, FR0, CT0, BA0, RL0, RR0, ...]
        music.stream.write(six_ch_frames)

    music.stop()
    return True

def assign_speaker(shared_music_l_volumes, shared_music_r_volumes):
    select_speaker = init_select_speaker()
    before_frames = None
    # 顔認識
    while(True):
        all_flames = select_speaker.estimate_head_orientation(1)
        if all_flames is None:
            if before_frames is None:
                # TODO: ここを決める
                l_volumes, r_volumes = np.array([1, 0, 0, 0, 0]), np.array([0, 0, 0, 1, 0])

            else:
                l_volumes, r_volumes = before_frames[0], before_frames[1]
            all_flames = [l_volumes, r_volumes]
        else:
            l_volumes, r_volumes = all_flames[0], all_flames[1]

        before_frames = copy.deepcopy(all_flames)

        for i in range(5):
            shared_music_l_volumes[i], shared_music_r_volumes[i] = l_volumes[i], r_volumes[i]


if __name__ == '__main__':
    l_volumes, r_volumes = np.array([1, 0, 0, 0, 0]), np.array([0, 0, 0, 1, 0])
    shared_music_l_volumes, shared_music_r_volumes = Array("f", l_volumes), Array("f", r_volumes)

    music_process = Process(target=play_music, args=[shared_music_l_volumes, shared_music_r_volumes])
    speaker_process = Process(target=assign_speaker, args=[shared_music_l_volumes, shared_music_r_volumes])
    music_process.start()
    speaker_process.start()
    music_process.join()
    speaker_process.join()
