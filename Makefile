# ================================================================================
# WHAT THIS FILE IS:
# A collection of shortcuts for common development commands.
#
# WHY YOU NEED IT:
# - Simplifies complex commands into easy-to-remember shortcuts
# - Documents how to perform common tasks
# - Makes onboarding new contributors easier
# - Shows you think about developer experience
#
# WHAT TO PUT IN IT:
# Commands you run frequently during development.
# Usage: make <command>  (e.g., make test, make lint, make run)
# ================================================================================

.PHONY: help install install-dev test lint format type-check run docker-build docker-run clean

# Default target - show help
help:
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests with coverage"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code with black and isort"
	@echo "  make type-check   - Run mypy type checking"
	@echo "  make run          - Run the application"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run with Docker Compose"
	@echo "  make clean        - Remove cache and build files"

# ---------------------------------------------------------
# Installation
# ---------------------------------------------------------
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------
test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-fast:
	pytest tests/ -v -x  # Stop on first failure

# ---------------------------------------------------------
# Code Quality
# ---------------------------------------------------------
lint:
	ruff check .
	black --check .
	isort --check-only .

format:
	black .
	isort .
	ruff check --fix .

type-check:
	mypy src/

# Run all quality checks
check: lint type-check test

# ---------------------------------------------------------
# Running the Application
# ---------------------------------------------------------
run:
	python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# For Streamlit apps:
# run:
# 	streamlit run src/app.py

# ---------------------------------------------------------
# Docker
# ---------------------------------------------------------
docker-build:
	docker build -t ai-research-assistant .

docker-run:
	docker-compose up

docker-down:
	docker-compose down

# ---------------------------------------------------------
# Cleanup
# ---------------------------------------------------------
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
