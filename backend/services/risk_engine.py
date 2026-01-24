from backend.utils.date_utils import days_until

def calculate_risk(passenger_data: dict):
    score = 0
    reasons = []

    passport = passenger_data["passport"]
    visa = passenger_data["visa"]
    enquiry = passenger_data["enquiry_form"]
    history = passenger_data["travel_history"]

    # Visa expiry risk
    visa_days_left = days_until(visa["expiry_date"])
    if visa_days_left < 30:
        score += 15
        reasons.append("Visa expiry is near")

    # Stay duration risk
    if enquiry["duration_of_stay_days"] > 30:
        score += 10
        reasons.append("Long duration of stay")

    # Return ticket risk
    if not enquiry["return_ticket"]:
        score += 20
        reasons.append("No return ticket")

    # Employment stability
    if enquiry["employment_status"] == "Unemployed":
        score += 10
        reasons.append("Unstable employment")
 
    # Travel history risk
    for trip in history:
        if trip["overstay_flag"]:
            score += 40
            reasons.append("Previous overstay detected")

        if trip["deportation_flag"]:
            score += 50
            reasons.append("Previous deportation detected")

    # Risk classification
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
