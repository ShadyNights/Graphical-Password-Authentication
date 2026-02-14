import secrets
from typing import List, Tuple
from hashlib import sha3_256
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.config import settings
from app.security.hsm_client import keys

# Argon2id Hasher
ph = PasswordHasher(
    memory_cost=settings.ARGON2_MEMORY_COST,
    time_cost=settings.ARGON2_TIME_COST,
    parallelism=settings.ARGON2_PARALLELISM,
    hash_len=32,
)

# Dynamic Grid based on Tolerance
# Tolerance is % of screen width/height that counts as "same cell"
# e.g. 0.10 (10%) of 1920 is 192px cell size
t = settings.CLICK_TOLERANCE
CELL_W = max(20, int(1920 * t))
CELL_H = max(20, int(1080 * t))
GRID_WIDTH = 1920 // CELL_W + 1
GRID_HEIGHT = 1080 // CELL_H + 1


def generate_salt() -> bytes:
    """Generate a 16-byte cryptographically secure random salt."""
    return secrets.token_bytes(16)


def grid_index(nx: float, ny: float) -> int:
    """Convert normalized coordinates to grid cell index."""
    x_pixel = nx * 1920
    y_pixel = ny * 1080
    gx = min(int(x_pixel / CELL_W), GRID_WIDTH - 1)
    gy = min(int(y_pixel / CELL_H), GRID_HEIGHT - 1)
    return gy * GRID_WIDTH + gx


def canonicalize_images(image_ids: List[str]) -> str:
    """Sort image IDs to ensure order independence."""
    return ",".join(sorted(image_ids))


def canonicalize_points(points: List[tuple]) -> str:
    """Convert points to grid cell indexes string."""
    indexes = [str(grid_index(x, y)) for x, y in points]
    return "|".join(indexes)


def get_gpa_debug_info(image_ids: List[str], points: List[tuple]) -> dict:
    """Return debug info about how inputs are interpreted."""
    return {
        "images_str": canonicalize_images(image_ids),
        "points_str": canonicalize_points(points),
        "grid_dims": f"{GRID_WIDTH}x{GRID_HEIGHT}",
        "cell_size": f"{CELL_W}x{CELL_H}",
        "tolerance": settings.CLICK_TOLERANCE
    }



def canonicalize_points(points: List[Tuple[float, float]]) -> str:
    """Output: '128|490|...|100'"""
    indexes = [str(grid_index(x, y)) for x, y in points]
    return "|".join(indexes)


def canonicalize_images(image_ids: List[str]) -> str:
    """Sort and join image IDs."""
    return ",".join(sorted(image_ids))


def build_secret_material(
    image_ids: List[str],
    points: List[Tuple[float, float]],
    salt: bytes
) -> bytes:
    """
    1. Canonicalize
    2. SHA3-256 prehash
    3. Append PEPPER (from HSM)
    """
    canonical_images = canonicalize_images(image_ids)
    canonical_points = canonicalize_points(points)

    combined = f"{canonical_images}|{canonical_points}".encode() + salt
    prehash = sha3_256(combined).digest()

    return prehash + keys.get_pepper()


def hash_gpa_secret(image_ids: List[str], points: List[Tuple[float, float]], salt: bytes) -> str:
    """Hash the GPA secret."""
    material = build_secret_material(image_ids, points, salt)
    return ph.hash(material)


def verify_gpa_secret(
    stored_hash: str,
    image_ids: List[str],
    points: List[Tuple[float, float]],
    salt: bytes
) -> bool:
    """Verify GPA secret."""
    material = build_secret_material(image_ids, points, salt)
    try:
        return ph.verify(stored_hash, material)
    except (VerifyMismatchError, Exception):
        return False


def generate_fake_hash():
    """Generate a fake hash to prevent timing attacks."""
    fake_salt = generate_salt()
    fake_data = sha3_256(secrets.token_bytes(32) + fake_salt).digest()
    ph.hash(fake_data + keys.get_pepper())
