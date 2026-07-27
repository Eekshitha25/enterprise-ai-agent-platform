"""
Tool: search the internal knowledge base (RAG over ingested docs).
"""
from langchain_core.tools import tool

from app.rag.retriever import retrieve


@tool
def search_knowledge_base(query: str) -> str:
    """Search company documents (PDFs, Confluence, Notion, emails) for information
    relevant to the query. Returns the top matching passages with their sources."""
    results = retrieve(query, top_k=5)
    if not results:
        return "No relevant documents found."
    formatted = []
    for r in results:
        formatted.append(f"[source: {r['source']}, relevance: {r['score']:.2f}]\n{r['text']}")
    return "\n\n---\n\n".join(formatted)
