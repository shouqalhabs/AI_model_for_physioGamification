import random
import time

from games.game_logic import CatchLogic
from games.game_session import GameSession


class Game2:

    def __init__(self, db_manager, user_id, side):
        self.user_id = user_id
        self.side = side

        self.session = GameSession()
        self.logic = CatchLogic(side=side, session=self.session)

        # Game state
        self.bubbles = []
        self.score = 0
        self.missed = 0

        self.last_spawn_time = time.time()

    # =========================
    # SPAWN BUBBLES
    # =========================
    def _spawn_bubble(self):
        self.bubbles.append({
            "x": random.randint(100, 500),
            "y": random.randint(50, 150),
            "size": random.randint(20, 40)
        })

    # =========================
    # UPDATE GAME
    # =========================
    def update(self, combined_tracker, frame, w, h, db_manager, patient_id):

        rotation_value = self.logic.update_logic(
            combined_tracker, w, h, frame, db_manager, patient_id
        )

        # Block if compensation detected
        if rotation_value is None:
            return self._state()

        # spawn bubbles
        if time.time() - self.last_spawn_time > 1.5:
            self._spawn_bubble()
            self.last_spawn_time = time.time()

        # shoulder elevation from tracker (already computed)
        shoulder = combined_tracker.pose_tracker.current["shoulder"]

        for bubble in self.bubbles[:]:

            # Convert shoulder elevation → reach ability
            reach = shoulder * 5  # scaling factor

            # POP condition
            if reach > bubble["y"]:
                self.score += 1
                self.bubbles.remove(bubble)

            elif bubble["y"] > h:
                self.missed += 1
                self.bubbles.remove(bubble)

        return self._state()

    # =========================
    # STATE
    # =========================
    def _state(self):
        return {
            "game": "game2",
            "score": self.score,
            "missed": self.missed,
            "bubbles": self.bubbles
        }

    # =========================
    # END GAME
    # =========================
    def end(self, user_id):
        self.session.submit(user_id)