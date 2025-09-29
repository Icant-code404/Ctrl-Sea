# test_retriever.py
"""
Quick sanity-check script for local Chroma retriever.
Run this AFTER build_vector_index.py to test retrieval.
"""

import chromadb
from sentence_transformers import SentenceTransformer

# -------------------------------
# Config
# -------------------------------
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "argo_meta"
EMBED_MODEL = "all-MiniLM-L6-v2"

# -------------------------------
# Load collection + embedder
# -------------------------------
print("🔄 Loading collection...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(COLLECTION_NAME)

print("🔄 Loading embedding model...")
model = SentenceTransformer(EMBED_MODEL)

# -------------------------------
# Run query
# -------------------------------
query = input("Type a query (e.g. 'temperature 28 near latitude 10'): ")

query_embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=5
)

# -------------------------------
# Show results
# -------------------------------
print("\n=== Top Results ===")
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"- {doc}")
    print(f"  metadata: {meta}\n")
