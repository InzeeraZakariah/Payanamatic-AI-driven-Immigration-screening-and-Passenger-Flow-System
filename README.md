# Payanamatic – AI-Driven Immigration Screening and Passenger Flow System

PayanamAI is a prototype immigration screening pipeline that integrates:
- **Frontend (HTML + JS)** for capturing passport number and live camera photo
- **FastAPI backend** for risk scoring and proxying requests
- **n8n workflow automation** for decision logic and orchestration

---

## 📂 Project Structure

```
PayanamAI/
├── backend/
│   ├── services/
│   │   ├── passport_service.py
│   │   ├── risk_engine.py
│   │   └── face_service.py
│   └── main.py              # FastAPI backend
├── frontend/
│   ├── index.html           # UI template
│   └── app.js               # Frontend logic
├── workflow.json            # n8n workflow export
└── README.md
```

---

## 🚀 Running the System

### 1. Backend (FastAPI)
Install dependencies:
```bash
pip install fastapi uvicorn httpx
```

Run the server:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:
- `POST /screen` → Direct risk scoring
- `POST /screen-through-n8n` → Proxy to n8n workflow
- `GET /get-result/{passport_number}` → Retrieve stored results

---

### 2. Workflow (n8n)
Run n8n (Docker example):
```bash
docker run -it --rm -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

Import `workflow.json` into n8n:
- Webhook: `POST /webhook/screen-passenger`
- Calls FastAPI `/screen`
- Applies risk logic (flagged vs normal)
- Responds with JSON payload



### 3. Frontend
Open `frontend/index.html` in a browser.

Features:
- Capture photo via webcam
- Enter passport number
- Call backend `/screen-through-n8n`
- Display result card with risk score, lane assignment, and decision
- Officer Dashboard counters (total, normal, risk, detain)

---

## 🔄 Data Flow

1. **Frontend** → `POST /screen-through-n8n`  
2. **FastAPI** → forwards to n8n webhook  
3. **n8n** → calls `/screen`, applies decision logic  
4. **n8n** → responds with JSON `{ message, result }`  
5. **FastAPI** → returns result to frontend  
6. **Frontend** → renders result card + updates dashboard

---

## ✅ Example Response

```json
{
  "message": "Immigration Screening Completed",
  "result": {
    "passport_number": "N1234567",
    "full_name": "Inzeera",
    "risk_score": "15",
    "risk_level": "LOW",
    "assigned_lane": "FAST_LANE",
    "final_decision": "Cleared",
    "verification_status": "Verified Successfully"
  }
}
```

---

## 📝 Notes
- Ensure field names are consistent (`assigned_lane` vs `final_lane`) between backend, workflow, and frontend.
- Use **Executions view** in n8n to inspect past runs.
- For local testing in PowerShell, use `Invoke-RestMethod` instead of `curl`.

---

## 👤 Author
Built by the team Techie Titansn for SHEHACKS 2026

Inzeera Z   
Hajira Fathima M 
Bismaya B


