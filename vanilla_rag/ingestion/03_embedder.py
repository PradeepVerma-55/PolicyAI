"""
03_embedder.py — Text embedding

RAG Step 3 of 3: Convert chunks into vectors.

Converts text chunks into 384-dimensional vectors using all-MiniLM-L6-v2.
The model runs fully offline after the first download (~90 MB, cached locally).
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

# Module-level singleton — model is loaded once and reused across all calls.
# Recreating SentenceTransformer on every call would add ~2 s of overhead each time.
_embedder: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    """
    Return the embedding model, loading it on the first call only.

    Subsequent calls return the already-loaded instance from module memory,
    so ingestion and query both share the same model without reloading.
    """
    global _embedder
    if _embedder is None:
        print(f"Loading embedding model '{EMBEDDING_MODEL}'...")
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def embed_chunks(chunks: list[dict]) -> np.ndarray:
    """
    Encode a list of chunk dicts into embedding vectors.

    Args:
        chunks : List of chunk dicts with a "content" key (output of 02_chunker.py).

    Returns:
        numpy array of shape (len(chunks), 384) — one vector per chunk.
        show_progress_bar is shown only for bulk ingestion (more than 1 chunk).
    """
    embedder = get_embedder()
    texts    = [c["content"] for c in chunks]

    print(f"Embedding {len(texts)} chunks...")
    embeddings = embedder.encode(texts, show_progress_bar=len(texts) > 1)

    print(f"Shape: {embeddings.shape}")
    return embeddings
