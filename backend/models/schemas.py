from pydantic import BaseModel
from typing import List, Optional

class ScreeningRequest(BaseModel):
    passport_number: str
    face_image: str  # base64 from camera

class ScreeningResponse(BaseModel):
    passport_number: str
    full_name: str
    risk_score: int
    risk_level: str
    assigned_lane: str
    reasons: List[str]
    verification_status: str
