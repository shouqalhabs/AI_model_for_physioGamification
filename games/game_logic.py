import cv2
import random
from games.game_session import GameSession
from database.db_manager import DatabaseManager


class CatchGame:
    def __init__(self, w, h, side="left", session: GameSession | None = None,
                 elbow_min: float | None = None, elbow_max: float | None = None,
                 shoulder_move_threshold: float = 15.0, hip_move_threshold: float = 15.0):
        self.w = w
        self.h = h
        self.side = side

        # موقع السلة
        self.basket_x = w // 2
        self.basket_y = h - 80

        # الجسم الساقط
        self.obj_x = random.randint(50, w - 50)
        self.obj_y = 0

        self.speed = 8
        self.score = 0

        # للتعويض بالكتف/الجذع (نخزن مواقع بكسل سابقة)
        self.prev_shoulder_px = None  # (x, y)
        self.prev_hip_px = None       # (x, y)

        # جلسة تسجيل بيانات (اختياري)
        self.session = session

        # رينج الكوع الافتراضي (يمكن استبداله من DB عند بدء الجلسة)
        self.elbow_min = elbow_min if elbow_min is not None else 60.0
        self.elbow_max = elbow_max if elbow_max is not None else 160.0

        # حساسية منع التعويض
        self.shoulder_move_threshold = shoulder_move_threshold
        self.hip_move_threshold = hip_move_threshold

    # -----------------------------
    # تحديث الجسم الساقط
    # -----------------------------
    def update_object(self):
        self.obj_y += self.speed
        if self.obj_y > self.h:
            self.obj_y = 0
            self.obj_x = random.randint(50, self.w - 50)

    # -----------------------------
    # فحص الالتقاط
    # -----------------------------
    def check_catch(self):
        if abs(self.obj_x - self.basket_x) < 60 and abs(self.obj_y - self.basket_y) < 40:
            self.score += 1
            self.obj_y = 0
            self.obj_x = random.randint(50, self.w - 50)

    # -----------------------------
    # رسم اللعبة
    # -----------------------------
    def draw(self, frame):
        cv2.rectangle(
            frame,
            (self.basket_x - 60, self.basket_y - 20),
            (self.basket_x + 60, self.basket_y + 20),
            (0, 255, 0),
            -1
        )
        cv2.circle(frame, (self.obj_x, self.obj_y), 15, (0, 0, 255), -1)
        cv2.putText(frame, f"Score: {self.score}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Elbow ROM: {int(self.elbow_min)}-{int(self.elbow_max)} deg",
                    (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 0), 2)

    # -----------------------------
    # تحميل رينج المريض من DB (اختياري)
    # -----------------------------
    def load_patient_rom(self, db_manager: DatabaseManager, patient_id):
        try:
            data = db_manager.get_stats(patient_id)
            if not data:
                return False

            # Elbow ROM
            elbow_base = data.get("elbow")
            if elbow_base is not None:
                elbow_base = float(elbow_base)
                self.elbow_min = elbow_base - 50
                self.elbow_max = elbow_base + 50

            # Shoulder internal/external ROM
            int_rom = data.get("sholder_int_rotation")
            ext_rom = data.get("sholder_ext_rotation")

            self.internal_rom = float(int_rom) if int_rom not in (None, 0) else 60
            self.external_rom = float(ext_rom) if ext_rom not in (None, 0) else 60

            return True

        except Exception:
            return False


    # -----------------------------
    # تحديث السلة بناءً على Trackers المدموج
    # -----------------------------
    def update_basket(self, combined_tracker, w, h, frame, db_manager: DatabaseManager, patient_id):

        pose_tracker = combined_tracker.pose_tracker
        hand_tracker = combined_tracker.hand_tracker
        pose_landmarks = combined_tracker.pose_landmarks

        # Load ROM once
        if not hasattr(self, "_rom_loaded"):
            self.load_patient_rom(db_manager, patient_id)
            self._rom_loaded = True

        # Read rotation values from PoseTracker
        pt = pose_tracker.current

        signed_rotation = pt.get("shoulder_rotation", 0.0)

        elbow_angle = pt.get("elbow", 0.0)

        # Normalize rotation to 0..1
        # Normalize signed rotation to -1..1
        max_rot = max(1.0, float(max(self.internal_rom, self.external_rom)))
        norm = signed_rotation / max_rot
        norm = max(-1.0, min(1.0, norm))

        # Convert -1..1 → 0..1
        rotation_value = (norm + 1.0) / 2.0


        # Compensation check
        if pose_landmarks is None:
            cv2.putText(frame, "Low Confidence", (20,120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            return

        if self.side == "left":
            shoulder_id, hip_id = 11, 23
        else:
            shoulder_id, hip_id = 12, 24

        sx, sy = int(pose_landmarks[shoulder_id].x * w), int(pose_landmarks[shoulder_id].y * h)
        hx, hy = int(pose_landmarks[hip_id].x * w), int(pose_landmarks[hip_id].y * h)

        if self.prev_shoulder_px is None:
            self.prev_shoulder_px = (sx, sy)
            self.prev_hip_px = (hx, hy)

        shoulder_move = abs(sx - self.prev_shoulder_px[0]) + abs(sy - self.prev_shoulder_px[1])
        hip_move = abs(hx - self.prev_hip_px[0]) + abs(hy - self.prev_hip_px[1])

        self.prev_shoulder_px = (sx, sy)
        self.prev_hip_px = (hx, hy)

        compensation = False

        if shoulder_move > self.shoulder_move_threshold:
            compensation = True
            cv2.putText(frame, "Keep shoulder stable!", (50,120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        if hip_move > self.hip_move_threshold:
            compensation = True
            cv2.putText(frame, "Keep trunk stable!", (50,160),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        # Elbow ROM check
        if not (self.elbow_min <= elbow_angle <= self.elbow_max):
            compensation = True
            cv2.putText(frame,
                        f"Keep elbow between {int(self.elbow_min)}-{int(self.elbow_max)} deg",
                        (50,200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        if compensation:
            return

        # Move basket
        target_x = int(rotation_value * self.w)
        self.basket_x = int(0.7 * self.basket_x + 0.3 * target_x)

        # Log session
        if self.session is not None:
            self.session.add_data(
                shoulder_angle= pt.get("shoulder", 0),
                shoulder_external_rotation= pt.get("shoulder_external_rotation", 0),
                shoulder_internal_rotation= pt.get("shoulder_internal_rotation", 0),
                elbow_angle= elbow_angle,
                wrist_angle= pt.get("wrist", 0),
                thumb= hand_tracker.finger_angles.get("thumb", 0),
                index= hand_tracker.finger_angles.get("index", 0),
                middle= hand_tracker.finger_angles.get("middle", 0),
                ring= hand_tracker.finger_angles.get("ring", 0),
                pinky= hand_tracker.finger_angles.get("pinky", 0)
            )
