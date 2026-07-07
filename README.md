# Insurance RAG Assistant

An AI-powered insurance question-answering system built using Retrieval-Augmented Generation (RAG). The system retrieves relevant insurance policy information from documents and generates accurate responses using semantic search and LLM-based retrieval.

---

## Features

* Insurance policy Q&A
* Semantic document retrieval
* Hybrid Search (BM25 + Vector Search)
* FastAPI REST API
* Swagger API documentation
* ChromaDB vector database
* Hugging Face embeddings

---

## Tech Stack

* Python
* FastAPI
* LangChain
* ChromaDB
* Hugging Face
* BM25Okapi

---

## System Architecture

User Query → Embedding Model → Vector Search + BM25 Retrieval → Relevant Chunks → LLM Response

---

## Installation

```bash
git clone https://github.com/your-username/insurance-rag-assistant.git

cd insurance-rag-assistant

pip install -r requirements.txt

uvicorn app:app --reload
```

---

## API Endpoint

```bash
GET /ask?query=What is claim settlement?
```

---

## Example Query

```bash
What is covered under accidental insurance?
```

---

## Future Improvements

* Multi-document support
* PDF upload feature
* Conversational memory
* Multilingual support
