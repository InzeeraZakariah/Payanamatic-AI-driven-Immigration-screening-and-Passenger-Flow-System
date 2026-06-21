from sqlalchemy import func
from models import ScreeningResult, Passenger


def get_dashboard_summary(db):

    total_screenings = (
        db.query(ScreeningResult)
        .count()
    )

    verified = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.verification_status == "VERIFIED"
        )
        .count()
    )

    manual_review = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.final_decision == "MANUAL_REVIEW"
        )
        .count()
    )

    high_risk = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.risk_level == "HIGH"
        )
        .count()
    )

    medium_risk = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.risk_level == "MEDIUM"
        )
        .count()
    )

    low_risk = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.risk_level == "LOW"
        )
        .count()
    )

    fast_lane = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.assigned_lane == "FAST_LANE"
        )
        .count()
    )

    assisted_counter = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.assigned_lane == "ASSISTED_COUNTER"
        )
        .count()
    )

    secondary_screening = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.assigned_lane == "SECONDARY_SCREENING"
        )
        .count()
    )

    recent_screenings = (
        db.query(
            ScreeningResult,
            Passenger.full_name,
            Passenger.passport_number
        )
        .join(
            Passenger,
            Passenger.id == ScreeningResult.passenger_id
        )
        .order_by(
            ScreeningResult.screened_at.desc()
        )
        .limit(10)
        .all()
    )

    recent = []

    for result, name, passport in recent_screenings:

        recent.append({
            "id": result.id,
            "full_name": name,
            "passport_number": passport,
            "risk_level": result.risk_level,
            "verification_status": result.verification_status,
            "final_decision": result.final_decision,
            "screened_at": str(result.screened_at)
        })

    return {
        "total_screenings": total_screenings,
        "verified": verified,
        "manual_review": manual_review,

        "risk_distribution": {
            "LOW": low_risk,
            "MEDIUM": medium_risk,
            "HIGH": high_risk
        },

        "lane_distribution": {
            "FAST_LANE": fast_lane,
            "ASSISTED_COUNTER": assisted_counter,
            "SECONDARY_SCREENING": secondary_screening
        },

        "recent_screenings": recent
    }