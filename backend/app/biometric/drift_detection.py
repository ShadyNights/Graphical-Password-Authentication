import numpy as np
from typing import List


class UserProfile:
    """
    Per-user behavioral profile for self-learning biometrics.
    Tracks online mean/variance of key features using Welford's algorithm.
    """
    def __init__(self, username: str):
        self.username = username
        self.count = 0
        # Tracks: [velocity_variance, click_entropy, curvature, dwell_time]
        self.means = np.zeros(4)
        self.M2 = np.zeros(4)  # Sum of squares of differences

    def update(self, features: List[float]):
        """Update profile with new feature vector (online learning)."""
        # Feature indices: 0=vel_var, 2=entropy, 3=curvature, 4=dwell
        selected = np.array([features[0], features[2], features[3], features[4]])
        
        self.count += 1
        delta = selected - self.means
        self.means += delta / self.count
        delta2 = selected - self.means
        self.M2 += delta * delta2

    def z_scores(self, features: List[float]) -> np.ndarray:
        """Calculate Z-scores of current features against history."""
        if self.count < 2:
            return np.zeros(4)
        
        variances = self.M2 / (self.count - 1)
        stds = np.sqrt(variances)
        
        # Avoid division by zero
        stds[stds < 1e-6] = 1.0
        
        selected = np.array([features[0], features[2], features[3], features[4]])
        return np.abs((selected - self.means) / stds)
