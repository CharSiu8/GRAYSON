"""Minimal demo using OpenAlex API to show titles and links for a query.

This requires only the `requests` package (install with `pip install requests` or
`pip install -r requirements.txt`).

Usage:
    python src/demo_simple.py "Kant ethics"
"""
import sys
import requests
from urllib.parse import urlencode

API = "https://api.openalex.org/works"


def search_openalex(query: str, per_page: int = 5):
    params = {"search": query, "per-page": per_page}
    url = f"{API}?{urlencode(params)}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    out = []
    for item in data.get("results", []):
        title = item.get("title")
        doi = item.get("doi")
        primary = item.get("primary_location") or {}
        url = primary.get("url") or item.get("id")
        out.append({"title": title, "doi": doi, "url": url, "year": item.get("publication_year")})
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/demo_simple.py \"your query\"")
        sys.exit(1)
    q = sys.argv[1]
    print(f"Searching OpenAlex for: {q}\n")
    try:
        results = search_openalex(q, per_page=5)
        for i, r in enumerate(results, start=1):
            print(f"{i}. {r['title']} ({r.get('year')})")
            if r.get('doi'):
                print(f"   DOI: {r['doi']}")
            print(f"   Link: {r['url']}\n")
    except Exception as e:
        print("Error during search:", e)
        sys.exit(2)
