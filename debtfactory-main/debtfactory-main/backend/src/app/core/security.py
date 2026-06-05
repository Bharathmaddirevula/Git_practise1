"""Password hashing and token helper primitives (shared, framework-agnostic).

Thin wrappers the auth service builds on. Stubs only — no implementation yet.
"""

from __future__ import annotations


def hash_password(plain_password: str) -> str:
    """Return a salted hash of ``plain_password``.

    TODO(core): implement with passlib/argon2 or bcrypt.
    """
    raise NotImplementedError


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if ``plain_password`` matches ``hashed_password``.

    TODO(core): implement constant-time verification via passlib.
    """
    raise NotImplementedError
