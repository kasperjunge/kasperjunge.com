# Project Instructions

## Commands
### One-time setup
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

Set `backend/.env` for host-run backend:
```dotenv
DATABASE_URL=postgresql+psycopg://kasperjunge:replace-with-local-password@localhost:5432/kasperjunge
REDIS_URL=redis://localhost:6379/0
```

### Start local dev loop (always this order)
1. Infra:
```bash
docker compose up -d postgres redis
docker compose run --rm migrate
```
2. Backend (hot reload):
```bash
cd backend
uv sync --dev
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```
3. Frontend (build + serve):
```bash
uv run python build.py --serve
```
4. Browser for agent validation:
```text
http://localhost:8000
```

Notes:
- Use `localhost` (not `127.0.0.1`) to match default CORS and avoid preflight failures.
- Backend should be reachable at `http://localhost:8001`.
- Frontend is a static site built with `build.py` and served on port 8000 (not live-server).
- Keep both server processes running while editing for feedback loop.
- If Postgres auth fails, align `POSTGRES_PASSWORD` in `.env` and `DATABASE_URL` in `backend/.env` with the credentials used by the existing `postgres_data` volume.

## Architecture
- The frontend is a static site built by `build.py` (Python + Mustache templates), served locally with `build.py --serve` in dev and deployed to GitHub Pages.
- `backend/` is a FastAPI service with API routes in `backend/app/api/v1/*`, business logic in `backend/app/services/*`, and settings in `backend/app/core/config.py`.
- Persistence is Postgres with Alembic migrations (`backend/alembic/*`), and rate limiting uses Redis when enabled with in-memory fallback if Redis is unavailable.
- In Docker Compose, `migrate` runs as a one-shot job before `backend`; there is no frontend container — static site uses `build.py --serve`.

## Code Style (HOW)
...

## Boundaries

### Always Do
...

### Ask First
...

### Never Do
...

## Security
...
