"""Script to scan password hashes in the database and optionally rehash bcrypt -> argon2.

Usage:
    uv run python scripts/scan_password_hashes.py

This script uses the app's SQLModel session from `app.core.db` and inspects the
`hashed_password` column on the users table to determine how many hashes are
argon2, bcrypt, or unknown. Optionally, set REHASH=True to replace bcrypt hashes
with Argon2 hashes (requires write access and will update user records).
"""

from __future__ import annotations

import re
from typing import Tuple

from sqlmodel import select

from app.core.db import get_session
from app.modules.users.model.user import User
from app.modules.auth.crud.crud_auth import CRUDAuth

BCRYPT_RE = re.compile(r"^\$2[aby]\$")
ARGON_RE = re.compile(r"^\$argon2")


def classify_hash(h: str) -> str:
    if not h or not isinstance(h, str):
        return "empty/invalid"
    if ARGON_RE.match(h):
        return "argon2"
    if BCRYPT_RE.match(h):
        return "bcrypt"
    return "unknown"


def scan_and_report(rehash: bool = False) -> Tuple[int, int, int, int]:
    auth = CRUDAuth()
    with get_session() as session:
        users = session.exec(select(User)).all()
        counts = {"argon2": 0, "bcrypt": 0, "unknown": 0, "empty/invalid": 0}
        for u in users:
            h = getattr(u, "hashed_password", None)
            kind = classify_hash(h)
            counts[kind] += 1
            if rehash and kind == "bcrypt":
                # Attempt to verify using a fallback: skip verification and
                # directly rehash only if you have the plaintext (you don't),
                # so here we cannot rehash safely. Instead, mark user for reset.
                # For safety, we'll append a note to a column if it exists.
                try:
                    if hasattr(u, "needs_password_reset"):
                        setattr(u, "needs_password_reset", True)
                        session.add(u)
                except Exception:
                    pass
        session.commit()
    return (
        counts["argon2"],
        counts["bcrypt"],
        counts["unknown"],
        counts["empty/invalid"],
    )


if __name__ == "__main__":
    print("Scanning password hashes...")
    a, b, u, e = scan_and_report(rehash=False)
    print(f"argon2: {a}\nbcrypt: {b}\nunknown: {u}\nempty/invalid: {e}")
    if b:
        print(
            "\nNote: bcrypt hashes detected. You should prompt those users to reset passwords\nor run a controlled migration that captures plaintext (e.g. via login rehashing)."
        )
