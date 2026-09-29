import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = client.get_or_create_collection(name="passenger_faces")


def get_passenger_embeddings(passenger_id):
    return collection.get(
        where={"passenger_id": str(passenger_id)},
        include=["embeddings", "metadatas"]
    )


def store_passenger_embedding(passenger_id, embedding, image_name):
    collection.add(
        ids=[f"{passenger_id}_{image_name}"],
        embeddings=[embedding],
        metadatas=[{"passenger_id": str(passenger_id), "image_name": image_name}]
    )


def delete_passenger_embeddings(passenger_id):
    collection.delete(where={"passenger_id": str(passenger_id)})


def get_collection_count():
    return collection.count()
