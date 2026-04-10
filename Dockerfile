FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PostgreSQL (psycopg2) and cryptography
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full build context. If you build from the monorepo root, app + alembic may live in ortopedia-backend/.
COPY . .

RUN set -e; \
  if [ -f alembic.ini ]; then \
    :; \
  elif [ -f ortopedia-backend/alembic.ini ]; then \
    cp -a ortopedia-backend/. .; \
  else \
    echo "alembic.ini not found at ./alembic.ini or ./ortopedia-backend/alembic.ini"; \
    echo "Fix: set Render Root Directory to the backend folder, or commit alembic.ini + alembic/."; \
    ls -la; \
    exit 1; \
  fi; \
  grep -q "script_location" alembic.ini

# Migrations then API. Use explicit -c so Alembic always finds config in /app.
CMD ["sh", "-c", "python -m alembic -c alembic.ini upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
