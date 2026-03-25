import cv2
import mediapipe as mp
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from database.db_manager import DatabaseManager
from tracker.pose_tracker import PoseTracker
from tracker.hand_tracker import HandTracker
from tracker.combined_tracker import CombinedTracker
from assessment.initial_assessment import InitialAssessment

from games.game_logic import CatchGame
from games.game_session import GameSession

POSE_MODEL_PATH = "pose_landmarker_full.task"
HAND_MODEL_PATH = "hand_landmarker.task"

BaseOptions = python.BaseOptions
VisionRunningMode = vision.RunningMode

pose_options = vision.PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=POSE_MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_poses=1
)

hand_options = vision.HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=HAND_MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2
)

cap = cv2.VideoCapture(0)
start_time = time.time()

USER_ID = 1

# INIT CLASSES
db = DatabaseManager()
pose_tracker = PoseTracker()
hand_tracker = HandTracker()
combined = CombinedTracker(pose_tracker, hand_tracker)
# assessment = InitialAssessment(db, pose_tracker, hand_tracker,USER_ID)

session = GameSession()


affected_arm = db.get_affected_arm(USER_ID) # takes left or right as values

ret, frame = cap.read()
h, w, _ = frame.shape

game1 = CatchGame(w, h, side=affected_arm, session=session)

with vision.PoseLandmarker.create_from_options(pose_options) as pose_landmarker, \
     vision.HandLandmarker.create_from_options(hand_options) as hand_landmarker:

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb_frame)
        timestamp_ms = int((time.time() - start_time) * 1000)

        combined.run(frame, w, h, mp_image, timestamp_ms,
                     hand_landmarker, pose_landmarker, affected_arm)

        # cv2.imshow("Physio Assessment", frame)

        
        game1.update_basket(
            combined,
            w, h,
            frame,
            db,
            USER_ID
        )
        game1.update_object()
        game1.check_catch()
        game1.draw(frame)

        #session.add_data(
        #    pose_tracker.current_shoulder,
        #    pose_tracker.current_elbow,
        #    hand_tracker.current_grip,
        #    pose_tracker.current_shoulder  # external rotation approx
        #)

        cv2.imshow("eggs Game", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

#averages = session.get_averages()

#db.submit_game_session(
#    USER_ID,
#    averages["shoulder"],
#    averages["elbow"],
#    averages["grip"],
#    averages["rotation"]
#)

cap.release()
cv2.destroyAllWindows()

# assessment.save()
session.submit(USER_ID)