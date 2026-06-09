"""
config.py — Central configuration for PolicyAI (LangChain implementation)

Rules:
    - Secrets (API keys)      → .env file only, never hardcoded here
    - App config (models, DB) → this file
    - All other files import from here — nothing else defines these constants
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env lives at the project root — resolve relative to this file, not cwd
load_dotenv(Path(__file__).parent.parent / ".env")

# ── Secrets ────────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# ── LLM ────────────────────────────────────────────────────────────────────────
GROQ_MODEL: str = "llama-3.1-8b-instant"

# ── Embedding ──────────────────────────────────────────────────────────────────
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"   # 384-dim, runs fully offline

# ── Vector database ────────────────────────────────────────────────────────────
QDRANT_PATH:     str = "./qdrant_data"        # local folder, no server needed
COLLECTION_NAME: str = "policies_lc"          # separate collection from vanilla_rag

# ── Chunking ───────────────────────────────────────────────────────────────────
CHUNK_SIZE:      int = 500    # characters per chunk (LangChain uses chars, not words)
CHUNK_OVERLAP:   int = 50     # overlap between chunks to preserve context at boundaries

# ── Retrieval ──────────────────────────────────────────────────────────────────
TOP_K: int = 5   # number of chunks returned per query

# ── Source document ────────────────────────────────────────────────────────────
PDF_URL: str = "https://rikalp.in/wp-content/uploads/2024/07/HR-Policy.pdf"
