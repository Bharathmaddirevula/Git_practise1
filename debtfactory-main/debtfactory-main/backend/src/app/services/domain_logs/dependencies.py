"""Domain Logs FastAPI dependencies. Stub only."""

from __future__ import annotations

from app.services.domain_logs.service import DomainLogsService


def get_domain_logs_service() -> DomainLogsService:
    """Provide a :class:`DomainLogsService`.  TODO(domain_logs)."""
    raise NotImplementedError
