import numpy as np
import math

class AngleMath:

    @staticmethod
    def calculate_angle(a, b, c):
        # Extract normalized 3D coordinates
        ax, ay, az = a.x, a.y, a.z
        bx, by, bz = b.x, b.y, b.z
        cx, cy, cz = c.x, c.y, c.z

        # Create vectors AB and CB
        ab = (ax - bx, ay - by, az - bz)
        cb = (cx - bx, cy - by, cz - bz)

        # Dot product
        dot = ab[0]*cb[0] + ab[1]*cb[1] + ab[2]*cb[2]

        # Magnitudes
        mag_ab = math.sqrt(ab[0]**2 + ab[1]**2 + ab[2]**2)
        mag_cb = math.sqrt(cb[0]**2 + cb[1]**2 + cb[2]**2)

        # Avoid division by zero
        if mag_ab == 0 or mag_cb == 0:
            return 0.0

        # Clamp to avoid domain errors
        cos_angle = max(-1.0, min(1.0, dot / (mag_ab * mag_cb)))

        # Convert to degrees
        return math.degrees(math.acos(cos_angle))

    @staticmethod
    def smooth_angle(prev, current, velocity, base_alpha=0.7):
        # First frame
        if prev is None:
            return current

        # Adaptive smoothing
        if velocity > 15:
            alpha = 0.5
        else:
            alpha = base_alpha

        # Exponential smoothing
        return alpha * prev + (1 - alpha) * current

    @staticmethod
    def remove_spikes(prev, current, threshold=40):
        # First frame
        if prev is None:
            return current

        # If jump is too large → treat as noise
        if abs(current - prev) > threshold:
            return prev

        return current


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
