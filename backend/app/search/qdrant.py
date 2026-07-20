import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "manufacturing_chunks"

class VectorSearchClient:
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        # Using a small, fast model for embeddings by default
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_size = self.model.get_sentence_embedding_dimension()
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    def encode(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()

    def insert_chunk(self, chunk_id: str, text: str, payload: dict):
        vector = self.encode(text)
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(id=chunk_id, vector=vector, payload=payload)]
        )

    def search(self, query_text: str, limit: int = 5, filters: dict = None):
        vector = self.encode(query_text)
        # We can construct Qdrant filters based on `filters` dictionary if needed
        # For now, simple vector search
        hits = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=limit,
        )
        return hits

    def delete_document_chunks(self, document_id: str):
        # We would need to search for points with this document_id and delete them,
        # or use qdrant payload filters to delete.
        pass

vector_client = VectorSearchClient()
