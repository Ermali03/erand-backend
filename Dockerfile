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

# Copy application code
COPY . .

# Apply migrations, then run API server on the host-provided port when available.
CMD ["sh", "-c", "alembic upgrade head && fastapi run app/main.py --port ${PORT:-8000} --host 0.0.0.0"]
