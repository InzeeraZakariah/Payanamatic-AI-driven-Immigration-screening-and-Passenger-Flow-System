import httpx

N8N_WEBHOOK_URL="http://localhost:5678/webhook-test/passenger-alert"

# =========================
# SEND PASSENGER EMAIL
# =========================
async def send_passenger_email(
    email: str,
    full_name: str,
    passport_number: str,
    final_decision: str,
    risk_level: str,
    risk_score: int
) -> bool:
    if not email:
        print("Passenger email not available.")
        return False

    payload = {
        "email": email,
        "full_name": full_name,
        "passport_number": passport_number,
        "final_decision": final_decision,
        "risk_level": risk_level,
        "risk_score": risk_score,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                N8N_WEBHOOK_URL,
                json=payload,
                timeout=10
            )

        print("n8n status:", response.status_code)
        print("n8n response:", response.text)

        return response.is_success

    except Exception as error:
        print("n8n notification error:", error)
        return False
