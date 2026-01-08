# ================================================================================
# WHAT THIS FILE IS:
# Ingestion utilities for fetching academic papers from OpenAlex and Semantic Scholar.
#
# WHY YOU NEED IT:
# - Provides the data pipeline for populating the vector database
# - Filters results to theology, philosophy, and biblical studies
# - Handles API communication with academic data sources
# - Normalizes paper metadata for consistent storage
# ================================================================================

"""Ingestion utilities for theology, philosophy, and biblical studies.

This module focuses exclusively on academic sources in theology, philosophy, and religion.
"""
import os
import requests
from typing import List, Dict
from urllib.parse import urlencode, quote

from .config import get_settings

SETTINGS = get_settings()

# OpenAlex concept IDs for filtering
THEOLOGY_CONCEPTS = [
    "C138885662",    # Philosophy
    "C2778407487",   # Theology
    "C175444787",    # Religious studies
    "C41008148",     # Religion
    "C2522767166",   # Biblical studies
]


def _inverted_index_to_text(inverted_index: dict) -> str:
    """Convert OpenAlex inverted index abstract format to plain text."""
    if not inverted_index or not isinstance(inverted_index, dict):
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(word for _, word in word_positions)


def search_openalex(query: str, per_page: int = 10) -> List[Dict]:
    """Search OpenAlex for theology/philosophy/religion papers.

    Results are automatically filtered to relevant academic disciplines.
    """
    base = "https://api.openalex.org/works"

    # Build concept filter for theology/philosophy/religion
    concept_filter = "|".join(f"https://openalex.org/{c}" for c in THEOLOGY_CONCEPTS)

    params = {
        "search": query,
        "per-page": per_page,
        "filter": f"concepts.id:{concept_filter}",
    }
    url = f"{base}?{urlencode(params, safe=':|')}"

    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()

    results = []
    for item in data.get("results", []):
        # Handle OpenAlex inverted index abstract format
        abstract = ""
        if item.get("abstract_inverted_index"):
            abstract = _inverted_index_to_text(item.get("abstract_inverted_index"))
        elif item.get("abstract"):
            abstract = item.get("abstract")

        results.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "doi": item.get("doi"),
            "abstract": abstract,
            "year": item.get("publication_year"),
        })
    return results


def search_semanticscholar(query: str, limit: int = 10) -> List[Dict]:
    """Search Semantic Scholar for theology/philosophy papers."""
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY") or SETTINGS.semantic_scholar_api_key
    headers = {"Accept": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    # Append theology context to improve relevance
    enhanced_query = f"{query} theology philosophy religion"

    params = {
        "query": enhanced_query,
        "limit": limit,
        "fields": "title,abstract,year,doi,url,externalIds"
    }
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()

    results = []
    for el in data.get("data", []):
        results.append({
            "id": el.get("paperId"),
            "title": el.get("title"),
            "abstract": el.get("abstract"),
            "year": el.get("year"),
            "doi": (el.get("externalIds") or {}).get("DOI"),
            "url": el.get("url"),
        })
    return results


def ingest_openalex_query(query: str, max_results: int = 10) -> List[Dict]:
    """Ingest theology/philosophy papers from OpenAlex.

    Returns list of records with `id`, `title`, `text`, `metadata`.
    """
    results = search_openalex(query, per_page=max_results)
    records = []

    for r in results:
        text = r.get("abstract") or ""
        metadata = {
            "title": r.get("title") or "",
            "doi": r.get("doi") or "",
            "year": r.get("year") or 0,
            "url": r.get("doi") or r.get("id") or "",
        }
        records.append({
            "id": r.get("id"),
            "title": r.get("title"),
            "text": text,
            "metadata": metadata
        })
    return records
