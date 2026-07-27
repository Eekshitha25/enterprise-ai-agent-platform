"""
Document ingestion pipeline: load -> chunk -> embed -> upsert into Qdrant.
Supports PDFs out of the box; Confluence/Notion/email loaders are stubbed
with clear extension points (LangChain has first-party loaders for both).
"""
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.rag.embeddings import get_embedding_model
from app.rag.vector_store import get_vector_store

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def load_pdf(path: str, source_name: str) -> list[dict]:
    loader = PyPDFLoader(path)
    pages = loader.load()
    chunks = splitter.split_documents(pages)
    return [{"text": c.page_content, "source": source_name} for c in chunks]


def load_raw_text(text: str, source_name: str) -> list[dict]:
    chunks = splitter.split_text(text)
    return [{"text": c, "source": source_name} for c in chunks]


def ingest_chunks(chunks: list[dict], doc_id: str) -> int:
    """Embed a list of {text, source} chunks and upsert to the vector store."""
    if not chunks:
        return 0

    embedder = get_embedding_model()
    texts = [c["text"] for c in chunks]
    vectors = embedder.embed_documents(texts)

    points = [
        {
            "id": str(uuid.uuid4()),
            "vector": vectors[i],
            "payload": {"text": chunks[i]["text"], "source": chunks[i]["source"], "doc_id": doc_id},
        }
        for i in range(len(chunks))
    ]

    store = get_vector_store()
    store.upsert_chunks(points)
    return len(points)


# --- Extension points for enterprise connectors ---
def load_confluence(space_key: str, url: str, username: str, api_token: str) -> list[dict]:
    """Stub: wire up langchain_community.document_loaders.ConfluenceLoader here."""
    raise NotImplementedError("Plug in ConfluenceLoader with your Confluence creds.")


def load_notion(database_id: str, integration_token: str) -> list[dict]:
    """Stub: wire up langchain_community.document_loaders.NotionDBLoader here."""
    raise NotImplementedError("Plug in NotionDBLoader with your Notion integration token.")
