# tests/ - Test Suite

## Overview

This directory contains the pytest test suite for GRAYSON. Tests ensure the reliability and correctness of the backend components.

## Structure

| File | Purpose |
|------|---------|
| `conftest.py` | Pytest configuration and shared fixtures |
| `test_main.py` | Tests for the FastAPI application |
| `__init__.py` | Package initialization |

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run tests matching a pattern
pytest -k "test_health"
```

## Test Configuration

The `conftest.py` file contains shared fixtures available to all tests:
- Environment setup fixtures
- Mock LLM fixtures (avoid real API calls)
- FastAPI test client
- Sample document fixtures
- Temporary database fixtures

## Writing Tests

### Example Test Structure

```python
def test_health_endpoint(client):
    """Test the health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Best Practices

1. **Mock External APIs**: Always mock OpenAI, OpenAlex, and other external services
2. **Use Fixtures**: Leverage `conftest.py` fixtures for common setup
3. **Test Edge Cases**: Include tests for error conditions and edge cases
4. **Keep Tests Fast**: Avoid slow operations; use mocks where possible
5. **Descriptive Names**: Use clear, descriptive test function names

## Coverage

Test coverage reports are generated in `htmlcov/` directory:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## CI Integration

Tests run automatically on every push via GitHub Actions (`.github/workflows/ci.yml`).
