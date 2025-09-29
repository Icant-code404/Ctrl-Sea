# vector_agent.py
import chromadb

class VectorRetriever:
    def __init__(self, path="./chroma_db", collection_name="argo_meta"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(collection_name)

    def search(self, query: str, top_k=3):
        results = self.collection.query(query_texts=[query], n_results=top_k)
        return results
