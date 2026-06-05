"""OCR Jobs ORM models: OcrJob, OcrResult. Stub: columns declared."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OcrJob(Base):
    """A queued / running / finished OCR job."""

    __tablename__ = "ocr_jobs_job"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_uri: Mapped[str] = mapped_column(String(1024))
    language: Mapped[str] = mapped_column(String(16), default="eng")
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    result: Mapped[OcrResult | None] = relationship(back_populates="job", uselist=False)


class OcrResult(Base):
    """Extracted text for a completed job."""

    __tablename__ = "ocr_jobs_result"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("ocr_jobs_job.id"), unique=True)
    text: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    job: Mapped[OcrJob] = relationship(back_populates="result")

    # TODO(ocr_jobs): page-level results, bounding boxes.
