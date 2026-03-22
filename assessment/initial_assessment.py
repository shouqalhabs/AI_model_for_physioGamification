class InitialAssessment:

    def __init__(self, db_manager, pose_tracker, hand_tracker):
        self.db = db_manager
        self.pose_tracker = pose_tracker
        self.hand_tracker = hand_tracker

    def save(self):
        print("Saving results...")

        self.db.update_strengths(
            25,
            int(self.pose_tracker.max_shoulder),
            int(self.pose_tracker.max_elbow),
            int(self.hand_tracker.max_grip)
        )

        print("Saved to database")
        print("Shoulder:", self.pose_tracker.max_shoulder)
        print("Elbow:", self.pose_tracker.max_elbow)
        print("Grip:", self.hand_tracker.max_grip)