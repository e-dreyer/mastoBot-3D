# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
	apt-get install -y --no-install-recommends git && \
	rm -rf /var/lib/apt/lists/*

# Copy mastoBot first so uv can find it when resolving local path dependency
COPY mastoBot /mastoBot

# Copy pyproject.toml and uv.lock first (for better layer caching)
COPY mastoBot-3D/pyproject.toml mastoBot-3D/uv.lock ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy the rest of the application
COPY mastoBot-3D/ .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Set the entry point
CMD ["uv", "run", "main.py"]
