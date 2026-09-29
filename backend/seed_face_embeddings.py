from pathlib import Path
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Passenger
from services.face_service import generate_embedding
from services.chroma_service import (
    store_passenger_embedding,
    delete_passenger_embeddings
)

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"

PASSENGER_FOLDERS = {
    "N1234567": "Inzeera",
    "N3456789": "Hajira",
    "N2345678": "Bismaya"

}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_image_files(folder):
    if not folder.exists():
        return []

    return [
        file for file in folder.iterdir()
        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
    ]


def seed_embeddings():
    print("=" * 70)
    print("Payanamatic - Face Embedding Seeder")
    print("=" * 70)

    print(f"\nBASE_DIR  : {BASE_DIR}")
    print(f"IMAGE_DIR : {IMAGE_DIR}")
    print(f"EXISTS    : {IMAGE_DIR.exists()}")

    if not IMAGE_DIR.exists():
        print("\nERROR: Images directory does not exist.")
        print(f"Expected: {IMAGE_DIR}")
        return

    db: Session = SessionLocal()

    try:
        passengers = db.query(Passenger).all()

        if not passengers:
            print("\nERROR: No passengers found in database.")
            return

        print(f"\nPassengers found: {len(passengers)}")

        total_stored = 0

        for passenger in passengers:
            passport_number = passenger.passport_number
            folder_name = PASSENGER_FOLDERS.get(passport_number)

            print("\n" + "-" * 70)
            print(f"Passenger : {passenger.full_name}")
            print(f"Passport  : {passport_number}")

            if not folder_name:
                print("WARNING: No folder mapping found.")
                print("Add this passport number to PASSENGER_FOLDERS.")
                continue

            passenger_folder = IMAGE_DIR / folder_name

            print(f"Folder    : {passenger_folder}")

            if not passenger_folder.exists():
                print("ERROR: Image folder does not exist.")
                continue

            image_files = get_image_files(passenger_folder)

            if not image_files:
                print("ERROR: No images found.")
                continue

            print(f"Images    : {len(image_files)}")

            print("Deleting old embeddings...")
            delete_passenger_embeddings(passenger.id)

            stored = 0

            for image_path in image_files:
                print(f"\nProcessing: {image_path.name}")

                try:
                    embedding = generate_embedding(str(image_path))

                    if embedding is None or len(embedding) == 0:
                        print("FAILED: Empty embedding.")
                        continue

                    store_passenger_embedding(
                        passenger_id=passenger.id,
                        embedding=embedding,
                        image_name=image_path.name
                    )

                    stored += 1
                    total_stored += 1

                    print("SUCCESS: Embedding stored.")

                except Exception as error:
                    print("FAILED:")
                    print(error)

            print(f"\nResult: {stored}/{len(image_files)} embeddings stored.")

        print("\n" + "=" * 70)
        print("EMBEDDING SEEDING COMPLETED")
        print("=" * 70)
        print(f"Total embeddings stored: {total_stored}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_embeddings()