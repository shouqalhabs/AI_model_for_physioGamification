class CombinedTracker:

    def __init__(self, pose_tracker, hand_tracker):
        self.pose_tracker = pose_tracker
        self.hand_tracker = hand_tracker
        self.pose_landmarks = None

    def run(self, frame, w, h, mp_image, timestamp_ms,
            hand_landmarker, pose_landmarker, injured_hand):

        self.hand_tracker.process(injured_hand, frame, w, h,
                                  mp_image, timestamp_ms, hand_landmarker)

        pose_result = pose_landmarker.detect_for_video(mp_image, timestamp_ms)

        if pose_result.pose_landmarks:
            self.pose_landmarks = pose_result.pose_landmarks[0]

            valid = self.pose_tracker.process(
                frame,
                self.pose_landmarks,
                w,
                h,
                side=injured_hand
            )

            return valid

        return False