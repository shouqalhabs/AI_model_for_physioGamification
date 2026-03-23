import cv2
from utils.angle_math import AngleMath

class PoseTracker:

    def __init__(self):
        # Previous smoothed values
        self.prev = {
            "shoulder": None,
            "elbow": None,
            "wrist": None
        }

        # Current values
        self.current = {
            "shoulder": 0,
            "elbow": 0,
            "wrist": 0
        }

        # Range of Motion tracking
        self.rom_min = {
            "shoulder": 999,
            "elbow": 999,
            "wrist": 999
        }

        self.rom_max = {
            "shoulder": 0,
            "elbow": 0,
            "wrist": 0
        }

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
        # إزالة القفزات
        # -----------------------------
        shoulder_angle = AngleMath.remove_spikes(self.prev["shoulder"], shoulder_angle)
        elbow_angle = AngleMath.remove_spikes(self.prev["elbow"], elbow_angle)
        wrist_angle = AngleMath.remove_spikes(self.prev["wrist"], wrist_angle)

        # -----------------------------
        # سرعة التغير
        # -----------------------------
        vel_s = 0 if self.prev["shoulder"] is None else abs(shoulder_angle - self.prev["shoulder"])
        vel_e = 0 if self.prev["elbow"] is None else abs(elbow_angle - self.prev["elbow"])
        vel_w = 0 if self.prev["wrist"] is None else abs(wrist_angle - self.prev["wrist"])

        # -----------------------------
        # تنعيم متكيف
        # -----------------------------
        shoulder_angle = AngleMath.smooth_angle(self.prev["shoulder"], shoulder_angle, vel_s)
        elbow_angle = AngleMath.smooth_angle(self.prev["elbow"], elbow_angle, vel_e)
        wrist_angle = AngleMath.smooth_angle(self.prev["wrist"], wrist_angle, vel_w)

        # حفظ السابق
        self.prev["shoulder"] = shoulder_angle
        self.prev["elbow"] = elbow_angle
        self.prev["wrist"] = wrist_angle

        # حفظ الحالي
        self.current["shoulder"] = shoulder_angle
        self.current["elbow"] = elbow_angle
        self.current["wrist"] = wrist_angle

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

        return True
