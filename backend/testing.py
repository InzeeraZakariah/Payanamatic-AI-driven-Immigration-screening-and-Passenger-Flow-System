from services.face_service import (
    generate_embedding,
    similarity_score
)

img1 = "image1.jpeg"
img2 = "image2.jpeg"

e1 = generate_embedding(img1)
e2 = generate_embedding(img2)

print(len(e1))
print(len(e2))

score = similarity_score(
    e1,
    e2
)

print(score)