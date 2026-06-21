from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# =====================================================
# PASSENGER DETAILS
# =====================================================

class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, index=True)
    passport_number = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    nationality = Column(String(50))
    gender = Column(String(10))
    dob = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    email = Column(String(50), unique = True)

# =====================================================
# PASSPORT DETAILS
# =====================================================

class PassportDetail(Base):
    __tablename__ = "passport_details"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    passport_number = Column(String(20), unique=True) 
    passport_type = Column(String(30))
    issuing_country = Column(String(50))
    issue_date = Column(Date)
    expiry_date = Column(Date)


# =====================================================
# VISA DETAILS
# =====================================================

class VisaDetail(Base):
    __tablename__ = "visa_details"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    visa_type = Column(String(50))
    issue_date = Column(Date)
    expiry_date = Column(Date)


# =====================================================
# ENQUIRY FORMS
# =====================================================

class EnquiryForm(Base):
    __tablename__ = "enquiry_forms"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    purpose_of_visit = Column(String(100))
    destination_address = Column(Text)
    duration_of_stay_days = Column(Integer)
    return_ticket = Column(Boolean, default=False)
    employment_status = Column(String(50))


# =====================================================
# TRAVEL HISTORY
# =====================================================

class TravelHistory(Base):
    __tablename__ = "travel_history"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    country = Column(String(100))
    arrival_date = Column(Date)
    departure_date = Column(Date)
    overstay_flag = Column(Boolean, default=False)
    deportation_flag = Column(Boolean, default=False)


# =====================================================
# PASSENGER IMAGES
# =====================================================

class PassengerImage(Base):
    __tablename__ = "passenger_images"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    image_path = Column(Text, nullable=False)
    photo_year = Column(Integer)
    age_at_capture = Column(Integer)
    image_type = Column(String(30), default="PASSPORT")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


# =====================================================
# SCREENING RESULTS
# =====================================================

class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    similarity_score = Column(String(20))
    verification_status = Column(String(30))
    risk_score = Column(Integer)
    risk_level = Column(String(20))
    assigned_lane = Column(String(30))
    final_decision = Column(String(50))
    screened_at = Column(DateTime(timezone=True), server_default=func.now())