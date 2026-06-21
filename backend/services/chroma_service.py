import chromadb

client = chromadb.PersistentClient(path="backend/chroma_db")
collection = client.get_or_create_collection(name="passenger_faces")

# Saving embedding
def save_embedding(passenger_id: int, image_id: int, full_name:str, photo_year: int, age:int, embedding:list):
    vector_id = f"{passenger_id}_{image_id}"
    collection.add(
        ids=[vector_id],
        embeddings=[embedding],
        metadatas=[{
            "passenger_id":passenger_id,
            "image_id":image_id,
            "full_name":full_name,
            "photo_year":photo_year,
            "age":age
        }])

# Get Passenger Embedding
def get_passenger_embeddings(passenger_id:int):
    results = collection.get(where={"passenger_id":passenger_id},
                             include=["embeddings","metadatas"])
    return results

# Search by Embedding 
def search_embedding(embedding,top_k=5):
    results = collection.query(
        query_embeddings = [embedding],
        n_results = top_k
    )
    return results
