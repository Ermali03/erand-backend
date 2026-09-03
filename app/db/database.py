import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings

database_url = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine_options: dict[str, object] = {"pool_pre_ping": True}

if database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
elif os.getenv("VERCEL"):
    # On Vercel each request runs in a short-lived serverless instance, so a
    # persistent connection pool would hold stale/idle connections. Open a
    # fresh connection per request instead and let the DB (e.g. Neon's pooled
    # endpoint) handle pooling.
    engine_options["poolclass"] = NullPool

engine = create_engine(database_url, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
