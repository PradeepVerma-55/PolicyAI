"""
01_ingest.py — Multi-Source Ingestion Pipeline (LangChain)

Downloads every policy document listed in POLICY_SOURCES (config.py),
loads it with PyMuPDFLoader, stamps each page with policy_name and
policy_category metadata, splits into chunks, then embeds and indexes
all chunks in a single Qdrant collection.

  vanilla_rag                         langchain_rag
  ──────────────────────────────────  ──────────────────────────────────────
  requests + fitz (manual)         →  PyMuPDFLoader
  custom word-window loop          →  RecursiveCharacterTextSplitter
  SentenceTransformer + PointStruct →  HuggingFaceEmbeddings + QdrantVectorStore

The metadata stamps (policy_name, policy_category) are what allow the
query pipeline to show users which specific policy document answered
their question, not just the raw filename.

Run once before querying:
    cd langchain_rag
    python 01_ingest.py
"""

import requests
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters             import RecursiveCharacterTextSplitter
from langchain_huggingface                import HuggingFaceEmbeddings
from langchain_qdrant                     import QdrantVectorStore

from config import (
    POLICY_SOURCES, COLLECTION_NAME, QDRANT_PATH,
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
)

data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)

# ── Step 1 — Download & load each policy source ────────────────────────────────
#
# PyMuPDFLoader returns one Document per page; each Document has:
#   .page_content → extracted text
#   .metadata     → {"source": filepath, "page": 0-based index}
#
# We add policy_name and policy_category to metadata *before* splitting
# so every chunk automatically inherits these fields.  After splitting,
# the metadata dict is read-only from Qdrant's perspective — the only
# reliable window to inject custom metadata is here, at load time.

all_chunks = []

for source in POLICY_SOURCES:
    pdf_path = data_dir / source["filename"]

    if not pdf_path.exists():
        print(f"Downloading: {source['name']} ...")
        try:
            resp = requests.get(source["url"], timeout=120)
            resp.raise_for_status()
            pdf_path.write_bytes(resp.content)
            print(f"  Saved: {pdf_path.name}")
        except Exception as exc:
            print(f"  SKIP — download failed: {exc}")
            continue
    else:
        print(f"Cached   : {source['name']}")

    docs = PyMuPDFLoader(str(pdf_path)).load()

    for doc in docs:
        doc.metadata["policy_name"]     = source["name"]
        doc.metadata["policy_category"] = source["category"]

    chunks = splitter.split_documents(docs)
    all_chunks.extend(chunks)
    print(f"  {len(docs):>3} pages -> {len(chunks):>4} chunks  [{source['category']}]")

print(f"\nTotal chunks across all sources: {len(all_chunks)}")


# ── Step 2 — Embed & Store in Qdrant ──────────────────────────────────────────
#
# HuggingFaceEmbeddings wraps sentence-transformers through the LangChain
# Embeddings interface — swap for OpenAI/Cohere without changing other code.
#
# QdrantVectorStore.from_documents() does three things in one call:
#   1. Embeds every chunk using the provided embedder
#   2. Creates (or recreates) the Qdrant collection
#   3. Upserts all vectors + metadata (including our custom policy_* fields)
#
# force_recreate=True drops and rebuilds on re-runs — safe for development.

embedder = HuggingFaceEmbeddings(model_name=f"sentence-transformers/{EMBEDDING_MODEL}")
print(f"\nEmbedding model loaded: {EMBEDDING_MODEL}")
print(f"Embedding {len(all_chunks)} chunks and indexing into '{COLLECTION_NAME}'...")

QdrantVectorStore.from_documents(
    documents=all_chunks,
    embedding=embedder,
    path=QDRANT_PATH,
    collection_name=COLLECTION_NAME,
    force_recreate=True,
)

print(f"\nIndexed {len(all_chunks)} chunks into collection '{COLLECTION_NAME}'.")
print("Ingestion complete. Ready to query.")
