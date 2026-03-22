import sqlite3

#NDB_PATH = "C:\\Users\\Dell\\physio-gamification-project-grad\\rehab.db"
SDB_PATH = "C:\\Users\\sh210\\aiphysio\\AI_model_for_physioGamification\\rehab.db"

class DatabaseManager:

    SDB_PATH = "C:\\Users\\sh210\\aiphysio\\AI_model_for_physioGamification\\rehab.db"

    def get_affected_arm(self, user_id):
        conn = sqlite3.connect(SDB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT affected_arm FROM patients WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        return result[0].lower() if result else "left"
    # fetch injured hand from database for given user_id either "left" or "right" from patients table

    def get_stats(self, user_id):
        conn = sqlite3.connect(SDB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT shoulder_strength, elbow_strength, grip_strength
            FROM patients
            WHERE user_id = ?
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "shoulder": result[0],
                "elbow": result[1],
                "grip": result[2]
            }
        else:
            return {
                "shoulder": 0,
                "elbow": 0,
                "grip": 0
            }

    def submit_game_session(self, user_id, shoulder, elbow, grip, rotation):
        conn = sqlite3.connect(SDB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO game_sessions 
            (patient_id, shoulder_activation, elbow_activation, grip_activation, external_rotation)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, shoulder, elbow, grip, rotation))

        conn.commit()
        conn.close()

    def update_strengths(self, user_id, shoulder, elbow, grip):
        conn = sqlite3.connect(SDB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE patients
            SET 
                shoulder_strength=?,
                elbow_strength=?, 
                grip_strength=?
            WHERE user_id=?
        """, (shoulder, elbow, grip, user_id))

        conn.commit()
        conn.close()
        # update shoulder, elbow and grip strength for given user_id in database from to patients table
