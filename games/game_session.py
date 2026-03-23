class GameSession:

    def __init__(self):
        self.shoulder_values = []
        self.elbow_values = []
        self.grip_values = []
        self.rotation_values = []

    def add_data(self, shoulder, elbow, grip, rotation):
        self.shoulder_values.append(shoulder)
        self.elbow_values.append(elbow)
        self.grip_values.append(grip)
        self.rotation_values.append(rotation)

    def average(self, arr):
        return sum(arr) / len(arr) if arr else 0

    def get_averages(self):
        return {
            "shoulder": int(self.average(self.shoulder_values)),
            "elbow": int(self.average(self.elbow_values)),
            "grip": int(self.average(self.grip_values)),
            "rotation": int(self.average(self.rotation_values))
        }
