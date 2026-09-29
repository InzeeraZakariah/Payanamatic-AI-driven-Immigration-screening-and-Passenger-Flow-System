Payanamatic --- AI-Based Smart Border & Immigration Screening System

Overview

Payanamatic is an AI-powered smart border and immigration screening
system designed to assist immigration officers in passenger identity
verification, risk assessment, and passenger flow management.

The system combines face verification, passenger data, visa
information, enquiry forms, travel history, risk scoring, officer
monitoring, and automated notifications into a single screening
workflow.

The application is designed to work with a live camera and existing
passenger records, providing an automated screening result that can be
reviewed by an immigration officer.

Problem Statement

Traditional immigration screening relies heavily on manual verification
of passenger documents, identity, travel history, and risk indicators.
This can increase processing time and place a significant workload on
immigration officers.

A smart screening system is needed to:

Verify passenger identity automatically.

Analyze passenger and travel information.

Identify potential risk indicators.

Assign passengers to appropriate screening lanes.

Provide officers with real-time screening information.

Maintain screening records for monitoring and review.

Reduce repetitive manual work while keeping officers involved in
final decisions.

Proposed Solution

Payanamatic provides an AI-assisted immigration screening workflow:

The officer enters the passenger's passport number.

The system retrieves the passenger's registered information.

A live image is captured using the camera.

A face embedding is generated using DeepFace with ArcFace.

The live embedding is compared with stored passenger face
embeddings.

The system calculates a risk score using passenger, visa, enquiry,
and travel-history information.

A risk level and screening lane are assigned.

A final screening decision is generated.

The screening result is displayed immediately on the passenger
screening page.

The result is stored in PostgreSQL.

Optional passenger notification is sent through n8n.

Officers can monitor screening activity through the dashboard.

Key Features

1. Passenger Screening

Passport-number based passenger lookup.

Live camera capture.

Face embedding generation.

AI-based face verification.

Similarity score calculation.

Verification status.

Risk scoring.

Risk-level classification.

Screening-lane assignment.

Final screening decision.

Screening reason display.

2. Face Verification

The system uses:

DeepFace

ArcFace

Face embeddings

Cosine similarity

Verification states include:

VERIFIED

MANUAL_REVIEW

FAILED

NO_IMAGES_FOUND

The current similarity thresholds are:

Similarity Score   Status

>= 0.75          VERIFIED
0.60 – 0.7499    MANUAL_REVIEW
< 0.60           FAILED

These thresholds are configurable in the face-verification service.

Risk Assessment

Payanamatic calculates a risk score using passenger screening
information.

Current Risk Rules

Condition                      Score

Visa expiry within 30 days       +15
Stay longer than 30 days         +10
No return ticket                 +20
Unemployed                       +10
Previous overstay                +40
Previous deportation             +50

Risk Levels

  Score Risk Level   Assigned Lane

 `0–20` LOW          FAST_LANE
`21–50` MEDIUM       ASSISTED_COUNTER
  `>50` HIGH         SECONDARY_SCREENING

Final Decision Logic

The final decision combines face verification and risk assessment.

Condition                           Final Decision

Face verification is not VERIFIED MANUAL_REVIEW

Verification is VERIFIED and risk SECONDARY_SCREENING
is HIGH

The system is intended as an officer-assistance system. The generated
result supports the screening workflow and does not replace authorized
officer review.

Officer Dashboard

The Officer Dashboard provides a centralized view of recent immigration
screening activity.

Dashboard Cards

The dashboard displays four main summary cards:

Total Screenings

Verified

Manual Review

High Risk

These cards provide a quick overview of the current screening activity.

Risk Distribution Cards

The dashboard also displays screening counts for:

LOW

MEDIUM

HIGH

Passenger Flow Cards

Passenger allocation is displayed using:

FAST LANE

ASSISTED COUNTER

SECONDARY SCREENING

Recent Screenings Table

The dashboard provides a detailed table containing:

Screening ID

Passenger name

Passport number

Risk score

Risk level

Verification status

Final decision

Screening date/time

Action

The dashboard automatically refreshes screening information so officers
can monitor recent activity.

System Architecture

                     ┌───────────────────────┐
                     │      Passenger        │
                     │ Passport + Live Face  │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │   FastAPI Backend     │
                     │      /screen          │
                     └───────────┬───────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐    ┌──────────────┐   ┌─────────────┐
       │ Face Service│    │ Passenger    │   │ Risk Engine │
       │ DeepFace    │    │ Profile      │   │ Risk Score  │
       │ ArcFace     │    │ Data         │   │ & Rules     │
       └──────┬──────┘    └──────┬───────┘   └──────┬──────┘
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐    ┌──────────────┐   ┌─────────────┐
       │ ChromaDB    │    │ PostgreSQL   │   │ Risk Level  │
       │ Embeddings  │    │ Passenger    │   │ & Lane      │
       └─────────────┘    │ Data         │   └──────┬──────┘
                          │ Screening    │          │
                          │ Results      │          │
                          └──────┬───────┘          │
                                 │                  │
                                 └────────┬─────────┘
                                          ▼
                               ┌────────────────────┐
                               │ Screening Result   │
                               │ Final Decision     │
                               └─────────┬──────────┘
                                         │
                    ┌────────────────────┼───────────────────┐
                    │                    │                   │
                    ▼                    ▼                   ▼
             ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
             │ Screening   │     │ Officer     │     │     n8n     │
             │ Page        │     │ Dashboard   │     │ Notification│
             └─────────────┘     └─────────────┘     └─────────────┘

Technology Stack

Frontend

HTML5

CSS3

JavaScript

Browser MediaDevices API

Live camera capture

Dashboard cards

Dashboard tables

Backend

Python

FastAPI

Uvicorn

SQLAlchemy

Pydantic

Artificial Intelligence

DeepFace

ArcFace

Face embeddings

Cosine similarity

Vector Database

ChromaDB

Relational Database

PostgreSQL

psycopg2

Automation

n8n

HTTP webhook

Development Tools

Python virtual environment

VS Code

Jupyter/Colab for experimentation

Git/GitHub

Project Structure

Payanamatic/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── services/
│   │   ├── face_service.py
│   │   ├── screening_service.py
│   │   ├── risk_service.py
│   │   ├── notification_service.py
│   │   └── chroma_service.py
│   │
│   ├── utils/
│   │   └── date_utils.py
│   │
│   ├── images/
│   │   ├── Inzeera/
│   │   ├── Hajira/
│   │   ├── Bismaya/
│   │   └── live/
│   │
│   └── chroma_db/
│
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── app.js
│   ├── dashboard.js
│   └── style.css
│
└── README.md

Folder names may vary depending on the local project setup.

Backend API

POST /screen

Performs passenger screening.

Request

{
  "passport_number": "N1234567",
  "face_image": "data:image/jpeg;base64,..."
}

Response

{
  "message": "Screening Completed",
  "result": {
    "screening_id": 33,
    "passport_number": "N1234567",
    "full_name": "Passenger Name",
    "gender": "Female",
    "nationality": "Indian",
    "similarity_score": 0.87,
    "verification_status": "VERIFIED",
    "risk_score": 10,
    "risk_level": "LOW",
    "assigned_lane": "FAST_LANE",
    "final_decision": "CLEARED",
    "reasons": [],
    "email_sent": false
  }
}

GET /dashboard/summary

Returns officer dashboard information.

The response includes:

Total screening count

Verified count

Manual-review count

Risk distribution

Lane distribution

Recent screening records

Database Entities

The system uses PostgreSQL for structured passenger and screening
information.

Passengers

Stores:

Passenger ID

Full name

Gender

Date of birth

Nationality

Passport number

Email

Passport Details

Stores passport-related information.

Visa Details

Stores visa-related information including expiry information.

Enquiry Forms

Stores passenger enquiry information such as:

Duration of stay

Return-ticket status

Employment status

Travel History

Stores previous travel records and risk indicators.

Screening Results

Stores:

Passenger ID

Similarity score

Verification status

Risk score

Risk level

Assigned lane

Final decision

Screening timestamp

ChromaDB

ChromaDB stores passenger face embeddings.

Each stored embedding contains metadata such as:

passenger_id
image_name

Passenger embeddings are retrieved using the passenger ID before face
verification.

n8n Notification

Payanamatic can send passenger screening information to an n8n webhook.

Current webhook:

http://localhost:5678/webhook/passenger-alert

The notification payload contains:

{
  "email": "passenger@example.com",
  "full_name": "Passenger Name",
  "passport_number": "N1234567",
  "final_decision": "CLEARED",
  "risk_level": "LOW",
  "risk_score": 10
}

The notification workflow is optional and does not prevent the screening
result from being generated if the notification fails.

Installation

1. Clone the Repository

git clone <repository-url>
cd Payanamatic

2. Create a Virtual Environment

Windows:

python -m venv venv
venv\Scripts\activate

Linux/macOS:

python3 -m venv venv
source venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

4. Configure PostgreSQL

Create a PostgreSQL database and configure the connection string in the
backend configuration.

Example:

postgresql+psycopg2://postgres:<password>@localhost:5432/Payanamatic

5. Start the Backend

uvicorn main:app --reload

The API will normally be available at:

http://127.0.0.1:8000

6. Start the Frontend

Open the frontend using a local web server.

For example:

python -m http.server 5500

Then open:

http://127.0.0.1:5500

Basic Usage

Passenger Screening

Open the Screening page.

Enter a valid passport number.

Allow browser camera access.

Capture the passenger image.

Click Screen Passenger.

Wait for face verification and risk assessment.

Review the generated screening result.

Officer Dashboard

Open Officer Dashboard.

Review the summary cards.

Check risk distribution.

Check passenger-flow allocation.

Review the recent-screenings table.

Refresh the dashboard when required.

Screening Result

The screening page displays:

Passenger Information

Screening ID

Full name

Passport number

Gender

Nationality

Identity Verification

Similarity score

Verification status

Risk Assessment

Risk score

Risk level

Assigned lane

Final Decision

Final decision

Passenger notification status

Screening Reasons

Risk indicators contributing to the risk score are displayed when
applicable.

Current Workflow

Passport Number
      │
      ▼
Passenger Lookup
      │
      ▼
Live Camera Capture
      │
      ▼
Face Embedding
      │
      ▼
Face Verification
      │
      ▼
Passenger + Visa + Enquiry + Travel History
      │
      ▼
Risk Calculation
      │
      ▼
Risk Level + Lane
      │
      ▼
Final Decision
      │
      ├──────────────► Screening Result
      │
      ├──────────────► PostgreSQL
      │
      ├──────────────► Officer Dashboard
      │
      └──────────────► n8n Notification

Security and Operational Considerations

Camera access requires browser permission.

PostgreSQL credentials should not be hard-coded in production.

API endpoints should be protected before production deployment.

HTTPS should be used when deploying the system.

Passenger biometric information should be handled according to
applicable privacy and data-protection requirements.

Officer access controls should be added for production deployments.

AI-generated screening results should remain subject to authorized
human review.

Current Project Status

Implemented

Passenger lookup

Live camera capture

Face embedding generation

ArcFace-based face verification

ChromaDB face embedding storage

PostgreSQL passenger data

Risk scoring

Risk-level classification

Screening-lane assignment

Final decision generation

Screening-result storage

Same-page screening result display

Officer dashboard

Dashboard summary cards

Risk distribution cards

Passenger-flow cards

Recent-screenings table

Automatic dashboard refresh

n8n notification integration

Future Enhancements

Officer authentication and role-based access control

Advanced dashboard analytics

Screening-result history and filtering

Exportable screening reports

Audit logs

Improved camera-quality validation

Multi-camera integration

Production deployment

Secure biometric-data management

Model evaluation using a larger and more representative dataset

Example Screening States

VERIFIED
   │
   ├── LOW/MEDIUM RISK ──► CLEARED
   │
   └── HIGH RISK ────────► SECONDARY_SCREENING

MANUAL_REVIEW
   │
   └─────────────────────► MANUAL_REVIEW

FAILED
   │
   └─────────────────────► MANUAL_REVIEW


*Developed by* 
   - Inzeera Z
   - Hajira Fathima M
   - Bismaya B

SHEHACKS - FINALE (30th Jan 2026)

