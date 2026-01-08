# ================================================================================
# WHAT THIS FILE IS:
# Embeddings wrapper for converting text to vector representations.
#
# WHY YOU NEED IT:
# - Converts text into semantic vectors for similarity search
# - Uses OpenAI embeddings API for high-quality, low-memory embeddings
# - Enables semantic search in the vector database
# ================================================================================

"""Embeddings helper using OpenAI API.
"""
from typing import List
import numpy as np
from openai import OpenAI

from .config import get_settings
from .usage_tracker import check_usage_limit, record_usage

SETTINGS = get_settings()

_CLIENT = None


def get_client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = OpenAI(api_key=SETTINGS.openai_api_key)
    return _CLIENT


def embed_texts(texts: List[str]) -> np.ndarray:
    """Convert texts to embeddings using OpenAI API."""
    # Check usage limit before making API call
    is_allowed, remaining, limit_message = check_usage_limit()
    if not is_allowed:
        raise RuntimeError(limit_message)

    client = get_client()

    # Handle empty texts
    if not texts:
        return np.array([])

    # OpenAI embeddings API
    response = client.embeddings.create(
        model=SETTINGS.embedding_model,
        input=texts
    )

    # Record token usage
    if response.usage:
        record_usage("text-embedding-3-small", response.usage.total_tokens)

    # Extract embeddings and convert to numpy array
    embeddings = [item.embedding for item in response.data]
    return np.array(embeddings)
