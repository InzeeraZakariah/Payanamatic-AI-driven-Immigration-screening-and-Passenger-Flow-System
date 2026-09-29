# Payanamatic: AI-powered smart immigration screening and passenger flow system

## Overview
Payanamatic is an AI-powered smart border and immigration screening system designed to assist immigration officers in:
- Passenger identity verification
- Risk assessment
- Passenger flow management

It integrates face verification, passenger data, visa information, enquiry forms, travel history, risk scoring, officer monitoring, and automated notifications into a single workflow.

---

## Problem Statement
Traditional immigration screening relies heavily on manual verification of documents, identity, and travel history.  
This increases processing time and workload for officers.

**Payanamatic aims to:**
- Automate identity verification
- Analyze passenger and travel information
- Identify risk indicators
- Assign passengers to appropriate lanes
- Provide real-time screening information
- Reduce repetitive manual work while keeping officers in control

---

## Proposed Solution
1. Officer enters passport number  
2. System retrieves passenger info  
3. Live image captured via camera  
4. Face embedding generated using **DeepFace + ArcFace**  
5. Embedding compared with stored passenger embeddings  
6. Risk score calculated from visa, enquiry, and travel history  
7. Risk level + lane assigned  
8. Final decision generated and displayed  
9. Result stored in **PostgreSQL**  
10. Optional notification sent via **n8n**

---

## Key Features
### Passenger Screening
- Passport lookup
- Live camera capture
- Face embedding + verification
- Risk scoring & classification
- Lane assignment
- Final decision with reasons

### Face Verification
- Uses **DeepFace + ArcFace**
- Cosine similarity thresholds:
  - `>= 0.75` → VERIFIED
  - `0.60–0.7499` → MANUAL_REVIEW
  - `< 0.60` → FAILED

### Risk Assessment
**Risk Rules:**
- Visa expiry < 30 days → +15  
- Stay > 30 days → +10  
- No return ticket → +20  
- Unemployed → +10  
- Previous overstay → +40  
- Previous deportation → +50  

**Risk Levels:**
- `0–20` → LOW → FAST_LANE  
- `21–50` → MEDIUM → ASSISTED_COUNTER  
- `>50` → HIGH → SECONDARY_SCREENING  

---

## Officer Dashboard
- **Summary Cards:** Total Screenings, Verified, Manual Review, High Risk  
- **Risk Distribution:** LOW, MEDIUM, HIGH  
- **Passenger Flow:** FAST LANE, ASSISTED COUNTER, SECONDARY SCREENING  
- **Recent Screenings Table:** ID, Name, Passport, Risk Score, Status, Decision, Timestamp  

---

## System Architecture
- **Frontend:** HTML5, CSS3, JS, MediaDevices API  
- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic  
- **AI:** DeepFace, ArcFace, Cosine similarity  
- **Databases:** PostgreSQL (structured data), ChromaDB (face embeddings)  
- **Automation:** n8n webhook notifications  

---

## Project Structure

---

## Basic Usage

### Passenger Screening
1. Open the **Screening Page**
2. Enter a valid passport number
3. Allow browser camera access
4. Capture the passenger image
5. Click **Screen Passenger**
6. Wait for face verification and risk assessment
7. Review the generated screening result

### Officer Dashboard
- Open the **Officer Dashboard**
- Review summary cards
- Check risk distribution
- Check passenger-flow allocation
- Review the recent-screenings table
- Dashboard auto-refreshes for live monitoring

### Screening Result Display
The screening page shows:
- Passenger Information (ID, Name, Passport, Gender, Nationality)
- Identity Verification (Similarity score, Verification status)
- Risk Assessment (Risk score, Risk level, Assigned lane)
- Final Decision
- Notification status
- Screening reasons (risk indicators contributing to score)

---

## Workflow Diagram

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
├──► Screening Result
├──► PostgreSQL
├──► Officer Dashboard
└──► n8n Notification


---

## Security & Operational Considerations
- Camera access requires browser permission  
- PostgreSQL credentials must be secured (no hardcoding)  
- Protect API endpoints before production deployment  
- Use **HTTPS** in production  
- Handle biometric data according to privacy laws  
- Officer access controls required  
- AI-generated results must remain subject to human review  

---

## Example Screening States
- **VERIFIED**
  - LOW/MEDIUM RISK → CLEARED
  - HIGH RISK → SECONDARY_SCREENING
- **MANUAL_REVIEW**
  - Always → MANUAL_REVIEW
- **FAILED**
  - Always → MANUAL_REVIEW

---

## Future Enhancements
- Officer authentication & role-based access control  
- Advanced dashboard analytics  
- Screening-result history & filtering  
- Exportable screening reports  
- Audit logs  
- Improved camera-quality validation  
- Multi-camera integration  
- Secure biometric-data management  
- Larger dataset for model evaluation  

---

## License
This project is developed for **SHEHACKS Finale (30th Jan 2026)**.  
Future licensing terms to be defined for production deployment.

---

## Contributors
- **Inzeera Z**  
- **Hajira Fathima M**  
- **Bismaya B**

