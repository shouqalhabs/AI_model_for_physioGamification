import time
import numpy as np
import cv2
from utils.angle_math import AngleMath


class PoseTracker:

    def __init__(self):

        self.prev = {
            "shoulder": None,
            "elbow": None,
            "wrist": None,
            "shoulder_external_rotation": None,
            "shoulder_internal_rotation": None,
            "shoulder_rotation": None
        }

        self.current = {
            "shoulder": 0,
            "elbow": 0,
            "wrist": 0,
            "shoulder_external_rotation": 0,
            "shoulder_internal_rotation": 0,
            "shoulder_rotation": 0
        }

        self.rom_min = {k: 999 for k in self.current}
        self.rom_max = {k: 0 for k in self.current}

        # =============================
        # CALIBRATION (CONTROLLED EXTERNALLY)
        # =============================

        self.calibration_started = False
        self.calibration_done = False
        self.calibration_start_time = None
        self.calibration_duration = 2
        self.calibration_samples = []
        self.ref_vector = None

    # =============================
    # EXTERNAL CONTROL
    # =============================

    def start_calibration(self):
        self.calibration_started = True
        self.calibration_done = False
        self.calibration_start_time = time.time()
        self.calibration_samples = []
        self.ref_vector = None

    # =============================
    # PROCESS
    # =============================

    def process(self, frame, landmarks, w, h, side="left", calculate=["all"]):

        if side == "left":
            hip_id, shoulder_id, elbow_id, wrist_id = 23, 11, 13, 15
        else:
            hip_id, shoulder_id, elbow_id, wrist_id = 24, 12, 14, 16

        # =============================
        # VISIBILITY CHECK
        # =============================

        if not all(lm.visibility > 0.5 for lm in [landmarks[hip_id],
                                                   landmarks[shoulder_id],
                                                   landmarks[elbow_id],
                                                   landmarks[wrist_id]]):
            return False

        # =============================
        # ANGLES
        # =============================

        shoulder_angle = self.current["shoulder"]
        elbow_angle = self.current["elbow"]
        wrist_angle = self.current["wrist"]

        if "all" in calculate or "shoulder" in calculate:
            shoulder_angle = AngleMath.calculate_angle(
                landmarks[hip_id], landmarks[shoulder_id], landmarks[elbow_id]
            )

        if "all" in calculate or "elbow" in calculate:
            elbow_angle = AngleMath.calculate_elbow_angle(
                landmarks[shoulder_id], landmarks[elbow_id], landmarks[wrist_id], w, h
            )

        if "all" in calculate or "wrist" in calculate:
            wrist_angle = AngleMath.calculate_angle(
                landmarks[elbow_id], landmarks[wrist_id], landmarks[9]
            )

        # =============================
        # CALIBRATION (ONLY IF STARTED)
        # =============================

        shoulder_xyz = np.array([landmarks[shoulder_id].x,
                                 landmarks[shoulder_id].y,
                                 landmarks[shoulder_id].z])

        wrist_xyz = np.array([landmarks[wrist_id].x,
                              landmarks[wrist_id].y,
                              landmarks[wrist_id].z])

        elbow_xyz = np.array([landmarks[elbow_id].x,
                              landmarks[elbow_id].y,
                              landmarks[elbow_id].z])

        if self.calibration_started and not self.calibration_done:

            elapsed = time.time() - self.calibration_start_time

            if elapsed < self.calibration_duration:
                vec = wrist_xyz - shoulder_xyz
                self.calibration_samples.append(vec)
                return True

            else:
                self.ref_vector = np.mean(self.calibration_samples, axis=0)
                self.calibration_done = True
                self.calibration_started = False

        # =============================
        # ROTATIONS
        # =============================

        shoulder_rotation = self.current["shoulder_rotation"]
        shoulder_external_rotation = self.current["shoulder_external_rotation"]
        shoulder_internal_rotation = self.current["shoulder_internal_rotation"]

        if self.calibration_done:

            if "all" in calculate or "shoulder_rotation" in calculate:
                shoulder_rotation = AngleMath.calculate_signed_rotation(
                    shoulder_xyz, elbow_xyz, wrist_xyz, self.ref_vector
                )

            if "all" in calculate or "shoulder_external_rotation" in calculate:
                shoulder_external_rotation = AngleMath.calculate_external_rotation(
                    shoulder_xyz, elbow_xyz, wrist_xyz, self.ref_vector
                )

            if "all" in calculate or "shoulder_internal_rotation" in calculate:
                shoulder_internal_rotation = AngleMath.calculate_internal_rotation(
                    shoulder_xyz, elbow_xyz, wrist_xyz, self.ref_vector
                )

        # =============================
        # SMOOTHING
        # =============================

        shoulder_angle = AngleMath.remove_spikes(self.prev["shoulder"], shoulder_angle)
        elbow_angle = AngleMath.remove_spikes(self.prev["elbow"], elbow_angle)
        wrist_angle = AngleMath.remove_spikes(self.prev["wrist"], wrist_angle)

        shoulder_rotation = AngleMath.remove_spikes(self.prev["shoulder_rotation"], shoulder_rotation)
        shoulder_external_rotation = AngleMath.remove_spikes(self.prev["shoulder_external_rotation"], shoulder_external_rotation)
        shoulder_internal_rotation = AngleMath.remove_spikes(self.prev["shoulder_internal_rotation"], shoulder_internal_rotation)

        # =============================
        # SAVE
        # =============================

        self.prev.update({
            "shoulder": shoulder_angle,
            "elbow": elbow_angle,
            "wrist": wrist_angle,
            "shoulder_rotation": shoulder_rotation,
            "shoulder_external_rotation": shoulder_external_rotation,
            "shoulder_internal_rotation": shoulder_internal_rotation
        })

        self.current.update(self.prev)

        # =============================
        # ROM TRACKING
        # =============================

        for k, v in self.current.items():
            self.rom_min[k] = min(self.rom_min[k], v)
            self.rom_max[k] = max(self.rom_max[k], v)

        return True