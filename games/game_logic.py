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

    def update_basket(self, hand_landmarks, w):
        if hand_landmarks:
            wrist = hand_landmarks[0]

            # ✅ Smooth movement (optional but recommended)
            target_x = int(wrist.x * w)
            self.basket_x = int(0.7 * self.basket_x + 0.3 * target_x)

    def update_object(self):
        self.obj_y += self.speed

        if self.obj_y > self.h:
            self.obj_y = 0
            self.obj_x = random.randint(50, self.w-50)

    # ✅ FIXED: No grip required anymore
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