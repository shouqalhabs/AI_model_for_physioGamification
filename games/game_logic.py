import random
import cv2

class CatchGame:

    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.basket_x = w // 2
        self.basket_y = h - 80

        self.obj_x = random.randint(50, w-50)
        self.obj_y = 0

        self.speed = 8
        self.score = 0


    def update_object(self):
        self.obj_y += self.speed

        if self.obj_y > self.h:
            self.obj_y = 0
            self.obj_x = random.randint(50, self.w-50)

    def check_catch(self):
        if abs(self.obj_x - self.basket_x) < 60 and abs(self.obj_y - self.basket_y) < 40:
            self.score += 1
            self.obj_y = 0
            self.obj_x = random.randint(50, self.w-50)

    def draw(self, frame):

        # Basket
        cv2.rectangle(frame,
                      (self.basket_x-60, self.basket_y-20),
                      (self.basket_x+60, self.basket_y+20),
                      (0,255,0), -1)

        # Falling object
        cv2.circle(frame, (self.obj_x, self.obj_y), 15, (0,0,255), -1)

        # Score
        cv2.putText(frame, f"Score: {self.score}",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255,255,255), 2)
###########################


    def update_basket(self, hand_landmarks, pose_landmarks, w, h, frame):

        if not hand_landmarks or not pose_landmarks:
            return

        wrist = hand_landmarks[0]

        # 🟡 shoulder landmark (حسب اليد المصابة)
        shoulder = pose_landmarks[11]  # left shoulder (غيرها إذا يمين)

        # تحويل إلى إحداثيات
        shoulder_x = int(shoulder.x * w)
        shoulder_y = int(shoulder.y * h)

        # 🧠 نخزن موقع الكتف السابق
        if not hasattr(self, "prev_shoulder_x"):
            self.prev_shoulder_x = shoulder_x
            self.prev_shoulder_y = shoulder_y

        # حساب حركة الكتف
        shoulder_movement = abs(shoulder_x - self.prev_shoulder_x) + abs(shoulder_y - self.prev_shoulder_y)

        # تحديث القيم السابقة
        self.prev_shoulder_x = shoulder_x
        self.prev_shoulder_y = shoulder_y

        # 🎯 إذا الكتف تحرك كثير → امنع الحركة
        if shoulder_movement > 15:
            cv2.putText(frame, "Keep your shoulder stable!",
                        (50,100), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0,0,255), 3)
            return

        # ✅ إذا كل شيء طبيعي → حرّك السلة
        target_x = int(wrist.x * w)
        self.basket_x = int(0.7 * self.basket_x + 0.3 * target_x)
    
import random
import cv2

class CatchGame:

    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.basket_x = w // 2
        self.basket_y = h - 80

        self.obj_x = random.randint(50, w-50)
        self.obj_y = 0

        self.speed = 8
        self.score = 0

        self.prev_shoulder_x = None
        self.prev_shoulder_y = None

    def update_basket(self, hand_landmarks, pose_landmarks, w, h, frame):

        if not hand_landmarks or not pose_landmarks:
            return

        wrist = hand_landmarks[0]
        shoulder = pose_landmarks[11]

        sx = int(shoulder.x * w)
        sy = int(shoulder.y * h)

        if self.prev_shoulder_x is None:
            self.prev_shoulder_x = sx
            self.prev_shoulder_y = sy

        movement = abs(sx - self.prev_shoulder_x) + abs(sy - self.prev_shoulder_y)

        self.prev_shoulder_x = sx
        self.prev_shoulder_y = sy

        # ❌ منع الغش
        if movement > 15:
            cv2.putText(frame, "Keep shoulder stable!",
                        (50,150), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0,0,255), 3)
            return

        target_x = int(wrist.x * w)
        self.basket_x = int(0.7*self.basket_x + 0.3*target_x)

    def update_object(self):
        self.obj_y += self.speed

        if self.obj_y > self.h:
            self.obj_y = 0
            self.obj_x = random.randint(50, self.w-50)

    def check_catch(self):
        if abs(self.obj_x - self.basket_x) < 60 and abs(self.obj_y - self.basket_y) < 40:
            self.score += 1
            self.obj_y = 0
            self.obj_x = random.randint(50, self.w-50)

    def draw(self, frame):
        cv2.rectangle(frame,
                      (self.basket_x-60, self.basket_y-20),
                      (self.basket_x+60, self.basket_y+20),
                      (0,255,0), -1)

        cv2.circle(frame, (self.obj_x, self.obj_y), 15, (0,0,255), -1)

        cv2.putText(frame, f"Score: {self.score}",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255,255,255), 2)