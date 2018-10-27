import numpy as np

def require_ears_angle(ear_theta, speaker_radians1, speaker_radians2):
    comp1 = np.abs(ear_theta - speaker_radians1)
    comp2 = np.abs(ear_theta - speaker_radians2)
    return comp1, comp2

def require_speaker_volumes(comp1, comp2):
    speaker_volume1 = comp2 / (comp1 + comp2)
    speaker_volume2 = comp1 / (comp1 + comp2)
    return speaker_volume1, speaker_volume2

def setting_volumes(speaker_radians, ear_vector):
    speaker_volumes = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    ear_cos = ear_vector[0] / np.sqrt(ear_vector[0] ** 2 + ear_vector[1] ** 2)
    ear_theta = np.arccos(ear_cos)
    if ear_vector[1] < 0:
        ear_theta = 2 * np.pi - ear_theta

    if ear_theta == 0.0:
        speaker_volumes[4] = 1.0
        return speaker_volumes

    elif speaker_radians[0] < ear_theta and ear_theta < speaker_radians[1]:
        comp1, comp2 = require_ears_angle(ear_theta, speaker_radians[0], speaker_radians[1])
        speaker_volumes[0], speaker_volumes[1] = require_speaker_volumes(comp1, comp2)
        return speaker_volumes

    elif ear_theta == speaker_radians[1]:
        speaker_volumes[1] = 1.0
        return speaker_volumes

    elif speaker_radians[1] < ear_theta and ear_theta < speaker_radians[2]:
        comp1, comp2 = require_ears_angle(ear_theta, speaker_radians[1], speaker_radians[2])
        speaker_volumes[1], speaker_volumes[2] = require_speaker_volumes(comp1, comp2)
        return speaker_volumes

    elif ear_theta == speaker_radians[2]:
        speaker_volumes[2] = 1.0
        return speaker_volumes

    elif speaker_radians[2] < ear_theta and ear_theta < speaker_radians[3]:
        comp1, comp2 = require_ears_angle(ear_theta, speaker_radians[2], speaker_radians[3])
        speaker_volumes[2], speaker_volumes[3] = require_speaker_volumes(comp1, comp2)
        return speaker_volumes

    elif ear_theta == speaker_radians[3]:
        speaker_volumes[3] = 1.0
        return speaker_volumes

    elif speaker_radians[3] < ear_theta and ear_theta < speaker_radians[4]:
        comp1 = np.deg2rad(180)
        comp2 = np.deg2rad(270)
        comp1 = abs(ear_theta - comp1)
        comp2 = abs(ear_theta - comp2)
        speaker_volumes[3] = comp2 / (comp1 + comp2)
        speaker_volumes[4] = comp1 / (comp1 + comp2)
        return speaker_volumes

    elif ear_theta == speaker_radians[4]:
        speaker_volumes[4] = 1.0
        return speaker_volumes

    elif speaker_radians[4] < ear_theta and ear_theta < np.deg2rad(360):
        comp1 = np.deg2rad(270)
        comp2 = np.deg2rad(360)
        comp1 = np.abs(ear_theta - comp1)
        comp2 = np.abs(ear_theta - comp2)
        speaker_volumes[0] = comp1 / (comp1 + comp2)
        speaker_volumes[4] = comp2 / (comp1 + comp2)
        return speaker_volumes
