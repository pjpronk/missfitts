import math


class HapticForceGenerator:
    def __init__(self, f_max: float = 1.0, sigma: float = 10.0):
        self.f_max = f_max  # peak force magnitude in Newtons
        self.sigma = sigma  # angular spread in degrees; peak force occurs at this distance

    def calculate_force(self, x_error: float, y_error: float, dead_zone: float = 1.0) -> tuple[float, float]:
        """Returns (fx, fy): Gaussian-shaped guidance toward the target.
        Force peaks at sigma degrees from the target and decays smoothly to zero
        both far away and on-target, preventing oscillation.
        No force inside dead_zone degrees of the target."""
        magnitude = math.sqrt(x_error ** 2 + y_error ** 2)
        if magnitude < max(dead_zone, 1e-6):
            return 0.0, 0.0
        envelope = math.exp(-(magnitude ** 2) / (2 * self.sigma ** 2))
        f = self.f_max * (magnitude / self.sigma ** 2) * envelope
        return f * (x_error / magnitude), f * (y_error / magnitude)
