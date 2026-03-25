from database.db_manager import DatabaseManager
db = DatabaseManager()
class GameSession:
    
    def __init__(self):
        self.shoulder_angles = []
        self.elbow_angles = []
        # self.rotation_values = []
        self.shoulder_external_rotation_values = []
        self.shoulder_internal_rotation_values = []
        self.wrist_angles = []
        self.max_thumb_angles = []
        self.max_index_angles = []
        self.max_middle_angles = []
        self.max_ring_angles = []
        self.max_pinky_angles = []

    def add_data(self, shoulder_angle, shoulder_external_rotation, shoulder_internal_rotation, elbow_angle, wrist_angle, max_thumb, max_index, max_middle, max_ring, max_pinky):
        self.shoulder_angles.append(shoulder_angle)
        self.elbow_angles.append(elbow_angle)
        # self.rotation_values.append(rotation_value)
        self.shoulder_external_rotation_values.append(shoulder_external_rotation)
        self.shoulder_internal_rotation_values.append(shoulder_internal_rotation)
        self.wrist_angles.append(wrist_angle)
        self.max_thumb_angles.append(max_thumb)
        self.max_index_angles.append(max_index)
        self.max_middle_angles.append(max_middle)
        self.max_ring_angles.append(max_ring)
        self.max_pinky_angles.append(max_pinky)

    # def average(self, arr):
    #     return sum(arr) / len(arr) if arr else 0

    # def get_summary(self):
    #     return {
    #         "avg_shoulder": int(self.average(self.shoulder_angles)),
    #         "avg_elbow": int(self.average(self.elbow_angles)),
    #         "avg_rotation": int(self.average(self.rotation_values)),
    #         "max_shoulder": int(max(self.shoulder_angles)) if self.shoulder_angles else 0,
    #         "min_elbow": int(min(self.elbow_angles)) if self.elbow_angles else 0,
    #         "max_rotation": int(max(self.rotation_values)) if self.rotation_values else 0
    #     }
    def submit(self, user_id):
        db.submit_game_session(
            user_id,
            int(max(self.shoulder_angles)) if self.shoulder_angles else 0,
            int(max(self.shoulder_external_rotation_values)) if self.shoulder_external_rotation_values else 0,
            int(max(self.shoulder_internal_rotation_values)) if self.shoulder_internal_rotation_values else 0,
            int(min(self.elbow_angles)) if self.elbow_angles else 0,
            int(max(self.wrist_angles)) if self.wrist_angles else 0,
            int(max(self.max_thumb_angles)) if self.max_thumb_angles else 0,
            int(max(self.max_index_angles)) if self.max_index_angles else 0,
            int(max(self.max_middle_angles)) if self.max_middle_angles else 0,
            int(max(self.max_ring_angles)) if self.max_ring_angles else 0,
            int(max(self.max_pinky_angles)) if self.max_pinky_angles else 0
        )