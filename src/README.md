# src/ - Backend Source Code

<!--
================================================================================
WHAT THIS FILE IS:
README for the src/ directory explaining the backend source code structure.

WHY YOU NEED IT:
- Helps developers understand the codebase organization
- Documents the purpose of each module
- Makes onboarding new contributors easier
- Shows thoughtful project organization to employers
================================================================================
-->

## Overview

This directory contains the core backend code for GRAYSON, a RAG (Retrieval-Augmented Generation) chatbot for theology and philosophy research.

## Module Structure

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point with API endpoints |
| `config.py` | Configuration management using pydantic-settings |
| `ingest.py` | Paper ingestion from OpenAlex and Semantic Scholar APIs |
| `embeddings.py` | Sentence-transformers embedding wrapper |
| `vectorstore.py` | ChromaDB vector database operations |
| `llm.py` | LLM client for generating responses (OpenAI API) |
| `demo_simple.py` | Minimal demo script for quick testing |

## Architecture

```
User Query → main.py → vectorstore.py (semantic search)
                    → llm.py (generate response)
                    → Return answer + sources

Ingestion  → ingest.py → embeddings.py → vectorstore.py
```

## Key Components

### `main.py` - API Server
The FastAPI application exposes three endpoints:
- `GET /health` - Health check
- `POST /ingest` - Ingest papers from OpenAlex API
- `POST /query` - Query the knowledge base with semantic search

### `config.py` - Configuration
Centralized configuration using Pydantic Settings:
- API keys (OpenAI, Semantic Scholar)
- Vector database settings
- Embedding model configuration
- Server host/port settings

### `ingest.py` - Data Ingestion
Fetches academic papers from OpenAlex API filtered to theology/philosophy concepts:
- Philosophy (C138885662)
- Theology (C124101348)
- Religious Studies (C177028987)
- Religion (C136116916)
- Biblical Studies (C67961920)

### `vectorstore.py` - Vector Database
ChromaDB wrapper for storing and querying embeddings:
- Persistent storage in `chroma_db/`
- Semantic similarity search
- Metadata filtering

### `embeddings.py` - Text Embeddings
Sentence-transformers wrapper using `all-MiniLM-L6-v2` model for converting text to vector embeddings.

### `llm.py` - Language Model
OpenAI API client for generating research responses with:
- Context from retrieved documents
- Source citations
- "Have you considered?" suggestions
- Library links (OMNI, JSTOR)

## Running the Backend

```bash
# From project root
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Required configuration (set in `.env`):
- `OPENAI_API_KEY` - For LLM responses (optional, falls back to placeholder)
- `CHROMA_DB_PATH` - Vector database location (default: `./chroma_db`)
