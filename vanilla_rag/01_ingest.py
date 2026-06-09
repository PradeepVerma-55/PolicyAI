"""
01_ingest.py — Ingestion Pipeline

Orchestrates the full ingestion flow:
    1. Load PDF      →  ingestion/01_doc_loader.py
    2. Chunk text    →  ingestion/02_chunker.py
    3. Embed chunks  →  ingestion/03_embedder.py
    4. Store vectors →  Qdrant (local file store)

Run this once per document before querying:
    cd vanilla_rag
    python 01_ingest.py
"""

from ingestion import load_pdf, extract_pages, chunk_pages, embed_chunks, get_embedder
from qdrant_client        import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import PDF_URL, COLLECTION_NAME, QDRANT_PATH

SOURCE_NAME = PDF_URL.split("/")[-1]

# ── Step 1 — Load PDF ──────────────────────────────────────────────────────────
pdf_bytes = load_pdf(PDF_URL)
pages     = extract_pages(pdf_bytes, SOURCE_NAME)

# Sanity check — print the first 300 chars of page 1
print(pages[0]["text"][:300])

# ── Step 2 — Chunk ─────────────────────────────────────────────────────────────
chunks = chunk_pages(pages)

# Inspect a couple of chunks to verify the output looks correct
for chunk in chunks[:2]:
    print("-" * 55)
    print(f"Page    : {chunk['page']}")
    print(f"Content : {chunk['content'][:200]}")

# ── Step 3 — Embed ─────────────────────────────────────────────────────────────
embeddings = embed_chunks(chunks)

# ── Step 4 — Store in Qdrant ───────────────────────────────────────────────────
# path= stores everything in a local folder — no Docker or server required
client = QdrantClient(path=QDRANT_PATH)
DIM    = get_embedder().get_embedding_dimension()   # 384

# Drop and rebuild so re-runs always start from a clean state
if client.collection_exists(COLLECTION_NAME):
    client.delete_collection(COLLECTION_NAME)
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
)
print("Collection created.")

# Each PointStruct holds: a unique ID, the embedding vector, and a payload
# with the chunk text + citation metadata (source filename + page number)
points = [
    PointStruct(
        id=idx,
        vector=embedding.tolist(),
        payload={
            "content": chunk["content"],
            "page":    chunk["page"],
            "source":  chunk["source"],
        },
    )
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
]

# wait=True blocks until Qdrant finishes indexing before returning
result = client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
print(f"Indexed {len(points)} points — status: {result.status}")
print("\nIngestion complete. Ready to query.")
