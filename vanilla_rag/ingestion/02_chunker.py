"""
02_chunker.py — Text chunking

RAG Step 2 of 3: Prepare the data.

Splits page text into fixed-size word windows so each chunk fits within
the embedding model's token limit and carries enough context to be useful.
"""

from config import CHUNK_SIZE, CHUNK_MIN_WORDS


def chunk_pages(pages: list[dict], chunk_size: int = CHUNK_SIZE) -> list[dict]:
    """
    Split each page's text into non-overlapping word windows of `chunk_size` words.

    Why word-based chunking?
    - Predictable size regardless of sentence length.
    - 100 words fits comfortably within the all-MiniLM-L6-v2 token limit (256 tokens).

    Each chunk inherits the page number and source filename from its parent page
    so citations remain accurate after retrieval.

    Args:
        pages      : Output of 01_doc_loader.extract_pages().
        chunk_size : Number of words per chunk. Defaults to CHUNK_SIZE.

    Returns:
        List of chunk dicts:
            { "chunk_index": int,   — sequential ID across all chunks
              "content":     str,   — chunk text
              "page":        int,   — page this chunk came from
              "source":      str }  — source filename
    """
    chunks = []

    for page in pages:
        words = page["text"].split()

        for i in range(0, len(words), chunk_size):
            chunk_words = words[i : i + chunk_size]

            # Skip very small trailing fragments — not enough context to be useful
            if len(chunk_words) < CHUNK_MIN_WORDS:
                continue

            chunks.append({
                "chunk_index": len(chunks),
                "content":     " ".join(chunk_words),
                "page":        page["page"],
                "source":      page["source"],
            })

    print(f"Created {len(chunks)} chunks")
    return chunks
