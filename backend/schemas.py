from pydantic import BaseModel
from typing import List, Optional

class FaceVerificationRequest(BaseModel):
    passport_number: str
    face_image: str

class ScreeningRequest(BaseModel):
    passport_number: str
    face_image: str


class ScreeningResponse(BaseModel):
    passport_number: str
    full_name: str
    similarity_score: float
    verification_status: str
    risk_score: int
    risk_level: str
    assigned_lane: str
    final_decision: str
    reasons: List[str]


class DecisionUpdateRequest(BaseModel):
    decision: str
    officer_note: Optional[str] = None
