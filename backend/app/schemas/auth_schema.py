from pydantic import BaseModel, Field
from typing import List, Optional


class Point(BaseModel):
    x: float = Field(..., ge=0.0, le=1.0, description="Normalized x-coord (0-1)")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalized y-coord (0-1)")


class ChallengeRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)


class ChallengeResponse(BaseModel):
    challenge_id: str
    image_pool: List[dict]  
    message: str = "Challenge issued"


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    challenge_id: str
    selected_image_ids: List[str] = Field(..., min_length=3, max_length=3)
    click_points: List[Point] = Field(..., min_length=6, max_length=6)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    challenge_id: str
    selected_image_ids: List[str] = Field(..., min_length=3, max_length=3)
    click_points: List[Point] = Field(..., min_length=6, max_length=6)
    mouse_metrics: Optional[dict] = None  
    device_fingerprint: Optional[str] = None  


class AuthResponse(BaseModel):
    status: str = "processing"
    challenge_id: Optional[str] = None
    message: str = "Authentication result pending"
    token: Optional[str] = None
    risk_level: Optional[str] = None  
