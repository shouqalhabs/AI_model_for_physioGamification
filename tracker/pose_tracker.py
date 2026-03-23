import cv2
from utils.angle_math import AngleMath

class PoseTracker:

    def __init__(self):
        self.max_shoulder = 0
        self.max_elbow = 0

        self.current_shoulder = 0  
        self.current_elbow = 0  

        self.prev_left_elbow = None
        self.prev_right_elbow = None
        self.prev_left_shoulder = None
        self.prev_right_shoulder = None
    
    def draw_connections(self, frame, landmarks, w, h):

        connections = [
            (11, 13), (13, 15),   # left arm
            (12, 14), (14, 16),   # right arm
            (11, 12),             # shoulders
            (11, 23), (12, 24),   # torso sides
            (23, 24)              # hips
        ]

        for start_idx, end_idx in connections:
            start = landmarks[start_idx]
            end = landmarks[end_idx]

            x1, y1 = int(start.x * w), int(start.y * h)
            x2, y2 = int(end.x * w), int(end.y * h)

            cv2.line(frame, (x1, y1), (x2, y2), (0,255,0), 3)

        key_points = [11,12,13,14,15,16,23,24]

        for idx in key_points:
            lm = landmarks[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 6, (0,0,255), -1)

    def process_left_side(self, frame, landmarks, w, h):

        self.draw_connections(frame, landmarks, w, h)

        shoulder_angle = AngleMath.calculate_angle(landmarks[23], landmarks[11], landmarks[13], w, h)
        elbow_angle = AngleMath.calculate_elbow_angle(landmarks[11], landmarks[13], landmarks[15], w, h)

        shoulder_angle = AngleMath.smooth_angle(self.prev_left_shoulder, shoulder_angle)
        elbow_angle = AngleMath.smooth_angle(self.prev_left_elbow, elbow_angle)

        self.prev_left_shoulder = shoulder_angle
        self.prev_left_elbow = elbow_angle

        self.current_shoulder = shoulder_angle
        self.current_elbow = elbow_angle      

        if shoulder_angle > self.max_shoulder:
            self.max_shoulder = shoulder_angle

        if elbow_angle > self.max_elbow:
            self.max_elbow = elbow_angle

        cv2.putText(frame,f"L Shoulder: {int(shoulder_angle)}",(20,40),
        cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)

        cv2.putText(frame,f"L Elbow: {int(elbow_angle)}",(20,70),
        cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)


    def process_right_side(self, frame, landmarks, w, h):

        self.draw_connections(frame, landmarks, w, h)

        shoulder_angle = AngleMath.calculate_angle(landmarks[24], landmarks[12], landmarks[14], w, h)
        elbow_angle = AngleMath.calculate_elbow_angle(landmarks[12], landmarks[14], landmarks[16], w, h)

        shoulder_angle = AngleMath.smooth_angle(self.prev_right_shoulder, shoulder_angle)
        elbow_angle = AngleMath.smooth_angle(self.prev_right_elbow, elbow_angle)

        self.prev_right_shoulder = shoulder_angle
        self.prev_right_elbow = elbow_angle

        self.current_shoulder = shoulder_angle  
        self.current_elbow = elbow_angle   

        if shoulder_angle > self.max_shoulder:
            self.max_shoulder = shoulder_angle

        if elbow_angle > self.max_elbow:
            self.max_elbow = elbow_angle

        cv2.putText(frame,f"R Shoulder: {int(shoulder_angle)}",(w-220,40),
        cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)

        cv2.putText(frame,f"R Elbow: {int(elbow_angle)}",(w-220,70),
        cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)


import cv2
from utils.angle_math import AngleMath

class PoseTracker:

    def __init__(self):
        self.prev_shoulder = None
        self.prev_elbow = None

        self.current_shoulder = 0
        self.current_elbow = 0

        # 🎯 Range of Motion
        self.min_elbow = 999
        self.max_elbow = 0

        self.min_shoulder = 999
        self.max_shoulder = 0

    def is_visible(self, landmark, threshold=0.5):
        return landmark.visibility > threshold

    def valid_angle(self, angle):
        return 10 < angle < 170

    def process(self, frame, landmarks, w, h, side="left"):

        if side == "left":
            ids = (23,11,13,15)
        else:
            ids = (24,12,14,16)

        # 📊 Confidence check
        if not all(self.is_visible(landmarks[i]) for i in ids):
            cv2.putText(frame, "Low Confidence",
                        (20,120), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0,0,255), 2)
            return False

        shoulder = AngleMath.calculate_angle(landmarks[ids[0]], landmarks[ids[1]], landmarks[ids[2]], w, h)
        elbow = AngleMath.calculate_angle(landmarks[ids[1]], landmarks[ids[2]], landmarks[ids[3]], w, h)

        # إزالة القفزات
        shoulder = AngleMath.remove_spikes(self.prev_shoulder, shoulder)
        elbow = AngleMath.remove_spikes(self.prev_elbow, elbow)

        # سرعة التغير
        vel_s = 0 if self.prev_shoulder is None else abs(shoulder - self.prev_shoulder)
        vel_e = 0 if self.prev_elbow is None else abs(elbow - self.prev_elbow)

        # 🧠 Adaptive smoothing
        shoulder = AngleMath.smooth_angle(self.prev_shoulder, shoulder, vel_s)
        elbow = AngleMath.smooth_angle(self.prev_elbow, elbow, vel_e)

        self.prev_shoulder = shoulder
        self.prev_elbow = elbow

        if not self.valid_angle(elbow):
            return False

        self.current_shoulder = shoulder
        self.current_elbow = elbow

        # 🎯 ROM tracking
        self.min_elbow = min(self.min_elbow, elbow)
        self.max_elbow = max(self.max_elbow, elbow)

        self.min_shoulder = min(self.min_shoulder, shoulder)
        self.max_shoulder = max(self.max_shoulder, shoulder)

        # 🏥 Clinical feedback
        self.target_min = 30   # حسب حالة المريض
        self.target_max = 100  # قابل للتعديل

        if elbow < self.target_min:
            status = "Good extension"
        elif elbow > self.target_max:
            status = "Good flexion"
        else:
            status = "In range"

        # 📊 Display
        cv2.putText(frame, f"Elbow: {int(elbow)}",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0),2)

        cv2.putText(frame, f"ROM: {int(self.min_elbow)}-{int(self.max_elbow)}",
                    (20,70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255),2)

        cv2.putText(frame, f"Status: {status}",
                    (20,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0),2)

        return True