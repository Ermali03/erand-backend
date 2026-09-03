"""Create the initial Admin user.

Run this once against the production database after migrations. Vercel does not
run ASGI lifespan events, so the app's in-process bootstrap won't fire there;
this script is the reliable way to create the first Admin so someone can log in.

Usage (env vars must point at the target database):

    DATABASE_URL=postgresql://... \
    INITIAL_ADMIN_EMAIL=admin@example.com \
    INITIAL_ADMIN_PASSWORD='a-strong-password' \
    python -m scripts.seed_admin

Idempotent: if a user with that email already exists, it does nothing.
"""

import os
import sys

from app.core.config import settings
from app.crud import user as crud_user
from app.db.database import SessionLocal
from app.schemas.user import UserCreate


def main() -> int:
    email = settings.INITIAL_ADMIN_EMAIL or os.getenv("INITIAL_ADMIN_EMAIL")
    password = settings.INITIAL_ADMIN_PASSWORD or os.getenv("INITIAL_ADMIN_PASSWORD")

    if not email or not password:
        print(
            "ERROR: set INITIAL_ADMIN_EMAIL and INITIAL_ADMIN_PASSWORD "
            "environment variables.",
            file=sys.stderr,
        )
        return 1

    db = SessionLocal()
    try:
        existing = crud_user.get_user_by_email(db, email=email)
        if existing:
            print(f"Admin '{email}' already exists — nothing to do.")
            return 0
        crud_user.create_user(
            db,
            user=UserCreate(email=email, password=password),
            initial_role="Admin",
        )
        print(f"Created Admin user '{email}'.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
