import cv2
import math
from games.game_session import GameSession
from database.db_manager import DatabaseManager


class CatchLogic:
    def __init__(self, side, session: GameSession | None = None,
                 elbow_min: float | None = None, elbow_max: float | None = None):

        self.side = side
        self.session = session

        # ROM limits
        self.elbow_min = elbow_min
        self.elbow_max = elbow_max

        # Trunk compensation thresholds (from Osaka City Medical Journal. 67(2); 81-90)
        self.min_trunk_deg = 5.0    # عند ~90°
        self.max_trunk_deg = 12.0   # عند ~180°

    # ----------------------------------------------------
    # Load ROM from database
    # ----------------------------------------------------
    def load_patient_rom(self, db_manager: DatabaseManager, patient_id):
        try:
            data = db_manager.get_stats(patient_id)
            if not data:
                return False

            # Elbow ROM
            elbow_base = data.get("elbow")
            if elbow_base is not None:
                elbow_base = float(elbow_base)
                self.elbow_max = elbow_base + 50

            # Shoulder internal/external ROM
            int_rom = data.get("sholder_int_rotation")
            ext_rom = data.get("sholder_ext_rotation")

            self.internal_rom = float(int_rom)
            self.external_rom = float(ext_rom)

            return True

        except Exception:
            return False

    # ----------------------------------------------------
    # Dynamic trunk threshold (based on paper)
    # ----------------------------------------------------
    def get_trunk_threshold(self, shoulder_angle):
        shoulder_angle = max(0, min(180, shoulder_angle))
        return self.min_trunk_deg + (shoulder_angle / 180.0) * (self.max_trunk_deg - self.min_trunk_deg)

    # ----------------------------------------------------
    # Main logic update
    # ----------------------------------------------------
    def update_logic(self, combined_tracker, w, h, frame,
                     db_manager: DatabaseManager, patient_id):

        pose_tracker = combined_tracker.pose_tracker
        hand_tracker = combined_tracker.hand_tracker
        pose_landmarks = combined_tracker.pose_landmarks

        # Load ROM once
        if not hasattr(self, "_rom_loaded"):
            self.load_patient_rom(db_manager, patient_id)
            self._rom_loaded = True

        pt = pose_tracker.current

        # Shoulder rotation (signed)
        signed_rotation = pt.get("shoulder_rotation", 0.0)

        # Elbow angle
        elbow_angle = pt.get("elbow", 0.0)

        # Shoulder elevation angle (IMPORTANT for compensation logic)
        shoulder_angle = pt.get("shoulder", 0.0)

        # Normalize rotation (0..1)
        max_rot = max(1.0, float(max(self.internal_rom, self.external_rom)))
        norm = signed_rotation / max_rot
        norm = max(-1.0, min(1.0, norm))
        rotation_value = (norm + 1.0) / 2.0

        # Check landmarks
        if pose_landmarks is None:
            cv2.putText(frame, "Low Confidence", (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return None

        # Select side
        if self.side == "left":
            shoulder_id, hip_id = 11, 23
        else:
            shoulder_id, hip_id = 12, 24

        sx = pose_landmarks[shoulder_id].x * w
        sy = pose_landmarks[shoulder_id].y * h
        hx = pose_landmarks[hip_id].x * w
        hy = pose_landmarks[hip_id].y * h

        # ----------------------------------------------------
        # Compute trunk angle (degrees)
        # ----------------------------------------------------
        dx = sx - hx
        dy = hy - sy

        if dy == 0:
            trunk_angle = 0.0
        else:
            trunk_angle = abs(math.degrees(math.atan(dx / dy)))

        # ----------------------------------------------------
        # Get dynamic threshold (from paper)
        # ----------------------------------------------------
        trunk_threshold = self.get_trunk_threshold(shoulder_angle)

        compensation = False

        # ----------------------------------------------------
        # Trunk compensation detection
        # ----------------------------------------------------
        if trunk_angle > trunk_threshold:
            compensation = True
            cv2.putText(frame,
                        f"Trunk compensation! ({int(trunk_angle)} deg)",
                        (50, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2) ## this is the message you should replace in game

        # Early compensation (important clinically)
        elif trunk_angle > 5 and shoulder_angle < 60:
            compensation = True
            cv2.putText(frame,
                        "Avoid leaning early!",
                        (50, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2) ## this is the message you should replace in game (soft message just a note like)

        # ----------------------------------------------------
        # Elbow ROM check
        # ----------------------------------------------------
        if not (elbow_angle <= self.elbow_max):
            compensation = True
            cv2.putText(frame,
                        f"Higher Your Elbow",
                        (50, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2) ## this is the message you should replace in game

        # Stop movement if compensation detected
        if compensation:
            return None

        # ----------------------------------------------------
        # Log session data
        # ----------------------------------------------------
        if self.session is not None:
            self.session.add_data(
                shoulder_angle=shoulder_angle,
                shoulder_external_rotation=pt.get("shoulder_external_rotation", 0),
                shoulder_internal_rotation=pt.get("shoulder_internal_rotation", 0),
                elbow_angle=elbow_angle,
                wrist_angle=pt.get("wrist", 0),
                thumb=hand_tracker.finger_angles.get("thumb", 0),
                index=hand_tracker.finger_angles.get("index", 0),
                middle=hand_tracker.finger_angles.get("middle", 0),
                ring=hand_tracker.finger_angles.get("ring", 0),
                pinky=hand_tracker.finger_angles.get("pinky", 0)
            )

        return rotation_value