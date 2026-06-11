---
title: PolicyAI
emoji: 🔒
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "6.17.3"
app_file: chatbot/app.py
pinned: false
---

# PolicyAI 🔒📄

> **"Your company's HR and IT Security policies, finally answerable in seconds."**

An AI-powered policy intelligence system that reads official policy documents — HR manuals, NIST cybersecurity standards, incident response guides, and more — and answers employee questions instantly, with exact citations, zero hallucination, and zero manual searching.

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

2:00 PM  — Developer asks IT: "What do I do if I suspect a phishing attack?"
           IT Security searches the NIST incident response guide + internal docs...
           40 minutes wasted.

4:00 PM  — Remote employee asks: "What VPN and security tools do I need?"
           Three people CC'd on email. Nobody has the right version.
```

**500 employees × 3 questions × every week = 1,500 manual searches. Every. Single. Week.**

---

## ✅ The Solution — PolicyAI

**With PolicyAI — the same reality:**

```
Employee  ->  "What do I do if I suspect a phishing attack?"

PolicyAI  ->  When a security incident is suspected, users should immediately
              report it to the IT Security team. Preserve all evidence —
              do not delete emails or logs. Isolate the affected system from
              the network if possible. Document the timeline of events.

              Source: NIST SP 800-61r2 [Incident Response] — Page 21
              Time  : 3 seconds
```

```
Employee  ->  "How many sick leaves do I get?"

PolicyAI  ->  Employees are entitled to 18 Earned Leaves per calendar year.
              Leave is calculated on a pro-rata basis for mid-year joiners.
              Sick leave beyond 3 consecutive days requires a medical certificate.

              Source: HR Policy [Human Resources] — Page 3
              Time  : 3 seconds
```

---

## 📚 Policy Library (5 Sources, Indexed Automatically)

All documents are publicly available and downloaded on first run:

| # | Document | Category | Source |
|---|---|---|---|
| 1 | HR Policy | Human Resources | rikalp.in |
| 2 | NIST Cybersecurity Framework v1.1 | IT Security | nvlpubs.nist.gov |
| 3 | NIST SP 800-114r1: Telework & Remote Access Security | Remote Work Security | nvlpubs.nist.gov |
| 4 | NIST SP 800-50: Building an IT Security Awareness Program | Security Training | nvlpubs.nist.gov |
| 5 | NIST SP 800-61r2: Computer Security Incident Handling | Incident Response | nvlpubs.nist.gov |

**Total indexed:** ~1,600 chunks across 268 pages of policy content.

To add new sources, append an entry to `POLICY_SOURCES` in `langchain_rag/config.py` and delete `qdrant_data/` to trigger re-indexing.

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
+-------------------------------------------------------------+
|                   INGESTION PHASE                           |
|            (runs once — all 5 sources)                      |
|                                                             |
|   Source 1: HR Policy PDF          (Human Resources)        |
|   Source 2: NIST CSF v1.1 PDF      (IT Security)            |
|   Source 3: NIST 800-114r1 PDF     (Remote Work Security)   |
|   Source 4: NIST 800-50 PDF        (Security Training)      |
|   Source 5: NIST 800-61r2 PDF      (Incident Response)      |
|         |                                                   |
|         v                                                   |
|   Extract text page by page        [PyMuPDFLoader]          |
|   Tag each page: policy_name,                               |
|                  policy_category   [custom metadata]        |
|         |                                                   |
|         v                                                   |
|   Split into 500-char chunks       [RecursiveCharSplitter]  |
|         |                                                   |
|         v                                                   |
|   Convert each chunk -> vector     [all-MiniLM-L6-v2]       |
|         |                                                   |
|         v                                                   |
|   Store: vector + text + metadata  [Qdrant — 1,600 chunks]  |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                    QUERY PHASE                              |
|               (runs on every question)                      |
|                                                             |
|   Employee question  (plain English)                        |
|         |                                                   |
|         v                                                   |
|   Convert question -> vector       [same embedding model]   |
|         |                                                   |
|         v                                                   |
|   Semantic search — top 6 chunks   [Qdrant HNSW index]      |
|   Results span all 5 policy sources automatically           |
|         |                                                   |
|         v                                                   |
|   Build cited context block                                 |
|   "[NIST SP 800-61r2 [Incident Response] — Page 21]"        |
|         |                                                   |
|         v                                                   |
|   Generate grounded answer         [Groq — llama-3.1-8b]   |
|         |                                                   |
|         v                                                   |
|   Answer + Policy Name + Category + Page Number             |
+-------------------------------------------------------------+
```

---

## 📁 Project Structure

```
PolicyAI/
|
+-- vanilla_rag/                  <- Pure Python -- no frameworks
|   +-- ingestion/
|   |   +-- 01_doc_loader.py      <- fetch PDF, extract pages with PyMuPDF
|   |   +-- 02_chunker.py         <- split pages into 100-word chunks
|   |   +-- 03_embedder.py        <- embed chunks with sentence-transformers
|   |   +-- __init__.py           <- re-exports all functions cleanly
|   +-- config.py                 <- all constants and env vars
|   +-- 01_ingest.py              <- orchestrates the ingestion pipeline
|   +-- 02_query.py               <- retrieve() + build_context() + rag()
|   +-- 03_demo.py                <- runs sample questions end-to-end
|
+-- langchain_rag/                <- Same pipeline via LangChain abstractions
|   +-- config.py                 <- POLICY_SOURCES list + all constants
|   +-- 01_ingest.py              <- multi-source download, stamp metadata, index
|   +-- 02_query.py               <- retriever + ChatGroq + LCEL chain
|   +-- 03_demo.py                <- runs HR + IT Security sample questions
|
+-- chatbot/                      <- Gradio chat UI (Hugging Face Spaces ready)
|   +-- app.py                    <- entry point: path bootstrap + launch()
|   +-- pipeline.py               <- ensure_indexed() for all 5 sources + rag()
|   +-- handlers.py               <- respond() + clear_chat() handlers
|   +-- styles.py                 <- dark-theme CSS
|   +-- ui.py                     <- Gradio layout + event wiring
|
+-- data/                         <- PDFs downloaded here (gitignored)
+-- qdrant_data/                  <- Qdrant vector index (gitignored)
+-- .env                          <- GROQ_API_KEY (never commit this)
+-- .gitignore
+-- requirements.txt
+-- README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **PDF Extraction** | PyMuPDF | Fast, reliable, page-level metadata |
| **Chunking** | RecursiveCharacterTextSplitter | Preserves context, respects token limits |
| **Embeddings** | all-MiniLM-L6-v2 (sentence-transformers) | 384-dim semantic vectors, runs fully offline |
| **Vector Database** | Qdrant | Local file-based, no Docker or server needed |
| **Search Index** | HNSW (Hierarchical Navigable Small World) | Millisecond semantic search across 1,600+ chunks |
| **LLM Inference** | Groq — llama-3.1-8b-instant | Free tier, ultra-fast inference |
| **Framework** | LangChain + LCEL | Industry-standard RAG abstractions |
| **Chat UI** | Gradio | Web interface, one-command HF Spaces deploy |
| **Language** | Python 3.10+ | |

---

## 🤔 Why RAG — Not Just Asking GPT?

| Challenge | GPT Alone | PolicyAI (RAG) |
|---|---|---|
| Your private HR manual | ❌ Has never seen it | ✅ Fully indexed and searchable |
| 200-page NIST PDF | ❌ Context window too small | ✅ Retrieves only the relevant chunks |
| Policy updated last week | ❌ Training cutoff months ago | ✅ Re-index in minutes |
| Cited, verifiable answer | ❌ Confident but unverifiable | ✅ Exact policy name, category, and page |
| Private company data | ❌ Data sent to external servers | ✅ Everything runs locally |
| Multi-domain questions | ❌ No document context at all | ✅ Searches all 5 sources simultaneously |

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

```bash
python chatbot\app.py
```

Then open **http://localhost:7860** in your browser.

On first run, the app automatically downloads all 5 policy PDFs (~8 MB total) and indexes 1,600+ chunks into Qdrant (~2–3 minutes). Every subsequent start skips this step and loads in seconds.

---

### 🐍 Vanilla RAG (CLI)

```bash
# Step 1 — ingest the HR Policy PDF (run once)
python vanilla_rag\01_ingest.py

# Step 2 — ask a question interactively
python vanilla_rag\02_query.py

# Step 3 — run the full demo
python vanilla_rag\03_demo.py
```

### 🦜 LangChain RAG (CLI)

```bash
# Step 1 — download and index all 5 policy sources (run once)
python langchain_rag\01_ingest.py

# Step 2 — ask a question interactively
python langchain_rag\02_query.py

# Step 3 — run the full demo with HR + IT Security questions
python langchain_rag\03_demo.py
```

---

## 🌐 Deploy to Hugging Face Spaces

1. **Push this repo to GitHub**

2. **Create a new Space** at [huggingface.co/new-space](https://huggingface.co/new-space)
   - SDK: **Gradio**
   - Link your GitHub repository

3. **Set your API key** — Space Settings → Variables and Secrets → add `GROQ_API_KEY`

On cold start, the Space automatically downloads all 5 policy PDFs and indexes them (~3 minutes), then serves queries instantly.

---

## 💡 Sample Questions

```
HR Domain
---------------------------------------------
"What are the leave entitlements for employees?"
"What is the maternity leave policy?"
"How does the performance appraisal process work?"
"What are the travel expense reimbursement rules?"
"What are the disciplinary action procedures?"

IT Security Domain
---------------------------------------------
"What are the password and authentication requirements?"
"What does the NIST Cybersecurity Framework say about threat detection?"
"How should a security incident be reported and handled?"
"What are the five core functions of the NIST CSF?"

Remote Work Security
---------------------------------------------
"What security measures are required for remote work?"
"What VPN and device requirements apply to remote employees?"
"How should employees handle sensitive data on personal devices?"

Incident Response
---------------------------------------------
"What are the steps to contain a cybersecurity incident?"
"What evidence should be preserved after a security breach?"
"What is the difference between an incident and an event?"

Security Awareness
---------------------------------------------
"How should employees be trained on IT security?"
"What are the key components of a security awareness program?"
```

---

## 🧠 Key Concepts Demonstrated

**RAG (Retrieval-Augmented Generation)** — instead of asking the LLM from memory, we retrieve the most relevant document chunks first, then ask the LLM to answer using only those chunks. Prevents hallucination and makes every answer verifiable.

**Multi-source retrieval** — a single query searches all 5 policy sources simultaneously. Qdrant's HNSW index returns the top-6 most semantically relevant chunks regardless of which document they came from.

**Metadata-enriched chunks** — every chunk is stamped with `policy_name` and `policy_category` at ingestion time, so citations always show which document and policy domain answered the question.

**Semantic search** — questions are matched by *meaning*, not keywords. *"What do I do if someone hacks us?"* finds the incident response guide even though it doesn't use the word "hack".

**LCEL chain (LangChain)** — LangChain Expression Language declares the entire RAG pipeline with the `|` operator:

```python
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)
```

**Separation of concerns (chatbot/)** — each file has exactly one responsibility: `pipeline.py` owns RAG init, `handlers.py` owns Gradio callbacks, `styles.py` owns CSS, `ui.py` owns layout, `app.py` is the entry point.

---

## 🗺️ Roadmap

```
Phase 1 — Complete
  HR Policy document ingestion and Q&A
  Page-level citations
  Semantic search with Qdrant
  Groq LLM grounded answers
  vanilla_rag  -- pure Python, no frameworks
  langchain_rag -- LangChain + LCEL chain
  chatbot/      -- Gradio UI, Hugging Face Spaces ready

Phase 2 — Complete
  Multi-domain support: HR + IT Security + Incident Response + Remote Work
  5 publicly available policy sources indexed automatically
  Policy category tags on every source citation
  Configurable POLICY_SOURCES list for easy extension

Phase 3 — Next
  Source filtering (HR questions -> search only HR docs)
  Upgrade PDF parsing to Docling (hierarchical chunking)
  Add web page support (HTML policies, not just PDFs)

Phase 4 — Future
  REST API via FastAPI
  Slack bot integration
  Role-based access -- employees only see permitted documents
  Conflict detection -- "Do these two policies contradict each other?"
  Auto-refresh -- re-index when a document is updated
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
- [NIST](https://www.nist.gov) — publicly available cybersecurity frameworks and guidelines
