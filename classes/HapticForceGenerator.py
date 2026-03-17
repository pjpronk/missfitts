import time


class HapticForceGenerator:
    def __init__(self, kp: float = 1.0, kd: float = 0.0):
        self.kp = kp
        self.kd = kd
        self._last_error = (0.0, 0.0)
        self._last_time = time.monotonic()

    def calculate_force(self, yaw_error: float, pitch_error: float) -> tuple[float, float]:
        """Returns (fx, fy) from a PD controller on angular error in degrees."""
        now = time.monotonic()
        dt = now - self._last_time

        if dt > 0:
            dyaw   = (yaw_error   - self._last_error[0]) / dt
            dpitch = (pitch_error - self._last_error[1]) / dt
        else:
            dyaw, dpitch = 0.0, 0.0

        self._last_error = (yaw_error, pitch_error)
        self._last_time = now

        fx = self.kp * yaw_error   + self.kd * dyaw
        fy = self.kp * pitch_error + self.kd * dpitch
        return fx, fy
