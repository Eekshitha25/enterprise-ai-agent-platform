from app.rag.embeddings import get_embedding_model
from app.rag.vector_store import get_vector_store


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Embed the query and return the top_k most relevant chunks with source + score."""
    embedder = get_embedding_model()
    query_vector = embedder.embed_query(query)
    store = get_vector_store()
    return store.search(query_vector, top_k=top_k)
