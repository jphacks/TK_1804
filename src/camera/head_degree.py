import numpy as np
class HeadDegree:
    def __init__(self):
        self.before_degree = 0
        self.low_threshold = 30
        self.heigh_threshold = 60

    def estimate_camera_none_head_orientation(self):
        right_volume = np.array(np.array([0.0, 0.0, 0.0, 0.0, 0.0]))
        left_volume = np.array(np.array([0.0, 0.0, 0.0, 0.0, 0.0]))

        if self.before_degree > self.heigh_threshold:
            left_volume[1] = 0.5
            left_volume[2] = 0.5
            right_volume[4] = 1.0

        elif self.before_degree > self.low_threshold:
            left_volume[1] = 0.7
            left_volume[2] = 0.3
            right_volume[3] = 0.3
            right_volume[4] = 0.7

        elif self.before_degree < self.heigh_threshold * -1:
            left_volume[4] = 1.0
            right_volume[1] = 0.5
            right_volume[2] = 0.5

        elif self.before_degree < self.low_threshold * -1:
            left_volume[0] = 0.3
            left_volume[4] = 0.7
            right_volume[1] = 0.3
            right_volume[2] = 0.7

        return [right_volume, left_volume]
