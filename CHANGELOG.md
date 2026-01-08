# Changelog

<!--
================================================================================
WHAT THIS FILE IS:
A chronological log of notable changes made to your project.

WHY YOU NEED IT:
- Documents the evolution of your project
- Helps users understand what's new in each version
- Shows employers you maintain projects professionally
- Can be auto-generated from conventional commits

WHAT TO PUT IN IT:
Follow the Keep a Changelog format (https://keepachangelog.com/).
Update this file with each release or significant change.
================================================================================
-->

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- `docs/overview.md` detailing architecture, goals, and data flow.
- `src/ingest.py`: OpenAlex and Semantic Scholar ingestion helpers and PDF fetching.
- `src/embeddings.py`: sentence-transformers embedding helper.
- `src/vectorstore.py`: Chroma-backed vectorstore wrapper (add/query).
- `src/llm.py`: LLM wrapper with OpenAI API mode and local placeholder.
- `src/demo_simple.py`: minimal OpenAlex demo script for quick testing.
- `scripts/setup-windows-buildchain.ps1`: one-click installer helper for Windows build tools and Rust (requires admin).

### Changed
- Populated `README.md` sections after `## Features` with setup, usage, and tech-stack guidance.
- Updated `docs/overview.md` to include Semantic Scholar and ingestion notes.
- Added `SEMANTIC_SCHOLAR_API_KEY` to `.env.example`.
- Updated `pyproject.toml` description to mention Semantic Scholar integration.
- Adjusted `requirements.txt` pins for compatibility and added runtime dependencies.
- Implemented `src/main.py` as a FastAPI app with `/ingest` and `/query` endpoints.
- Finalized `LICENSE` to MIT under the copyright holder "Steven Polino".

### Fixed
- Resolved packaging and dependency issues in `requirements.txt` (httpx, fastapi/pydantic compatibility)

### Notes
- The project currently uses a pre-ingest workflow (index data before querying). For a quick demo, run `src/demo_simple.py` which requires only `requests`.
- Windows users may need to install build tools and Rust to compile some packages; `scripts/setup-windows-buildchain.ps1` can assist.

## [0.1.0] - YYYY-MM-DD

### Added
- Initial project setup
- Basic project structure
- CI/CD pipeline configuration
- Documentation templates

<!--
================================================================================
EXAMPLE ENTRIES (delete when you add real entries):

## [1.2.0] - 2024-03-15

### Added
- PDF document ingestion with automatic text extraction
- Semantic search across uploaded documents
- Export research findings to Markdown

### Changed
- Improved chunking strategy for better retrieval accuracy
- Updated to LangChain 0.1.5

### Fixed
- Memory leak when processing large documents
- Incorrect citation numbering in summaries

================================================================================
-->
