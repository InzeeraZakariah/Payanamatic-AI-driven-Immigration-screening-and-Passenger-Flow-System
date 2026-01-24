from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from backend.services.passport_service import get_passenger_by_passport
from backend.services.risk_engine import calculate_risk
from backend.services.face_service import store_face_image

# Request model
class ScreeningRequest(BaseModel):
    passport_number: str
    face_image: str

app = FastAPI(title="Immigration Screening System")

# Allow CORS for n8n/frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for screening results
SCREENING_RESULTS = {}

# --- FastAPI Endpoints ---

@app.post("/screen")
def screen_passenger(req: ScreeningRequest):
    passenger_data = get_passenger_by_passport(req.passport_number)
    if not passenger_data:
        raise HTTPException(status_code=404, detail="Passenger not found")

    # Store face image
    store_face_image(req.passport_number, req.face_image)

    # Calculate risk
    score, level, lane, reasons = calculate_risk(passenger_data)

    payload = {
        "passport_number": req.passport_number,
        "full_name": passenger_data["passenger"]["full_name"],
        "risk_score": score,
        "risk_level": level,
        "assigned_lane": lane,
        "verification_status": "Verified Successfully",
        "reasons": reasons
    }

    SCREENING_RESULTS[req.passport_number] = payload
    return {"message": "Screening started", "result": payload}

@app.get("/get-result/{passport_number}")
def get_result(passport_number: str):
    return SCREENING_RESULTS.get(passport_number, {"status": "PENDING"})

@app.get("/")
def root():
    return {"message": "Immigration Screening API is running"}

# --- Integration with n8n ---
@app.post("/screen-through-n8n")
async def screen_through_n8n(req: ScreeningRequest):
    """
    Proxy endpoint: frontend calls this, backend forwards to n8n webhook,
    n8n calls /screen, applies decision logic, responds back.
    """
    n8n_webhook_url = "http://localhost:5678/webhook/screen-passenger"

    async with httpx.AsyncClient() as client:
        response = await client.post(n8n_webhook_url, json=req.dict())

    result = response.json()
    SCREENING_RESULTS[req.passport_number] = result["result"]
    return result
