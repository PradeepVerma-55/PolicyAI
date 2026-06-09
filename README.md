# PolicyAI 🤖📄

> **"Your company's policies, finally answerable in seconds."**

An AI-powered policy intelligence system that reads your company's PDF documents and answers employee questions instantly — with exact citations, zero hallucination, and zero manual searching.

Built **two ways** side by side — once from scratch (Vanilla RAG) and once using LangChain — so you can clearly see what each layer of abstraction does for you.

---

## 🚨 The Problem

Every company has the same invisible crisis.

Hundreds of policy documents sit in shared drives, intranets, and email attachments — unread, unsearchable, and impossible to navigate when someone urgently needs an answer.

**Without PolicyAI — the daily reality:**

```
9:00 AM  — New hire asks HR: "How many sick leaves do I get?"
           HR opens a 120-page PDF, searches manually...
           25 minutes later replies with an answer.

2:00 PM  — Site manager asks Safety: "What PPE is needed for excavation?"
           Safety officer searches OSHA manual + internal doc...
           40 minutes wasted.

4:00 PM  — Finance asks: "What is the vendor payment approval limit?"
           Three people CC'd on email. Nobody has the right version.
```

**500 employees × 3 questions × every week = 1,500 manual searches. Every. Single. Week.**

---

## ✅ The Solution — PolicyAI

**With PolicyAI — the same reality:**

```
Employee  →  "How many sick leaves do I get?"

PolicyAI  →  All regular employees are entitled to 18 Earned Leaves
             in a calendar year. If you joined mid-year, leaves are
             calculated on a pro-rata basis. Sick leave beyond 3
             consecutive days requires a medical certificate.

             📄 Source: HR-Policy.pdf — Page 3
             ⏱  Time: 3 seconds
```

---

## 🔀 Two Implementations — Same Pipeline

This project solves the same problem **twice** — so you understand both the raw concepts and what a framework like LangChain actually abstracts away.

| Step | 🐍 vanilla_rag | 🦜 langchain_rag |
|---|---|---|
| **PDF Loading** | `requests` + `PyMuPDF` (manual) | `PyMuPDFLoader` |
| **Chunking** | Custom 100-word word window | `RecursiveCharacterTextSplitter` |
| **Embedding** | `SentenceTransformer.encode()` | `HuggingFaceEmbeddings` |
| **Vector Store** | Manual `PointStruct` + `client.upsert()` | `QdrantVectorStore.from_documents()` |
| **Retrieval** | Manual `query_points()` call | `vectorstore.as_retriever()` |
| **LLM Call** | Raw `groq.chat.completions.create()` | `ChatGroq` |
| **Prompt** | f-string | `ChatPromptTemplate` |
| **Pipeline** | Manual `rag()` function | LCEL chain with `\|` operator |

---

## 🏗️ How PolicyAI Works

```
┌─────────────────────────────────────────────────────────────┐
│                   INGESTION PHASE                           │
│                (run once per document)                      │
│                                                             │
│   PDF Document  (URL or local file)                         │
│         ↓                                                   │
│   Extract text page by page      [PyMuPDF / PyMuPDFLoader]  │
│         ↓                                                   │
│   Split into chunks              [word window / splitter]   │
│         ↓                                                   │
│   Convert each chunk → vector    [all-MiniLM-L6-v2, 384-dim]│
│         ↓                                                   │
│   Store vector + text + page     [Qdrant local file store]  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    QUERY PHASE                              │
│               (runs on every question)                      │
│                                                             │
│   Employee question  (plain English)                        │
│         ↓                                                   │
│   Convert question → vector      [same embedding model]     │
│         ↓                                                   │
│   Semantic search — top 5 chunks [Qdrant HNSW index]        │
│         ↓                                                   │
│   Build context block with citations                        │
│         ↓                                                   │
│   Generate grounded answer       [Groq — llama-3.1-8b]      │
│         ↓                                                   │
│   Answer + Source Document + Page Number                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
PolicyAI/
│
├── vanilla_rag/                  ← Pure Python — no frameworks
│   ├── ingestion/
│   │   ├── 01_doc_loader.py      ← fetch PDF, extract pages with PyMuPDF
│   │   ├── 02_chunker.py         ← split pages into 100-word chunks
│   │   ├── 03_embedder.py        ← embed chunks with sentence-transformers
│   │   └── __init__.py           ← re-exports all functions cleanly
│   ├── config.py                 ← all constants and env vars in one place
│   ├── 01_ingest.py              ← orchestrates the ingestion pipeline
│   ├── 02_query.py               ← retrieve() + build_context() + rag()
│   └── 03_demo.py                ← runs 5 sample questions end-to-end
│
├── langchain_rag/                ← Same pipeline via LangChain abstractions
│   ├── config.py                 ← all constants and env vars in one place
│   ├── 01_ingest.py              ← PyMuPDFLoader + splitter + QdrantVectorStore
│   ├── 02_query.py               ← retriever + ChatGroq + LCEL chain
│   └── 03_demo.py                ← runs 5 sample questions end-to-end
│
├── data/                         ← PDFs downloaded here (gitignored)
├── .env                          ← GROQ_API_KEY (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **PDF Extraction** | PyMuPDF 1.27.2 | Fast, reliable, no model download needed |
| **Chunking** | Word window / RecursiveCharacterTextSplitter | Preserves context, respects token limits |
| **Embeddings** | all-MiniLM-L6-v2 (sentence-transformers) | 384-dim semantic vectors, runs fully offline |
| **Vector Database** | Qdrant 1.18.0 | Local file-based, no Docker or server needed |
| **Search Index** | HNSW (Hierarchical Navigable Small World) | Millisecond semantic search |
| **LLM Inference** | Groq — llama-3.1-8b-instant | Free tier, ultra-fast inference |
| **Framework** | LangChain + LCEL | Industry-standard RAG abstractions |
| **Language** | Python 3.10+ | |

---

## 🤔 Why RAG — Not Just Asking GPT?

| Challenge | GPT Alone | PolicyAI (RAG) |
|---|---|---|
| Your private HR manual | ❌ Has never seen it | ✅ Fully indexed and searchable |
| 200-page PDF | ❌ Context window too small | ✅ Retrieves only the relevant chunks |
| Policy updated last week | ❌ Training cutoff months ago | ✅ Re-index in minutes |
| Cited, verifiable answer | ❌ Confident but unverifiable | ✅ Exact page number and section |
| Private company data | ❌ Data sent to external servers | ✅ Everything runs locally |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Groq API key — free at [console.groq.com](https://console.groq.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/PolicyAI.git
cd PolicyAI

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

---

## ▶️ Running the Project

### 🐍 Vanilla RAG

```bash
# Step 1 — ingest the PDF (run once)
python vanilla_rag\01_ingest.py

# Step 2 — ask a question interactively
python vanilla_rag\02_query.py

# Step 3 — run the full demo with 5 sample questions
python vanilla_rag\03_demo.py
```

### 🦜 LangChain RAG

```bash
# Step 1 — ingest the PDF (run once)
python langchain_rag\01_ingest.py

# Step 2 — ask a question interactively
python langchain_rag\02_query.py

# Step 3 — run the full demo with 5 sample questions
python langchain_rag\03_demo.py
```

---

## 💡 Sample Questions

```
HR Domain
─────────────────────────────────────
"What are the leave entitlements for employees?"
"What is the maternity leave policy?"
"How does the performance appraisal process work?"
"What are the travel expense reimbursement rules?"
"What are the disciplinary action procedures?"

IT & Security Domain
─────────────────────────────────────
"Can employees use personal devices for work?"
"What should I do if I suspect a security breach?"
"What is the password policy?"
```

---

## 🧠 Key Concepts Demonstrated

**RAG (Retrieval-Augmented Generation)** — instead of asking the LLM from memory, we retrieve the most relevant document chunks first, then ask the LLM to answer using only those chunks. This prevents hallucination and makes every answer verifiable.

**Semantic search** — questions are matched to chunks by *meaning*, not keywords. *"How many days off do I get?"* finds the leave policy even though it doesn't use the word "leave".

**LCEL chain (LangChain)** — LangChain Expression Language lets you declare the entire RAG pipeline with the `|` operator instead of writing step-by-step procedural code:

```python
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)
```

**Same embedding model at ingestion and query time** — vectors are only comparable when produced by the same model. Using a different model at query time would return meaningless results.

---

## 🗺️ Roadmap

```
Phase 1 — Complete ✅
  ✅ HR Policy document ingestion and Q&A
  ✅ Page-level citations
  ✅ Semantic search with Qdrant
  ✅ Groq LLM grounded answers
  ✅ vanilla_rag  — pure Python, no frameworks
  ✅ langchain_rag — LangChain + LCEL chain

Phase 2 — Next 🔲
  🔲 Multi-domain support (HR + Safety + IT + Legal)
  🔲 Source filtering (HR questions → search only HR docs)
  🔲 Upgrade PDF parsing to Docling (hierarchical chunking)

Phase 3 — Future 🔲
  🔲 REST API via FastAPI
  🔲 Slack bot integration
  🔲 Role-based access — employees only see permitted documents
  🔲 Conflict detection — "Do these two policies contradict each other?"
  🔲 Auto-refresh — re-index when a document is updated
```

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [Qdrant](https://qdrant.tech) — open-source vector database
- [Sentence Transformers](https://www.sbert.net) — all-MiniLM-L6-v2 embedding model
- [Groq](https://console.groq.com) — fast LLM inference
- [LangChain](https://python.langchain.com) — LLM application framework


---


