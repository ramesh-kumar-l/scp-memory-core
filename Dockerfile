# Production image for the SCP Memory Engine (Phase 6).
# Includes the [observability] extra so OTLP tracing can be enabled at runtime
# via SCP_TRACING_ENABLED=true (see deploy/observability/).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --upgrade pip && pip install ".[observability]"

# Run as a non-root user (16-security-model).
RUN useradd --create-home --uid 10001 scp
USER scp

EXPOSE 8000

# Liveness/readiness probes are served by the app itself (/health, /health/ready).
CMD ["uvicorn", "scp_memory.api.app:create_app", "--factory", \
     "--host", "0.0.0.0", "--port", "8000"]
