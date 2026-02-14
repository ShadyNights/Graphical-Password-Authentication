import time
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import User
from app.schemas.auth_schema import RegisterRequest, AuthResponse
from app.security import (
    validate_challenge, generate_salt, hash_gpa_secret,
    encrypt_recognition_data, create_jwt_token,
    audit_log, keys
)
# Note: enforce_constant_time logic should be imported if strict timing is needed on register failure
# For now, we assume simple timing protection provided by hash steps

router = APIRouter()

@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Register a new user with graphical password.
    Stores Argon2id hash of: sorted_image_ids | quantized_click_points | salt | pepper
    """
    client_ip = request.client.host if request.client else "unknown"

    # Validate challenge nonce
    challenge = validate_challenge(req.challenge_id, req.username)
    if not challenge:
        audit_log("register_invalid_challenge", username=req.username, client_ip=client_ip)
        return AuthResponse(status="error", message="Invalid or expired challenge")

    # Check if username exists
    result = await db.execute(select(User).where(User.username == req.username))
    existing = result.scalar_one_or_none()
    if existing:
        audit_log("register_duplicate_user", username=req.username, client_ip=client_ip)
        return AuthResponse(status="error", message="Registration failed")

    # Generate salt and hash the GPA secret
    salt = generate_salt()
    points = [(p.x, p.y) for p in req.click_points]
    gpa_hash = hash_gpa_secret(req.selected_image_ids, points, salt)

    # Encrypt recognition image IDs with AES-256-GCM
    recognition_data = encrypt_recognition_data(req.selected_image_ids)

    # Create user
    user = User(
        username=req.username,
        gpa_hash=gpa_hash.encode("utf-8"),
        salt=salt,
        recognition_blob=recognition_data,
    )
    db.add(user)
    await db.commit()

    token = create_jwt_token(user.id, user.username)

    audit_log("register_success", username=req.username, client_ip=client_ip)

    debug_info = get_gpa_debug_info(req.selected_image_ids, points)
    return AuthResponse(
        status="success",
        message=f"Registration complete. DEBUG: {json.dumps(debug_info)}",
        token=token,
        risk_level="normal",
    )
