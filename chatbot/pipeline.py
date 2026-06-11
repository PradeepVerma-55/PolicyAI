"""
pipeline.py — RAG pipeline initialisation for PolicyAI Chatbot

Responsibilities
----------------
- ensure_indexed()  : download all policy documents in POLICY_SOURCES and build
                      the Qdrant index on first run; skipped on subsequent starts.
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
    QDRANT_PATH, COLLECTION_NAME, POLICY_SOURCES,
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
)


def ensure_indexed() -> None:
    """
    Check whether the Qdrant collection already exists.
    If not: download all policy PDFs, chunk them, embed them, and store in Qdrant.
    Sources that fail to download are skipped with a warning.
    """
    client = QdrantClient(path=QDRANT_PATH)
    exists = client.collection_exists(COLLECTION_NAME)
    client.close()

    if exists:
        print(f"[pipeline] Collection '{COLLECTION_NAME}' ready.")
        return

    print(f"[pipeline] Collection not found — indexing {len(POLICY_SOURCES)} policy sources...")

    import requests
    from langchain_community.document_loaders import PyMuPDFLoader
    from langchain_text_splitters             import RecursiveCharacterTextSplitter
    from langchain_huggingface                import HuggingFaceEmbeddings
    from langchain_qdrant                     import QdrantVectorStore

    root     = Path(__file__).parent.parent
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )

    all_chunks = []

    for source in POLICY_SOURCES:
        pdf_path = data_dir / source["filename"]

        if not pdf_path.exists():
            print(f"[pipeline] Downloading: {source['name']} ...")
            try:
                resp = requests.get(source["url"], timeout=120)
                resp.raise_for_status()
                pdf_path.write_bytes(resp.content)
            except Exception as exc:
                print(f"[pipeline] SKIP '{source['name']}' — {exc}")
                continue

        docs = PyMuPDFLoader(str(pdf_path)).load()

        for doc in docs:
            doc.metadata["policy_name"]     = source["name"]
            doc.metadata["policy_category"] = source["category"]

        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)
        print(f"[pipeline]   {source['name']}: {len(chunks)} chunks [{source['category']}]")

    if not all_chunks:
        raise RuntimeError("[pipeline] No chunks indexed — all downloads failed.")

    embedder = HuggingFaceEmbeddings(
        model_name=f"sentence-transformers/{EMBEDDING_MODEL}"
    )
    QdrantVectorStore.from_documents(
        documents=all_chunks, embedding=embedder,
        path=QDRANT_PATH, collection_name=COLLECTION_NAME,
        force_recreate=True,
    )
    print(f"[pipeline] Indexed {len(all_chunks)} chunks into '{COLLECTION_NAME}'.")


def _load_rag():
    """Import and return the rag() function from langchain_rag/02_query.py."""
    module = importlib.import_module("02_query")
    return module.rag


# Run ingestion check at import time, then expose rag()
ensure_indexed()
rag = _load_rag()
