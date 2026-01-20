# src/ - Backend Source Code

## Overview

This directory contains the core backend implementation for **GRAYSON**, an AI-powered theology and philosophy research assistant. The system uses intelligent book extraction and direct library integration rather than traditional vector database RAG.

## Module Architecture

```
┌─────────────────────────────────────────────────┐
│                   main.py                       │
│        (FastAPI app & endpoints)                │
└─────────────────────────────────────────────────┘
         │                    │                 │
         ▼                    ▼                 ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
│   ingest.py  │   │     llm.py       │   │ pdf_lookup.py│
│ (Sem Scholar)│   │ (Book extraction)│   │ (Free PDFs)  │
└──────────────┘   └──────────────────┘   └──────────────┘
         │                    │                 │
         └────────────────────┴─────────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │   config.py      │
                  │  (Settings mgmt) │
                  └──────────────────┘
```

## Core Modules

### `main.py` - FastAPI Application
**Purpose:** HTTP API server with endpoints for queries and feedback

**Endpoints:**
- `GET /` - Serves the frontend HTML
- `GET /health` - Health check endpoint
- `POST /query` - Process research questions
- `POST /feedback` - User feedback via Discord webhook

**Key Functions:**
- `query()` - Main query processing pipeline (lines 167-263)
  1. Search Semantic Scholar for papers
  2. Generate LLM answer with context
  3. Extract book mentions from answer
  4. Enrich sources with PDFs and library links

### `llm.py` - LLM Client & Book Extraction
**Purpose:** OpenAI integration and intelligent book citation parsing

**Key Functions:**
- `extract_book_mentions(text: str)` - Dual-pattern regex extraction (lines 36-82)
  - Pattern 1: `"Title" by Author`
  - Pattern 2: `Author in "Title"`
  - Returns list of (title, author) tuples
- `generate_library_links(query: str)` - Generate uOttawa OMNI/JSTOR links (lines 15-33)
- `LLMClient.generate()` - Call OpenAI GPT-4o-mini with context (lines 158-227)

**Prompt Engineering:**
- Instructs LLM to reference sources by title
- Requests "Have you considered?" suggestions
- Returns JSON with answer, sources_used array, suggestions

### `ingest.py` - Academic Paper Search
**Purpose:** Semantic Scholar API integration for paper discovery

**Key Functions:**
- `search_semanticscholar(query: str, limit: int)` - Search academic papers (lines 15-43)
  - Uses clean queries (no artificial enhancement)
  - Returns papers with title, abstract, DOI, year
  - Handles API key for higher rate limits

**Configuration:**
- Free tier: 100 requests per 5 minutes
- Optional API key: Higher limits + metadata

### `pdf_lookup.py` - Free PDF Discovery
**Purpose:** Search for open access versions and generate library links

**Key Functions:**
- `lookup_unpaywall(doi: str)` - Query Unpaywall API for free PDFs
- `lookup_semanticscholar_pdf(title: str)` - Search Semantic Scholar for PDFs
- `generate_uottawa_link(doi: str, title: str)` - Create institutional library links
  - DOI-based: Direct resolver link
  - Title-based: OMNI search link
- `enrich_sources_with_pdfs(sources: list)` - Batch enrich all sources

**Link Generation:**
```python
# With DOI: Direct access via resolver
https://uottawa.primo.exlibrisgroup.com/discovery/openurl?doi={doi}

# Without DOI: Title-based OMNI search
https://ocul-uo.primo.exlibrisgroup.com/discovery/search?query={title}
```

### `config.py` - Configuration Management
**Purpose:** Type-safe settings using pydantic-settings

**Settings:**
- `openai_api_key` - Required for LLM (str | None)
- `semantic_scholar_api_key` - Optional for higher limits (str | None)
- `discord_webhook_url` - Optional for feedback (str | None)
- `chroma_persist_directory` - Future vector DB storage (str)
- `embedding_model` - OpenAI embedding model (str)
- `host`, `port` - Server configuration

**Usage:**
```python
from .config import get_settings

settings = get_settings()  # Cached singleton
api_key = settings.openai_api_key
```

### `usage_tracker.py` - Cost Management
**Purpose:** Track OpenAI API usage and enforce monthly spending limits

**Key Functions:**
- `check_usage_limit()` - Verify budget before API calls
- `record_usage(model: str, tokens: int)` - Log token consumption
- Default limit: $5/month
- Resets automatically on first day of month

**Pricing Tracked:**
- `gpt-4o-mini-input`: $0.15 per 1M tokens
- `gpt-4o-mini-output`: $0.60 per 1M tokens
- `text-embedding-3-small`: $0.02 per 1M tokens

### `embeddings.py` - Text Embeddings
**Purpose:** OpenAI embeddings wrapper for future vector DB integration

**Current Status:** Not used in query pipeline (reserved for future enhancements)

### `vectorstore.py` - Vector Database
**Purpose:** ChromaDB wrapper for persistent vector storage

**Current Status:** Not used in query pipeline (reserved for paper caching)

**Future Use Cases:**
- Cache Semantic Scholar papers to reduce API calls
- Enable offline queries
- Improve response time with pre-indexed papers

## Data Models

### Request Models (Pydantic)
```python
class QueryRequest(BaseModel):
    question: str      # User's research question
    top_k: int = 5     # Number of sources to return

class FeedbackRequest(BaseModel):
    message: str       # User feedback text
```

### Response Format
```python
{
    "answer": str,                    # LLM-generated response
    "sources": [                      # Enriched source list
        {
            "title": str,
            "author": str,            # Stored separately
            "doi": str,
            "year": str,
            "uottawa_link": str,      # Always present
            "free_pdf": str | None    # If found
        }
    ],
    "library_links": {
        "omni": str,                  # OCUL Discovery Network
        "jstor": str                  # uOttawa Library
    }
}
```

## Environment Configuration

Create `.env` file in project root:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (improves functionality)
SEMANTIC_SCHOLAR_API_KEY=...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Server settings
HOST=0.0.0.0
PORT=8000
```

## Running the Backend

### Development Server
```bash
# From project root
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Make
```bash
make run   # Runs with auto-reload
```

## Code Quality

### Type Checking
```bash
mypy src/
```

### Linting
```bash
ruff check src/
```

### Formatting
```bash
black src/
isort src/
```

## Key Implementation Details

### Book Extraction Regex

**Challenge:** LLMs mention books in various formats

**Solution:** Dual-pattern matching
```python
# Handles: "The Historical Jesus" by John Dominic Crossan
pattern1 = r'["\']([^"\']+)["\']\s+by\s+([A-Z][^.,;\n)]+?)(?:[.,;\n)]|$)'

# Handles: N.T. Wright in "Jesus and the Victory of God"
# Length limit prevents false matches like "Exploring the differences..."
pattern2 = r'([A-Z][A-Za-z\.\s]{2,50}?)\s+in\s+["\']([^"\']+)["\']'
```

### Title-Only Library Searches

**Why?** Searching for "Title by Author" returns poor results in library systems.

**Implementation:**
1. Store title and author separately in source object
2. Generate uOttawa link with **title only**
3. Frontend displays `Title by Author` for clarity
4. Result: Significantly improved library search accuracy

### Graceful API Degradation

**Semantic Scholar Rate Limiting:**
```python
try:
    sem_results = search_semanticscholar(query, limit=top_k)
except Exception as e:
    logger.info(f"Semantic Scholar failed: {e}")
    # Continue without paper context - LLM still provides books
```

**Benefits:**
- System never fails completely
- Book extraction works regardless of API status
- uOttawa links always generated

## Performance Considerations

- **Response Time:** 2-5 seconds per query
- **Bottlenecks:** OpenAI API latency (1-2s), Semantic Scholar search (1-2s)
- **Optimization Opportunities:**
  - Enable ChromaDB caching to reduce API calls
  - Parallel PDF lookups (currently sequential)
  - Response streaming for immediate feedback

## Security Notes

- ✅ API keys via environment variables only
- ✅ No user authentication (stateless)
- ✅ Usage limits prevent runaway costs
- ✅ CORS configured for frontend access
- ⚠️ No rate limiting on endpoints (consider adding)

## Future Enhancements

1. **Vector DB Integration**
   - Cache Semantic Scholar papers in ChromaDB
   - Enable offline/cached queries
   - Reduce API dependencies

2. **Advanced Source Discovery**
   - JSTOR direct API integration
   - ATLA Religion Database access
   - Google Scholar fallback

3. **Export Features**
   - BibTeX citation export
   - RIS format support
   - EndNote integration

## Related Documentation

- [../README.md](../README.md) - Main project documentation
- [../docs/overview.md](../docs/overview.md) - Technical architecture
- [../CHANGELOG.md](../CHANGELOG.md) - Version history
