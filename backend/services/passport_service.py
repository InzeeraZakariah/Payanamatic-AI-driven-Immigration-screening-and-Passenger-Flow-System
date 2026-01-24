# backend/services/passport_service.py
import json

def get_passenger_by_passport(passport_number):
    with open("backend/data/passenger.json") as f:
        data = json.load(f)
    if data["passenger"]["passport_number"] == passport_number:
        return data  # return full JSON for risk_engine
    return None
