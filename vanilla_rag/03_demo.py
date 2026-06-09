"""
03_demo.py — Demo Script

Runs a curated set of sample HR policy questions through the full RAG pipeline
and prints each answer with its source citations.

Use this to verify the pipeline end-to-end after running 01_ingest.py.

Usage:
    cd vanilla_rag
    python 03_demo.py
"""

import importlib

# Standard Python imports cannot reference modules whose names start with a digit.
# importlib.import_module() handles this case cleanly.
_query = importlib.import_module("02_query")
rag    = _query.rag   # bring rag() into local scope

# ── Sample questions ───────────────────────────────────────────────────────────
# These cover the most common policy topics employees ask about.
# Extend this list to test additional domains (IT, Safety, Finance, etc.)
SAMPLE_QUESTIONS = [
    "What are the leave entitlements for employees?",
    "What is the maternity leave policy?",
    "How does the performance appraisal process work?",
    "What are the travel expense reimbursement rules?",
    "What are the disciplinary action procedures?",
]

# ── Run demo ───────────────────────────────────────────────────────────────────
print("=" * 60)
print("   PolicyAI (Vanilla RAG) — Full Pipeline Demo")
print("=" * 60)

for i, question in enumerate(SAMPLE_QUESTIONS, start=1):
    print(f"\n[{i}/{len(SAMPLE_QUESTIONS)}] {question}")
    print("-" * 60)

    # rag() returns (answer, context) — context holds the raw source chunks
    answer, context = rag(question)

    print(answer)
    print(f"\nSOURCES:\n{context}")
    print()

print("=" * 60)
print("  Demo complete.")
print("=" * 60)
