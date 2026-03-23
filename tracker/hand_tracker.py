import cv2
from utils.angle_math import AngleMath

class HandTracker:

    def __init__(self):

        self.current_hand_landmarks = None
        self.current_grip = 0     

        self.finger_angles = {
            "thumb":  None,
            "index":  None,
            "middle": None,
            "ring":   None,
            "pinky":  None
        } ## none cuz we didn't calculate them yet, in db should be none not 0, to distinguish between not calculated and fully extended, later we change with baseline values for each patient

        self.max_finger_angles = {
            "thumb": 0,
            "index": 0,
            "middle": 0,
            "ring": 0,
            "pinky": 0
        }
        
        self.HAND_CONNECTIONS = [
        (0,1),(1,2),(2,3),(3,4),
        (0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),
        (0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20)
        ]

    def draw_connections(self, frame, landmarks, w, h): ## to be removed when launching the game, only for debugging
        for start_idx, end_idx in self.HAND_CONNECTIONS:

            start = landmarks[start_idx]
            end = landmarks[end_idx]

            x1, y1 = int(start.x * w), int(start.y * h)
            x2, y2 = int(end.x * w), int(end.y * h)

            cv2.line(frame, (x1, y1), (x2, y2), (255,200,0), 4)

        for lm in landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 6, (0,0,255), -1)

    def process(self, hand_type, frame, w, h, mp_image, timestamp_ms, hand_landmarker):

        hand_result = hand_landmarker.detect_for_video(mp_image, timestamp_ms)

        if hand_result.hand_landmarks and hand_result.handedness:

            for i in range(len(hand_result.hand_landmarks)):

                hand_landmarks = hand_result.hand_landmarks[i]
                hand_label = hand_result.handedness[i][0].category_name.lower()

                if hand_label != hand_type:
                    continue

                self.current_hand_landmarks = hand_landmarks  

                self.draw_connections(frame, hand_landmarks, w, h) ## to be removed when launching the game, only for debugging

                raw_angles = {
                "thumb":  AngleMath.calculate_angle(hand_landmarks[0], hand_landmarks[1], hand_landmarks[4]),
                "index":  AngleMath.calculate_angle(hand_landmarks[0], hand_landmarks[5], hand_landmarks[8]),
                "middle": AngleMath.calculate_angle(hand_landmarks[0], hand_landmarks[9], hand_landmarks[12]),
                "ring":   AngleMath.calculate_angle(hand_landmarks[0], hand_landmarks[13], hand_landmarks[16]),
                "pinky":  AngleMath.calculate_angle(hand_landmarks[0], hand_landmarks[17], hand_landmarks[20])
                }

                # تنعيم + إزالة spikes لكل إصبع
                for finger, current_angle in raw_angles.items():

                    prev_angle = self.finger_angles[finger]

                    # إزالة القفزات المفاجئة
                    cleaned = AngleMath.remove_spikes(prev_angle, current_angle)

                    # حساب سرعة التغير
                    velocity = 0 if prev_angle is None else abs(cleaned - prev_angle)

                    # تنعيم الزاوية
                    smoothed = AngleMath.smooth_angle(prev_angle, cleaned, velocity)

                    # حفظ النتيجة
                    self.finger_angles[finger] = smoothed

                for finger, angle in self.finger_angles.items():
                    if angle is not None:
                        self.max_finger_angles[finger] = max(self.max_finger_angles[finger], angle)

                # عرض الزوايا (للتقييم)
                y = 120
                for finger, angle in self.finger_angles.items():
                    if angle is not None:
                        cv2.putText(frame, f"{finger}: {int(angle)}°", (30, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                    y += 30
                