import os
import traceback

from database import sessionLocal
from models import Passenger, PassengerImage, VisaDetail, EnquiryForm, TravelHistory, PassportDetail

from services.face_service import generate_embedding
from services.chroma_service import save_embedding

import pandas as pd

DATASET_DIR = "dataset"

passengers_df = pd.read_csv(os.path.join("dataset", "passengers.csv"))
passport_details_df = pd.read_csv(os.path.join("dataset", "passport_details.csv"))
travel_history_df = pd.read_csv(os.path.join("dataset", "travel_history.csv"))
visa_details_df = pd.read_csv(os.path.join("dataset", "visa_details.csv"))
enquiry_forms_df = pd.read_csv(os.path.join("dataset", "enquiry_forms.csv"))


def parse_filename(filename):
    """
    Expected format:
    Inzeera_2024_28.jpg

    Returns:
    name, photo_year, age
    """
    filename = os.path.splitext(filename)[0]
    parts = filename.split("_")

    if len(parts) != 3:
        raise ValueError(
            f"Invalid filename format: {filename}\n"
            "Expected: Name_Year_Age.jpg"
        )

    name = parts[0]
    photo_year = int(parts[1])
    age = int(parts[2])

    return name, photo_year, age


def import_dataset():

    db = sessionLocal()

    total_passengers = 0
    total_images = 0

    try:

        for folder_name in os.listdir(DATASET_DIR):

            folder_path = os.path.join(DATASET_DIR, folder_name)

            if not os.path.isdir(folder_path):
                continue

            passenger_name = folder_name

            print(f"\nProcessing Passenger: {passenger_name}")

            # Check if passenger already exists
            passenger = (
                db.query(Passenger)
                .filter(Passenger.full_name == passenger_name)
                .first()
            )

            if not passenger:
                passenger_row = passengers_df[passengers_df["full_name"] == passenger_name]

                if passenger_row.empty:
                    print(f"No CSV record found for {passenger_name}")
                    continue

                passenger_data = passenger_row.iloc[0]
                dob = pd.to_datetime(passenger_data["date_of_birth"]).date()

                passenger = Passenger(
                    passport_number=passenger_data["passport_number"],
                    full_name=passenger_data["full_name"],
                    gender=passenger_data["gender"],
                    nationality=passenger_data["nationality"],
                    dob=dob,
                    email=passenger_data["email"]
                )

                db.add(passenger)
                db.commit()
                db.refresh(passenger) 

                try:

                    # Passport details
                    passport_row = passport_details_df[passport_details_df["passport_number"] == passenger.passport_number]
                    passport_data = passport_row.iloc[0]
                    passport_record = PassportDetail(
                        passenger_id=passenger.id,
                        passport_number=passenger.passport_number,
                        passport_type=passport_data["passport_type"],
                        issuing_country=passport_data["issuing_country"],
                        issue_date=pd.to_datetime(passport_data["issue_date"]).date(),
                        expiry_date=pd.to_datetime(passport_data["expiry_date"]).date()
                    )
                    db.add(passport_record)

                    # Visa details
                    visa_row = visa_details_df[
                        visa_details_df["passport_number"] == passenger.passport_number
                    ]
                    visa_data = visa_row.iloc[0]
                    visa_record = VisaDetail(
                        passenger_id=passenger.id,
                        visa_type=visa_data["visa_type"],
                        issue_date=pd.to_datetime(visa_data["issue_date"]).date(),
                        expiry_date=pd.to_datetime(visa_data["expiry_date"]).date()
                    )
                    db.add(visa_record)

                    # Enquiry form
                    enquiry_row = enquiry_forms_df[
                        enquiry_forms_df["passport_number"] == passenger.passport_number
                    ]
                    enquiry_data = enquiry_row.iloc[0]
                    enquiry_record = EnquiryForm(
                        passenger_id=passenger.id,
                        purpose_of_visit=enquiry_data["purpose_of_visit"],
                        destination_address=enquiry_data["destination_address"],
                        duration_of_stay_days=int(enquiry_data["duration_of_stay_days"]),
                        return_ticket=str(enquiry_data["return_ticket"]).lower() == "true",
                        employment_status=enquiry_data["employment_status"]
                    )
                    db.add(enquiry_record)

                    # Travel History
                    history_row = travel_history_df[
                        travel_history_df["passport_number"] == passenger.passport_number
                    ]
                    for _, history in history_row.iterrows():
                        history_record = TravelHistory(
                            passenger_id=passenger.id,
                            country=history["country"],
                            arrival_date=pd.to_datetime(history["arrival_date"]).date(),
                            departure_date=pd.to_datetime(history["departure_date"]).date(),
                            overstay_flag=str(history["overstay_flag"]).lower() == "true",
                            deportation_flag=str(history["deportation_flag"]).lower() == "true"
                        )
                        db.add(history_record)

                    db.commit()
                    total_passengers += 1
                    print(f"Created Passenger: {passenger.full_name}")

                except Exception as e:
                    db.rollback()
                    print(f"Failed to insert related records for {passenger_name}: {e}")
                    traceback.print_exc()
                    continue

            else:
                print(f"Passenger already exists: {passenger_name}, skipping record creation.")

            # Process Images — skip if already imported
            existing_images = db.query(PassengerImage).filter(
                PassengerImage.passenger_id == passenger.id
            ).count()

            if existing_images > 0:
                print(f"Images already imported for {passenger_name}, skipping.")
                continue

            for image_file in os.listdir(folder_path):

                if not image_file.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue

                image_path = os.path.join(folder_path, image_file)

                try:
                    (name, photo_year, age) = parse_filename(image_file)
                    print(f"Generating embedding for: {image_file}")

                    # Save image metadata
                    image_record = PassengerImage(
                        passenger_id=passenger.id,
                        image_path=image_path,
                        photo_year=photo_year,
                        age_at_capture=age
                    )
                    db.add(image_record)
                    db.commit()
                    db.refresh(image_record)

                    # Generate embedding
                    embedding = generate_embedding(image_path)

                    # Store in ChromaDB
                    save_embedding(
                        passenger_id=passenger.id,
                        image_id=image_record.id,
                        full_name=passenger.full_name,
                        photo_year=photo_year,
                        age=age,
                        embedding=embedding
                    )

                    total_images += 1
                    print(f"Imported: {image_file}")

                except Exception as e:
                    print(f"\nFailed: {image_file}")
                    traceback.print_exc()

        print("\nImport Complete")
        print(f"Passengers Imported: {total_passengers}")
        print(f"Images Imported: {total_images}")

    finally:
        db.close()


if __name__ == "__main__":
    import_dataset()
