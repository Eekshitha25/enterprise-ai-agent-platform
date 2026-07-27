"""
Embedding model wrapper.

Free/local path (default): sentence-transformers via HuggingFace, runs on
your own CPU, zero API cost, zero API key needed.

Paid path: set EMBEDDING_PROVIDER=openai in .env to use OpenAI's hosted
embeddings instead (higher quality, costs a fraction of a cent per query).
"""
from functools import lru_cache

from app.core.config import get_settings

settings = get_settings()


@lru_cache
def get_embedding_model():
    if settings.embedding_provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)

    # Free, local, no API key required. Downloads once (~90MB) then runs offline.
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
