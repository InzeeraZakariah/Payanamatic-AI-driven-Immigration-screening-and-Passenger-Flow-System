from database import sessionLocal
from models import Passenger, PassportDetail, VisaDetail, EnquiryForm, TravelHistory, PassengerImage

db = sessionLocal()

passengers = db.query(Passenger).all()

print(f"\n{'='*60}")
print(f"Total Passengers: {len(passengers)}")
print(f"{'='*60}")

missing = {
    "passport_details": [],
    "visa_details": [],
    "enquiry_forms": [],
    "travel_history": [],
    "images": []
}

for p in passengers:
    print(f"\nPassenger: {p.full_name} (ID: {p.id})")

    passport = db.query(PassportDetail).filter(PassportDetail.passenger_id == p.id).first()
    print(f"  Passport Detail : {'✅ Found' if passport else '❌ MISSING'}")
    if not passport:
        missing["passport_details"].append(p.full_name)

    visa = db.query(VisaDetail).filter(VisaDetail.passenger_id == p.id).first()
    print(f"  Visa Detail     : {'✅ Found' if visa else '❌ MISSING'}")
    if not visa:
        missing["visa_details"].append(p.full_name)

    enquiry = db.query(EnquiryForm).filter(EnquiryForm.passenger_id == p.id).first()
    print(f"  Enquiry Form    : {'✅ Found' if enquiry else '❌ MISSING'}")
    if not enquiry:
        missing["enquiry_forms"].append(p.full_name)

    history = db.query(TravelHistory).filter(TravelHistory.passenger_id == p.id).all()
    print(f"  Travel History  : {'✅ ' + str(len(history)) + ' record(s)' if history else '❌ MISSING'}")
    if not history:
        missing["travel_history"].append(p.full_name)

    images = db.query(PassengerImage).filter(PassengerImage.passenger_id == p.id).all()
    print(f"  Images          : {'✅ ' + str(len(images)) + ' image(s)' if images else '❌ MISSING'}")
    if not images:
        missing["images"].append(p.full_name)

print(f"\n{'='*60}")
print("SUMMARY OF MISSING DATA")
print(f"{'='*60}")
any_missing = False
for table, names in missing.items():
    if names:
        any_missing = True
        print(f"\n❌ {table}: missing for {len(names)} passenger(s)")
        for name in names:
            print(f"     - {name}")

if not any_missing:
    print("✅ All records are complete for every passenger!")

db.close()