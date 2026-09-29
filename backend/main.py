from fastapi import FastAPI, HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from schemas import ScreeningRequest, DecisionUpdateRequest
from models import Passenger, ScreeningResult
from services.passport_service import get_passenger_profile, get_passenger_by_passport
from services.risk_engine import calculate_risk
from services.face_service import save_live_image, generate_embedding, verify_passenger_face
from services.screening_service import save_screening_result, get_latest_result
from services.dashboard_service import get_dashboard_summary
from services.notification_service import send_passenger_email

# DATABASE TABLES
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Payanamatic",
    description="AI-Based Smart Border & Immigration Screening System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {
        "status": "success",
        "application": "Payanamatic",
        "message": "API Running Successfully",
    }

# GET PASSENGER
@app.get("/passenger/{passport_number}")
def get_passenger(passport_number: str, db: Session = Depends(get_db)):
    profile = get_passenger_profile(db, passport_number)
    if not profile:
        raise HTTPException(status_code=404, detail="Passenger not found")

    passenger = profile["passenger"]
    return {
        "passport_number": passenger.passport_number,
        "full_name": passenger.full_name,
        "gender": passenger.gender,
        "nationality": passenger.nationality,
        "date_of_birth": str(passenger.dob),
        "email": passenger.email,
        "passport_details": profile["passport"],
        "visa_details": profile["visa"],
        "enquiry_form": profile["enquiry_form"],
        "travel_history": profile["travel_history"],
    }

@app.post("/screen")
async def screen(req: ScreeningRequest,db:Session=Depends(get_db)):
    print("\n========== SCREENING START ==========")
    print("Passport:",req.passport_number)

    profile=get_passenger_profile(db,req.passport_number)

    if not profile:
        raise HTTPException(status_code=404,detail="Passenger not found")

    passenger=profile["passenger"]

    try:
        live_image_path=save_live_image(
            req.passport_number,
            req.face_image
        )
        print("Live image saved:",live_image_path)
    except Exception as error:
        print("Image error:",error)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image: {error}"
        )

    try:
        live_embedding=generate_embedding(
            live_image_path
        )
        print("Embedding generated")
    except Exception as error:
        print("Embedding error:",error)
        raise HTTPException(
            status_code=400,
            detail=f"Face detection/embedding failed: {error}"
        )

    verification=verify_passenger_face(passenger.id,live_embedding)

    print("Verification:",verification)

    print("STEP 5 - BEFORE RISK CALCULATION")

    score,level,lane,reasons=calculate_risk(profile)

    print("STEP 6 - RISK:",score,level,lane,reasons)

    if verification["verification_status"]!="VERIFIED":
        final_decision="MANUAL_REVIEW"
    elif level=="HIGH":
        final_decision="SECONDARY_SCREENING"
    else:
        final_decision="CLEARED"

    print("STEP 7 - FINAL DECISION:",final_decision)

    score,level,lane,reasons=calculate_risk(profile)

    print("Risk:",score,level,lane)

    if verification["verification_status"]!="VERIFIED":
        final_decision="MANUAL_REVIEW"
    elif level=="HIGH":
        final_decision="SECONDARY_SCREENING"
    else:
        final_decision="CLEARED"

    print("Decision:",final_decision)

    screening_result=save_screening_result(
        db=db,
        passenger_id=passenger.id,
        similarity_score=verification["similarity_score"],
        verification_status=verification["verification_status"],
        risk_score=score,
        risk_level=level,
        assigned_lane=lane,
        final_decision=final_decision
    )

    print("Screening ID:",screening_result.id)

    # N8N
    email_sent=False

    if passenger.email:
        email_sent=await send_passenger_email(
            email=passenger.email,
            full_name=passenger.full_name,
            passport_number=passenger.passport_number,
            final_decision=final_decision,
            risk_level=level,
            risk_score=score
        )

    print("N8N email sent:",email_sent)

    # THIS IS WHAT THE FRONTEND RECEIVES
    response={
        "message":"Screening Completed",
        "result":{
            "screening_id":screening_result.id,
            "passport_number":passenger.passport_number,
            "full_name":passenger.full_name,
            "gender":passenger.gender,
            "nationality":passenger.nationality,
            "similarity_score":verification["similarity_score"],
            "verification_status":verification["verification_status"],
            "risk_score":score,
            "risk_level":level,
            "assigned_lane":lane,
            "final_decision":final_decision,
            "reasons":reasons,
            "email_sent":email_sent
        }
    }

    print("RETURNING RESULT:")
    print(response)
    print("========== SCREENING END ==========\n")

    return response

# GET LATEST RESULT
@app.get("/get-result/{passport_number}")
def get_result(passport_number: str, db: Session = Depends(get_db)):
    passenger = get_passenger_by_passport(db, passport_number)
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")

    result = get_latest_result(db, passenger.id)
    if not result:
        return {"status": "NO_SCREENING_FOUND"}

    return {
        "passport_number": passport_number,
        "similarity_score": float(result.similarity_score),
        "verification_status": result.verification_status,
        "risk_score": result.risk_score,
        "risk_level": result.risk_level,
        "assigned_lane": result.assigned_lane,
        "final_decision": result.final_decision,
        "screened_at": result.screened_at,
    }


# SCREENING HISTORY
@app.get("/screening-history")
def screening_history(db: Session = Depends(get_db)):
    records = (db.query(ScreeningResult).order_by(ScreeningResult.screened_at.desc()).all())

    results = []
    for record in records:
        passenger = db.query(Passenger).filter(Passenger.id == record.passenger_id).first()
        results.append({
            "passenger_id": record.passenger_id,
            "full_name": passenger.full_name if passenger else None,
            "passport_number": passenger.passport_number if passenger else None,
            "similarity_score": float(record.similarity_score),
            "verification_status": record.verification_status,
            "risk_score": record.risk_score,
            "risk_level": record.risk_level,
            "assigned_lane": record.assigned_lane,
            "decision": record.final_decision,
            "screened_at": record.screened_at,
        })

    return results


# DASHBOARD SUMMARY
@app.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)



# DASHBOARD
@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    passengers = db.query(Passenger).count()
    screenings = db.query(ScreeningResult).count()
    cleared = db.query(ScreeningResult).filter(ScreeningResult.final_decision == "CLEARED").count()
    review = db.query(ScreeningResult).filter(ScreeningResult.final_decision == "MANUAL_REVIEW").count()
    secondary = db.query(ScreeningResult).filter(ScreeningResult.final_decision == "SECONDARY_SCREENING").count()

    return {
        "total_passengers": passengers,
        "total_screenings": screenings,
        "cleared": cleared,
        "manual_review": review,
        "secondary_screening": secondary,
    }


# OFFICER CLEAR MANUAL REVIEW
@app.patch("/screening/{screening_id}/decision")
async def update_screening_decision(screening_id: int, req: DecisionUpdateRequest, db: Session = Depends(get_db)):
    allowed_decisions = ["CLEARED", "SECONDARY_SCREENING", "MANUAL_REVIEW"]

    if req.decision not in allowed_decisions:
        raise HTTPException(status_code=400, detail=f"Invalid decision. Allowed values: {allowed_decisions}")

    result = db.query(ScreeningResult).filter(ScreeningResult.id == screening_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Screening result not found")

    result.final_decision = req.decision
    db.commit()
    db.refresh(result)

    passenger = db.query(Passenger).filter(Passenger.id == result.passenger_id).first()

    # Send updated decision to n8n
    if passenger and passenger.email:
        await send_passenger_email(
            email=passenger.email,
            full_name=passenger.full_name,
            passport_number=passenger.passport_number,
            final_decision=result.final_decision,
            risk_level=result.risk_level,
            risk_score=result.risk_score,
        )

    return {
        "message": "Screening decision updated",
        "screening_id": result.id,
        "final_decision": result.final_decision,
    }


@app.post("/test-n8n")
async def test_n8n():
    success = await send_passenger_email(
        email="your-email@example.com",
        full_name="Test Passenger",
        passport_number="TEST123456",
        final_decision="CLEARED",
        risk_level="LOW",
        risk_score=10,
    )
    return {"n8n_email_sent": success}
