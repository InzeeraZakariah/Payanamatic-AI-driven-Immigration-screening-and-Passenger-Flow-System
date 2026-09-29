import os
import base64
from pathlib import Path

from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity

from services.chroma_service import get_passenger_embeddings

BASE_DIR = Path(__file__).resolve().parent.parent
LIVE_IMAGE_DIR = BASE_DIR / "images" / "live"
LIVE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def save_live_image(passport_number: str, image_data: str) -> str:
    image_data = image_data.split(",")[-1]
    image_bytes = base64.b64decode(image_data)
    file_path = LIVE_IMAGE_DIR / f"{passport_number}.jpg"

    with open(file_path, "wb") as file:
        file.write(image_bytes)

    return str(file_path)


# =========================
# GENERATE ARC-FACE EMBEDDING
# =========================
def generate_embedding(image_path: str) -> list[float]:
    result = DeepFace.represent(
        img_path=image_path,
        model_name="ArcFace",
        enforce_detection=True
    )
    return result[0]["embedding"]


def similarity_score(embedding1, embedding2) -> float:
    similarity = cosine_similarity([embedding1], [embedding2])[0][0]
    return float(similarity)

def verify_passenger_face(passenger_id: int, live_embedding: list[float]) -> dict:
    results = get_passenger_embeddings(passenger_id)
    embeddings = results.get("embeddings")

    # Chroma may return NumPy ndarray
    if embeddings is None or len(embeddings) == 0:
        return {"similarity_score": 0.0, "verification_status": "NO_IMAGES_FOUND"}

    best_score = 0.0
    for stored_embedding in embeddings:
        score = similarity_score(live_embedding, stored_embedding)
        if score > best_score:
            best_score = score

    # Thresholds
    if best_score >= 0.75:
        status = "VERIFIED"
    elif best_score >= 0.60:
        status = "MANUAL_REVIEW"
    else:
        status = "FAILED"

    return {
        "similarity_score": round(best_score, 4),
        "verification_status": status,
    }
