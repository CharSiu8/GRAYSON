# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-19

### Major Changes
This release represents a significant architectural shift from vector database RAG to intelligent book extraction with direct library integration.

### Added
- **Intelligent Book Extraction**: Dual-pattern regex system extracts scholarly books from LLM responses
  - Pattern 1: `"Title" by Author` format
  - Pattern 2: `Author in "Title"` format
  - Handles both single and double quotes
  - Length limits prevent false matches
- **uOttawa OMNI Integration**: Every source now includes direct library search links
  - Title-based search for better accuracy
  - Separate display of author name in frontend
  - Always available, no API dependency
- **Simplified Source Generation**: Books extracted from LLM answers become sources directly
  - No API search required for book sources
  - Eliminates rate limiting issues
  - Faster response times
- **Professional Documentation**: Complete README rewrite with accurate architecture
  - Added badges (Python, FastAPI, License)
  - Updated architecture diagram
  - Removed outdated OpenAlex references
  - Added Key Features section explaining book extraction

### Changed
- **Removed OpenAlex API**: System now uses only Semantic Scholar for paper discovery
  - Eliminated source irrelevance issues
  - Simplified codebase
  - Reduced API dependencies
- **LLM Model Update**: Now using GPT-4o-mini (updated from GPT-3.5-turbo)
- **Source Priority**: Semantic Scholar results prioritized over fallback options
- **Source Display**: Title and author stored separately for better library searches
- **Frontend**: Author name now displayed alongside title

### Fixed
- **Book Extraction Accuracy**:
  - Fixed regex capturing long phrases as author names
  - Added character limits (2-50) for author field
  - Strip trailing parentheses and punctuation
- **uOttawa Link Specificity**:
  - Links now search by title only (not "Title by Author")
  - Significantly improved library search results
- **Embedded Sources**: Removed duplicate sources appearing in answer text
- **Query Enhancement**: Removed "theology philosophy religion" pollution from Semantic Scholar queries

### Removed
- **OpenAlex Integration**: All OpenAlex functions commented out or removed
  - Eliminated `search_openalex()` function
  - Removed `ingest_openalex_query()` function
  - Removed `THEOLOGY_CONCEPTS` filter constants
  - Disabled `/ingest` endpoint (was OpenAlex-based)
- **Vector Database Queries**: ChromaDB no longer used for source retrieval
  - Kept code for future enhancements
  - Simplified to direct LLM-to-source pipeline

## [1.5] - 2026-01-08

### Added
- Dark mode support for frontend
- Usage tracking with monthly spending limits ($5/month default)
- Discord webhook integration for user feedback
- Free PDF discovery via Unpaywall and Semantic Scholar APIs
- uOttawa library search links (OMNI and JSTOR)

### Changed
- Page background now updates with dark mode toggle
- Improved frontend styling and responsiveness

### Fixed
- Dark mode now properly changes page background color

## [1.0] - 2026-01-07

### Added
- Initial project setup with FastAPI backend
- ChromaDB vector database integration
- OpenAI embeddings (text-embedding-3-small)
- Semantic Scholar API integration
- Basic web chat interface
- OpenAlex API integration for theology/philosophy papers
- Environment variable configuration
- MIT License
- Contributing guidelines
- GitHub issue and PR templates

### Project Structure
- `src/` - Backend source code
- `frontend/` - Web interface
- `tests/` - Test suite
- `docs/` - Documentation
- `.github/` - GitHub templates

## Upgrade Notes

### Upgrading from 1.x to 2.0

**Breaking Changes:**
1. `/ingest` endpoint has been disabled (OpenAlex removed)
2. ChromaDB no longer used for query operations
3. Source format changed to include `author` field separately

**Migration Steps:**
1. Update to latest code: `git pull origin main`
2. No database migration needed (vector DB not queried)
3. Update any scripts calling `/ingest` endpoint (now disabled)
4. Test queries to verify book extraction working

**Configuration Changes:**
- No new environment variables required
- `SEMANTIC_SCHOLAR_API_KEY` remains optional
- Consider getting Semantic Scholar API key for better rate limits

## Notes

### Rate Limiting
Semantic Scholar free tier: 100 requests per 5 minutes. When rate limited:
- System falls back to LLM's own knowledge
- Book extraction still works
- uOttawa links still generated
- Only academic paper search affected

### Future Enhancements
- Vector database re-integration for paper caching
- Additional library integrations (JSTOR direct, ATLA)
- Citation export formats
- Advanced filtering options

---

For detailed commit history, see: https://github.com/CharSiu8/GRAYSON/commits/main
