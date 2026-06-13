# Backend

FastAPI + PostgreSQL backend for the AISI Project. Mirrors the data currently stored in the
mobile app's `AsyncStorage` (auth, onboarding, profile metrics, calories, books, workouts,
nutrition, progress, chat) as a real REST API with JWT authentication.

## Tech stack

- **FastAPI** (async) + **Uvicorn**
- **PostgreSQL** via **SQLAlchemy 2.0** (async, `asyncpg`)
- **Alembic** for migrations
- **Pydantic v2** for request/response schemas
- **JWT** access tokens + rotating refresh tokens (stored hashed in the database)

## Prerequisites

- **Python 3.11+** (with `pip` and `venv`)
- **Docker** + **Docker Compose** (to run PostgreSQL via the [Database](../Database) repo),
  or a locally installed PostgreSQL instance

## Setup

1. Start PostgreSQL (from the `Database` repo, in a sibling directory):

   ```bash
   cd ../Database
   docker compose up -d
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and adjust values if needed (in particular `DATABASE_URL`
   must match the credentials/port from the `Database` repo, and `JWT_SECRET_KEY` should be
   a long random string in any non-local environment):

   ```bash
   cp .env.example .env
   ```

4. Apply database migrations:

   ```bash
   alembic upgrade head
   ```

5. Run the development server:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI.

## Project structure

```
app/
  main.py            # FastAPI app, CORS, router registration
  core/              # settings, DB session/engine, security (JWT, password hashing)
  api/
    deps.py          # get_db, get_current_user dependencies
    routes/          # one router per domain (auth, users, onboarding, calories, ...)
  models/            # SQLAlchemy ORM models, one file per domain
  schemas/           # Pydantic request/response schemas, one file per domain
  services/          # cross-cutting business logic (e.g. onboarding -> goal seeding)
alembic/             # migration environment (async) and versions/
```

## Authentication

- `POST /api/auth/register` — create a user, returns an access/refresh token pair
- `POST /api/auth/login` — verify credentials, returns an access/refresh token pair
- `POST /api/auth/refresh` — rotates the refresh token, returns a new pair
- `POST /api/auth/logout` — revokes a refresh token

All other endpoints require `Authorization: Bearer <access_token>`.

## Database migrations

New migrations are generated with Alembic, based on the SQLAlchemy models in `app/models/`:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The initial migration (`alembic/versions/0001_initial_schema.py`) creates all tables and seeds
four global sample recipes (matching the frontend's built-in recipe list).
