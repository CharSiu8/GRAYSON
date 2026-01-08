# ================================================================================
# WHAT THIS FILE IS:
# Pytest configuration and shared fixtures for all tests.
#
# WHY YOU NEED IT:
# - Centralizes test setup and teardown logic
# - Defines reusable fixtures (test data, mock objects, etc.)
# - Automatically discovered by pytest - no imports needed
# - Reduces code duplication across test files
#
# WHAT TO PUT IN IT:
# Fixtures, configuration, and setup code shared across tests.
# ================================================================================

"""
Pytest configuration and shared fixtures.

Fixtures defined here are automatically available to all tests
without needing to import them.
"""

import pytest


# ---------------------------------------------------------
# Example: Environment fixture
# Sets up test environment variables
# ---------------------------------------------------------
# @pytest.fixture(autouse=True)
# def setup_test_env(monkeypatch):
#     """Set up test environment variables."""
#     monkeypatch.setenv("ENVIRONMENT", "test")
#     monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")


# ---------------------------------------------------------
# Example: Mock LLM fixture
# Avoids calling real APIs during tests
# ---------------------------------------------------------
# @pytest.fixture
# def mock_llm(mocker):
#     """Mock LLM that returns predictable responses."""
#     mock = mocker.patch("src.llm.get_llm_response")
#     mock.return_value = "This is a mock response for testing."
#     return mock


# ---------------------------------------------------------
# Example: Test client fixture for FastAPI
# ---------------------------------------------------------
# from fastapi.testclient import TestClient
# from src.main import app
#
# @pytest.fixture
# def client():
#     """FastAPI test client."""
#     return TestClient(app)


# ---------------------------------------------------------
# Example: Sample documents fixture
# ---------------------------------------------------------
# @pytest.fixture
# def sample_documents():
#     """Sample documents for testing retrieval."""
#     return [
#         {"id": "1", "content": "The quick brown fox jumps over the lazy dog."},
#         {"id": "2", "content": "Machine learning is a subset of artificial intelligence."},
#         {"id": "3", "content": "Python is a popular programming language for AI."},
#     ]


# ---------------------------------------------------------
# Example: Temporary database fixture
# ---------------------------------------------------------
# import tempfile
# import shutil
#
# @pytest.fixture
# def temp_db():
#     """Create a temporary database directory."""
#     temp_dir = tempfile.mkdtemp()
#     yield temp_dir
#     shutil.rmtree(temp_dir)


# ---------------------------------------------------------
# Placeholder fixture - Remove when implementing
# ---------------------------------------------------------
@pytest.fixture
def sample_data():
    """Sample fixture - replace with your actual test data."""
    return {"key": "value"}
