# 🚀 Semantic Search & RAG System

A powerful document intelligence platform that combines **Semantic Search**, **Vector Databases**, and **Retrieval-Augmented Generation (RAG)** to enable intelligent querying of PDFs, DOCX files, and web content.

Built using:

- Python
- ChromaDB
- LangChain
- Google Gemini
- Ollama
- Poetry

---

## ✨ Features

### 📥 Multi-Source Content Ingestion

Ingest knowledge from:

- PDF documents
- DOCX documents
- Websites (URLs)

The system automatically:

1. Loads the content
2. Cleans and normalizes text
3. Chunks documents
4. Generates embeddings
5. Stores vectors in ChromaDB

---

### 🧩 Advanced Chunking Engine

Choose one or multiple chunking strategies during ingestion.

Available strategies:

- Recursive Chunking ✅
- Character Chunking
- Structural Chunking
- Semantic Chunking 🔥
- Fixed-Length Chunking
- Overlapping Chunking

This allows experimentation and optimization of retrieval quality.

---

### 🔍 Semantic Search

Perform vector-based search instead of traditional keyword matching.

Search capabilities include:

- Natural language queries
- Metadata filtering
- Collection-specific search
- Source-specific filtering
- Chunking strategy filtering

---

### 🤖 AI-Powered RAG

Ask questions against your documents using Google Gemini or Ollama.

Workflow:

```text
User Question
      ↓
Vector Retrieval
      ↓
Relevant Chunks
      ↓
Context Construction
      ↓
Gemini / Ollama
      ↓
Grounded Answer + Citations
```

---

### 📚 Collection Management

Manage document collections directly from the terminal UI.

Features:

- Create collections
- Merge documents into existing collections
- View collections
- List collection contents
- Delete collections

---

### 🔒 Duplicate Detection

Every source is fingerprinted using SHA256 hashing.

When a duplicate document is detected:

```text
1. Skip
2. Re-embed
3. Replace Existing Content
```

This prevents unnecessary storage usage and duplicate embeddings.

---

### 🧹 Automatic ChromaDB Cleanup

Built-in maintenance utilities:

- Detect orphan storage folders
- Detect orphan database segments
- Delete stale entries
- Deep cleanup mode
- Storage reports

---

## 🏗️ Architecture

```text
PDF / DOCX / URL
        │
        ▼
Document Loader
        │
        ▼
Text Cleaning
        │
        ▼
Chunking Engine
        │
        ▼
Embedding Model
(Gemini / Ollama)
        │
        ▼
ChromaDB
        │
 ┌──────┴──────┐
 ▼             ▼
Search       RAG
```

---

## 📂 Project Structure

```text
src/
│
├── cleanup/
│   ├── cleanup.py
│   └── cleanup_runner.py
│
├── collections/
│   └── collection_ui.py
│
├── ingestion/
│   └── ingest.py
│
├── loaders/
│   └── document_loader.py
│
├── pipeline/
│   ├── chunking_ui.py
│   └── query.py
│
├── preprocessing/
│   ├── cleaning.py
│   ├── chunking.py
│   └── file_utils.py
│
├── rag/
│   ├── generator.py
│   ├── prompts.py
│   └── query_engine.py
│
├── retrieval/
│   └── retrieval.py
│
├── ui/
│   └── main.py
│
├── config.py
├── db.py
└── embedding.py
```

---

# ⚙️ Prerequisites

- Python 3.11+
- Poetry
- Google Gemini API Key (optional)
- Ollama (optional)

---

# 📦 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/semantic-search-rag.git

cd semantic-search-rag
```

---

## Install Dependencies Using Poetry

```bash
poetry install
```

---

## Activate Environment

```bash
poetry shell
```

Or run commands directly:

```bash
poetry run python -m src.ui.main
```

---

# 🔑 Environment Variables

Create a `.env` file from `.env.example`.

```bash
cp .env.example .env
```

Update the configuration values as needed.

## Example

```env
# AI Provider
PROVIDER=google

# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

# Embeddings
GOOGLE_EMBEDDING_MODEL=gemini-embedding-001

# Answer Generation
GOOGLE_CHAT_MODEL=gemini-3.1-flash-lite

# Ollama Configuration
OLLAMA_MODEL=phi-3.5-mini_q4_k_m
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_API_KEY=ollama

# Vector Database
CHROMA_PATH=.storage/chroma_db

# Chunking Settings
CHUNK_SIZE=800
CHUNK_OVERLAP=100
BATCH_SIZE=30

# Retrieval Settings
TOP_K=5
MAX_CONTEXT_CHARS=12000

# Generation Settings
TEMPERATURE=0.1

# Application Settings
USER_AGENT=SemanticSearchSystem/1.0
```

---

# 🤖 AI Provider Configuration

## Google Gemini

Configure:

```env
PROVIDER=google
GOOGLE_API_KEY=YOUR_API_KEY
```

Used for:

- Embeddings
- Retrieval-Augmented Generation
- Semantic Understanding

---

## Ollama

For fully local execution:

```env
PROVIDER=ollama
```

Start Ollama:

```bash
ollama serve
```

Download model:

```bash
ollama pull phi3.5
```

---

# ▶️ Running the Application

Start the interactive console application:

```bash
poetry run python -m src.ui.main
```

---

# Main Menu

```text
📦 SEMANTIC SEARCH SYSTEM

1. Ingest Content
2. View Collections & Files
3. Storage & Cleanup
4. Query Existing Collection
5. Query Collection With AI
6. Exit
```

---

# 📥 Data Ingestion

Supported sources:

### PDF

```text
CompanyHandbook.pdf
```

### DOCX

```text
HR_Policy.docx
```

### Websites

```text
https://example.com
```

---

# 🔍 Semantic Search

Search documents using natural language.

Example queries:

```text
What are the employee responsibilities?
```

```text
How does the approval workflow work?
```

Available filters:

- Source Name
- Source Type
- Chunking Strategy

---

# 🤖 RAG Question Answering

Example:

```text
Question:
What is the leave approval process?

Answer:
The leave approval process requires employees
to submit requests through the HR portal...

Citations:
• Employee Handbook (page 5)
• HR Policy (page 12)
```

Responses are generated using retrieved document context only.
--------------------------------------------------------------

## 📸 Example Workflow

The following example demonstrates an end-to-end workflow using the **Bhagavad Gita PDF**, including document ingestion, vector storage, semantic search, and AI-powered question answering.

### Step 1 — Start the Application

```bash
poetry run python -B -m src.ui.main
```

### Step 2 — Ingest a Document

Select a PDF from the resources folder and create a new collection.

```text
📥 INGEST CONTENT

Select option: 1

📚 Available Files

1. NIPS-2017-attention-is-all-you-need-Paper.pdf
2. bhagavad-gita-in-english-source-file-copy.pdf

Select file: 2

🆕 New source detected

Choose storage option:

1. Merge into existing collection
2. Create new collection

❌ No collections exist

Enter collection name: BhagavadGita
```

### Step 3 — Select Chunking Strategy

Choose how documents should be split before embedding.

```text
🧩 Choose Chunking Strategies

1. Recursive ✅
2. Character
3. Structural
4. Semantic 🔥
5. Fixed
6. Overlap

Enter choices: 3

✅ Selected strategies: ['structural']
```

### Step 4 — Process & Store Content

The document is loaded, chunked, embedded, and stored inside ChromaDB.

```text
⚡ Processing using 1 strategy(s)

⚙️ Applying structural

📥 Loaded 53 document(s)

🧩 Chunking strategy: structural

✅ Generated 119 chunks

📦 Batch 0 → 30
📦 Batch 30 → 60
📦 Batch 60 → 90
📦 Batch 90 → 119

✅ Content stored successfully

📄 Source : bhagavad-gita-in-english-source-file-copy
📦 Type   : pdf
🧩 Chunks : 119
```

### Step 5 — View Collections

```text
📚 Collections:

1. BhagavadGita

📄 Files inside collection:

 - bhagavad-gita-in-english-source-file-copy
```

### Step 6 — Perform Semantic Search

Query the collection using natural language.

**Query**

```text
What does Arjuna ask Krishna about sin and human actions?
```

**Retrieved Results**

```text
🌍 SEARCH RESULTS

📄 Source   : bhagavad-gita-in-english-source-file-copy
📦 Type     : pdf
📑 Page     : 13
📚 Section  : 3.26
🧩 Chunking : structural

📖 Content:

All work is done by the energy and power of nature,
but due to ignorance people assume themselves to be the doer
and thus incur karmic bondage.
```

### Step 7 — Ask Questions Using RAG

Ask questions directly against the ingested knowledge base.

**Question**

```text
What did the Supreme Lord say when Arjuna asked:

"O Krishna, what impels one to commit sin as if unwillingly and forced against one's will?"
```

**AI Generated Answer**

```text
💡 ANSWER

The Supreme Lord explained that lust (desire), born from passion,
is what drives a person to commit sinful actions. When desire is
unfulfilled it transforms into anger. Krishna describes this desire
as an insatiable enemy that clouds wisdom and compels individuals
to act against their better judgment.
```

**Citations**

```text
📚 CITATIONS

• bhagavad-gita-in-english-source-file-copy (page 13)
• bhagavad-gita-in-english-source-file-copy (page 49)
• bhagavad-gita-in-english-source-file-copy (page 28)
• bhagavad-gita-in-english-source-file-copy (page 21)
• bhagavad-gita-in-english-source-file-copy (page 42)
```

### Workflow Summary

```text
PDF / DOCX / URL
        │
        ▼
Document Loader
        │
        ▼
Text Cleaning
        │
        ▼
Chunking Strategy
        │
        ▼
Embedding Generation
(Gemini / Ollama)
        │
        ▼
ChromaDB Storage
        │
 ┌──────┴──────┐
 ▼             ▼
Semantic     RAG
 Search      Q&A
              │
              ▼
     Answer + Citations
```

---

# 🧩 Supported Chunking Strategies

| Strategy   | Description               |
| ---------- | ------------------------- |
| Recursive  | General-purpose chunking  |
| Character  | Character-based splitting |
| Structural | Splits by sections        |
| Semantic   | Embedding-aware chunking  |
| Fixed      | Fixed-size chunks         |
| Overlap    | Fixed chunks with overlap |

---

# 🧹 Storage Maintenance

## Storage Report

Provides:

- Collection count
- Active segments
- UUID storage folders
- Orphan directories
- SQLite database size
- Total storage consumption

---

## Deep Cleanup

Performs:

```text
Remove Orphan DB Entries
        ↓
Delete Orphan UUID Folders
        ↓
Generate Storage Report
```

---

# 🔒 Duplicate Protection

The ingestion pipeline computes SHA256 hashes for:

- Documents
- Web content

If a duplicate is found:

```text
1. Skip
2. Re-embed
3. Replace
```

---

# 📁 Storage Layout

```text
storage/
└── chroma_db/
    ├── chroma.sqlite3
    └── UUID segment folders
```

---

# 🛠️ Tech Stack

### Core

- Python
- Poetry

### Vector Database

- ChromaDB

### AI & LLMs

- Google Gemini
- Ollama

### Frameworks

- LangChain

### ML Libraries

- NumPy
- Scikit-Learn

### Storage

- SQLite

### Configuration

- python-dotenv

---

# ✅ Supported Content Types

| Content Type | Supported |
| ------------ | --------- |
| PDF          | ✅        |
| DOCX         | ✅        |
| Web Pages    | ✅        |

---

# 🎯 Use Cases

- Enterprise Knowledge Bases
- Internal Document Search
- AI Document Assistants
- Research Repositories
- Compliance Documentation
- Company Policy Search
- Technical Documentation Search
- RAG Experiments

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

## Yash Dhanraj Mahajan

**GenAI Developer**

Passionate about Generative AI, Retrieval-Augmented Generation (RAG), LLM applications, Semantic Search, and building intelligent knowledge systems using modern AI technologies.

### Connect

📧 Email: yashmahajan18521@gmail.com

🐙 GitHub: https://github.com/yashmahajan4

---

# 🤝 Contributing

Contributions, feature requests, and improvements are welcome.

If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push your branch
5. Open a Pull Request

---

# ⭐ Support

If you find this project useful, consider giving it a star on GitHub.

Feedback, bug reports, and suggestions are always appreciated.

---

