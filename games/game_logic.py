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
        self.elbow_max = 180
        # elbow range calculation is wrong, better to be between the elbow strength not 180 to his/her best
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
        """
        يحاول جلب elbow_min/elbow_max من قاعدة البيانات.
        يفترض أن db_manager.get_initial_assessment(patient_id) يعيد dict أو None.
        """
        try:
            data = db_manager.get_stats(patient_id)
            if not data:
                return False
            
            elbow_min = data.get("elbow")

            if elbow_min is not None:
                self.elbow_min = float(elbow_min)
                self.elbow_max = 180.0   # ثابت دائماً
                return True
            
            return False
        
        except Exception:
            # لا نرمي استثناء هنا، نستخدم القيم الافتراضية
            return False

    # -----------------------------
    # تحديث السلة بناءً على Trackers المدموج
    # -----------------------------
    def update_basket(self, combined_tracker, w, h, frame, db_manager: DatabaseManager, patient_id):
        """
        combined_tracker: instance of CombinedTracker الذي يحتوي على pose_tracker و hand_tracker و pose_landmarks
        db_manager, patient_id: اختياريان لتحميل ROM المريض قبل بدء اللعب
        """

        pose_tracker = combined_tracker.pose_tracker
        hand_tracker = combined_tracker.hand_tracker
        pose_landmarks = combined_tracker.pose_landmarks

        self.load_patient_rom(db_manager, patient_id)

        # تأكد من وجود قيم جاهزة في الـ trackers
        shoulder_angle = getattr(pose_tracker, "current", {}).get("shoulder", None)
        elbow_angle = getattr(pose_tracker, "current", {}).get("elbow", None)


        # rotation_value من HandTracker: حاول استخدام خاصية موجودة أو احسب من wrist landmark
        rotation_value = None
        if hasattr(hand_tracker, "rotation_value"):
            rotation_value = getattr(hand_tracker, "rotation_value")
        elif hand_tracker.current_hand_landmarks is not None and pose_landmarks is not None:
            # حساب بسيط كنقطة احتياط: فرق X بين رسغ اليد وكتف الجسم (normalized)
            # in the initial assessment sholder rotation need to be deducted. also need to be added to the database.
            try:
                # wrist from hand landmarks (index 0) و shoulder from pose_landmarks
                wrist_lm = hand_tracker.current_hand_landmarks[0]
                if self.side == "left":
                    shoulder_id = 11
                else:
                    shoulder_id = 12
                shoulder_lm = pose_landmarks[shoulder_id]
                rel_x = wrist_lm.x - shoulder_lm.x
                rotation_value = (rel_x + 0.3) / 0.6
                rotation_value = max(0.0, min(1.0, rotation_value))
            except Exception:
                rotation_value = 0.5
        else:
            rotation_value = 0.5
        # these values needs to be more precise and get the sholder external and internal rotaion. also need to be added to the database.
        # this rotation calculation algorithm is very basic and needs to be improved by using the wrist and shoulder landmarks to calculate the actual rotation of the arm, also need to be calibrated for each patient in the initial assessment and saved in the database for better accuracy during the game sessions.

        # مواقع بكسل للكتف والورك (لاحتساب الحركة)
        if pose_landmarks is None:
            # لا توجد بيانات وضعية كافية
            cv2.putText(frame, "Low Confidence", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return

        if self.side == "left":
            shoulder_id, hip_id = 11, 23
        else:
            shoulder_id, hip_id = 12, 24

        sx, sy = int(pose_landmarks[shoulder_id].x * w), int(pose_landmarks[shoulder_id].y * h)
        hx, hy = int(pose_landmarks[hip_id].x * w), int(pose_landmarks[hip_id].y * h)

        # حساب حركة الكتف والجذع (تعويض) بناءً على مواقع البكسل السابقة
        if self.prev_shoulder_px is None:
            self.prev_shoulder_px = (sx, sy)
            self.prev_hip_px = (hx, hy)

        shoulder_move = abs(sx - self.prev_shoulder_px[0]) + abs(sy - self.prev_shoulder_px[1])
        hip_move = abs(hx - self.prev_hip_px[0]) + abs(hy - self.prev_hip_px[1])

        # تحديث السابق
        self.prev_shoulder_px = (sx, sy)
        self.prev_hip_px = (hx, hy)

        # -----------------------------
        # منطق منع التعويض باستخدام ROM المريض
        # -----------------------------
        compensation = False

        if shoulder_move > self.shoulder_move_threshold:
            compensation = True
            cv2.putText(frame, "Keep shoulder stable!", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if hip_move > self.hip_move_threshold:
            compensation = True
            cv2.putText(frame, "Keep trunk stable!", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # استخدم رينج الكوع الخاص بالمريض
        try:
            # إذا pose_tracker يحتفظ بـ rom_min/rom_max استخدمها كـ fallback
            if elbow_angle is None:
                elbow_angle = getattr(pose_tracker, "current", {}).get("elbow", None)

            elbow_min = getattr(self, "elbow_min", None)
            elbow_max = getattr(self, "elbow_max", None)

            # fallback إلى pose_tracker ROM لو لم تتوفر من DB
            if (elbow_min is None or elbow_max is None) and hasattr(pose_tracker, "rom_min"):
                elbow_min = min(elbow_min or 999, pose_tracker.rom_min.get("elbow", 999))
                elbow_max = max(elbow_max or 0, pose_tracker.rom_max.get("elbow", 0))

            if elbow_angle is not None and (elbow_min is not None and elbow_max is not None):
                if not (elbow_min <= elbow_angle <= elbow_max):
                    compensation = True
                    cv2.putText(frame,
                                f"Keep elbow between {int(elbow_min)}-{int(elbow_max)} deg",
                                (50, 200),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8,
                                (0, 0, 255),
                                2)
        except Exception:
            # لا نوقف اللعبة بسبب خطأ بسيط في الفحص
            pass

        # لو فيه تعويض → لا نحرك السلة
        if compensation:
            return

        # -----------------------------
        # تحريك السلة بناءً على rotation_value
        # -----------------------------
        target_x = int(rotation_value * self.w)
        self.basket_x = int(0.7 * self.basket_x + 0.3 * target_x)

        # -----------------------------
        # تسجيل بيانات الجلسة (إن وُجدت)
        # -----------------------------
        if self.session is not None:
            self.session.add_data(
                shoulder_angle=shoulder_angle if shoulder_angle is not None else 0,
                elbow_angle=elbow_angle if elbow_angle is not None else 0,
                rotation_value=rotation_value
            )
            # either here on in session. data need to be exported to the database.
