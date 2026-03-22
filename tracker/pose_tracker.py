import cv2
from utils.angle_math import AngleMath

class PoseTracker:

    def __init__(self):
        self.max_shoulder = 0
        self.max_elbow = 0

        self.prev_left_elbow = None
        self.prev_right_elbow = None
        self.prev_left_shoulder = None
        self.prev_right_shoulder = None

    def process_left_side(self, frame, landmarks, w, h):

        shoulder_angle = AngleMath.calculate_angle(landmarks[23], landmarks[11], landmarks[13], w, h)
        elbow_angle = AngleMath.calculate_elbow_angle(landmarks[11], landmarks[13], landmarks[15], w, h)

        shoulder_angle = AngleMath.smooth_angle(self.prev_left_shoulder, shoulder_angle)
        elbow_angle = AngleMath.smooth_angle(self.prev_left_elbow, elbow_angle)

        self.prev_left_shoulder = shoulder_angle
        self.prev_left_elbow = elbow_angle

        if shoulder_angle > self.max_shoulder:
            self.max_shoulder = shoulder_angle

        if elbow_angle > self.max_elbow:
            self.max_elbow = elbow_angle

        cv2.putText(frame,f"L Shoulder: {int(shoulder_angle)}",(20,40),
        cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)

        cv2.putText(frame,f"L Elbow: {int(elbow_angle)}",(20,70),
        cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)

    def process_right_side(self, frame, landmarks, w, h):

        shoulder_angle = AngleMath.calculate_angle(landmarks[24], landmarks[12], landmarks[14], w, h)
        elbow_angle = AngleMath.calculate_elbow_angle(landmarks[12], landmarks[14], landmarks[16], w, h)

        shoulder_angle = AngleMath.smooth_angle(self.prev_right_shoulder, shoulder_angle)
        elbow_angle = AngleMath.smooth_angle(self.prev_right_elbow, elbow_angle)

        self.prev_right_shoulder = shoulder_angle
        self.prev_right_elbow = elbow_angle

        if shoulder_angle > self.max_shoulder:
            self.max_shoulder = shoulder_angle

        if elbow_angle > self.max_elbow:
            self.max_elbow = elbow_angle

        cv2.putText(frame,f"R Shoulder: {int(shoulder_angle)}",(w-220,40),
        cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)

        cv2.putText(frame,f"R Elbow: {int(elbow_angle)}",(w-220,70),
        cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)