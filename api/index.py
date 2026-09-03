"""Vercel serverless entrypoint.

Vercel's Python runtime serves the ASGI ``app`` object exported here. The whole
project is bundled, so ``app`` (the package at the repo root) is importable.

Note: Vercel does not run ASGI lifespan events, so the initial admin is seeded
out-of-band via ``scripts/seed_admin.py`` (see README) instead of the FastAPI
lifespan hook.
"""

from app.main import app

# Vercel looks for a module-level ASGI callable named ``app``.
__all__ = ["app"]
