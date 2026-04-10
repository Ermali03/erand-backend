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

# Copy application code (alembic.ini + alembic/ must be present at image root)
COPY . .

RUN test -f alembic.ini && grep -q "script_location" alembic.ini

# Migrations then API. Use explicit -c so Alembic always finds config in /app.
CMD ["sh", "-c", "python -m alembic -c alembic.ini upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
