# ================================================================================
# WHAT THIS FILE IS:
# The main entry point for your application.
#
# WHY YOU NEED IT:
# - Initializes and starts your application
# - Configures logging, settings, and dependencies
# - For APIs: sets up the web server and routes
# - For CLIs: handles command-line arguments
#
# WHAT TO PUT IN IT:
# Your application's startup logic. Examples below for different app types.
# ================================================================================

"""
Main application entry point.

This file initializes the AI Research Assistant application.
Choose and implement one of the patterns below based on your architecture.
"""

# ---------------------------------------------------------
# OPTION 1: FastAPI Application (recommended for AI projects)
# Great for building APIs that can be called from frontends or other services
# ---------------------------------------------------------

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
#
# app = FastAPI(
#     title="AI Research Assistant",
#     description="An AI-powered research assistant API",
#     version="0.1.0",
# )
#
# # Enable CORS for frontend access
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure appropriately for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint for monitoring."""
#     return {"status": "healthy"}
#
# @app.post("/query")
# async def query(question: str):
#     """Process a research query."""
#     # Your AI logic here
#     return {"answer": "Implement your research logic here"}


# ---------------------------------------------------------
# OPTION 2: Streamlit Application (great for demos and prototypes)
# Perfect for portfolio projects - easy to build impressive UIs
# ---------------------------------------------------------

# import streamlit as st
#
# st.set_page_config(
#     page_title="AI Research Assistant",
#     page_icon="🔬",
#     layout="wide",
# )
#
# st.title("AI Research Assistant")
# st.write("Enter your research question below:")
#
# query = st.text_input("Your question:")
# if st.button("Research"):
#     with st.spinner("Researching..."):
#         # Your AI logic here
#         st.write("Implement your research logic here")


# ---------------------------------------------------------
# OPTION 3: CLI Application
# Good for tools that run from the command line
# ---------------------------------------------------------

# import argparse
#
# def main():
#     parser = argparse.ArgumentParser(description="AI Research Assistant")
#     parser.add_argument("query", help="Your research question")
#     parser.add_argument("--sources", nargs="+", help="Source documents")
#     args = parser.parse_args()
#
#     # Your AI logic here
#     print(f"Researching: {args.query}")
#
# if __name__ == "__main__":
#     main()


# ---------------------------------------------------------
# Placeholder - Remove when implementing
# ---------------------------------------------------------
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import get_settings
from .ingest import ingest_openalex_query
from .vectorstore import add_documents, query as vector_query
from .llm import LLMClient, generate_library_links

app = FastAPI(title="GRAYSON - AI Research Assistant")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

settings = get_settings()
llm = LLMClient()


class IngestRequest(BaseModel):
    query: str
    max_results: int = 5


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/ingest")
async def ingest(req: IngestRequest):
    try:
        records = ingest_openalex_query(req.query, max_results=req.max_results)
        add_documents(records)
        return {"ingested": len(records)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query(req: QueryRequest):
    hits = vector_query(req.question, top_k=req.top_k)
    answer = llm.generate(req.question, hits)
    library_links = generate_library_links(req.question)
    return {
        "answer": answer,
        "sources": [h.get("metadata") for h in hits],
        "library_links": {
            "omni": library_links["omni"],
            "jstor": library_links["jstor"],
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")
