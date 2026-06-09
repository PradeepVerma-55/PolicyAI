---
title: PolicyAI
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "6.17.3"
app_file: chatbot/app.py
pinned: false
---

# PolicyAI 🤖📄

> **"Your company's policies, finally answerable in seconds."**

An AI-powered policy intelligence system that reads your company's PDF documents and answers employee questions instantly — with exact citations, zero hallucination, and zero manual searching.

Built **three ways**:
- **`vanilla_rag/`** — pure Python, no frameworks, every step explicit
- **`langchain_rag/`** — same pipeline via LangChain + LCEL abstractions
- **`chatbot/`** — professional Gradio chat UI on top of the LangChain pipeline, deployable to Hugging Face Spaces

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

PolicyAI  →  Employees are entitled to 18 Earned Leaves per calendar year.
             Leave is calculated on a pro-rata basis for mid-year joiners.
             Sick leave beyond 3 consecutive days requires a medical certificate.

             📄 Source: HR-Policy.pdf — Page 3
             ⏱  Time: 3 seconds
```

---

## 🔀 Three Implementations — Same Pipeline

| Step | 🐍 vanilla_rag | 🦜 langchain_rag | 💬 chatbot |
|---|---|---|---|
| **PDF Loading** | `requests` + `PyMuPDF` | `PyMuPDFLoader` | via langchain_rag |
| **Chunking** | Custom 100-word window | `RecursiveCharacterTextSplitter` | via langchain_rag |
| **Embedding** | `SentenceTransformer.encode()` | `HuggingFaceEmbeddings` | via langchain_rag |
| **Vector Store** | Manual `PointStruct` + `upsert()` | `QdrantVectorStore` | via langchain_rag |
| **Retrieval** | Manual `query_points()` | `vectorstore.as_retriever()` | via langchain_rag |
| **LLM** | Raw `groq.chat.completions` | `ChatGroq` | via langchain_rag |
| **Pipeline** | Manual `rag()` function | LCEL chain `\|` | via langchain_rag |
| **UI** | CLI / terminal | CLI / terminal | Gradio web app |
| **Deploy** | Local only | Local only | Hugging Face Spaces |

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
│   ├── config.py                 ← all constants and env vars
│   ├── 01_ingest.py              ← orchestrates the ingestion pipeline
│   ├── 02_query.py               ← retrieve() + build_context() + rag()
│   └── 03_demo.py                ← runs 5 sample questions end-to-end
│
├── langchain_rag/                ← Same pipeline via LangChain abstractions
│   ├── config.py                 ← all constants and env vars
│   ├── 01_ingest.py              ← PyMuPDFLoader + splitter + QdrantVectorStore
│   ├── 02_query.py               ← retriever + ChatGroq + LCEL chain
│   └── 03_demo.py                ← runs 5 sample questions end-to-end
│
├── chatbot/                      ← Gradio chat UI (Hugging Face Spaces ready)
│   ├── app.py                    ← entry point: path bootstrap + launch()
│   ├── pipeline.py               ← ensure_indexed() + exposes rag()
│   ├── handlers.py               ← respond() + clear_chat() handlers
│   ├── styles.py                 ← dark-theme CSS
│   └── ui.py                     ← Gradio layout + event wiring
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
| **PDF Extraction** | PyMuPDF 1.27.2 | Fast, reliable, page-level metadata |
| **Chunking** | Word window / RecursiveCharacterTextSplitter | Preserves context, respects token limits |
| **Embeddings** | all-MiniLM-L6-v2 (sentence-transformers) | 384-dim semantic vectors, runs fully offline |
| **Vector Database** | Qdrant 1.18.0 | Local file-based, no Docker or server needed |
| **Search Index** | HNSW (Hierarchical Navigable Small World) | Millisecond semantic search |
| **LLM Inference** | Groq — llama-3.1-8b-instant | Free tier, ultra-fast inference |
| **Framework** | LangChain + LCEL | Industry-standard RAG abstractions |
| **Chat UI** | Gradio 6 | Web interface, one-command HF Spaces deploy |
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

### 💬 Chatbot UI (Recommended)

The fastest way to experience PolicyAI — a professional dark-theme web interface with a chat panel and a live sources panel.

```bash
python chatbot\app.py
```

Then open **http://localhost:7860** in your browser.

On first run, the app automatically downloads the HR Policy PDF and indexes it (~30 seconds). Every subsequent start skips this step.

---

### 🐍 Vanilla RAG (CLI)

```bash
# Step 1 — ingest the PDF (run once)
python vanilla_rag\01_ingest.py

# Step 2 — ask a question interactively
python vanilla_rag\02_query.py

# Step 3 — run the full demo with 5 sample questions
python vanilla_rag\03_demo.py
```

### 🦜 LangChain RAG (CLI)

```bash
# Step 1 — ingest the PDF (run once)
python langchain_rag\01_ingest.py

# Step 2 — ask a question interactively
python langchain_rag\02_query.py

# Step 3 — run the full demo with 5 sample questions
python langchain_rag\03_demo.py
```

---

## 🌐 Deploy to Hugging Face Spaces

1. **Push this repo to GitHub**

2. **Create a new Space** at [huggingface.co/new-space](https://huggingface.co/new-space)
   - SDK: **Gradio**
   - Link your GitHub repository

3. **Set your API key** — Space Settings → Variables and Secrets → add `GROQ_API_KEY`

4. **Add the Space config** — prepend this block to `README.md` in your Space:

```yaml
---
title: PolicyAI
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "6.17.3"
app_file: chatbot/app.py
pinned: false
---
```

On cold start, the Space automatically downloads and indexes the PDF (~60 seconds), then serves queries instantly.

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

**LCEL chain (LangChain)** — LangChain Expression Language lets you declare the entire RAG pipeline with the `|` operator:

```python
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)
```

**Same embedding model at ingestion and query time** — vectors are only comparable when produced by the same model. Using a different model at query time returns meaningless results.

**Separation of concerns (chatbot/)** — each file has exactly one responsibility: `pipeline.py` owns RAG init, `handlers.py` owns Gradio callbacks, `styles.py` owns CSS, `ui.py` owns layout, `app.py` is the entry point.

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
  ✅ chatbot/      — Gradio UI, Hugging Face Spaces ready

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
- [Gradio](https://gradio.app) — web UI framework for ML apps

---

