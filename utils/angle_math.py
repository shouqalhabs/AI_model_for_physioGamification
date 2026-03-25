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
    
    @staticmethod
    def calculate_signed_rotation(shoulder, elbow, wrist, ref_vector=None, eps=1e-8):
        s = np.asarray(shoulder, dtype=float)
        e = np.asarray(elbow, dtype=float)
        w = np.asarray(wrist, dtype=float)

        # 1) humerus axis (shoulder -> elbow)
        u = e - s
        u_norm = np.linalg.norm(u) + eps
        u_hat = u / u_norm

        # 2) wrist vector relative to shoulder
        w_vec = w - s

        # 3) project wrist vector onto plane perpendicular to humerus axis
        w_proj = w_vec - np.dot(w_vec, u_hat) * u_hat
        w_proj_norm = np.linalg.norm(w_proj) + eps
        w_p = w_proj / w_proj_norm

        # 4) reference vector: if provided use it, else use a fallback
        if ref_vector is not None:
            r = np.asarray(ref_vector, dtype=float)
            r_proj = r - np.dot(r, u_hat) * u_hat
            r_proj_norm = np.linalg.norm(r_proj) + eps
            r_p = r_proj / r_proj_norm
        else:
            # fallback: construct a lateral reference using shoulder-elbow and global up
            # This is a weak fallback; better to supply a calibrated ref_vector per patient.
            global_up = np.array([0.0, -1.0, 0.0])  # image coords: negative y = up (adjust if needed)
            # make sure global_up not parallel to u_hat
            if abs(np.dot(global_up, u_hat)) > 0.95:
                global_up = np.array([0.0, 0.0, 1.0])
            r_proj = global_up - np.dot(global_up, u_hat) * u_hat
            r_proj_norm = np.linalg.norm(r_proj) + eps
            r_p = r_proj / r_proj_norm

        # 5) compute signed angle between r_p and w_p around axis u_hat
        cross = np.cross(r_p, w_p)
        cross_dot = np.dot(u_hat, cross)  # sign
        dot = np.dot(r_p, w_p)
        angle_rad = np.arctan2(cross_dot, dot)

        return np.degrees(angle_rad)
    
    @staticmethod
    def calculate_internal_rotation(shoulder, elbow, wrist, ref_vector=None):
        angle = AngleMath.calculate_signed_rotation(shoulder, elbow, wrist, ref_vector)
        if angle > 0:
            return abs(angle)
        return 0.0
    
    @staticmethod
    def calculate_external_rotation(shoulder, elbow, wrist, ref_vector=None):
        angle = AngleMath.calculate_signed_rotation(shoulder, elbow, wrist, ref_vector)
        if angle < 0:
            return abs(angle)
        return 0.0
