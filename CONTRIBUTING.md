# Contributing to AI Research Assistant

<!--
================================================================================
WHAT THIS FILE IS:
Guidelines for how others can contribute to your project.

WHY YOU NEED IT:
- Shows you understand open-source collaboration
- Demonstrates you can write clear documentation
- Makes your project appear more professional and maintainable
- Employers value collaboration skills

WHAT TO PUT IN IT:
Customize the sections below for your specific project.
================================================================================
-->

Thank you for your interest in contributing! This document provides guidelines
for contributing to the AI Research Assistant project.

## Getting Started

### Prerequisites
<!--
List what contributors need to have installed.
Example:
- Python 3.11+
- Git
- A code editor (VS Code recommended)
-->

### Setting Up the Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/ai-research-assistant.git
   cd ai-research-assistant
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Branching Strategy
<!--
Explain your branching model. Example:
-->
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features (e.g., `feature/add-pdf-parsing`)
- `fix/*` - Bug fixes (e.g., `fix/memory-leak`)

### Making Changes

1. Create a new branch from `develop`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Write or update tests
4. Run the test suite:
   ```bash
   pytest tests/ -v
   ```
5. Run linting:
   ```bash
   ruff check .
   black .
   ```
6. Commit your changes (see commit guidelines below)
7. Push and create a pull request

### Commit Message Guidelines
<!--
Following conventional commits makes your history readable and enables automated changelogs.
-->

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add PDF document ingestion
fix: resolve memory leak in vector store
docs: update installation instructions
```

## Code Style

### Python Style Guide
<!--
Define your code standards. Example:
-->
- Follow [PEP 8](https://pep8.org/)
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters (Black default)
- Use docstrings for all public functions and classes

### Documentation
- Update the README if you change functionality
- Add docstrings to new functions and classes
- Include examples in docstrings where helpful

## Testing

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_retriever.py -v
```

### Writing Tests
- Place tests in the `tests/` directory
- Mirror the source structure (e.g., `src/retriever.py` -> `tests/test_retriever.py`)
- Use descriptive test names: `test_retriever_returns_relevant_documents`
- Aim for high coverage on critical paths

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Fill out the pull request template completely
4. Request review from maintainers
5. Address any feedback

## Questions?

Feel free to open an issue for any questions or concerns.
