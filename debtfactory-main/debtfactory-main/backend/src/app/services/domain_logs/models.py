"""Domain Logs ORM models: LogSource, LogEntry. Stub: columns declared."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LogSource(Base):
    """A named source that emits log entries."""

    __tablename__ = "domain_logs_source"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)

    entries: Mapped[list[LogEntry]] = relationship(back_populates="source")


class LogEntry(Base):
    """A persisted log line belonging to a source."""

    __tablename__ = "domain_logs_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("domain_logs_source.id"))
    level: Mapped[str] = mapped_column(String(16))
    message: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped[LogSource] = relationship(back_populates="entries")

    # TODO(domain_logs): structured fields / indexes for tailing.
