"""
pipeline.py — RAG pipeline initialisation for PolicyAI Chatbot

Responsibilities
----------------
- ensure_indexed()  : download the HR Policy PDF and build the Qdrant index
                      on first run; skipped on every subsequent start.
- rag               : the callable imported from langchain_rag/02_query.py.
                      Exposed here so the rest of the chatbot imports from
                      one place instead of reaching into langchain_rag directly.

NOTE: sys.path and os.chdir are set by app.py *before* this module is
      imported, so `from config import ...` resolves to langchain_rag/config.py.
"""

import importlib
from pathlib import Path

from qdrant_client import QdrantClient
from config import (
    QDRANT_PATH, COLLECTION_NAME, PDF_URL,
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
)


def ensure_indexed() -> None:
    """
    Check whether the Qdrant collection already exists.
    If not: download the PDF, chunk it, embed it, and store it in Qdrant.
    """
    client = QdrantClient(path=QDRANT_PATH)
    exists = client.collection_exists(COLLECTION_NAME)
    client.close()

    if exists:
        print(f"[pipeline] Collection '{COLLECTION_NAME}' ready.")
        return

    print(f"[pipeline] Collection not found — indexing PDF...")

    import requests
    from langchain_community.document_loaders import PyMuPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_qdrant import QdrantVectorStore

    root     = Path(__file__).parent.parent
    pdf_path = root / "data" / "HR-Policy.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        print("[pipeline] Downloading PDF...")
        resp = requests.get(PDF_URL, timeout=60)
        resp.raise_for_status()
        pdf_path.write_bytes(resp.content)

    pages    = PyMuPDFLoader(str(pdf_path)).load()
    chunks   = RecursiveCharacterTextSplitter(
                   chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
               ).split_documents(pages)
    embedder = HuggingFaceEmbeddings(
                   model_name=f"sentence-transformers/{EMBEDDING_MODEL}"
               )
    QdrantVectorStore.from_documents(
        documents=chunks, embedding=embedder,
        path=QDRANT_PATH, collection_name=COLLECTION_NAME,
        force_recreate=True,
    )
    print(f"[pipeline] Indexed {len(chunks)} chunks into '{COLLECTION_NAME}'.")


def _load_rag():
    """Import and return the rag() function from langchain_rag/02_query.py."""
    module = importlib.import_module("02_query")
    return module.rag


# Run ingestion check at import time, then expose rag()
ensure_indexed()
rag = _load_rag()
