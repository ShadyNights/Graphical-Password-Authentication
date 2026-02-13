import logging
import numpy as np
from typing import List
from sklearn.ensemble import IsolationForest

from .feature_extractor import extract_feature_vector
from .drift_detection import UserProfile
from .model_loader import load_model, save_model

logger = logging.getLogger("gpa.ml")


class BiometricRiskEngine:
    """
    Hybrid Anomaly Detection:
    1. Global Isolation Forest (General Bot Detection)
    2. Per-User Z-Score Profiling (Account Takeover / Drift Detection)
    """

    def __init__(self, min_training_samples: int = 50):
        self._model = None
        self._training_data: List[List[float]] = []
        self._user_profiles: dict[str, UserProfile] = {}
        self._min_samples = min_training_samples
        self._is_trained = False
        
        # Load state
        data = load_model()
        self._model = data.get("model")
        self._user_profiles = data.get("profiles", {})
        if self._model:
            self._is_trained = True

    def record_human_session(self, username: str, features: List[float]):
        """
        Online learning: Update global training data AND user-specific profile.
        """
        # 1. Global training
        self._training_data.append(features)
        if len(self._training_data) >= self._min_samples and not self._is_trained:
            self.train()
        
        # 2. Per-user adaptive profiling
        try:
            if username not in self._user_profiles:
                self._user_profiles[username] = UserProfile(username)
            
            self._user_profiles[username].update(features)
            
            # Periodic save
            if len(self._training_data) % 10 == 0:
                save_model(self._model, self._user_profiles)
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")

    def train(self):
        """Train global Isolation Forest."""
        if len(self._training_data) < 10: return
        
        X = np.array(self._training_data)
        self._model = IsolationForest(contamination=0.05, random_state=42)
        self._model.fit(X)
        self._is_trained = True
        save_model(self._model, self._user_profiles)
        logger.info(f"Retrained global Isolation Forest on {len(self._training_data)} samples")

    def compute_risk(self, username: str, features: List[float]) -> dict:
        """
        Compute risk using Global ML + Personal Drift Detection.
        """
        result = {
            "ml_score": 0.0,
            "ml_risk_level": "unknown",
            "ml_available": False,
            "drift_score": 0.0,
            "anomalies": []
        }

        # 1. Global ML Check
        if self._is_trained and self._model:
            try:
                score = self._model.decision_function([features])[0]
                result["ml_score"] = round(float(score), 4)
                if score > -0.2: result["ml_risk_level"] = "normal"
                elif score > -0.5: result["ml_risk_level"] = "suspicious"
                else: result["ml_risk_level"] = "bot_likely"
                result["ml_available"] = True
            except Exception: pass

        # 2. Personal Drift Check (Z-Score)
        try:
            profile = self._user_profiles.get(username)
            if profile and profile.count > 5:
                z_scores = profile.z_scores(features)
                max_z = np.max(z_scores)
                result["drift_score"] = round(float(max_z), 2)
                
                # If any feature deviates > 3 sigma -> Anomaly
                if max_z > 3.0:
                     result["anomalies"].append(f"drift_z_score_{max_z}")
                     # Escalate risk if drift is extreme
                     if result["ml_risk_level"] == "normal":
                         result["ml_risk_level"] = "suspicious"
        except Exception as e:
            logger.error(f"Drift check error: {e}")

        return result

    @property
    def is_trained(self) -> bool:
        return self._is_trained


# Singleton ML engine
risk_engine = BiometricRiskEngine()
