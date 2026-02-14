import json
import time
import secrets
import random
from typing import Optional
from app.config import settings
from app.security.audit import audit_log
from app.db.redis_client import redis_client

# Fallback in-memory store if Redis fails
_local_challenges: dict = {}

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
    
    challenge_data = {
        "created_at": time.time(),
        "used": False,
        "username": username,
        "image_pool": pool,
    }

    if redis_client:
        try:
            # Store with 5 minute TTL (300s)
            redis_client.setex(
                f"challenge:{challenge_id}",
                300,
                json.dumps(challenge_data)
            )
        except Exception:
            _local_challenges[challenge_id] = challenge_data
    else:
        _local_challenges[challenge_id] = challenge_data

    audit_log("challenge_issued", username=username)

    return {
        "challenge_id": challenge_id,
        "image_pool": [{"id": img["id"], "label": img["label"], "category": img["category"]} for img in pool],
    }


def validate_challenge(challenge_id: str, username: str) -> Optional[dict]:
    """Validate and consume a challenge nonce (one-time use)."""
    challenge_data = None
    
    # Try Redis first
    if redis_client:
        try:
            data_str = redis_client.get(f"challenge:{challenge_id}")
            if data_str:
                challenge_data = json.loads(data_str)
        except Exception:
            pass
    
    # Try local if not found (fallback)
    if not challenge_data:
        challenge_data = _local_challenges.get(challenge_id)

    if not challenge_data:
        return None

    if challenge_data.get("used"):
        audit_log("challenge_replay_attempt", username=username, details={"challenge_id": challenge_id})
        return None

    if challenge_data.get("username") != username:
        return None
        
    # Check expiry (Redis handles cleaning, but explicit check is good)
    if time.time() - challenge_data["created_at"] > 300:
        if redis_client:
            redis_client.delete(f"challenge:{challenge_id}")
        else:
            del _local_challenges[challenge_id]
        return None

    # Mark as used (Atomic delete in Redis to prevent replay? Or strict used flag?)
    # Deleting it is safest for one-time use.
    if redis_client:
        redis_client.delete(f"challenge:{challenge_id}")
    else:
        del _local_challenges[challenge_id]

    # Return the data (even if deleted, we have the variable)
    return challenge_data


def _cleanup_challenges():
    """Remove expired challenges (Only for local fallback)."""
    now = time.time()
    expired = [cid for cid, c in _local_challenges.items() if now - c["created_at"] > 300]
    for cid in expired:
        del _local_challenges[cid]
