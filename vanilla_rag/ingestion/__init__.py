"""
ingestion/__init__.py

Re-exports all public functions from the numbered ingestion modules so the
rest of the codebase can import cleanly:

    from ingestion import load_pdf, extract_pages, chunk_pages, embed_chunks

Python's import statement cannot reference module names that start with a digit,
so importlib.import_module() is used here to load them by string name.
"""

import importlib

_doc_loader = importlib.import_module("ingestion.01_doc_loader")
_chunker    = importlib.import_module("ingestion.02_chunker")
_embedder   = importlib.import_module("ingestion.03_embedder")

# Document loading
load_pdf      = _doc_loader.load_pdf
extract_pages = _doc_loader.extract_pages

# Chunking
chunk_pages   = _chunker.chunk_pages

# Embedding
get_embedder  = _embedder.get_embedder
embed_chunks  = _embedder.embed_chunks
