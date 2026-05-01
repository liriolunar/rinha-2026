FROM python:3.13-slim AS builder

WORKDIR /

# Install build deps for numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

# Copy dependency manifests
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment using the lockfile
RUN uv sync --frozen --no-install-project

# Runtime stage
FROM python:3.13-slim

WORKDIR /

# Copy virtual environment from builder
COPY --from=builder /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Copy app code and resources
COPY *.py ./
COPY resources/ /resources/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV RESOURCES_PATH=/resources
ENV PORT=9999

EXPOSE 9999

CMD ["python", "main.py"]
