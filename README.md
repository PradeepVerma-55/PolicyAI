# PolicyAI

> **"Your company's policies, finally answerable in seconds."**

An AI-powered policy intelligence system that reads your company's PDF documents and answers employee questions instantly — with exact citations, zero hallucination, and zero manual searching.

Built **two ways** side by side — once from scratch (vanilla RAG) and once using LangChain — so you can see exactly what the framework does for you.

---

## The Problem

Every company has the same invisible crisis.

Hundreds of policy documents sit in shared drives, intranets, and email attachments — unread, unsearchable, and impossible to navigate when someone urgently needs an answer.

```
9:00 AM  — New hire asks HR: "How many sick leaves do I get?"
           HR opens a 120-page PDF, searches manually...
           25 minutes later replies with an answer.

2:00 PM  — Site manager asks Safety: "What PPE is needed for excavation?"
           Safety officer searches OSHA manual + internal doc...
           40 minutes wasted.
```

**500 employees x 3 questions x every week = 1,500 manual searches. Every single week.**

---

## The Solution

```
Employee  ->  "How many sick leaves do I get?"

PolicyAI  ->  All regular employees are entitled to 18 Earned Leaves
              in a calendar year. If you joined mid-year, leaves are
              calculated on a pro-rata basis.

              Source: HR-Policy.pdf -- Page 3
              Time: 3 seconds
```

---

## Two Implementations

This project builds the same RAG pipeline twice — so you understand both the concepts and the framework.

| | vanilla_rag | langchain_rag |
|---|---|---|
| PDF loading | `requests` + `PyMuPDF` (manual) | `PyMuPDFLoader` |
| Chunking | Custom 100-word word window | `RecursiveCharacterTextSplitter` |
| Embedding | `SentenceTransformer.encode()` | `HuggingFaceEmbeddings` |
| Vector store | Manual `PointStruct` + `client.upsert()` | `QdrantVectorStore.from_documents()` |
| Retrieval | Manual `query_points()` call | `vectorstore.as_retriever()` |
| LLM call | Raw `groq.chat.completions.create()` | `ChatGroq` |
| Prompt | f-string | `ChatPromptTemplate` |
| Pipeline | Manual `rag()` function | LCEL chain with `\|` operator |

---

## How It Works

```
INGESTION  (run once per document)
------------------------------------------------------------------
PDF (URL or local file)
      |
      v
Extract text page by page          [PyMuPDF / PyMuPDFLoader]
      |
      v
Split into chunks                  [word window / RecursiveCharacterTextSplitter]
      |
      v
Convert each chunk to vector       [all-MiniLM-L6-v2, 384 dimensions]
      |
      v
Store vector + text + page number  [Qdrant local file store]

QUERY  (runs on every question)
------------------------------------------------------------------
Employee question (plain English)
      |
      v
Convert question to vector         [same embedding model]
      |
      v
Semantic search -- top 5 chunks    [Qdrant HNSW index]
      |
      v
Build context block with citations
      |
      v
Generate grounded answer           [Groq -- llama-3.1-8b-instant]
      |
      v
Answer + Source Document + Page Number
```

---

## Project Structure

```
PolicyAI/
|
|-- vanilla_rag/                <- pure Python, no frameworks
|   |-- ingestion/
|   |   |-- 01_doc_loader.py   <- fetch PDF, extract pages with PyMuPDF
|   |   |-- 02_chunker.py      <- split pages into 100-word chunks
|   |   |-- 03_embedder.py     <- embed chunks with sentence-transformers
|   |   `-- __init__.py
|   |-- config.py              <- all constants and env vars
|   |-- 01_ingest.py           <- orchestrates ingestion pipeline
|   |-- 02_query.py            <- retrieve() + build_context() + rag()
|   `-- 03_demo.py             <- runs 5 sample questions
|
|-- langchain_rag/              <- same pipeline using LangChain abstractions
|   |-- config.py              <- all constants and env vars
|   |-- 01_ingest.py           <- PyMuPDFLoader + splitter + QdrantVectorStore
|   |-- 02_query.py            <- retriever + ChatGroq + LCEL chain
|   `-- 03_demo.py             <- runs 5 sample questions
|
|-- data/                       <- PDFs downloaded here (gitignored)
|-- .env                        <- GROQ_API_KEY (never commit)
|-- .gitignore
|-- requirements.txt
`-- README.md
```

---

## Tech Stack

| Component | Technology |
|---|---|
| PDF parsing | PyMuPDF 1.27.2 |
| Embeddings | all-MiniLM-L6-v2 (sentence-transformers) — 384-dim, runs offline |
| Vector database | Qdrant 1.18.0 — local file mode, no Docker needed |
| LLM | Groq — llama-3.1-8b-instant (free tier) |
| LangChain | langchain, langchain-community, langchain-groq, langchain-qdrant, langchain-huggingface |
| Language | Python 3.10+ |

---

## Getting Started

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

Add your Groq API key to `.env` in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

---

## Running vanilla_rag

```bash
# Step 1 -- ingest the PDF (run once)
python vanilla_rag\01_ingest.py

# Step 2 -- ask a question interactively
python vanilla_rag\02_query.py

# Step 3 -- run the full demo with 5 sample questions
python vanilla_rag\03_demo.py
```

## Running langchain_rag

```bash
# Step 1 -- ingest the PDF (run once)
python langchain_rag\01_ingest.py

# Step 2 -- ask a question interactively
python langchain_rag\02_query.py

# Step 3 -- run the full demo with 5 sample questions
python langchain_rag\03_demo.py
```

---

## Sample Questions

```
"What are the leave entitlements for employees?"
"What is the maternity leave policy?"
"How does the performance appraisal process work?"
"What are the travel expense reimbursement rules?"
"What are the disciplinary action procedures?"
"Can employees use personal devices for work?"
"What should I do if I suspect a security breach?"
```

---

## Key Concepts Demonstrated

**RAG (Retrieval-Augmented Generation)** — instead of asking the LLM from memory, we retrieve relevant chunks from the document first, then ask the LLM to answer using only those chunks. This prevents hallucination and enables citations.

**Semantic search** — questions are matched to chunks by meaning, not keywords. "How many days off do I get?" finds the leave policy even though it doesn't use the word "leave".

**LCEL chain (LangChain only)** — LangChain Expression Language lets you declare the pipeline with the `|` operator instead of writing procedural code:

```python
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)
```

**Why the same embedding model at ingestion and query time?** — vectors are only comparable when produced by the same model. Using a different model at query time would return garbage results.

---

## Roadmap

```
Phase 1 -- Done
  [x] HR Policy document ingestion and Q&A
  [x] Page-level citations
  [x] Semantic search with Qdrant
  [x] Groq LLM grounded answers
  [x] vanilla_rag  -- pure Python, no frameworks
  [x] langchain_rag -- LangChain + LCEL chain

Phase 2 -- Next
  [ ] Multi-domain support (HR + Safety + IT + Legal)
  [ ] Source filtering (ask HR questions -> search only HR docs)
  [ ] Upgrade PDF reading to Docling (hierarchical chunking)

Phase 3 -- Future
  [ ] REST API via FastAPI
  [ ] Slack bot integration
  [ ] Role-based access -- employees only see permitted documents
  [ ] Conflict detection -- "Do these two policies contradict each other?"
  [ ] Auto-refresh -- re-index when a document is updated
```

---

## Acknowledgements

- [Qdrant](https://qdrant.tech) — open-source vector database
- [Sentence Transformers](https://www.sbert.net) — all-MiniLM-L6-v2 embedding model
- [Groq](https://console.groq.com) — fast LLM inference
- [LangChain](https://python.langchain.com) — LLM application framework

---

*Built as part of the Codebasics AI Engineering Bootcamp.*
*Demonstrating: RAG pipeline, vector databases, semantic search, LLM grounding, vanilla Python vs LangChain comparison.*
