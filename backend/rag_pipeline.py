import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
import platform
import os

if platform.system() == "Windows":
    CHROMA_PATH = os.path.join(os.environ.get('USERPROFILE', 'C:\\'), 'Drishti', 'drishti', 'chroma_db')
else:
    CHROMA_PATH = "./chroma_db"

# Initialize local embedding model (free, open source)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("crime_records")

def embed_and_store_crimes(crimes_df):
    """Store crime records in ChromaDB"""
    for idx, crime in crimes_df.iterrows():
        text = f"Case {crime['case_id']}: {crime['crime_type']} in {crime['district']} on {crime['crime_date']}. {crime['description']}"
        embedding = embedding_model.encode(text).tolist()
        
        collection.upsert(
            ids=[str(crime['id'])],
            embeddings=[embedding],
            metadatas=[{
                "case_id": crime['case_id'],
                "crime_type": crime['crime_type'],
                "district": crime['district'],
                "date": str(crime['crime_date']),
                "status": crime['status']
            }],
            documents=[text]
        )

def retrieve_relevant_crimes(query, top_k=10):
    """Retrieve most relevant crimes for a query"""
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results
