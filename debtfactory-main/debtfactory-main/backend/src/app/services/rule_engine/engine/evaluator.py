"""Stage 4: evaluate applicants against the JDM via zen-engine.

Wraps ``zen.ZenEngine``. The zen-engine API used here:

.. code-block:: python

    import zen
    engine = zen.ZenEngine()
    decision = engine.create_decision(jdm_dict)
    result = decision.evaluate(applicant_dict)  # -> {"result": [...]}

With the ``collect`` hit policy the decision table returns a list of output
objects — one per matching rule — which we adapt into ``EligibilityResult``.
"""

from __future__ import annotations

from typing import Any

import zen

from app.services.rule_engine.engine.jdm_builder import JdmGraph
from app.services.rule_engine.exceptions import EvaluationError
from app.services.rule_engine.schemas import ApplicantInput, EligibilityResult


class Evaluator:
    """Holds a loaded JDM decision and evaluates applicants against it."""

    def __init__(self, jdm: JdmGraph) -> None:
        """Load ``jdm`` into a ``zen.ZenEngine`` decision."""
        self._jdm = jdm
        try:
            self._engine = zen.ZenEngine()
            # zen-engine accepts a JDM mapping at runtime; its type hint is narrower.
            self._decision = self._engine.create_decision(jdm)  # type: ignore[arg-type]
        except Exception as exc:
            raise EvaluationError(
                f"Failed to load JDM into zen-engine: {exc}",
            ) from exc

    def evaluate(self, applicant: ApplicantInput) -> list[EligibilityResult]:
        """Return every bank the applicant is eligible for.

        Args:
            applicant: Validated applicant profile.

        Returns:
            One :class:`EligibilityResult` per matching rule (possibly empty).

        Raises:
            EvaluationError: if zen-engine evaluation fails.
        """
        context = applicant.model_dump()
        try:
            response = self._decision.evaluate(context)
        except Exception as exc:
            raise EvaluationError(
                f"zen-engine evaluation failed: {exc}",
                details={"applicant": context},
            ) from exc

        return [self._to_result(item) for item in _extract_rows(response)]

    @staticmethod
    def _to_result(item: dict[str, Any]) -> EligibilityResult:
        description = item.get("description")
        return EligibilityResult(
            bank_name=str(item.get("bank_name", "")),
            description=str(description) if description not in (None, "") else None,
        )


def _extract_rows(response: Any) -> list[dict[str, Any]]:
    """Normalize a zen-engine response into a list of output dicts.

    ``collect`` yields ``{"result": [ {...}, ... ]}``; a single-hit policy would
    yield ``{"result": {...}}``. Handle both, plus a bare list/dict.
    """
    payload = response.get("result", response) if isinstance(response, dict) else response

    if payload is None:
        return []
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        return [payload]
    return []
