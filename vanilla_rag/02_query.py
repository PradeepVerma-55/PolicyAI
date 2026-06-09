"""
02_query.py — Query Pipeline

Exposes a single rag() function that takes a plain-English question,
finds the most relevant policy chunks via semantic search, and returns
a grounded answer with exact document and page citations.

Run interactively:
    cd vanilla_rag
    python 02_query.py

Or import rag() into other scripts (e.g. 03_demo.py).
"""

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from groq import Groq
from config import COLLECTION_NAME, EMBEDDING_MODEL, GROQ_MODEL, TOP_K, QDRANT_PATH, GROQ_API_KEY

# System prompt constrains the LLM to the retrieved context only,
# preventing hallucination on topics not covered by the indexed documents
SYSTEM_PROMPT = """You are a helpful HR policy assistant.
Answer the user's question using ONLY the context provided below.
Always cite the source document and page number when referencing specific information.
If the context does not contain enough information, say so — do not make things up."""

# ── Clients ────────────────────────────────────────────────────────────────────
# Both clients are created once at module load and reused across all calls
embedder    = SentenceTransformer(EMBEDDING_MODEL)
qdrant      = QdrantClient(path=QDRANT_PATH)
groq_client = Groq(api_key=GROQ_API_KEY)


# ── Retrieval ──────────────────────────────────────────────────────────────────
def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Convert the query into an embedding vector and search Qdrant for the
    top-k most semantically similar chunks.

    The same embedding model used during ingestion must be used here —
    vectors are only comparable when produced by the same model.

    Returns a list of payload dicts with an extra "score" field (cosine similarity).
    """
    # Encode the question into the same 384-dim vector space as the stored chunks
    query_vector = embedder.encode(query).tolist()

    hits = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,   # include text + citation metadata in results
    )

    return [
        {**hit.payload, "score": round(hit.score, 4)}
        for hit in hits.points
    ]


# ── Context builder ────────────────────────────────────────────────────────────
def build_context(chunks: list[dict]) -> str:
    """
    Format the retrieved chunks into a numbered context block for the LLM prompt.

    Each chunk is prefixed with its source document and page number so the LLM
    can include accurate citations in its answer.

    Example output:
        [Source 1 | HR-Policy.pdf — Page 12]
        Employees are entitled to 10 days of sick leave per year...

        ---

        [Source 2 | HR-Policy.pdf — Page 13]
        Sick leave beyond 3 consecutive days requires a medical certificate...
    """
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Source {i} | {chunk['source']} — Page {chunk['page']}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


# ── RAG pipeline ───────────────────────────────────────────────────────────────
def rag(query: str, top_k: int = TOP_K) -> tuple[str, str]:
    """
    End-to-end Retrieval-Augmented Generation pipeline.

    Steps:
        1. Retrieve — find the top-k most relevant chunks from Qdrant
        2. Build context — format chunks into a cited context block
        3. Generate — send system prompt + context + question to Groq LLM

    Args:
        query  : Plain-English question from the user.
        top_k  : How many chunks to retrieve (more = broader context, higher cost).

    Returns:
        answer  : LLM-generated answer grounded in the retrieved context.
        context : The raw context block sent to the LLM (useful for debugging).
    """
    # Step 1 — Retrieve the most relevant chunks
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return "No relevant content found in the policy documents.", ""

    # Step 2 — Format chunks into a context block with citations
    context = build_context(chunks)

    # Step 3 — Build the prompt and call the LLM
    # Splitting into system + user messages gives the LLM a clear role boundary:
    # the system message sets behaviour, the user message provides data + question
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.2,   # low temperature = factual, deterministic answers
    )

    return response.choices[0].message.content, context


# ── Run interactively ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    question = input("Ask a policy question: ").strip()

    if question:
        answer, context = rag(question)
        print(f"\n{'-' * 55}")
        print(answer)
        print(f"\n{'-' * 55}\nSOURCES:\n{context}")
