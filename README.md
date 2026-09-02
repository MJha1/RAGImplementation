# Sage — AI Knowledge Assistant

Sage is a Retrieval-Augmented Generation (RAG) app that answers questions using
**only** the content of your documents — grounded, with sources cited, no
hallucinations. It pairs local semantic search with a fast Groq LLM, wrapped in
a clean Streamlit web UI.

## How it works

A RAG needs two things: a way to **search** your documents, and a way to
**write** an answer from what it finds.

1. **Retrieve** — Semantic search finds the most relevant passages in your
   documents. Embeddings run **locally** via ChromaDB's built-in model
   (`all-MiniLM-L6-v2`) — no API key, no cost. (Groq doesn't offer an embeddings
   API, so this part stays local.)
2. **Augment** — Those passages are passed to the model as grounded context.
3. **Generate** — Groq's LLM (default: `openai/gpt-oss-120b`) writes an answer
   using only that context, and cites its sources.

## Setup

### 1. Install dependencies

The virtual environment is already set up. To recreate it:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your Groq API key

Get a **free** key from the [Groq Console](https://console.groq.com/keys), then
put it in the `.env` file:

```
GROQ_API_KEY=gsk-your-actual-api-key-here
```

The app loads it automatically via `python-dotenv` — no manual environment
variables needed.

### 3. Add your documents

Drop `.txt` files into the `docs/` folder. The repo ships with a sample set for
a fictional SaaS product (Northwind Analytics):

- `product-overview.txt` — features and pricing plans
- `onboarding-faq.txt` — getting started
- `security-policy.txt` — data security and compliance

Replace these with your own documents any time, then rebuild the index (delete
the `chroma/` folder, or just restart the app).

### 4. Run it

**Web UI (recommended):**

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

Opens a chat interface at http://localhost:8501.

**Terminal:**

```powershell
.\venv\Scripts\python.exe rag.py
```

> The first run downloads the small local embedding model (~90 MB). It's cached
> after that.

## Usage

Ask a question and Sage answers from your documents, listing the sources it
used:

```
You: How is my data secured?
Sage: Your data is encrypted in transit (TLS 1.2+) and at rest (AES-256)…
      📄 Sources: security-policy.txt
```

## Project structure

```
my-first-rag/
├── app.py                 # Streamlit web UI
├── rag.py                 # Core RAG logic (indexing, retrieval, answering)
├── test_rag.py            # Test script
├── docs/                  # Your documents (indexed for search)
│   ├── product-overview.txt
│   ├── onboarding-faq.txt
│   └── security-policy.txt
├── docs_archive/          # Earlier sample docs (not indexed)
├── chroma/                # Vector store (auto-created)
├── .streamlit/config.toml # UI theme
├── venv/                  # Virtual environment
├── .env                   # GROQ_API_KEY
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## Tech stack

- **Groq** — LLM inference for answer generation
- **ChromaDB** — vector store + local embeddings (`all-MiniLM-L6-v2`)
- **Streamlit** — web UI
- **python-dotenv** — configuration
- Python 3.13

## Configuration

**Change the model:** edit `CHAT_MODEL` near the top of `rag.py`. Run
`client.models.list()` or see the [Groq models list](https://console.groq.com/docs/models)
for the models your key can access (e.g. `openai/gpt-oss-20b` for faster
responses).

**Change the theme:** edit `.streamlit/config.toml`.

## Troubleshooting

**Missing / invalid API key** — make sure `GROQ_API_KEY` is set in `.env` and
valid. Get a free one at https://console.groq.com/keys.

**Model not found (404)** — your key may not have access to the configured
model. List available models with `client.models.list()` and update
`CHAT_MODEL` in `rag.py`.

**Module import errors** — recreate the virtual environment:

```powershell
Remove-Item -Recurse -Force .\venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
