from models import Passenger, ScreeningResult

def get_dashboard_summary(db):
    total_screenings = db.query(ScreeningResult).count()

    verified = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.verification_status == "VERIFIED")
        .count()
    )

    manual_review = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.final_decision == "MANUAL_REVIEW")
        .count()
    )

    low_risk = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.risk_level == "LOW")
        .count()
    )

    medium_risk = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.risk_level == "MEDIUM")
        .count()
    )

    high_risk = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.risk_level == "HIGH")
        .count()
    )

    fast_lane = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.assigned_lane == "FAST_LANE")
        .count()
    )

    assisted_counter = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.assigned_lane == "ASSISTED_COUNTER")
        .count()
    )

    secondary_screening = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.assigned_lane == "SECONDARY_SCREENING")
        .count()
    )

    recent_records = (
        db.query(ScreeningResult, Passenger)
        .join(Passenger, ScreeningResult.passenger_id == Passenger.id)
        .order_by(ScreeningResult.screened_at.desc())
        .limit(10)
        .all()
    )

    recent = [
        {
            "id": result.id,
            "passenger_id": result.passenger_id,
            "full_name": passenger.full_name,
            "passport_number": passenger.passport_number,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "verification_status": result.verification_status,
            "final_decision": result.final_decision,
            "screened_at": result.screened_at,
        }
        for result, passenger in recent_records
    ]

    return {
        "total_screenings": total_screenings,
        "verified": verified,
        "manual_review": manual_review,
        "risk_distribution": {
            "LOW": low_risk,
            "MEDIUM": medium_risk,
            "HIGH": high_risk,
        },
        "lane_distribution": {
            "FAST_LANE": fast_lane,
            "ASSISTED_COUNTER": assisted_counter,
            "SECONDARY_SCREENING": secondary_screening,
        },
        "recent_screenings": recent,
    }
