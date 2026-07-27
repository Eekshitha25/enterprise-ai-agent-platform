"""
Thin wrapper around Qdrant for storing/retrieving document chunks.
Swap `QdrantVectorStore` for Pinecone/Weaviate clients if needed —
the rest of the codebase only depends on the methods defined here.
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import get_settings

settings = get_settings()

# all-MiniLM-L6-v2 (free local default) = 384 dims. text-embedding-3-large (OpenAI) = 3072.
EMBEDDING_DIM = 3072 if settings.embedding_provider == "openai" else 384


class VectorStore:
    def __init__(self):
        self.client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        self.collection = settings.qdrant_collection

    def ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=qmodels.VectorParams(
                    size=EMBEDDING_DIM, distance=qmodels.Distance.COSINE
                ),
            )

    def upsert_chunks(self, points: list[dict]):
        """points: [{id, vector, payload: {text, source, doc_id, ...}}]"""
        self.ensure_collection()
        self.client.upsert(
            collection_name=self.collection,
            points=[
                qmodels.PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
                for p in points
            ],
        )

    def search(self, query_vector: list[float], top_k: int = 5, filters: dict | None = None):
        self.ensure_collection()
        qfilter = None
        if filters:
            qfilter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(key=k, match=qmodels.MatchValue(value=v))
                    for k, v in filters.items()
                ]
            )
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qfilter,
        )
        return [
            {"text": r.payload.get("text"), "source": r.payload.get("source"), "score": r.score}
            for r in results
        ]


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
