# syntax=docker/dockerfile:1.7
# Multi-stage image: base (deps) -> dev (tooling + reload) / prod (slim, non-root).
# One image, one Python (3.12) — every developer and CI runs the exact same thing.

# --------------------------------------------------------------------------- #
# base — shared OS deps + Python runtime requirements.
# --------------------------------------------------------------------------- #
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src

# tesseract for the OCR jobs service; libpq for asyncpg.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Runtime deps come from the requirements/*.in fragments (no committed lockfiles).
# Constraint files (-c) can't carry extras, so strip them from base.in -> base.txt
# which the dev/service fragments reference.
COPY requirements/ requirements/
RUN sed 's/\[[^]]*\]//g' requirements/base.in > requirements/base.txt \
    && pip install \
        -r requirements/base.in \
        -r requirements/services/rule_engine.in \
        -r requirements/services/auth.in \
        -r requirements/services/domain_logs.in \
        -r requirements/services/ocr_jobs.in

COPY pyproject.toml alembic.ini ./
COPY src/ src/
COPY migrations/ migrations/
COPY scripts/ scripts/

# --------------------------------------------------------------------------- #
# dev — adds lint/format/type/test tooling. Source is bind-mounted in compose.dev.
# tests/ is copied so the image is self-contained for CI (the mount overlays it).
# --------------------------------------------------------------------------- #
FROM base AS dev
RUN pip install -r requirements/dev.in
COPY tests/ tests/
COPY docker/api/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --------------------------------------------------------------------------- #
# prod — slim, non-root, gunicorn + uvicorn workers.
# --------------------------------------------------------------------------- #
FROM base AS prod
RUN groupadd --system app && useradd --system --gid app --home /app app
COPY docker/api/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown -R app:app /app
USER app
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
