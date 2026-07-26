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
- `database/` — legacy SQLAlchemy ORM (models, schemas, engine). **This is what the app actually uses.**
- `src/db/` — newer SQLModel models. Partially defined, not fully wired into routes.
- `utils/api_types.py` — Pydantic request/response schemas
- `utils/error_decorators.py` — `@errorHandler` decorator that manages sessions and commits

## Gotchas

- **`tittle` is correct** in legacy `database/models.py` — it's a DB column name. Do not "fix" to `title`.
- The `@errorHandler("post")` decorator auto-commits; `"get"` does not. Route handlers return `[data, error]` tuples.
- Two ORM layers exist (`database/` and `src/db/models/`). The app imports from `database/`. Unless explicitly migrating, use `database/` models.
- No test suite, linter, or formatter is configured. There is nothing to run for verification beyond starting the server.
- `database/create_tables.py` is a standalone script (uses relative imports, meant to be run from the `database/` directory).
