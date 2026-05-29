# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile — Intelligent Email Phishing Detection Gateway (IPEDG)
#
# Multi-stage build:
#   Stage 1 (builder)  — install Python deps into a virtualenv
#   Stage 2 (runtime)  — copy only the venv + source; no build tools
#
# Build:  docker build -t ipedg:latest .
# Run:    docker-compose up   (see docker-compose.yml)
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System packages needed only at compile time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# Create isolated virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (layer-cached until requirements.txt changes)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==21.2.0


# ── Stage 2: lean runtime image ───────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Non-root user for security (Twelve-Factor App + CIS benchmark)
RUN groupadd -r ipedg && useradd -r -g ipedg -s /sbin/nologin ipedg

WORKDIR /app

# Runtime system packages only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 curl \
 && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY --chown=ipedg:ipedg . .

# Create required runtime directories and set permissions
RUN mkdir -p logs uploads instance data/models && \
    chown -R ipedg:ipedg logs uploads instance data

# Expose gunicorn port
EXPOSE 5000

# Health check — polls the Flask app every 30 s
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -fs http://localhost:5000/ || exit 1

# Drop to non-root
USER ipedg

# Gunicorn entry point — 4 sync workers (adjust via GUNICORN_WORKERS env var)
CMD ["sh", "-c", "gunicorn \
      --bind 0.0.0.0:5000 \
      --workers ${GUNICORN_WORKERS:-4} \
      --timeout 120 \
      --access-logfile - \
      --error-logfile - \
      --log-level info \
      'run:app'"]
