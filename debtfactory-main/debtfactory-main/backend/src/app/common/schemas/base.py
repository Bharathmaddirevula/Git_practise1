"""Shared base schemas: ORM-friendly model and a response envelope.

Cross-service Pydantic contracts live here (never service-specific ones). Stubs
only — the shapes are declared so services can subclass them consistently.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """Base for schemas read from SQLAlchemy ORM instances."""

    model_config = ConfigDict(from_attributes=True)


class ResponseEnvelope[T](BaseModel):
    """Standard success envelope mirroring the error envelope shape.

    TODO(common): finalize fields once response conventions are locked.
    """

    data: T
