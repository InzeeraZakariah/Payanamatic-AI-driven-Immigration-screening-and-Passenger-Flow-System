from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    gender = Column(String(20))
    dob = Column(Date)
    nationality = Column(String(100))
    passport_number = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255))

    passport = relationship("PassportDetail", back_populates="passenger", uselist=False, cascade="all, delete-orphan")
    visa = relationship("VisaDetail", back_populates="passenger", uselist=False, cascade="all, delete-orphan")
    enquiry_form = relationship("EnquiryForm", back_populates="passenger", uselist=False, cascade="all, delete-orphan")
    travel_history = relationship("TravelHistory", back_populates="passenger", cascade="all, delete-orphan")
    images = relationship("PassengerImage", back_populates="passenger", cascade="all, delete-orphan")
    screenings = relationship("ScreeningResult", back_populates="passenger", cascade="all, delete-orphan")


class PassportDetail(Base):
    __tablename__ = "passport_details"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    issue_country = Column(String(100))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    passport_type = Column(String(50))
    passport_photo = Column(Text)

    passenger = relationship("Passenger", back_populates="passport")


class VisaDetail(Base):
    __tablename__ = "visa_details"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    visa_type = Column(String(100))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    entry_type = Column(String(50))
    sponsor_type = Column(String(100))

    passenger = relationship("Passenger", back_populates="visa")



class EnquiryForm(Base):
    __tablename__ = "enquiry_forms"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    purpose_of_visit = Column(String(200))
    event_type = Column(String(200))
    duration_of_stay_days = Column(Integer)
    address_of_stay = Column(String(500))
    host_relation = Column(String(200))
    return_ticket = Column(Boolean)
    employment_status = Column(String(100))
    monthly_income_range = Column(String(100))
    previous_visits_count = Column(Integer)
    countries_visited_last_5_years = Column(Text)  # Stores JSON/list as text

    passenger = relationship("Passenger", back_populates="enquiry_form")


# =========================
# 5. TRAVEL HISTORY
# =========================
class TravelHistory(Base):
    __tablename__ = "travel_history"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    country = Column(String(100))
    visit_year = Column(Integer)
    overstay_flag = Column(Boolean, default=False)
    deportation_flag = Column(Boolean, default=False)

    passenger = relationship("Passenger", back_populates="travel_history")


class PassengerImage(Base):
    __tablename__ = "passenger_images"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    image_path = Column(String(500), nullable=False)

    passenger = relationship("Passenger", back_populates="images")


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    similarity_score = Column(Float)
    verification_status = Column(String(50))
    risk_score = Column(Integer)
    risk_level = Column(String(50))
    assigned_lane = Column(String(100))
    final_decision = Column(String(100))
    screened_at = Column(DateTime, default=datetime.utcnow)

    passenger = relationship("Passenger", back_populates="screenings")
