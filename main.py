from tracker.combined_tracker import CombinedTracker
from database.db_manager import DatabaseManager
from games.game1 import FirstGame

import cv2

USER_ID = 25

db = DatabaseManager()
injured_hand = db.get_injured_hand(USER_ID)

tracker = CombinedTracker()
game = FirstGame()

while True:
    frame, data = tracker.get_frame_data()
    if frame is None:
        break

    max_shoulder = game.update(data)

    cv2.putText(frame, f"Shoulder Max: {int(max_shoulder)}",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

    cv2.imshow("Physio Game", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

db.update_strengths(USER_ID, int(max_shoulder), 0, 0)
print("Saved to database")
