import time
import secrets
import random
from typing import Optional, List
from app.config import settings
from app.security.audit import audit_log

# In-Memory Stores (Redis replacement for demo)
# Challenge nonces: {challenge_id: {created_at, used, image_pool, username}}
_challenges: dict = {}

# Image pool — 20 abstract images
IMAGE_POOL = [
    {"id": f"img_{i:02d}", "label": f"Image {i}", "category": cat}
    for i, cat in enumerate([
        "mountain", "ocean", "forest", "desert", "city",
        "space", "underwater", "sunset", "snow", "volcano",
        "garden", "lighthouse", "bridge", "castle", "waterfall",
        "cave", "island", "aurora", "canyon", "meadow",
    ])
]


def create_challenge(username: str) -> dict:
    """Create a one-time server challenge with nonce and shuffled image pool."""
    challenge_id = secrets.token_urlsafe(32)
    pool = random.sample(IMAGE_POOL, settings.TOTAL_IMAGES_SHOWN)

    _challenges[challenge_id] = {
        "created_at": time.time(),
        "used": False,
        "username": username,
        "image_pool": pool,
    }

    _cleanup_challenges()
    audit_log("challenge_issued", username=username)

    return {
        "challenge_id": challenge_id,
        "image_pool": [{"id": img["id"], "label": img["label"], "category": img["category"]} for img in pool],
    }


def validate_challenge(challenge_id: str, username: str) -> Optional[dict]:
    """Validate and consume a challenge nonce (one-time use)."""
    challenge = _challenges.get(challenge_id)
    if not challenge:
        return None
    if challenge["used"]:
        audit_log("challenge_replay_attempt", username=username, details={"challenge_id": challenge_id})
        return None
    if challenge["username"] != username:
        return None
    if time.time() - challenge["created_at"] > 300:  # 5 min expiry
        del _challenges[challenge_id]
        return None

    challenge["used"] = True
    return challenge


def _cleanup_challenges():
    """Remove expired challenges."""
    now = time.time()
    expired = [cid for cid, c in _challenges.items() if now - c["created_at"] > 300]
    for cid in expired:
        del _challenges[cid]
