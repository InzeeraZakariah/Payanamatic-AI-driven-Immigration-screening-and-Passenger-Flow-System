from models import ScreeningResult

def save_screening_result(db,passenger_id,similarity_score,verification_status,risk_score,risk_level,assigned_lane,final_decision):

    result = ScreeningResult(
        passenger_id = passenger_id,
        similarity_score = str(similarity_score),
        verification_status = verification_status,
        risk_score = risk_score,
        risk_level = risk_level,
        assigned_lane = assigned_lane,
        final_decision = final_decision
    )

    db.add(result)

    db.commit()

    db.refresh(result)

    return result

def get_latest_result(db,passenger_id):
    return (db.query(ScreeningResult).filter(ScreeningResult.passenger_id == passenger_id).order_by(ScreeningResult.id.desc()).first())