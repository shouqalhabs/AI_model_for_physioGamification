import time
import numpy as np
import cv2
from utils.angle_math import AngleMath

class PoseTracker:

    def __init__(self):
        # Previous smoothed values
        self.prev = {
            "shoulder": None,
            "elbow": None,
            "wrist": None,
            "shoulder_external_rotation": None,
            "shoulder_internal_rotation": None
        }

        # Current values
        self.current = {
            "shoulder": 0,
            "elbow": 0,
            "wrist": 0,
            "shoulder_external_rotation": 0,
            "shoulder_internal_rotation": 0
        }

        # Range of Motion tracking
        self.rom_min = {
            "shoulder": 999,
            "elbow": 999,
            "wrist": 999,
            "shoulder_external_rotation": 999,
            "shoulder_internal_rotation": 999
        }

        self.rom_max = {
            "shoulder": 0,
            "elbow": 0,
            "wrist": 0,
            "shoulder_external_rotation": 0,
            "shoulder_internal_rotation": 0
        }
        # Calibration
        self.calibration_started = False
        self.calibration_done = False
        self.calibration_start_time = None
        self.calibration_delay = 5        # ننتظر 5 ثواني قبل البدء
        self.calibration_duration = 2     # نعاير لمدة ثانيتين
        self.calibration_samples = []
        self.ref_vector = None
        self.global_start_time = time.time()

    def is_visible(self, lm, threshold=0.5):
        return lm.visibility > threshold

    # -----------------------------
    # رسم النقاط والخطوط
    # -----------------------------
    def draw_pose(self, frame, landmarks, w, h, side):
        if side == "left":
            shoulder_id, elbow_id, wrist_id, hip_id = 11, 13, 15, 23
        else:
            shoulder_id, elbow_id, wrist_id, hip_id = 12, 14, 16, 24

        # خطوط
        connections = [
            (shoulder_id, elbow_id),
            (elbow_id, wrist_id),
            (hip_id, shoulder_id)
        ]

        for s, e in connections:
            sx, sy = int(landmarks[s].x * w), int(landmarks[s].y * h)
            ex, ey = int(landmarks[e].x * w), int(landmarks[e].y * h)
            cv2.line(frame, (sx, sy), (ex, ey), (0,255,0), 3)

        # نقاط
        for idx in [shoulder_id, elbow_id, wrist_id, hip_id]:
            x, y = int(landmarks[idx].x * w), int(landmarks[idx].y * h)
            cv2.circle(frame, (x, y), 7, (0,0,255), -1)

    # -----------------------------
    # المعالجة الأساسية
    # -----------------------------
    def process(self, frame, landmarks, w, h, side="left"):

        if side == "left":
            hip_id, shoulder_id, elbow_id, wrist_id = 23, 11, 13, 15
        else:
            hip_id, shoulder_id, elbow_id, wrist_id = 24, 12, 14, 16

        # Visibility check
        if not all(self.is_visible(landmarks[i]) for i in [hip_id, shoulder_id, elbow_id, wrist_id]):
            cv2.putText(frame, "Low Confidence", (20,120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            return False

        # -----------------------------
        # حساب الزوايا (3D)
        # -----------------------------
        shoulder_angle = AngleMath.calculate_angle(
            landmarks[hip_id], landmarks[shoulder_id], landmarks[elbow_id]
        )

        elbow_angle = AngleMath.calculate_elbow_angle(
            landmarks[shoulder_id], landmarks[elbow_id], landmarks[wrist_id], w, h
        )

        wrist_angle = AngleMath.calculate_angle(
            landmarks[elbow_id], landmarks[wrist_id], landmarks[9]  # MCP الوسطى
        )

        
        # -----------------------------
        # Calibration (shoulder-wrist baseline)
        # -----------------------------
        shoulder_xyz = np.array([landmarks[shoulder_id].x,
                                landmarks[shoulder_id].y,
                                landmarks[shoulder_id].z])

        wrist_xyz = np.array([landmarks[wrist_id].x,
                            landmarks[wrist_id].y,
                            landmarks[wrist_id].z])

        now = time.time()
        remaining = 0
        # 1) ننتظر 5 ثواني قبل بدء المعايرة
        if not self.calibration_started and not self.calibration_done:
            #if now - self.global_start_time >= self.calibration_delay:
            remaining = int(self.calibration_delay - (now - self.global_start_time))
        if remaining > 0:
            cv2.putText(frame, f"Calibration starts in: {remaining}",
                        (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
        # لا نبدأ حساب الدوران قبل انتهاء العدّاد
            return True
        else:
                self.calibration_started = True
                self.calibration_start_time = now

        # 2) أثناء المعايرة (لمدة 2 ثانية)
        if self.calibration_started and not self.calibration_done:
            #if now - self.calibration_start_time <= self.calibration_duration:
            elapsed = now - self.calibration_start_time
            remaining = int(self.calibration_duration - elapsed)

            if remaining >= 0:
                cv2.putText(frame, f"Calibrating... {remaining}",
                        (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                vec = wrist_xyz - shoulder_xyz
                self.calibration_samples.append(vec)
            else:
                # 3) انتهت المعايرة → نحسب المتوسط
                if len(self.calibration_samples) > 0:
                    self.ref_vector = np.mean(self.calibration_samples, axis=0)
                self.calibration_done = True
                self.calibration_started = False

        shoulder_external_rotation = AngleMath.calculate_external_rotation(
            shoulder_xyz, wrist_xyz, self.ref_vector
        )

        shoulder_internal_rotation = AngleMath.calculate_internal_rotation(
            shoulder_xyz, wrist_xyz, self.ref_vector
        )

        # -----------------------------
        # إزالة القفزات
        # -----------------------------
        shoulder_angle = AngleMath.remove_spikes(self.prev["shoulder"], shoulder_angle)
        elbow_angle = AngleMath.remove_spikes(self.prev["elbow"], elbow_angle)
        wrist_angle = AngleMath.remove_spikes(self.prev["wrist"], wrist_angle)
        shoulder_external_rotation = AngleMath.remove_spikes(self.prev["shoulder_external_rotation"], shoulder_external_rotation)
        shoulder_internal_rotation = AngleMath.remove_spikes(self.prev["shoulder_internal_rotation"], shoulder_internal_rotation)

        # -----------------------------
        # سرعة التغير
        # -----------------------------
        vel_s = 0 if self.prev["shoulder"] is None else abs(shoulder_angle - self.prev["shoulder"])
        vel_e = 0 if self.prev["elbow"] is None else abs(elbow_angle - self.prev["elbow"])
        vel_w = 0 if self.prev["wrist"] is None else abs(wrist_angle - self.prev["wrist"])
        vel_ser = 0 if self.prev["shoulder_external_rotation"] is None else abs(shoulder_external_rotation - self.prev["shoulder_external_rotation"])
        vel_sir = 0 if self.prev["shoulder_internal_rotation"] is None else abs(shoulder_internal_rotation - self.prev["shoulder_internal_rotation"])
        # -----------------------------
        # تنعيم متكيف
        # -----------------------------
        shoulder_angle = AngleMath.smooth_angle(self.prev["shoulder"], shoulder_angle, vel_s)
        elbow_angle = AngleMath.smooth_angle(self.prev["elbow"], elbow_angle, vel_e)
        wrist_angle = AngleMath.smooth_angle(self.prev["wrist"], wrist_angle, vel_w)
        shoulder_external_rotation = AngleMath.smooth_angle(self.prev["shoulder_external_rotation"], shoulder_external_rotation, vel_ser)
        shoulder_internal_rotation = AngleMath.smooth_angle(self.prev["shoulder_internal_rotation"], shoulder_internal_rotation, vel_sir)
        # حفظ السابق
        self.prev["shoulder"] = shoulder_angle
        self.prev["elbow"] = elbow_angle
        self.prev["wrist"] = wrist_angle
        self.prev["shoulder_external_rotation"] = shoulder_external_rotation
        self.prev["shoulder_internal_rotation"] = shoulder_internal_rotation
        # حفظ الحالي
        self.current["shoulder"] = shoulder_angle
        self.current["elbow"] = elbow_angle
        self.current["wrist"] = wrist_angle
        self.current["shoulder_external_rotation"] = shoulder_external_rotation
        self.current["shoulder_internal_rotation"] = shoulder_internal_rotation
        # -----------------------------
        # ROM tracking
        # -----------------------------
        for joint, angle in self.current.items():
            self.rom_min[joint] = min(self.rom_min[joint], angle)
            self.rom_max[joint] = max(self.rom_max[joint], angle)

        # -----------------------------
        # رسم الهيكل
        # -----------------------------
        self.draw_pose(frame, landmarks, w, h, side)

        # -----------------------------
        # عرض القيم
        # -----------------------------
        cv2.putText(frame, f"{side.capitalize()} Shoulder: {int(shoulder_angle)}",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0),2)

        cv2.putText(frame, f"{side.capitalize()} Elbow: {int(elbow_angle)}",
                    (20,70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0),2)

        cv2.putText(frame, f"{side.capitalize()} Wrist: {int(wrist_angle)}",
                    (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0),2)
        
        cv2.putText(frame, f"{side.capitalize()} Shoulder Ext Rot: {int(shoulder_external_rotation)}",
                    (20,130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0),2)
        
        cv2.putText(frame, f"{side.capitalize()} Shoulder Int Rot: {int(shoulder_internal_rotation)}",
                    (20,160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0),2)

        return True
