"""
02_query.py — Query Pipeline (LangChain)

Same goal as vanilla_rag/02_query.py but using LangChain abstractions.

The biggest difference here is the LCEL chain (LangChain Expression Language).
In vanilla_rag, rag() was a manual function with explicit steps.
In LangChain, those steps are declared as a pipeline using the | operator:

    rag_chain = retriever | format_docs | prompt | llm

Each | passes the output of the left side as input to the right side.
LangChain wires everything together — no manual step-by-step code needed.

Run interactively:
    cd langchain_rag
    python 02_query.py

Or import rag() into 03_demo.py.
"""

from langchain_huggingface              import HuggingFaceEmbeddings
from langchain_qdrant                   import QdrantVectorStore
from langchain_groq                     import ChatGroq
from langchain_core.prompts             import ChatPromptTemplate
from langchain_core.runnables           import RunnablePassthrough
from langchain_core.output_parsers      import StrOutputParser

from config import (
    COLLECTION_NAME, EMBEDDING_MODEL, GROQ_MODEL,
    TOP_K, QDRANT_PATH, GROQ_API_KEY,
)

# ── Embedder ───────────────────────────────────────────────────────────────────
#
# Must be the SAME model used during ingestion.
# Vectors are only comparable when produced by the same model.

embedder = HuggingFaceEmbeddings(model_name=f"sentence-transformers/{EMBEDDING_MODEL}")


# ── Vector store + Retriever ───────────────────────────────────────────────────
#
# from_existing_collection() connects to an already-indexed Qdrant collection.
# Compare to from_documents() in 01_ingest.py which created and populated it.
#
# as_retriever() wraps the vector store in LangChain's Retriever interface.
# A Retriever exposes a single method: .invoke(query) → List[Document]
# This is what the LCEL chain calls automatically during retrieval.
#
# search_kwargs={"k": TOP_K} → return top 5 most similar chunks per query.

vectorstore = QdrantVectorStore.from_existing_collection(
    embedding=embedder,
    path=QDRANT_PATH,
    collection_name=COLLECTION_NAME,
)

retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})


# ── LLM ────────────────────────────────────────────────────────────────────────
#
# ChatGroq is LangChain's wrapper around the Groq API.
# It implements the same ChatModel interface as ChatOpenAI, ChatAnthropic etc.
# Swapping the LLM provider = change one line here, nothing else changes.

llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0.2,   # low = factual, deterministic answers
)


# ── Prompt Template ────────────────────────────────────────────────────────────
#
# ChatPromptTemplate.from_messages() builds a reusable prompt with named slots.
# {context} and {question} are filled in at runtime by the LCEL chain.
#
# Splitting into system + human messages gives the LLM a clear role boundary:
#   system message → sets behaviour ("only use the context, cite sources")
#   human message  → provides the actual data + question

RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a knowledgeable HR and IT Security Policy assistant.\n"
        "Answer questions using ONLY the information in the context below, which comes from "
        "official policy documents: HR policies (leave, appraisal, conduct, travel), "
        "the NIST Cybersecurity Framework, remote work security guidelines, "
        "IT security awareness training materials, and incident response procedures.\n"
        "Write a clear, direct answer in professional language — do NOT copy source labels, "
        "page numbers, or document names into your answer. "
        "Those are shown separately to the user.\n"
        "If the answer is not in the context, say so honestly.",
    ),
    (
        "human",
        "Context:\n{context}\n\nQuestion: {question}",
    ),
])


# ── Document formatter ─────────────────────────────────────────────────────────
#
# The retriever returns a List[Document].
# The prompt expects a plain string for {context}.
# format_docs() bridges that gap — it's the only manual step in the chain.
#
# doc.metadata["source"] and doc.metadata["page"] come free from PyMuPDFLoader
# (set automatically during ingestion — no manual tracking needed).

def format_docs(docs: list) -> str:
    """Convert a list of retrieved Documents into a cited context string."""
    parts = []
    for i, doc in enumerate(docs, 1):
        name     = doc.metadata.get("policy_name") or \
                   doc.metadata.get("source", "unknown").split("\\")[-1].split("/")[-1]
        category = doc.metadata.get("policy_category", "")
        page     = doc.metadata.get("page", "?")
        label    = f"{name} [{category}] — Page {page}" if category else f"{name} — Page {page}"
        parts.append(f"[Source {i} | {label}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


# ── LCEL Chain ─────────────────────────────────────────────────────────────────
#
# This is the core LangChain concept — LangChain Expression Language (LCEL).
# The | operator chains Runnables together into a pipeline.
#
# How it works step by step:
#
#   Input: a plain string question  e.g. "What is the leave policy?"
#
#   Step 1 — The dict {"context": ..., "question": ...} splits the input:
#     "context"  branch: retriever fetches top-5 chunks → format_docs() converts to string
#     "question" branch: RunnablePassthrough() passes the question through unchanged
#
#   Step 2 — RAG_PROMPT fills {context} and {question} into the template
#
#   Step 3 — llm generates the answer (returns an AIMessage object)
#
#   Step 4 — StrOutputParser() extracts just the .content string from AIMessage
#
#   Output: a plain string answer
#
# Compare to vanilla_rag where we wrote all these steps manually inside rag().

rag_chain = (
    {
        "context":  retriever | format_docs,   # retrieve → format
        "question": RunnablePassthrough(),      # pass question through as-is
    }
    | RAG_PROMPT          # fill template slots
    | llm                 # generate answer
    | StrOutputParser()   # extract .content string from AIMessage
)


# ── rag() wrapper ──────────────────────────────────────────────────────────────
#
# A thin wrapper so 03_demo.py can call rag(question) just like vanilla_rag.
# Returns (answer, context) tuple to keep the same interface.

def rag(query: str) -> tuple[str, str]:
    """
    Run the full RAG pipeline for a question.

    Returns:
        answer  : LLM-generated answer grounded in retrieved policy chunks.
        context : The formatted context string sent to the LLM (for debugging).
    """
    # Retrieve docs separately so we can return the context for inspection
    docs    = retriever.invoke(query)
    context = format_docs(docs)
    answer  = str(rag_chain.invoke(query))   # TextAccessor → plain str
    return answer, context


# ── Run interactively ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    question = input("Ask a policy question: ").strip()

    if question:
        answer, context = rag(question)
        print(f"\n{'-' * 55}")
        print(answer)
        print(f"\n{'-' * 55}\nSOURCES:\n{context}")
