import sqlite3

class GameSession:

    def __init__(self, db_path):
        self.db_path = db_path

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
        if len(arr) == 0:
            return 0
        return sum(arr) / len(arr)

    def save(self, patient_id):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO game_sessions 
            (patient_id, shoulder_activation, elbow_activation, grip_activation, external_rotation)
            VALUES (?, ?, ?, ?, ?)
        """, (
            patient_id,
            int(self.average(self.shoulder_values)),
            int(self.average(self.elbow_values)),
            int(self.average(self.grip_values)),
            int(self.average(self.rotation_values))
        ))

        conn.commit()
        conn.close()

        print("✅ Game session saved")
