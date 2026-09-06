"""Seed staff (User + Doctor) accounts from .docs/lista_e_doktoreve-v2.csv.

Idempotent: existing emails are skipped. Target DB is chosen by DATABASE_URL.

Usage:
    DATABASE_URL=... python -m scripts.seed_staff [--write-credentials PATH]

Email:    accents stripped, lowercased, spaces removed, @ortopedia-qkuk.com
Password: <Firstname>123@@  (first letter upper, rest lower)
Role:     Doctor for everyone, except names in ADMIN_NAMES -> Admin
"""

from __future__ import annotations

import csv
import os
import sys
import unicodedata
from uuid import uuid4

from app.db.database import SessionLocal
import app.models  # noqa: F401  (register models on Base.metadata)
from app.models import Doctor, User
from app.core.security import get_password_hash
from app.core.roles import serialize_roles

CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", ".docs", "lista_e_doktoreve-v2.csv"
)
EMAIL_DOMAIN = "ortopedia-qkuk.com"

# Full names (lowercased) that should get the Admin role instead of Doctor.
ADMIN_NAMES = {"erand topalli"}


def strip_accents(value: str) -> str:
    return "".join(
        ch
        for ch in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(ch)
    )


def email_for(name: str) -> str:
    slug = "".join(ch for ch in strip_accents(name).lower() if ch.isalnum())
    return f"{slug}@{EMAIL_DOMAIN}"


def password_for(name: str) -> str:
    first = strip_accents(name.strip().split()[0])
    first = first[:1].upper() + first[1:].lower()
    return f"{first}123@@"


def role_for(name: str) -> str:
    return "Admin" if name.strip().lower() in ADMIN_NAMES else "Doctor"


def load_rows() -> list[tuple[str, str]]:
    with open(CSV_PATH, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)  # header
        rows: list[tuple[str, str]] = []
        for row in reader:
            if not row or not row[0].strip():
                continue
            name = row[0].strip()
            title = row[1].strip() if len(row) > 1 else "Specialist i Ortopedisë"
            rows.append((name, title))
        return rows


def main() -> None:
    write_credentials = None
    if "--write-credentials" in sys.argv:
        idx = sys.argv.index("--write-credentials")
        write_credentials = sys.argv[idx + 1]

    rows = load_rows()
    db = SessionLocal()
    created: list[tuple[str, str, str, str, str]] = []
    skipped: list[str] = []
    try:
        for name, title in rows:
            email = email_for(name)
            if db.query(User).filter(User.email == email).first():
                skipped.append(email)
                continue

            role = role_for(name)
            password = password_for(name)
            roles_str = serialize_roles([role])

            db.add(
                User(
                    email=email,
                    hashed_password=get_password_hash(password),
                    role=roles_str,
                )
            )
            db.add(
                Doctor(
                    id=f"DOC-{uuid4().hex[:8].upper()}",
                    name=name,
                    email=email,
                    specialty=title,
                    role=roles_str,
                )
            )
            created.append((name, email, password, role, title))
        db.commit()
    finally:
        db.close()

    print(f"Created {len(created)} staff account(s); skipped {len(skipped)} existing.")
    for name, email, password, role, _title in created:
        print(f"  + {name:<20} {email:<40} {password:<14} {role}")
    if skipped:
        print("Skipped existing:", ", ".join(skipped))

    if write_credentials and created:
        with open(write_credentials, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Emri", "Email", "Password", "Roli", "Pozita"])
            writer.writerows(created)
        print(f"Wrote credentials for {len(created)} account(s) to {write_credentials}")


if __name__ == "__main__":
    main()
