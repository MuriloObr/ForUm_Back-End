# ForUm Server

FastAPI forum backend. Python 3.13+, PostgreSQL, uv package manager.

## Run locally

```bash
uv sync                  # install deps
uv run uvicorn src.main:app --reload   # dev server on :8000
```

Requires `.env` with: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `POSTGRES_URL_LOCAL`, `POSTGRES_URL_PROD`, `ISPROD`.

## Docker

```bash
docker compose up --build
```

Exposes API on `:5001`, Postgres on `:5432`. Reads `.env` file.

## Architecture

- `src/main.py` — FastAPI app, routes, JWT cookie auth
- `src/user_actions.py`, `src/post_actions.py`, `src/comment_actions.py` — business logic
- `src/db/models/` — SQLModel ORM models (User, Post, Comment, link tables)
- `src/db/engine.py` — engine and env var config
- `utils/api_types.py` — Pydantic request/response schemas
- `utils/error_decorators.py` — `@errorHandler` decorator that manages sessions and commits

## Migrations (Alembic)

Alembic uses the same env vars as the app (`ISPROD`, `POSTGRES_URL_LOCAL`, `POSTGRES_URL_PROD`).

```bash
alembic revision --autogenerate -m "description"   # generate migration from model changes
alembic upgrade head                                # apply all pending migrations
alembic downgrade -1                                # rollback last migration
alembic check                                      # detect drift between models and DB
```

Alembic is configured against `src/db/models/` for autogenerate.

## Gotchas

- The `@errorHandler("post")` decorator auto-commits; `"get"` does not. Route handlers return `[data, error]` tuples.
- No test suite, linter, or formatter is configured. There is nothing to run for verification beyond starting the server.
- All models use `__tablename__` to match the plural DB table names (`users`, `posts`, `comments`, `posts_likes`, `posts_views`, `comments_likes`).
- Post tracks its answer via `answer_id: int | None` FK to `comments.id` (not a boolean on Comment).
