import time


class InitialAssessment:

    def __init__(self, db_manager, combined_tracker, user_id):
        self.db = db_manager
        self.combined = combined_tracker
        self.user_id = user_id

        self.start_time = None
        self.active = False

        # =============================
        # DATA
        # =============================

        self.data = {
            "shoulder": [],
            "rotation": [],
            "elbow": [],
            "wrist": [],
            "hand": [],
            "thumb": [],
            "index": [],
            "middle": [],
            "ring": [],
            "pinky": [],
            "shoulder_external_rotation": [],
            "shoulder_internal_rotation": []
        }

    # =============================
    # START
    # =============================

    def start(self):
        self.start_time = time.time()
        self.active = True

    # =============================
    # TIMELINE
    # =============================

    def get_phase(self, elapsed):

        if elapsed < 7:
            return "Rest", [], None

        elif elapsed < 12:
            return "Calibration", ["all"], None

        elif elapsed < 15:
            return "Rest", [], None

        elif elapsed < 20:
            return "Shoulder", ["shoulder"], "shoulder"

        elif elapsed < 23:
            return "Rest", [], None

        # =============================
        # ROTATION (EXT + INT TOGETHER)
        # =============================

        elif elapsed < 28:
            return "Rotation", [
                "shoulder_external_rotation",
                "shoulder_internal_rotation"
            ], "rotation"

        elif elapsed < 31:
            return "Rest", [], None

        elif elapsed < 36:
            return "Elbow", ["elbow"], "elbow"

        elif elapsed < 39:
            return "Rest", [], None

        elif elapsed < 44:
            return "Wrist", ["wrist"], "wrist"

        elif elapsed < 47:
            return "Rest", [], None

        # =============================
        # HAND (ALL FINGERS TOGETHER)
        # =============================

        elif elapsed < 52:
            return "Hand", [
                "thumb",
                "index",
                "middle",
                "ring",
                "pinky"
            ], "hand"

        else:
            return None, [], None

    # =============================
    # UPDATE
    # =============================

    def update(self, frame, elapsed):

        if not self.active:
            self.start()

        phase_text, calculate, key = self.get_phase(elapsed)

        if phase_text is None:
            self.active = False
            return None, None

        # =============================
        # GET DATA
        # =============================

        current = self.combined.current

        # =============================
        # CALIBRATION TRIGGER (IMPORTANT FIX)
        # =============================

        if phase_text == "Calibration":
            self.combined.pose_tracker.start_calibration()

        # =============================
        # DATA COLLECTION
        # =============================

        if key == "shoulder":
            self.data["shoulder"].append(current["shoulder"])

            self.data["shoulder_external_rotation"].append(
                current["shoulder_external_rotation"]
            )
            self.data["shoulder_internal_rotation"].append(
                current["shoulder_internal_rotation"]
            )

        elif key == "rotation":
            self.data["rotation"].append((
                current["shoulder_external_rotation"],
                current["shoulder_internal_rotation"]
            ))

        elif key == "elbow":
            self.data["elbow"].append(current["elbow"])

        elif key == "wrist":
            self.data["wrist"].append(current["wrist"])

        elif key == "hand":
            self.data["hand"].append(current.get("hand", 0))

        return phase_text, calculate

    # =============================
    # SAVE
    # =============================

    def save(self):

        self.db.update_strengths(
            self.user_id,

            int(max(self.data["shoulder"] or [0])),
            int(min(self.data["elbow"] or [0])),
            int(max(self.data["wrist"] or [0])),

            int(max(self.data["thumb"] or [0])),
            int(max(self.data["index"] or [0])),
            int(max(self.data["middle"] or [0])),
            int(max(self.data["ring"] or [0])),
            int(max(self.data["pinky"] or [0])),

            int(max([r[0] for r in self.data["rotation"]] or [0])),
            int(max([r[1] for r in self.data["rotation"]] or [0]))
        )

## after it takes any measuremednts it directly uploads it to db