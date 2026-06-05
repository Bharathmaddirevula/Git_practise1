"""OCR Jobs settings fragment (``OCR_`` env prefix). Stub only."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class OcrSettings(BaseSettings):
    """Configuration for the OCR Jobs service."""

    model_config = SettingsConfigDict(env_prefix="OCR_", extra="ignore")

    # Celery broker / backend (Redis by default).
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/1"

    # Default OCR engine + artifact store.
    engine: str = "tesseract"
    storage_root: str = "/var/lib/ocr-artifacts"

    # TODO(ocr_jobs): language packs, cloud OCR credentials.
