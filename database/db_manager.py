import sqlite3

#NDB_PATH = "C:\\Users\\Dell\\physio-gamification-project-grad\\rehab.db"
SDB_PATH = "C:\\Users\\sh210\\aiphysio\\AI_model_for_physioGamification\\rehab.db"

class DatabaseManager:

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
            SELECT shoulder_strength, elbow_strength, wrist_strength, max_thumb, max_index, max_middle, max_ring, max_pinky, sholder_ext_rotation, sholder_int_rotation
            FROM patients
            WHERE user_id = ?
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "shoulder": result[0],
                "elbow": result[1],
                "wrist": result[2],
                "max_thumb": result[3],
                "max_index": result[4],
                "max_middle": result[5],
                "max_ring": result[6],
                "max_pinky": result[7],
                "sholder_ext_rotation": result[8],
                "sholder_int_rotation": result[9]
            }
        else:
            return {
                "shoulder": 0,
                "elbow": 0,
                "wrist": 0,
                "max_thumb": 0,
                "max_index": 0,
                "max_middle": 0,
                "max_ring": 0,
                "max_pinky": 0,
                "sholder_ext_rotation": 0,
                "sholder_int_rotation": 0
            }
    # fetch strength for given user_id from database from patients table to be used as refrence

    def submit_game_session(self, user_id, shoulder_activation, shoulder_shrug, shoulder_external_rotation, shoulder_internal_rotation, elbow_activation, wrist_activation, max_thumb, max_index, max_middle, max_ring, max_pinky):
        conn = sqlite3.connect(SDB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO game_sessions 
            (shoulder_activation, shoulder_shrug, sholder_ext_rotation, sholder_int_rotation, elbow_activation, wrist_activation, max_thumb, max_index, max_middle, max_ring, max_pinky)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            WHERE patient_id = user_id
        """, (user_id, shoulder_activation, shoulder_shrug, shoulder_external_rotation, shoulder_internal_rotation, elbow_activation, wrist_activation, max_thumb, max_index, max_middle, max_ring, max_pinky))

        conn.commit()
        conn.close()
    # submit game session data to database for given user_id in game_sessions table

    def update_strengths(self, user_id, shoulder_strength, shoulder_ext_rotation, shoulder_int_rotation, elbow_strength, wrist_strength, max_thumb, max_index, max_middle, max_ring, max_pinky):
        conn = sqlite3.connect(SDB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE patients
            SET 
                shoulder_strength=?,
                sholder_ext_rotation=?,
                sholder_int_rotation=?,
                elbow_strength=?,
                wrist_strength=?, 
                max_thumb=?,
                max_index=?,
                max_middle=?,
                max_ring=?,
                max_pinky=?
            WHERE user_id=?
        """, (shoulder_strength, shoulder_ext_rotation, shoulder_int_rotation, elbow_strength, wrist_strength, max_thumb, max_index, max_middle, max_ring, max_pinky, user_id))

        conn.commit()
        conn.close()
        # update shoulder, elbow and grip strength for given user_id in database from to patients table
