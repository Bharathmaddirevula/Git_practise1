"""Artifact store protocol. Stub: interface only."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ArtifactStore(Protocol):
    """Stores and retrieves document/result artifacts by URI."""

    def get(self, uri: str) -> bytes:
        """Fetch raw bytes for ``uri``.  TODO(ocr_jobs)."""
        ...

    def put(self, key: str, data: bytes) -> str:
        """Store ``data`` under ``key`` and return its URI.  TODO(ocr_jobs)."""
        ...
