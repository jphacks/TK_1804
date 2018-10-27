import cv2
import numpy as np

class HeadVector:

    def __init__(self):
        self.face_vector = np.array([0, 0, 1])
        self.right_ear_vector = np.array([1, 0, 0])
        self.left_ear_vector = np.array([-1, 0, 0])


    def rotate(self, change_angel_x, change_angel_y, change_angel_z):
        """
        変化後の絶対座標からアングルを出す
        """
        # x軸回転
        rotation_x_matrix = np.array([[np.cos(change_angel_x), 0, np.sin(change_angel_x)], [0, 1, 0], [-np.sin(change_angel_x), 0, np.cos(change_angel_x)]])
        self.face_vector = np.dot(rotation_x_matrix, self.face_vector)
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
        self.face_vector = np.array([self.face_vector[0], self.face_vector[2]]) * parametor
        self.right_ear_vector = np.array([self.face_vector[1], -1 * self.face_vector[0]])
        self.left_ear_vector = np.array([-1 * self.face_vector[1], self.face_vector[0]])