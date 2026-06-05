"""Rule Engine FastAPI dependencies.

Provides a ready-to-use :class:`RuleEngineService` with a loaded
:class:`Evaluator` (JDM built from the matrix once, reused across requests). The
evaluator is cached at module level and can be swapped at runtime by ``reload``.
"""

from __future__ import annotations

from threading import Lock

from app.services.rule_engine.config import RuleEngineSettings
from app.services.rule_engine.service import (
    RuleEngineService,
    build_evaluator_from_matrix,
)

_lock = Lock()
_service: RuleEngineService | None = None


def get_settings() -> RuleEngineSettings:
    """Instantiate the Rule Engine settings fragment (``RULE_ENGINE_`` prefix)."""
    return RuleEngineSettings()


def get_rule_engine_service() -> RuleEngineService:
    """Provide a :class:`RuleEngineService` backed by the loaded JDM.

    The evaluator (and its compiled zen-engine decision) is built once on first
    use and cached for reuse across requests.
    """
    global _service
    if _service is None:
        with _lock:
            if _service is None:
                evaluator = build_evaluator_from_matrix(get_settings().matrix_path)
                _service = RuleEngineService(evaluator)
    return _service


def reset_rule_engine_service() -> RuleEngineService:
    """Rebuild the cached service from the current matrix and return it.

    Called by the ``/reload`` endpoint after regenerating the JDM artifact so the
    live evaluator reflects matrix edits without a process restart.
    """
    global _service
    with _lock:
        evaluator = build_evaluator_from_matrix(get_settings().matrix_path)
        _service = RuleEngineService(evaluator)
    return _service
