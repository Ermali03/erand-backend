# Backend

FastAPI backend for authentication, patient workflow, records, and user roles.

## Local development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 ./venv/bin/python -m pytest
./venv/bin/uvicorn app.main:app --reload
```

## Folder Notes

- `app/api`: API routes and dependencies
- `app/core`: Settings, auth, and role definitions
- `app/crud`: Database CRUD helpers
- `app/db`: Engine and session setup
- `app/models`: SQLAlchemy models
- `app/schemas`: Request and response models
- `app/services`: Higher-level business logic
- `alembic`: Database migrations
- `scripts`: One-off operational scripts (e.g. seeding the initial admin)
- `tests`: Backend tests
- `api/index.py` + `vercel.json`: Vercel serverless entrypoint

## Deploying to Vercel

The app runs as a single Python serverless function. `vercel.json` rewrites every
path to `api/index.py`, which exposes the FastAPI `app`.

### 1. Provision a database

Vercel functions are stateless with a read-only filesystem — SQLite will not work.
Use a managed Postgres such as **Neon** (recommended), Supabase, or Vercel Postgres.
Copy its **pooled** connection string (Neon's host contains `-pooler`).

### 2. Create the Vercel project

- Import this repository into Vercel (this `backend` folder is its own git repo, so
  its root is the project root — no "Root Directory" override needed).
- Framework preset: **Other**. No build command is required; Vercel detects the
  Python function from `api/index.py` and installs `requirements.txt`.

### 3. Set Environment Variables (Project → Settings → Environment Variables)

| Variable | Value |
| --- | --- |
| `ENVIRONMENT` | `production` |
| `DATABASE_URL` | your pooled Postgres URL (`...?sslmode=require`) |
| `SECRET_KEY` | a strong secret — generate with `openssl rand -hex 32` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | e.g. `720` |
| `CORS_ORIGINS` | your frontend origin(s), comma-separated, no trailing slash — e.g. `https://your-frontend.vercel.app` |

> `SECRET_KEY` is required in production — the app refuses to start with the
> insecure default when `ENVIRONMENT=production`.

### 4. Run migrations (once, and after any new migration)

Vercel does not run Alembic for you. From your machine, pointed at the prod DB:

```bash
DATABASE_URL='postgresql://...pooled-connection-string...' \
  python -m alembic upgrade head
```

### 5. Seed the initial admin (once)

Vercel does not run FastAPI lifespan events, so the in-app admin bootstrap does
not fire there. Create the first Admin explicitly:

```bash
DATABASE_URL='postgresql://...pooled-connection-string...' \
INITIAL_ADMIN_EMAIL='admin@example.com' \
INITIAL_ADMIN_PASSWORD='a-strong-password' \
  python -m scripts.seed_admin
```

This is idempotent — safe to re-run.

### 6. Deploy and verify

After deploying, check:

- `GET https://<your-app>.vercel.app/health` → `{"status":"ok",...}`
- `GET https://<your-app>.vercel.app/docs` → interactive API docs

Finally, set `NEXT_PUBLIC_API_BASE_URL` on the **frontend** to the deployed backend
URL and redeploy the frontend.

> Note: the included `Dockerfile` / `docker-compose.yml` are for container hosts
> (e.g. Render) and are not used by Vercel.
