import cv2
import numpy as np
import copy as cp
from camera.utils import get_diff_theta
from camera.utils import post_face_vector
import time

class HeadVector:

    def __init__(self):
        self.base_vector = np.array([0, 0, 1])
        self.face_vector = np.array([0, 0, 1])
        self.current_face_vector = np.array([0, 1])
        self.before_face_vector = np.array([0, 1])
        self.right_ear_vector = np.array([1, 0, 0])
        self.left_ear_vector = np.array([-1, 0, 0])
        self.high_threthold = np.deg2rad(20)
        self.low_threthold = np.deg2rad(3)


    def rotate(self, change_angel_x, change_angel_y, change_angel_z):
        """
        変化後の絶対座標からアングルを出す
        """
        # x軸回転
        rotation_x_matrix = np.array([[np.cos(change_angel_x), 0, np.sin(change_angel_x)], [0, 1, 0], [-np.sin(change_angel_x), 0, np.cos(change_angel_x)]])
        self.face_vector = np.dot(rotation_x_matrix, self.base_vector)
        # y軸回転
        rotation_y_matrix = np.array([[1, 0, 0], [0, np.cos(change_angel_y), -np.sin(change_angel_y)], [0, np.sin(change_angel_y), np.cos(change_angel_y)]])
        self.face_vector = np.dot(rotation_y_matrix, self.face_vector)
        # z軸回転
        rotation_z_matrix = np.array([[np.cos(change_angel_z), -np.sin(change_angel_z), 0], [np.sin(change_angel_z), np.cos(change_angel_z), 0], [0, 0, 1]])
        self.face_vector = np.dot(rotation_z_matrix, self.face_vector)


    def vector_size(self):
        return np.sqrt(self.face_vector[0] ** 2 + self.face_vector[1] ** 2 + self.face_vector[2] ** 2)

    def projection(self):
        parametor = np.sqrt((1 - self.face_vector[1]/self.vector_size()) ** 2)
        self.current_face_vector = np.array([self.face_vector[0], self.face_vector[2]]) * parametor
        theta = get_diff_theta(self.before_face_vector, self.current_face_vector)
        if np.abs(theta) >= self.high_threthold:
            theta = self.high_threthold
            if self.before_face_vector[0] < self.current_face_vector[0]:
                theta *= -1
            self.current_face_vector[0] = self.before_face_vector[0] * np.cos(theta) - self.before_face_vector[1] * np.sin(theta)
            self.current_face_vector[1] = self.before_face_vector[0] * np.sin(theta) + self.before_face_vector[1] * np.cos(theta)
        elif np.abs(theta) < self.low_threthold:
            self.current_face_vector = cp.deepcopy(self.before_face_vector)

        self.before_face_vector = cp.deepcopy(self.current_face_vector)
        
        self.right_ear_vector = np.array([self.current_face_vector[1], -1 * self.current_face_vector[0]])
        self.left_ear_vector = np.array([-1 * self.current_face_vector[1], self.current_face_vector[0]])

        print(self.current_face_vector)

        post_face_vector('127.0.0.1', 10001, [self.face_vector[1], 0 , self.face_vector[2]])

