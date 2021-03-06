import numpy as np
from head_vector import HeadVector
from select_speakers import SelectSpeakers

if __name__ == '__main__':
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

    while(True):
        print(select_speaker.estimate_head_orientation(1))
