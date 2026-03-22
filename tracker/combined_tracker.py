class CombinedTracker:

    def __init__(self, pose_tracker, hand_tracker):
        self.pose_tracker = pose_tracker
        self.hand_tracker = hand_tracker

    def run(self, frame, w, h, mp_image, timestamp_ms,
            hand_landmarker, pose_landmarker, injured_hand):

        self.hand_tracker.process(injured_hand, frame, w, h,
                                  mp_image, timestamp_ms, hand_landmarker)

        pose_result = pose_landmarker.detect_for_video(mp_image, timestamp_ms)

        if pose_result.pose_landmarks:

            landmarks = pose_result.pose_landmarks[0]

            if injured_hand == 'left':
                self.pose_tracker.process_left_side(frame, landmarks, w, h)
            else:
                self.pose_tracker.process_right_side(frame, landmarks, w, h)
        #print("DEBUG VALUES:")
        #print("Shoulder:", self.pose_tracker.max_shoulder)
        #print("Elbow:", self.pose_tracker.max_elbow)
        #print("Grip:", self.hand_tracker.max_grip)
        #problem: sholder and elbow captures gosts angles!!