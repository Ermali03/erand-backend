# Backend

FastAPI backend for authentication, patient workflow, records, and user roles.

## Commands

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
- `tests`: Backend tests

