class InitialAssessment:

    def __init__(self, db_manager, pose_tracker, hand_tracker, user_id):
        self.db = db_manager
        self.pose_tracker = pose_tracker
        self.hand_tracker = hand_tracker
        self.user_id = user_id

    def save(self):
        print("Saving results...")

        self.db.update_strengths(
            self.user_id,
            int(self.pose_tracker.rom_max["shoulder"]),
            int(self.pose_tracker.rom_max["elbow"]),
            int(self.pose_tracker.rom_max["wrist"]),
            int(self.hand_tracker.max_finger_angles["thumb"]),
            int(self.hand_tracker.max_finger_angles["index"]),
            int(self.hand_tracker.max_finger_angles["middle"]),
            int(self.hand_tracker.max_finger_angles["ring"]),
            int(self.hand_tracker.max_finger_angles["pinky"])
        )

        print("Saved to database")
        print("Shoulder:", self.pose_tracker.rom_max["shoulder"])
        print("Elbow:", self.pose_tracker.rom_max["elbow"])
        print("Wrist:", self.pose_tracker.rom_max["wrist"])
        print("Thumb:", self.hand_tracker.max_finger_angles["thumb"])
        print("Index:", self.hand_tracker.max_finger_angles["index"])
        print("Middle:", self.hand_tracker.max_finger_angles["middle"])
        print("Ring:", self.hand_tracker.max_finger_angles["ring"])
        print("Pinky:", self.hand_tracker.max_finger_angles["pinky"])