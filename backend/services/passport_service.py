from sqlalchemy.orm import Session
from models import Passenger, PassengerImage, PassportDetail, VisaDetail, EnquiryForm, TravelHistory

def get_passenger_by_passport(db:Session, passport_number: str):
    return (db.query(Passenger).filter(Passenger.passport_number==passport_number).first())


def get_passenger_profile(db:Session, passport_number:str):
    passenger = get_passenger_by_passport(db, passport_number)

    if not passenger:
        return "No passenger registered"
    
    passport = (db.query(PassportDetail).filter(PassportDetail.passenger_id == passenger.id).first())
    visa = (db.query(VisaDetail).filter(VisaDetail.passenger_id == passenger.id).first())
    enquiry = (db.query(EnquiryForm).filter(EnquiryForm.passenger_id == passenger.id).first())
    history = (db.query(TravelHistory).filter(TravelHistory.passenger_id == passenger.id).all())
    images = (db.query(PassengerImage).filter(PassengerImage.passenger_id == passenger.id).first())

    return {
        "passenger":passenger,
        "passport":passport,
        "visa": visa,
        "enquiry_form": enquiry,
        "travel_history": history,
        "images": images
    }