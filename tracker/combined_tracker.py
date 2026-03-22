import cv2
import mediapipe as mp
import time
from utils.angle_math import calculate_angle, calculate_elbow_angle, smooth_angle

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

POSE_MODEL_PATH = "pose_landmarker_full.task"
HAND_MODEL_PATH = "hand_landmarker.task"

class CombinedTracker:

    def __init__(self):
        BaseOptions = python.BaseOptions
        VisionRunningMode = vision.RunningMode

        # Pose
        PoseLandmarker = vision.PoseLandmarker
        PoseLandmarkerOptions = vision.PoseLandmarkerOptions

        pose_options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=POSE_MODEL_PATH),
            running_mode=VisionRunningMode.VIDEO,
            num_poses=1
        )

        # Hand
        HandLandmarker = vision.HandLandmarker
        HandLandmarkerOptions = vision.HandLandmarkerOptions

        hand_options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=HAND_MODEL_PATH),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=2
        )

        self.pose_landmarker = PoseLandmarker.create_from_options(pose_options)
        self.hand_landmarker = HandLandmarker.create_from_options(hand_options)

        self.cap = cv2.VideoCapture(0)
        self.start_time = time.time()

        self.prev = {
            "left_shoulder": None,
            "right_shoulder": None,
            "left_elbow": None,
            "right_elbow": None
        }

    def get_frame_data(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.time() - self.start_time) * 1000)

        # Pose
        pose_result = self.pose_landmarker.detect_for_video(mp_image, timestamp_ms)

        data = {
            "left_shoulder": 0,
            "right_shoulder": 0,
            "left_elbow": 0,
            "right_elbow": 0,
            "left_grip": 0,
            "right_grip": 0
        }

        if pose_result.pose_landmarks:
            lm = pose_result.pose_landmarks[0]

            # Left
            ls = calculate_angle(lm[23], lm[11], lm[13], w, h)
            le = calculate_elbow_angle(lm[11], lm[13], lm[15], w, h)

            # Right
            rs = calculate_angle(lm[24], lm[12], lm[14], w, h)
            re = calculate_elbow_angle(lm[12], lm[14], lm[16], w, h)

            data["left_shoulder"] = smooth_angle(self.prev["left_shoulder"], ls)
            data["right_shoulder"] = smooth_angle(self.prev["right_shoulder"], rs)
            data["left_elbow"] = smooth_angle(self.prev["left_elbow"], le)
            data["right_elbow"] = smooth_angle(self.prev["right_elbow"], re)

            self.prev.update({
                "left_shoulder": data["left_shoulder"],
                "right_shoulder": data["right_shoulder"],
                "left_elbow": data["left_elbow"],
                "right_elbow": data["right_elbow"]
            })

        return frame, data
