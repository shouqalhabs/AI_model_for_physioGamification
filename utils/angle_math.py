import numpy as np

class AngleMath:

    @staticmethod
    def smooth_angle(previous, current, alpha=0.7):
        if previous is None:
            return current
        return alpha * previous + (1 - alpha) * current

    @staticmethod
    def calculate_angle(a, b, c, w, h):
        a = np.array([a.x * w, a.y * h])
        b = np.array([b.x * w, b.y * h])
        c = np.array([c.x * w, c.y * h])

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    @staticmethod
    def calculate_elbow_angle(shoulder, elbow, wrist, w, h):
        shoulder = np.array([shoulder.x * w, shoulder.y * h])
        elbow = np.array([elbow.x * w, elbow.y * h])
        wrist = np.array([wrist.x * w, wrist.y * h])

        upper_arm = shoulder - elbow
        forearm = wrist - elbow

        cosine_angle = np.dot(upper_arm, forearm) / (
            np.linalg.norm(upper_arm) * np.linalg.norm(forearm)
        )

        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

        angle = np.arccos(cosine_angle)
        return np.degrees(angle)
