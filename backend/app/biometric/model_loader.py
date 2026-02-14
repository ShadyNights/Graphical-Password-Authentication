import logging
import joblib
from pathlib import Path
from typing import Any

logger = logging.getLogger("gpa.ml")


MODEL_PATH = Path(__file__).parent.parent.parent / "ml" / "isolation_forest.pkl"


def load_model() -> dict:
    """Load model and user profiles from disk."""
    if MODEL_PATH.exists():
        try:
            data = joblib.load(MODEL_PATH)
            if isinstance(data, dict) and "model" in data:
                logger.info(f"Loaded biometric model + {len(data.get('profiles', {}))} profiles")
                return data
            
            return {"model": data, "profiles": {}}
        except Exception as e:
            logger.warning(f"Failed to load ML state: {e}")
    return {"model": None, "profiles": {}}


def save_model(model: Any, user_profiles: dict):
    """Save model and profiles."""
    if model is not None or user_profiles:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "model": model,
            "profiles": user_profiles
        }
        joblib.dump(state, MODEL_PATH)
        logger.info("Saved biometric ML state")
