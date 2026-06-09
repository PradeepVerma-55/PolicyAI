"""
01_ingest.py — Ingestion Pipeline (LangChain)

Same goal as vanilla_rag/01_ingest.py but using LangChain abstractions:

  vanilla_rag                         langchain_rag
  ──────────────────────────────────  ──────────────────────────────────────
  requests + fitz (manual)         →  PyMuPDFLoader
  custom word-window loop          →  RecursiveCharacterTextSplitter
  SentenceTransformer + PointStruct →  HuggingFaceEmbeddings + QdrantVectorStore

LangChain wraps all of this behind a common Document interface, so every
loader, splitter, embedder, and vector store speaks the same language.

Run once before querying:
    cd langchain_rag
    python 01_ingest.py
"""

import requests
from pathlib import Path

from langchain_community.document_loaders  import PyMuPDFLoader
from langchain_text_splitters              import RecursiveCharacterTextSplitter
from langchain_huggingface                 import HuggingFaceEmbeddings
from langchain_qdrant                      import QdrantVectorStore

from config import PDF_URL, COLLECTION_NAME, QDRANT_PATH, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

# ── Step 1 — Download & Load PDF ───────────────────────────────────────────────
#
# PyMuPDFLoader is LangChain's wrapper around PyMuPDF (fitz).
# It reads each page and returns a list of Document objects.
#
# A Document is LangChain's standard data container:
#   doc.page_content → the extracted text of that page
#   doc.metadata     → dict with "source" (file path) and "page" (0-based index)
#
# We download the PDF once and save it to data/ so subsequent runs skip the download.

# __file__ is the script's absolute path — resolves correctly regardless of
# which directory you run python from
pdf_path = Path(__file__).parent.parent / "data" / "HR-Policy.pdf"

if not pdf_path.exists():
    print(f"Downloading PDF from {PDF_URL} ...")
    response = requests.get(PDF_URL, timeout=30)
    response.raise_for_status()
    pdf_path.write_bytes(response.content)
    print(f"Saved to {pdf_path}")
else:
    print(f"Using cached PDF: {pdf_path}")

loader = PyMuPDFLoader(str(pdf_path))
docs   = loader.load()   # returns List[Document], one per page

print(f"Loaded {len(docs)} pages")
print(f"Sample metadata : {docs[0].metadata}")
print(f"Sample content  : {docs[0].page_content[:300]}")


# ── Step 2 — Split into Chunks ─────────────────────────────────────────────────
#
# RecursiveCharacterTextSplitter is LangChain's most versatile splitter.
# It tries to split on paragraphs (\n\n), then sentences (\n), then words (" "),
# falling back to characters — always preferring the most natural boundary.
#
# Key parameters:
#   chunk_size    → max characters per chunk  (we use 500, set in config.py)
#   chunk_overlap → characters shared between adjacent chunks (50)
#                   Overlap prevents an answer from being cut across two chunks.
#
# split_documents() preserves the metadata from each source Document,
# so every chunk still knows its source file and page number.

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)
chunks = splitter.split_documents(docs)

print(f"\nTotal chunks : {len(chunks)}")
print(f"Chunk size   : ~{CHUNK_SIZE} chars  |  Overlap: {CHUNK_OVERLAP} chars")

# Inspect a couple of chunks
for chunk in chunks[:2]:
    print("-" * 55)
    print(f"Page    : {chunk.metadata.get('page')}")
    print(f"Content : {chunk.page_content[:200]}")


# ── Step 3 — Embed & Store in Qdrant ──────────────────────────────────────────
#
# HuggingFaceEmbeddings is LangChain's wrapper around sentence-transformers.
# It exposes the same model (all-MiniLM-L6-v2) but through the LangChain
# Embeddings interface — so it can be swapped for OpenAI / Cohere / etc.
# without changing any other code.

embedder = HuggingFaceEmbeddings(model_name=f"sentence-transformers/{EMBEDDING_MODEL}")
print(f"\nEmbedding model loaded: {EMBEDDING_MODEL}")

# QdrantVectorStore.from_documents() does three things in one call:
#   1. Embeds every chunk using the provided embedder
#   2. Creates (or recreates) the Qdrant collection
#   3. Upserts all vectors + metadata into it
#
# Compare to vanilla_rag where we did these three steps manually.
# The metadata (source, page) from each Document is automatically stored
# in the Qdrant payload — no manual PointStruct construction needed.

print(f"Embedding {len(chunks)} chunks and indexing in Qdrant ...")

vectorstore = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedder,
    path=QDRANT_PATH,
    collection_name=COLLECTION_NAME,
    force_recreate=True,   # drop and rebuild on re-runs, same as vanilla_rag
)

print(f"Indexed {len(chunks)} chunks into collection '{COLLECTION_NAME}'")
print("\nIngestion complete. Ready to query.")
