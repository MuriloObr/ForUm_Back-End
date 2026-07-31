# ---------------------------------------------------------------------------
# Stage 1: builder — install all dependencies (prod + test)
# ---------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-install-project

COPY src/ src/
COPY utils/ utils/
COPY alembic/ alembic/
COPY alembic.ini ./
COPY tests/ tests/

RUN uv sync --frozen --extra test

# ---------------------------------------------------------------------------
# Stage 2: runtime — production image (no test code)
# ---------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY src/ src/
COPY utils/ utils/
COPY alembic/ alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

# ---------------------------------------------------------------------------
# Stage 3: test — runs pytest
# ---------------------------------------------------------------------------
FROM builder AS test

CMD ["uv", "run", "pytest", "-v"]
