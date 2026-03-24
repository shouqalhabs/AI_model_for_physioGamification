class GameSession:
    
    def __init__(self):
        self.shoulder_angles = []
        self.elbow_angles = []
        self.rotation_values = []

    def add_data(self, shoulder_angle, elbow_angle, rotation_value):
        self.shoulder_angles.append(shoulder_angle)
        self.elbow_angles.append(elbow_angle)
        self.rotation_values.append(rotation_value)

    def average(self, arr):
        return sum(arr) / len(arr) if arr else 0

    def get_summary(self):
        return {
            "avg_shoulder": int(self.average(self.shoulder_angles)),
            "avg_elbow": int(self.average(self.elbow_angles)),
            "avg_rotation": int(self.average(self.rotation_values)),
            "max_shoulder": int(max(self.shoulder_angles)) if self.shoulder_angles else 0,
            "min_elbow": int(min(self.elbow_angles)) if self.elbow_angles else 0,
            "max_rotation": int(max(self.rotation_values)) if self.rotation_values else 0
        }