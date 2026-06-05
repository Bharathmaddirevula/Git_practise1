"""OCR engine protocol (tesseract / cloud). Stub: interface only."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class OcrEngine(Protocol):
    """Extracts text from a document's bytes."""

    name: str

    def extract_text(self, document: bytes, language: str = "eng") -> str:
        """Return recognized text for ``document``.  TODO(ocr_jobs)."""
        ...
