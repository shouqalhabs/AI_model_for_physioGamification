class FirstGame:

    def __init__(self):
        self.max_angle = 0

    def update(self, data):
        angle = data["left_shoulder"]
        if angle > self.max_angle:
            self.max_angle = angle

        return self.max_angle
