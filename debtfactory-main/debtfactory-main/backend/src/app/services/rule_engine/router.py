"""Rule Engine HTTP router.

HTTP only: declares paths, verbs, status codes, and request/response models, then
delegates to :class:`RuleEngineService`. No business logic, no DB access here.

The module-level ``router`` is auto-discovered and mounted by
:func:`app.api.router_registry.discover_routers`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.services.rule_engine.constants import ROUTE_PREFIX
from app.services.rule_engine.dependencies import (
    get_rule_engine_service,
    get_settings,
    reset_rule_engine_service,
)
from app.services.rule_engine.schemas import (
    ApplicantInput,
    EvaluateResponse,
    ReloadResponse,
)
from app.services.rule_engine.service import RuleEngineService

router = APIRouter(prefix=ROUTE_PREFIX, tags=["rule-engine"])


@router.post("/evaluate", response_model=EvaluateResponse, status_code=status.HTTP_200_OK)
async def evaluate(
    applicant: ApplicantInput,
    service: RuleEngineService = Depends(get_rule_engine_service),
) -> EvaluateResponse:
    """Evaluate an applicant and return the banks they are eligible for."""
    eligible = service.evaluate(applicant)
    return EvaluateResponse(eligible_banks=eligible, matched_rule_count=len(eligible))


@router.post("/reload", response_model=ReloadResponse, status_code=status.HTTP_200_OK)
async def reload() -> ReloadResponse:
    """Re-parse the matrix, rebuild the JDM artifact, and swap the live engine."""
    settings = get_settings()
    rows_parsed, jdm_path = RuleEngineService.reload_matrix(
        settings.matrix_path, settings.decisions_dir
    )
    reset_rule_engine_service()
    return ReloadResponse(rows_parsed=rows_parsed, jdm_path=str(jdm_path))
