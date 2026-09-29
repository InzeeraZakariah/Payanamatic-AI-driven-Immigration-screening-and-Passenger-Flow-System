from models import ScreeningResult

def save_screening_result(db, passenger_id: int, similarity_score: float, verification_status: str, risk_score: int, risk_level: str, assigned_lane: str, final_decision: str) -> ScreeningResult:
    result = ScreeningResult(
        passenger_id=passenger_id,
        similarity_score=str(similarity_score),  # stored as string in DB
        verification_status=verification_status,
        risk_score=risk_score,
        risk_level=risk_level,
        assigned_lane=assigned_lane,
        final_decision=final_decision,
    )

    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_latest_result(db, passenger_id: int) -> ScreeningResult | None:
    return (
        db.query(ScreeningResult)
        .filter(ScreeningResult.passenger_id == passenger_id)
        .order_by(ScreeningResult.screened_at.desc())
        .first()
    )
