"""Ingestion utilities for theology, philosophy, and biblical studies.

This module focuses exclusively on academic sources in theology, philosophy, and religion.
"""
import os
import requests
from typing import List, Dict

from .config import get_settings

SETTINGS = get_settings()


def search_semanticscholar(query: str, limit: int = 10) -> List[Dict]:
    """Search Semantic Scholar for theology/philosophy papers."""
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY") or SETTINGS.semantic_scholar_api_key
    headers = {"Accept": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    # Use original query - Semantic Scholar's AI handles relevance
    params = {
        "query": query,
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
