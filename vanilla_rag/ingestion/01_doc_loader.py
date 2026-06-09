"""
01_doc_loader.py — PDF fetching and text extraction

RAG Step 1 of 3: Load the document.

Responsibilities:
    - Download a PDF from a remote URL
    - Open it in memory (no temp files)
    - Extract raw text from every page, preserving page numbers for citations
"""

import requests
import fitz                 # PyMuPDF — fast, reliable PDF text extraction
from io import BytesIO


def load_pdf(url: str) -> BytesIO:
    """
    Download a PDF from a remote URL and return it as an in-memory byte stream.

    Using BytesIO avoids writing a temp file to disk — fitz can open it
    directly from memory via the stream= argument.

    Raises:
        requests.HTTPError — if the server returns 4xx or 5xx
    """
    print(f"Fetching PDF: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return BytesIO(response.content)


def extract_pages(pdf_bytes: BytesIO, source_name: str) -> list[dict]:
    """
    Open the PDF from a byte stream and extract the text of every page.

    Args:
        pdf_bytes   : In-memory PDF content returned by load_pdf().
        source_name : Filename used as the citation label (e.g. "HR-Policy.pdf").

    Returns:
        List of page dicts:
            { "page": int,     — 1-based page number
              "text": str,     — raw extracted text
              "source": str }  — source filename for citations

    Pages with no extractable text (e.g. scanned images) are skipped.
    """
    doc   = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:
            pages.append({
                "page":   page_num,
                "text":   text,
                "source": source_name,
            })

    print(f"Extracted {len(pages)} pages from '{source_name}'")
    return pages
