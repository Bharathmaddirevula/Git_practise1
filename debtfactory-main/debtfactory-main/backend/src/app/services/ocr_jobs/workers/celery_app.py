"""Celery application factory. Stub: signatures only."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from celery import Celery


def create_celery_app() -> Celery:
    """Build the Celery app from :class:`OcrSettings`.

    TODO(ocr_jobs): construct ``Celery(...)`` with broker/result backend and
    autodiscover ``tasks``.
    """
    raise NotImplementedError
