"""PDF lookup service using Unpaywall and Semantic Scholar APIs."""

import logging
from typing import Optional
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)

# Email for Unpaywall API (required, but they don't validate)
UNPAYWALL_EMAIL = "grayson@research.app"


async def lookup_pdf_by_doi(doi: str) -> Optional[str]:
    """
    Look up a free PDF URL using DOI.
    Tries Unpaywall first, then Semantic Scholar.

    Args:
        doi: The DOI of the paper (e.g., "10.1234/example")

    Returns:
        PDF URL if found, None otherwise
    """
    if not doi:
        return None

    # Clean DOI (remove URL prefix if present)
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")

    # Try Unpaywall first
    pdf_url = await _try_unpaywall(doi)
    if pdf_url:
        return pdf_url

    # Fall back to Semantic Scholar
    pdf_url = await _try_semantic_scholar(doi)
    if pdf_url:
        return pdf_url

    return None


async def lookup_pdf_by_title(title: str) -> Optional[str]:
    """
    Look up a free PDF URL using paper title.
    Uses Semantic Scholar search.

    Args:
        title: The title of the paper

    Returns:
        PDF URL if found, None otherwise
    """
    if not title:
        return None

    return await _try_semantic_scholar_search(title)


async def _try_unpaywall(doi: str) -> Optional[str]:
    """Query Unpaywall API for open access PDF."""
    try:
        url = f"https://api.unpaywall.org/v2/{quote(doi, safe='')}?email={UNPAYWALL_EMAIL}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                # Check for best open access location
                best_oa = data.get("best_oa_location")
                if best_oa and best_oa.get("url_for_pdf"):
                    logger.info(f"Unpaywall: Found PDF for DOI {doi}")
                    return best_oa["url_for_pdf"]
                # Try other OA locations
                for location in data.get("oa_locations", []):
                    if location.get("url_for_pdf"):
                        logger.info(f"Unpaywall: Found PDF for DOI {doi}")
                        return location["url_for_pdf"]
    except Exception as e:
        logger.debug(f"Unpaywall lookup failed for {doi}: {e}")
    return None


async def _try_semantic_scholar(doi: str) -> Optional[str]:
    """Query Semantic Scholar API for open access PDF using DOI."""
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{quote(doi, safe='')}?fields=openAccessPdf"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                oa_pdf = data.get("openAccessPdf")
                if oa_pdf and oa_pdf.get("url"):
                    logger.info(f"Semantic Scholar: Found PDF for DOI {doi}")
                    return oa_pdf["url"]
    except Exception as e:
        logger.debug(f"Semantic Scholar lookup failed for {doi}: {e}")
    return None


async def _try_semantic_scholar_search(title: str) -> Optional[str]:
    """Search Semantic Scholar by title for open access PDF."""
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={quote(title)}&fields=openAccessPdf&limit=1"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                papers = data.get("data", [])
                if papers:
                    oa_pdf = papers[0].get("openAccessPdf")
                    if oa_pdf and oa_pdf.get("url"):
                        logger.info(f"Semantic Scholar: Found PDF for title '{title[:50]}...'")
                        return oa_pdf["url"]
    except Exception as e:
        logger.debug(f"Semantic Scholar search failed for '{title}': {e}")
    return None


async def enrich_sources_with_pdfs(sources: list) -> list:
    """
    Add free PDF links to a list of sources.

    Args:
        sources: List of source metadata dicts with 'doi' and/or 'title' keys

    Returns:
        Same list with 'free_pdf' key added where available
    """
    enriched = []
    for source in sources:
        if source is None:
            enriched.append(source)
            continue

        source_copy = dict(source) if source else {}

        # Try DOI first
        doi = source_copy.get("doi") or source_copy.get("url", "")
        if "doi.org" in str(doi) or (isinstance(doi, str) and doi.startswith("10.")):
            pdf_url = await lookup_pdf_by_doi(doi)
            if pdf_url:
                source_copy["free_pdf"] = pdf_url
                enriched.append(source_copy)
                continue

        # Fall back to title search
        title = source_copy.get("title")
        if title:
            pdf_url = await lookup_pdf_by_title(title)
            if pdf_url:
                source_copy["free_pdf"] = pdf_url

        enriched.append(source_copy)

    return enriched
