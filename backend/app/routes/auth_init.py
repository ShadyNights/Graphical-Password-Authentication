from fastapi import APIRouter, Request
from app.schemas.auth_schema import ChallengeRequest, ChallengeResponse
from app.security import create_challenge, check_rate_limit, IMAGE_POOL

router = APIRouter()

@router.post("/challenge", response_model=ChallengeResponse)
async def request_challenge(req: ChallengeRequest, request: Request):
    """
    Issue a one-time challenge with shuffled image pool.
    Called before both registration and login.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Always return a challenge to prevent enumeration, even if rate limited
    if not check_rate_limit(client_ip):
        pass  # Logged internally in security module

    challenge = create_challenge(req.username)
    return ChallengeResponse(
        challenge_id=challenge["challenge_id"],
        image_pool=challenge["image_pool"],
        message="Challenge issued"
    )


@router.get("/images")
async def get_image_metadata():
    """Return all available image categories for front-end rendering."""
    return {"images": IMAGE_POOL}
