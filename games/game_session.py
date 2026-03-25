from database.db_manager import DatabaseManager
db = DatabaseManager()

class GameSession:
    
    def __init__(self):
        self.shoulder_angles = []
        self.elbow_angles = []
        self.shoulder_external_rotation_values = []
        self.shoulder_internal_rotation_values = []
        self.wrist_angles = []
        self.thumb_angles = []
        self.index_angles = []
        self.middle_angles = []
        self.ring_angles = []
        self.pinky_angles = []

    def add_data(self, shoulder_angle, shoulder_external_rotation, shoulder_internal_rotation, elbow_angle, wrist_angle, thumb, index, middle, ring, pinky):
        self.shoulder_angles.append(shoulder_angle)
        self.elbow_angles.append(elbow_angle)
        self.shoulder_external_rotation_values.append(shoulder_external_rotation)
        self.shoulder_internal_rotation_values.append(shoulder_internal_rotation)
        self.wrist_angles.append(wrist_angle)
        self.thumb_angles.append(thumb)
        self.index_angles.append(index)
        self.middle_angles.append(middle)
        self.ring_angles.append(ring)
        self.pinky_angles.append(pinky)

    def submit(self, user_id):
        db.submit_game_session(
            user_id,
            int(max(self.shoulder_angles)) if self.shoulder_angles else 0,
            int(max(self.shoulder_external_rotation_values)) if self.shoulder_external_rotation_values else 0,
            int(max(self.shoulder_internal_rotation_values)) if self.shoulder_internal_rotation_values else 0,
            int(min(self.elbow_angles)) if self.elbow_angles else 0,
            int(max(self.wrist_angles)) if self.wrist_angles else 0,
            int(max(self.thumb_angles)) if self.thumb_angles else 0,
            int(max(self.index_angles)) if self.index_angles else 0,
            int(max(self.middle_angles)) if self.middle_angles else 0,
            int(max(self.ring_angles)) if self.ring_angles else 0,
            int(max(self.pinky_angles)) if self.pinky_angles else 0
        )