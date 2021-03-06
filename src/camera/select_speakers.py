import cv2
import numpy as np
import dlib
from imutils import face_utils

from camera.head_vector import HeadVector
from camera.utils import setting_volumes
from camera.utils import post_face_vector
from time import sleep

class SelectSpeakers:

    def __init__(self, K, D, object_pts, reprojectsrc, line_pairs, face_landmark_path):
        self.cam_matrix = np.array(K).reshape(3, 3).astype(np.float32)
        self.dist_coeffs = np.array(D).reshape(5, 1).astype(np.float32)
        self.object_pts = object_pts
        self.reprojectsrc = reprojectsrc
        self.line_pairs = line_pairs
        self.face_landmark_path = face_landmark_path
        self.cap = cv2.VideoCapture(1)
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(face_landmark_path)

    def get_head_pose(self, shape):
        image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                                shape[39], shape[42], shape[45], shape[31], shape[35],
                                shape[48], shape[54], shape[57], shape[8]])

        _, rotation_vec, translation_vec = cv2.solvePnP(self.object_pts, image_pts, self.cam_matrix, self.dist_coeffs)

        reprojectdst, _ = cv2.projectPoints(self.reprojectsrc, rotation_vec, translation_vec, self.cam_matrix, self.dist_coeffs)

        reprojectdst = tuple(map(tuple, reprojectdst.reshape(8, 2)))

        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        pose_mat = cv2.hconcat((rotation_mat, translation_vec))
        _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)

        return reprojectdst, euler_angle

    def estimate_head_orientation(self, head, head_degree):
        # speakerの設定
        speaker_radians = np.array([0.0, np.deg2rad(60), np.deg2rad(120), np.deg2rad(180), np.deg2rad(270)])

        if not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if not ret:
            return [head_degree.before_volume_r, head_degree.before_volume_l]
        frame = cv2.flip(frame, -1)
        head_rects = self.detector(frame, 0)
        if len(head_rects) > 0:
            shape = self.predictor(frame, head_rects[0])
            shape = face_utils.shape_to_np(shape)

            _, euler_angle = self.get_head_pose(shape)

            for (x, y) in shape:
                    cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
            cv2.putText(frame, "X: " + "{:7.2f}".format(euler_angle[0, 0]), (20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 0, 255), thickness=2)
            cv2.putText(frame, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 0, 255), thickness=2)
            cv2.putText(frame, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), (20, 80), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 0, 255), thickness=2)

            head.rotate(np.deg2rad(euler_angle[0, 0]), np.deg2rad(euler_angle[1, 0]), np.deg2rad(euler_angle[2, 0]))
            #print(euler_angle[0, 0], euler_angle[1, 0], euler_angle[2, 0])
            head.projection()

            right_volume = setting_volumes(speaker_radians, head.right_ear_vector)
            left_volume = setting_volumes(speaker_radians, head.left_ear_vector)

            head_degree.before_degree = euler_angle[1, 0]
            head_degree.before_volume_r = right_volume
            head_degree.before_volume_l = left_volume

            cv2.flip(frame, -1)
            cv2.imshow("demo", frame)
            cv2.waitKey(1)

            return [right_volume, left_volume]
        else:
            cv2.flip(frame, -1)
            cv2.imshow("demo", frame)
            cv2.waitKey(1)

            return head_degree.estimate_camera_none_head_orientation()

