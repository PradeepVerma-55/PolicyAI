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
QDRANT_PATH:     str = "./qdrant_data"
COLLECTION_NAME: str = "it_security_policies"

# ── Chunking ───────────────────────────────────────────────────────────────────
CHUNK_SIZE:    int = 500    # characters per chunk
CHUNK_OVERLAP: int = 50     # overlap to preserve context at boundaries

# ── Retrieval ──────────────────────────────────────────────────────────────────
# Slightly higher than single-doc setup to surface relevant chunks across
# multiple policy sources in one query
TOP_K: int = 6

# ── Policy document library ────────────────────────────────────────────────────
# All sources are publicly available; downloaded once and cached in data/
# Each entry: name (display), category (tag), url (download), filename (cache key)
POLICY_SOURCES = [
    {
        "name":     "HR Policy",
        "category": "Human Resources",
        "url":      "https://rikalp.in/wp-content/uploads/2024/07/HR-Policy.pdf",
        "filename": "HR-Policy.pdf",
    },
    {
        "name":     "NIST Cybersecurity Framework v1.1",
        "category": "IT Security",
        "url":      "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.04162018.pdf",
        "filename": "NIST-CSF-v1.1.pdf",
    },
    {
        "name":     "NIST SP 800-114r1: Telework & Remote Access Security",
        "category": "Remote Work Security",
        "url":      "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-114r1.pdf",
        "filename": "NIST-SP-800-114r1-Telework.pdf",
    },
    {
        "name":     "NIST SP 800-50: Building an IT Security Awareness Program",
        "category": "Security Training",
        "url":      "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-50.pdf",
        "filename": "NIST-SP-800-50-Security-Awareness.pdf",
    },
    {
        "name":     "NIST SP 800-61r2: Computer Security Incident Handling",
        "category": "Incident Response",
        "url":      "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf",
        "filename": "NIST-SP-800-61r2-Incident-Response.pdf",
    },
]
