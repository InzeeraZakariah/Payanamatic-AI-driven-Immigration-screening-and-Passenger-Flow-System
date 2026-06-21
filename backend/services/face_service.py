import os
import base64
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity
from services.chroma_service import get_passenger_embeddings

# Save the live image
def save_live_image(passport_number:str, image_data:str):
    os.makedirs("backend/images/live", exist_ok=True)
    image_data = image_data.split(',')[-1]
    image_bytes = base64.b64decode(image_data)
    file_path = f"backend/images/live/{passport_number}.jpg"

    with open(file_path, "wb") as f:
        f.write(image_bytes)
    
    return file_path

# Generate Face Embeddings
def generate_embedding(image_path:str):
    result = DeepFace.represent(
        img_path=image_path,
        model_name="ArcFace",
        enforce_detection=True
    )
    return result[0]["embedding"]


# Similarity Score calculation
def similarity_score(embedding1, embedding2):
    similarity = cosine_similarity([embedding1],[embedding2])[0][0]
    return float(similarity)

# Face Verification Status
def verification_status(similarity_score:float):
    if similarity_score >= 0.90:
        return "Verified Successfully"
    elif similarity_score >= 0.75:
        return "Manual Review Needed"
    else:
        return "Failed"
    



def verify_passenger_face(passenger_id, live_embedding):

    results = (get_passenger_embeddings(passenger_id))
    embeddings = (results["embeddings"])

    print("\nCHROMA RESULTS:")
    print(type(results))
    print(results)

    embeddings = results["embeddings"]

    print("\nEMBEDDINGS TYPE:")
    print(type(embeddings))

    if embeddings is None or len(embeddings) == 0:
        return {
            "similarity_score": 0,
            "verification_status": "NO_IMAGES_FOUND"
        }

    best_score = 0

    for stored_embedding in embeddings:
        score = similarity_score(live_embedding,stored_embedding)

        if score > best_score:
            best_score = score

    if best_score >= 0.75:
        status = "VERIFIED"
    elif best_score >= 0.60:
        status = "MANUAL_REVIEW"
    else:
        status = "FAILED"

    return {
        "similarity_score":round(best_score, 4),
        "verification_status": status
    }

