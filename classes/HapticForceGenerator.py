import math


class HapticForceGenerator:
    def __init__(self, kp: float = 1.0, kd: float = 0.1):
        self.kp = kp
        self.kd = kd

    def calculate_force(
        self,
        yaw_error: float,
        pitch_error: float,
        vx: float = 0.0,
        vy: float = 0.0,
    ) -> tuple[float, float]:
        """Returns (fx, fy) using a P term on angular error and a D term on
        actual end-effector velocity for mechanical damping."""
        fx = self.kp * yaw_error   - self.kd * vx
        fy = self.kp * pitch_error - self.kd * vy
        return fx, fy
