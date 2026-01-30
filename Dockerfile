FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src ./src
COPY scripts ./scripts
COPY assets ./assets
COPY data ./data
COPY vector_store ./vector_store

# Create necessary directories
RUN mkdir -p logs

# Expose Gradio port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["uv", "run", "python", "-m", "src.ui.app"]