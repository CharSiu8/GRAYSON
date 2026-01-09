
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.11-slim as production

# Create non-root user for security
# (Running as root in containers is a security risk)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Add any system dependencies your app needs here
    # Example: libpq5 for PostgreSQL, curl for health checks
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY src/ ./src/
# COPY config/ ./config/  # Uncomment if you have a config directory

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Expose the port your app runs on
EXPOSE 8000

# Health check (important for orchestration platforms)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run your application
# Modify this based on your app's entry point
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---------------------------------------------------------
# Alternative commands based on framework:
# ---------------------------------------------------------
# FastAPI: CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Streamlit: CMD ["streamlit", "run", "src/app.py", "--server.port", "8000"]
# Flask: CMD ["gunicorn", "--bind", "0.0.0.0:8000", "src.main:app"]
# CLI tool: CMD ["python", "-m", "src.cli"]
