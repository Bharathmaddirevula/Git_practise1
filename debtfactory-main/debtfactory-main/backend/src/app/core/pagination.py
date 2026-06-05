"""Shared pagination params and response schema.

Reusable building blocks so every list endpoint paginates the same way. Stubs
only — shape is declared, behavior is left to implementers.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Standard offset/limit pagination query parameters."""

    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


class Page[T](BaseModel):
    """A single page of results plus the total count.

    TODO(core): wire helper constructors for SQLAlchemy result sets.
    """

    items: list[T]
    total: int
    offset: int
    limit: int
