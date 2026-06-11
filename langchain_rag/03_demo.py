"""
03_demo.py — Demo Script (LangChain)

Runs the same 5 sample questions as vanilla_rag/03_demo.py through the
LangChain RAG pipeline so you can compare answers side by side.

Usage:
    cd langchain_rag
    python 03_demo.py
"""

import importlib

# Python cannot import modules whose names start with a digit via normal syntax.
# importlib.import_module() handles this cleanly.
_query = importlib.import_module("02_query")
rag    = _query.rag

# ── Sample questions ───────────────────────────────────────────────────────────
SAMPLE_QUESTIONS = [
    "What are the password and authentication requirements?",
    "How should a security incident be reported and handled?",
    "What security measures are required for remote work and VPN access?",
    "What is the NIST Cybersecurity Framework's approach to threat detection?",
    "How should employees be trained on IT security awareness?",
    "What are the leave and HR policy entitlements for employees?",
]

# ── Run demo ───────────────────────────────────────────────────────────────────
print("=" * 60)
print("   PolicyAI (IT & Security RAG) — Full Pipeline Demo")
print("=" * 60)

for i, question in enumerate(SAMPLE_QUESTIONS, start=1):
    print(f"\n[{i}/{len(SAMPLE_QUESTIONS)}] {question}")
    print("-" * 60)

    answer, context = rag(question)

    print(answer)
    print(f"\nSOURCES:\n{context}")
    print()

print("=" * 60)
print("  Demo complete.")
print("=" * 60)
