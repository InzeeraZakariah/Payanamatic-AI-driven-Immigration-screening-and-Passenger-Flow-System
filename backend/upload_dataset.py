import os
import json
from datetime import datetime
from database import SessionLocal, Base, engine
from models import Passenger, PassportDetail, VisaDetail, EnquiryForm, TravelHistory

def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()

def clear_database(db):
    print("\nClearing old database data...")
    db.query(TravelHistory).delete()
    db.query(EnquiryForm).delete()
    db.query(VisaDetail).delete()
    db.query(PassportDetail).delete()
    db.query(Passenger).delete()
    db.commit()
    print("Old data deleted successfully.")

def load_passenger_json(db, json_file):
    print(f"\nLoading: {os.path.basename(json_file)}")
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    passenger_data = data["passenger"]
    passport_data = data["passport"]
    visa_data = data["visa"]
    enquiry_data = data["enquiry_form"]
    history_data = data.get("travel_history", [])

    passenger = Passenger(
        full_name=passenger_data["full_name"],
        gender=passenger_data.get("gender"),
        dob=parse_date(passenger_data.get("date_of_birth")),
        nationality=passenger_data.get("nationality"),
        passport_number=passenger_data["passport_number"],
        email=passenger_data.get("email")
    )
    db.add(passenger)
    db.flush()

    passport = PassportDetail(
        passenger_id=passenger.id,
        issue_country=passport_data.get("issue_country"),
        issue_date=parse_date(passport_data.get("issue_date")),
        expiry_date=parse_date(passport_data.get("expiry_date")),
        passport_type=passport_data.get("passport_type"),
        passport_photo=passport_data.get("passport_photo")
    )
    db.add(passport)

    visa = VisaDetail(
        passenger_id=passenger.id,
        visa_type=visa_data.get("visa_type"),
        issue_date=parse_date(visa_data.get("issue_date")),
        expiry_date=parse_date(visa_data.get("expiry_date")),
        entry_type=visa_data.get("entry_type"),
        sponsor_type=visa_data.get("sponsor_type")
    )
    db.add(visa)

    countries = enquiry_data.get("countries_visited_last_5_years", [])
    if isinstance(countries, list):
        countries = ", ".join(countries)

    enquiry = EnquiryForm(
        passenger_id=passenger.id,
        purpose_of_visit=enquiry_data.get("purpose_of_visit"),
        event_type=enquiry_data.get("event_type"),
        duration_of_stay_days=enquiry_data.get("duration_of_stay_days"),
        address_of_stay=enquiry_data.get("address_of_stay"),
        host_relation=enquiry_data.get("host_relation"),
        return_ticket=enquiry_data.get("return_ticket"),
        employment_status=enquiry_data.get("employment_status"),
        monthly_income_range=enquiry_data.get("monthly_income_range"),
        previous_visits_count=enquiry_data.get("previous_visits_count"),
        countries_visited_last_5_years=countries
    )
    db.add(enquiry)

    for trip in history_data:
        history = TravelHistory(
            passenger_id=passenger.id,
            country=trip.get("country"),
            visit_year=trip.get("visit_year"),
            overstay_flag=trip.get("overstay_flag", False),
            deportation_flag=trip.get("deportation_flag", False)
        )
        db.add(history)

    db.commit()
    print(f"Loaded successfully: {passenger.full_name} ({passenger.passport_number})")

def seed_database():
    print("\n======================================")
    print(" PAYANAMATIC DATABASE SEEDING")
    print("======================================")

    db = SessionLocal()

    try:
        print("\nChecking database tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables ready.")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        dataset_path = os.path.join(BASE_DIR, "..", "dataset")

        if not os.path.exists(dataset_path):
            dataset_path = os.path.join(BASE_DIR, "dataset")

        dataset_path = os.path.abspath(dataset_path)

        print(f"\nDataset folder:\n{dataset_path}")

        if not os.path.isdir(dataset_path):
            print("\nERROR: Dataset folder not found.")
            print("\nExpected either:")
            print(os.path.join(BASE_DIR, "..", "dataset"))
            print(os.path.join(BASE_DIR, "dataset"))
            return

        print("\nFiles inside dataset folder:")
        for file in os.listdir(dataset_path):
            print("  ", file)

        clear_database(db)

        json_files = sorted([
            os.path.join(dataset_path, file)
            for file in os.listdir(dataset_path)
            if file.lower().endswith(".json")
        ])

        if not json_files:
            print("\nERROR: No JSON files found.")
            return

        print(f"\nFound {len(json_files)} JSON file(s).")

        for json_file in json_files:
            try:
                load_passenger_json(db, json_file)
            except Exception as error:
                db.rollback()
                print(f"\nERROR loading {os.path.basename(json_file)}")
                print(error)

        print("\n======================================")
        print(" DATABASE VERIFICATION")
        print("======================================")

        passenger_count = db.query(Passenger).count()
        passport_count = db.query(PassportDetail).count()
        visa_count = db.query(VisaDetail).count()
        enquiry_count = db.query(EnquiryForm).count()
        history_count = db.query(TravelHistory).count()

        print(f"Passengers       : {passenger_count}")
        print(f"Passport Details : {passport_count}")
        print(f"Visa Details     : {visa_count}")
        print(f"Enquiry Forms    : {enquiry_count}")
        print(f"Travel History   : {history_count}")

        print("\n======================================")
        print(" DATABASE SEEDING COMPLETED")
        print("======================================\n")

    except Exception as error:
        db.rollback()
        print("\nDATABASE SEEDING FAILED:")
        print(error)

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
