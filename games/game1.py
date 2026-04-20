import random
import time

from games.game_logic import CatchLogic
from games.game_session import GameSession


class Game1:

    def __init__(self, db_manager, user_id, side):
        self.user_id = user_id
        self.side = side

        # Clinical + session layers
        self.session = GameSession()
        self.logic = CatchLogic(side=side, session=self.session)

        # Game state
        self.apples = []
        self.score = 0
        self.missed = 0

        self.last_spawn_time = time.time()

    # =========================
    # SPAWN APPLES
    # =========================
    def _spawn_apple(self):
        self.apples.append({
            "x": random.randint(50, 600),
            "y": 0,
            "speed": random.uniform(2, 5)
        })

    # =========================
    # UPDATE GAME
    # =========================
    def update(self, combined_tracker, frame, w, h, db_manager, patient_id):

        # Use ONLY processed logic (no raw math)
        rotation_value = self.logic.update_logic(
            combined_tracker, w, h, frame, db_manager, patient_id
        )

        # If compensation → freeze gameplay
        if rotation_value is None:
            return self._state()

        # Spawn apples over time
        if time.time() - self.last_spawn_time > 1.2:
            self._spawn_apple()
            self.last_spawn_time = time.time()

        # Move apples
        for apple in self.apples[:]:
            apple["y"] += apple["speed"]

            # Simple basket position from rotation
            basket_x = int(rotation_value * w)

            # Collision detection
            if abs(apple["x"] - basket_x) < 40 and apple["y"] > h - 100:
                self.score += 1
                self.apples.remove(apple)

            elif apple["y"] > h:
                self.missed += 1
                self.apples.remove(apple)

        return self._state()

    # =========================
    # OUTPUT STATE
    # =========================
    def _state(self):
        return {
            "game": "game1",
            "score": self.score,
            "missed": self.missed,
            "apples": self.apples
        }

    # =========================
    # END GAME
    # =========================
    def end(self, user_id):
        self.session.submit(user_id)