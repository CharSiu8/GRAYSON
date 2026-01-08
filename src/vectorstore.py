# ================================================================================
# WHAT THIS FILE IS:
# Vector database wrapper for storing and querying document embeddings.
#
# WHY YOU NEED IT:
# - Provides persistent storage for semantic embeddings
# - Enables fast similarity search across documents
# - Abstracts ChromaDB implementation details
# - Handles document chunking and metadata storage
# ================================================================================

"""Simple Chroma-backed vector store wrapper.
"""
from typing import List, Dict, Any
import chromadb

from .config import get_settings
from .embeddings import embed_texts

SETTINGS = get_settings()

_client = None
_collection = None


def get_client():
    global _client
    if _client is None:
        # Use PersistentClient for local persistence (new ChromaDB API)
        _client = chromadb.PersistentClient(path=SETTINGS.chroma_persist_directory)
    return _client


def get_collection(name: str = "grayson"):
    global _collection
    client = get_client()
    # Use get_or_create_collection (new ChromaDB API)
    _collection = client.get_or_create_collection(name)
    return _collection


def add_documents(documents: List[Dict[str, Any]]):
    """Documents: list of {id, text, metadata}.

    This function chunks documents simply and stores embeddings + metadata.
    """
    collection = get_collection()
    ids = []
    docs = []
    metadatas = []
    for d in documents:
        doc_id = str(d.get("id") or "").replace("/", "_").replace(":", "_")
        text = d.get("text", "") or ""
        ids.append(doc_id)
        docs.append(text)
        # Ensure all metadata values are simple types for ChromaDB
        raw_meta = d.get("metadata", {})
        if not isinstance(raw_meta, dict):
            raw_meta = {"value": str(raw_meta)} if raw_meta else {}
        clean_meta = {}
        for k, v in raw_meta.items():
            if isinstance(v, (str, int, float, bool)):
                clean_meta[k] = v
            elif v is None:
                clean_meta[k] = ""
            else:
                clean_meta[k] = str(v)
        metadatas.append(clean_meta)
    embeddings = embed_texts(docs).tolist()
    collection.add(ids=ids, documents=docs, metadatas=metadatas, embeddings=embeddings)


def query(query_text: str, top_k: int = 5):
    collection = get_collection()
    q_emb = embed_texts([query_text])[0].tolist()
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)
    # Normalize results - handle empty results gracefully
    out = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            out.append(
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None,
                }
            )
    return out
