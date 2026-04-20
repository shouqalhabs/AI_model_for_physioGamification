import random
import time

from games.game_logic import CatchLogic
from games.game_session import GameSession


class Game3:

    def __init__(self, db_manager, user_id, side):

        self.user_id = user_id
        self.side = side

        self.session = GameSession()
        self.logic = CatchLogic(side=side, session=self.session)

        # =========================
        # GAME STATE
        # =========================

        self.objects = []
        self.boxes = ["red", "green", "blue"]

        self.held_object = None

        self.score = 0
        self.missed = 0

        self.last_spawn = time.time()

    # =========================
    # SPAWN OBJECTS
    # =========================
    def _spawn_object(self):
        self.objects.append({
            "x": random.randint(100, 600),
            "y": random.randint(100, 400),
            "color": random.choice(self.boxes),
            "held": False
        })

    # =========================
    # GRIP DETECTION
    # =========================
    def _is_gripping(self, hand_tracker):
        # average finger angle
        fingers = hand_tracker.finger_angles

        valid = [v for v in fingers.values() if v is not None]

        if not valid:
            return False

        avg = sum(valid) / len(valid)

        # threshold (tune clinically later)
        return avg < 60  # closed hand

    # =========================
    # UPDATE GAME
    # =========================
    def update(self, combined_tracker, frame, w, h, db_manager, patient_id):

        rotation_value = self.logic.update_logic(
            combined_tracker, w, h, frame, db_manager, patient_id
        )

        if rotation_value is None:
            return self._state()

        pose = combined_tracker.pose_tracker.current
        hand = combined_tracker.hand_tracker

        hand_landmarks = hand.current_hand_landmarks

        if hand_landmarks is None:
            return self._state()

        grip = self._is_gripping(hand)

        hand_x = hand_landmarks[8].x * w
        hand_y = hand_landmarks[8].y * h

        # spawn objects
        if time.time() - self.last_spawn > 2:
            self._spawn_object()
            self.last_spawn = time.time()

        # =========================
        # PICK LOGIC
        # =========================
        if self.held_object is None:

            for obj in self.objects:
                dist = abs(obj["x"] - hand_x) + abs(obj["y"] - hand_y)

                if dist < 60 and grip:
                    self.held_object = obj
                    obj["held"] = True
                    break

        # =========================
        # MOVE HELD OBJECT
        # =========================
        if self.held_object:
            self.held_object["x"] = hand_x
            self.held_object["y"] = hand_y

        # =========================
        # DROP LOGIC
        # =========================
        if self.held_object and not grip:

            obj = self.held_object

            # check correct box
            box_x = {"red": 150, "green": 350, "blue": 550}

            if abs(obj["x"] - box_x[obj["color"]]) < 80:
                self.score += 1
            else:
                self.missed += 1

            self.objects.remove(obj)
            self.held_object = None

        return self._state()

    # =========================
    # STATE OUTPUT
    # =========================
    def _state(self):
        return {
            "game": "game3",
            "score": self.score,
            "missed": self.missed,
            "objects": self.objects,
            "boxes": self.boxes,
            "holding": self.held_object is not None
        }

    # =========================
    # END GAME
    # =========================
    def end(self, user_id):
        self.session.submit(user_id)