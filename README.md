# Payanamatic — AI-Based Smart Border & Immigration Screening System

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
