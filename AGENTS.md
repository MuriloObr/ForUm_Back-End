# ForUm Server

FastAPI forum backend. Python 3.13+, PostgreSQL, uv package manager.

## Run locally

```bash
uv sync                  # install deps
uv run uvicorn src.main:app --reload   # dev server on :8000
```

Requires `.env` with: `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`.

## Docker

```bash
docker compose up --build                        # dev (hot-reload)
docker compose --profile test up --build         # run tests in container
docker compose --profile prod up --build         # production-like local
```

Exposes API on `:5001`, Postgres on `:5432`. Reads `.env` file.
Entrypoint runs `alembic upgrade head` before starting uvicorn.

## Architecture

- `src/main.py` — FastAPI app, routes, JWT cookie auth
- `src/user_actions.py`, `src/post_actions.py`, `src/comment_actions.py` — business logic
- `src/db/models/` — SQLModel ORM models (User, Post, Comment, link tables)
- `src/db/engine.py` — engine and env var config
- `utils/api_types.py` — Pydantic request/response schemas
- `utils/error_decorators.py` — `@errorHandler` decorator that manages sessions and commits
- `entrypoint.sh` — Docker entrypoint: runs migrations then uvicorn
- `Dockerfile` — Multi-stage: `builder` → `runtime` (prod) / `test`

## Migrations (Alembic)

Alembic reads `DATABASE_URL` from the environment (or `.env` via python-dotenv).

```bash
alembic revision --autogenerate -m "description"   # generate migration from model changes
alembic upgrade head                                # apply all pending migrations
alembic downgrade -1                                # rollback last migration
alembic check                                      # detect drift between models and DB
```

Alembic is configured against `src/db/models/` for autogenerate.

## Tests

```bash
uv run pytest -v                    # run all tests
uv run pytest tests/test_auth.py   # run auth tests only
```

Uses SQLite in-memory for tests. No PostgreSQL required.

## Gotchas

- The `@errorHandler("post")` decorator auto-commits; `"get"` does not. Route handlers return `[data, error]` tuples.
- Never call `@errorHandler`-decorated functions from within another `@errorHandler` block — nested sessions on `StaticPool` cause silent rollbacks. Use `_get_user_data()` instead of `get_user_by_id()` for inline user lookups.
- `model_dump()` does not include relationship fields (`likes`, `views`). Iterate ORM attributes directly.
- All models use `__tablename__` to match the plural DB table names (`users`, `posts`, `comments`, `posts_likes`, `posts_views`, `comments_likes`).
- Post tracks its answer via `answer_id: int | None` FK to `comments.id` (not a boolean on Comment).
