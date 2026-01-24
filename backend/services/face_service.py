import os
import base64

def store_face_image(passport, image):
    os.makedirs("backend/images", exist_ok=True)
    try:
        image = image.split(",")[-1]
        img_bytes = base64.b64decode(image + "===")
        with open(f"backend/images/{passport}.jpg", "wb") as f:
            f.write(img_bytes)
    except Exception:
        with open(f"backend/images/{passport}.txt", "w") as f:
            f.write(image)
