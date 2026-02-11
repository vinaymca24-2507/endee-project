from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from core.database import db_client
from core.config import settings

class Retriever:
    def __init__(self):
        self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Semantically searches the codebase for the query.
        """
        # 1. Generate Query Embedding
        query_vector = self.embedder.encode(query).tolist()
        
        # 2. Search in Endee
        results = db_client.search(query_vector, limit=top_k)
        
        return results

retriever = Retriever()
