"""Rule Engine ORM models.

Persists an audit trail of evaluations for traceability. SQLAlchemy only — no
Pydantic, no business logic. Stub: columns declared, behavior left to migrations
and the service layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EvaluationAudit(Base):
    """One persisted record per applicant evaluation."""

    __tablename__ = "rule_engine_evaluation_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Snapshot of the applicant payload and the resulting eligible banks.
    applicant: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    eligible_banks: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    matched_rule_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Version/hash of the JDM artifact used, for reproducibility.
    jdm_version: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # TODO(rule_engine): add indexes / retention policy as needed.
