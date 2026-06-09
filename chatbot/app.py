"""
app.py — PolicyAI Chatbot entry point

Responsibilities (and ONLY these)
-----------------------------------
1. Bootstrap the Python path so sibling modules can import from langchain_rag/.
2. Import the pre-built Gradio demo from ui.py.
3. Call demo.launch() with server settings and the CSS theme.

Run locally
-----------
    cd D:\\...\\PolicyAI
    python chatbot\\app.py

Hugging Face Spaces
-------------------
    Set GROQ_API_KEY as a Space secret.
    README.md frontmatter: app_file: chatbot/app.py
"""

import os
import sys
from pathlib import Path

# ── Path bootstrap (must happen before any project imports) ───────────────────
# ROOT = PolicyAI/  (one level above chatbot/)
ROOT = Path(__file__).parent.parent

# Anchor relative paths (./qdrant_data, ./data/) to the project root
os.chdir(ROOT)

# Allow `from config import ...` and `import 02_query` to resolve from langchain_rag/
sys.path.insert(0, str(ROOT / "langchain_rag"))

# ── Application imports (after path bootstrap) ────────────────────────────────
from ui import demo          # builds the Gradio layout + wires events
from styles import CSS       # dark-theme stylesheet


# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",   # bind all interfaces (required for HF Spaces)
        server_port=7860,         # HF Spaces default port
        share=False,
        css=CSS,
    )
