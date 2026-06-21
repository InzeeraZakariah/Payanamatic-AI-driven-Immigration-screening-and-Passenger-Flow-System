from pydantic import BaseModel
from typing import List, Optional

# Requests 
class FaceVerificationRequest(BaseModel):
    passport_number: str
    face_image: str

class ScreeningRequest(BaseModel):
    passport_number: str
    face_image: str  # base64 from camera

# Responses
class FaceVerificationResponse(BaseModel):
    passport_number: str
    full_name: str
    similarity_score: float
    verification_status: str

class ScreeningResponse(BaseModel):
    passport_number: str
    full_name: str
    risk_score: int
    risk_level: str
    assigned_lane: str
    reasons: List[str]
    verification_status: str
    similarity_score: float 

class PassengerResponse(BaseModel):
    passport_number: str
    full_name: str
    nationality: Optional[str]

    class Config:
        from_attributes = True
