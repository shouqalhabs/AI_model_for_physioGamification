import sqlite3

SDB_PATH = "C:\\Users\\sh210\\aiphysio\\AI_model_for_physioGamification\\rehab.db"

class DatabaseManager:

    def get_injured_hand(self, user_id):
        conn = sqlite3.connect(SDB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT affected_hand FROM patients WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        return result[0].lower() if result else "left"

    def update_strengths(self, user_id, shoulder, elbow, grip):
        conn = sqlite3.connect(SDB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE patients
            SET shoulder_strength=?, elbow_strength=?, grip_strength=?
            WHERE user_id=?
        """, (shoulder, elbow, grip, user_id))

        conn.commit()
        conn.close()
