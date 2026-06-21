from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from schemas import FaceVerificationRequest, ScreeningRequest
from models import ScreeningResult, Passenger
from services.passport_service import get_passenger_by_passport,get_passenger_profile
from services.risk_engine import calculate_risk
from services.face_service import save_live_image, generate_embedding, verify_passenger_face
from services.screening_service import save_screening_result, get_latest_result
from services.dashboard_service import get_dashboard_summary
import httpx


app = FastAPI(title="Payanamatic: Immigration Screening System")

# Allow CORS for n8n/frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/passenger/{passport_number}")
def get_passenger(passport_number: str, db: Session = Depends(get_db)):

    profile = get_passenger_profile(db,passport_number)

    if not profile:
        raise HTTPException(status_code=404, detail="Passenger not found")

    print(profile)
    passenger = profile["passenger"]

    return {
        "passport_number": passenger.passport_number,
        "full_name": passenger.full_name,
        "gender": passenger.gender,
        "nationality": passenger.nationality,
        "date_of_birth": str(passenger.dob),

        "passport_details": profile["passport"],
        "visa_details": profile["visa"],
        "enquiry_form": profile["enquiry_form"],
        "travel_history": profile["travel_history"]
    }


@app.post("/verify-face")
def verify_face(req:FaceVerificationRequest, db: Session = Depends(get_db)):
    passenger = get_passenger_by_passport(db,req.passport_number)

    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    
    live_image_path = (save_live_image(req.passport_number, req.face_image))
    live_embedding = (generate_embedding(live_image_path))
    result = (verify_passenger_face(passenger.id,live_embedding))

    return {
        "passport_number":passenger.passport_number,
        "full_name": passenger.full_name,
        "similarity": result["similarity_score"],
        "verification_status": result["verification_status"]
    }

@app.post("/screen")
def screen(req: ScreeningRequest, db:Session = Depends(get_db)):
    profile = (get_passenger_profile(db, req.passport_number))

    if not profile:
        raise HTTPException(status_code=404, detail="Passenger not found")
    
    # Face verification
    live_image_path = (save_live_image(req.passport_number, req.face_image))
    live_embedding = (generate_embedding(live_image_path))
    verification = (verify_passenger_face(profile["passenger"].id, live_embedding))

    #  Risk calculation
    score, level, lane, reasons = (calculate_risk(profile))

    if (verification["verification_status"] != "VERIFIED"):
        final_decision = ("MANUAL_REVIEW")
    else:
        if level == "HIGH":
            final_decision = ("SECONDARY_SCREENING")
        else:
            final_decision = ("CLEARED")

    # Save to PostgreSQL
    save_screening_result(
        db=db,
        passenger_id = profile["passenger"].id,
        similarity_score = verification["similarity_score"],
        verification_status = verification["verification_status"],
        risk_score = score,
        risk_level = level,
        assigned_lane = lane,
        final_decision = final_decision
    )

    payload = {
            "passport_number": profile["passenger"].passport_number,
            "full_name": profile["passenger"].full_name,
            "gender": profile["passenger"].gender,
            "nationality": profile["passenger"].nationality,
            "date_of_birth": str(profile["passenger"].dob),
                "email": profile["passenger"].email,

            "similarity_score": verification["similarity_score"],
            "verification_status": verification["verification_status"],

            "risk_score": score,
            "risk_level": level,

            "assigned_lane": lane,
            "final_decision": final_decision,

            "reasons": reasons}

    return {"message": "Screening Completed", "result":payload}

@app.get("/screening-history")
def screening_history(db: Session = Depends(get_db)):
    records = (db.query(ScreeningResult).order_by(
            ScreeningResult.screened_at.desc()).all())

    results = []

    for r in records:

        results.append({
            "passenger_id": r.passenger_id,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "decision": r.final_decision,
            "screened_at": r.screened_at
        })

    return results

@app.get("/get-result/{passport_number}")
def get_result(passport_number: str, db:Session = Depends(get_db)):
    passenger = get_passenger_by_passport(db,passport_number)

    if not passenger:
        raise HTTPException(status_code=404,detail="Passenger not found")

    result = get_latest_result(db,passenger.id)

    if not result:
        return {"status":"NO_SCREENING_FOUND"}

    return {
        "passport_number": passport_number,
        "similarity_score": result.similarity_score,
        "verification_status": result.verification_status,
        "risk_score": result.risk_score,
        "risk_level": result.risk_level,
        "assigned_lane":  result.assigned_lane,
        "final_decision": result.final_decision,
        "screened_at": result.screened_at
    }

@app.post("/screen-through-n8n")
async def screen_through_n8n(req: ScreeningRequest):
    n8n_webhook_url = ("http://localhost:5678/webhook/screen-passenger")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            n8n_webhook_url,
            json=req.model_dump()
        )
    
    return response.json()

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    passengers = db.query(Passenger).count()
    screenings = db.query(ScreeningResult).count()
    cleared = (db.query(ScreeningResult).filter(ScreeningResult.final_decision== "CLEARED").count())
    review = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.final_decision == "MANUAL_REVIEW").count())

    secondary = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.final_decision == "SECONDARY_SCREENING") .count())

    return {
        "total_passengers": passengers,
        "total_screenings": screenings,
        "cleared": cleared,
        "manual_review": review,
        "secondary_screening": secondary
    }

@app.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models import ScreeningResult, Passenger
import requests

@app.put("/approve-screening/{screening_id}")
def approve_screening(screening_id: int,db: Session = Depends(get_db)):

    screening = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.id == screening_id)
        .first()
    )

    if not screening:
        raise HTTPException(status_code=404,detail="Screening not found"
)

    passenger = (
        db.query(Passenger)
        .filter(Passenger.id == screening.passenger_id)
        .first()
    )

    screening.final_decision = "CLEARED"

    db.commit()

    try:

        requests.post(
            "http://localhost:5678/webhook-test/passenger-alert",
            json={
                "full_name": passenger.full_name,
                "email": passenger.email,
                "passport_number": passenger.passport_number,
                "status": "CLEARED"
            }
        )

    except Exception as e:
        print("Email notification failed:", e)

    return {
        "message": "Passenger approved and notification sent"
    }
@app.get("/")
def health():
    return {
        "status": "success",
        "application": "Payanamatic",
        "message": "API Running Successfully"
    }