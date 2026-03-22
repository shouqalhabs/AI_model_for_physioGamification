import cv2
from utils.angle_math import AngleMath

class HandTracker:

    def __init__(self):
        self.max_grip = 0

        self.current_hand_landmarks = None   # ✅ NEW
        self.current_grip = 0                # ✅ NEW

        self.HAND_CONNECTIONS = [
        (0,1),(1,2),(2,3),(3,4),
        (0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),
        (0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20)
        ]

    def draw_connections(self, frame, landmarks, w, h):
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

                self.current_hand_landmarks = hand_landmarks  # ✅ NEW

                self.draw_connections(frame, hand_landmarks, w, h)

                index_angle = AngleMath.calculate_angle(hand_landmarks[0], hand_landmarks[5], hand_landmarks[8], w, h)
                middle_angle = AngleMath.calculate_angle(hand_landmarks[0], hand_landmarks[9], hand_landmarks[12], w, h)
                ring_angle = AngleMath.calculate_angle(hand_landmarks[0], hand_landmarks[13], hand_landmarks[16], w, h)
                pinky_angle = AngleMath.calculate_angle(hand_landmarks[0], hand_landmarks[17], hand_landmarks[20], w, h)

                avg_angle = (index_angle + middle_angle + ring_angle + pinky_angle) / 4

                open_percentage = int(((avg_angle - 60) / (180 - 60)) * 100)
                open_percentage = max(0, min(100, open_percentage))
                closed_percentage = 100 - open_percentage

                self.current_grip = closed_percentage  # ✅ NEW

                if closed_percentage > self.max_grip:
                    self.max_grip = closed_percentage

                text_x = 30 if hand_type == 'left' else w-200

                cv2.putText(frame,f"Open: {open_percentage}%",(text_x,120),
                cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,255,0),2)

                cv2.putText(frame,f"Closed: {closed_percentage}%",(text_x,160),
                cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,0,255),2)