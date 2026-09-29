from utils.date_utils import days_until


def calculate_risk(passenger_data: dict):
    score = 0
    reasons = []

    passport = passenger_data.get("passport")
    visa = passenger_data.get("visa")
    enquiry = passenger_data.get("enquiry_form")
    history = passenger_data.get("travel_history") or []

    # MISSING DATA
    if not visa:
        score += 20
        reasons.append("Visa information unavailable")
    else:
        visa_days_left = days_until(visa.expiry_date)
        if visa_days_left < 30:
            score += 15
            reasons.append("Visa expiry is near")

    # ENQUIRY
    if enquiry:
        if enquiry.duration_of_stay_days and enquiry.duration_of_stay_days > 30:
            score += 10
            reasons.append("Long duration of stay")

        if enquiry.return_ticket is False:
            score += 20
            reasons.append("No return ticket")

        if enquiry.employment_status and enquiry.employment_status.lower() == "unemployed":
            score += 10
            reasons.append("Unstable employment")

    # TRAVEL HISTORY
    for trip in history:
        if trip.overstay_flag:
            score += 40
            reasons.append("Previous overstay detected")

        if trip.deportation_flag:
            score += 50
            reasons.append("Previous deportation detected")

    # RISK LEVEL
    if score <= 20:
        risk_level = "LOW"
        lane = "FAST_LANE"
    elif score <= 50:
        risk_level = "MEDIUM"
        lane = "ASSISTED_COUNTER"
    else:
        risk_level = "HIGH"
        lane = "SECONDARY_SCREENING"

    return score, risk_level, lane, reasons
