"""Rule Engine settings fragment (``RULE_ENGINE_`` env prefix).

Discovered and composed by :mod:`app.core.settings_registry`. Stub: declares the
knobs implementers will read; no behavior here.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Service package directory, used to resolve default data/decisions paths.
_SERVICE_DIR = Path(__file__).resolve().parent


class RuleEngineSettings(BaseSettings):
    """Configuration for the Rule Engine service."""

    model_config = SettingsConfigDict(env_prefix="RULE_ENGINE_", extra="ignore")

    # Source matrix (source of truth) and JDM build-artifact output directory.
    matrix_path: Path = _SERVICE_DIR / "data" / "Bank_Eligibility_Matrix.xlsx"
    decisions_dir: Path = _SERVICE_DIR / "decisions"

    # Rebuild the JDM from the matrix on startup rather than loading the cached
    # artifact. Handy in development.
    rebuild_on_startup: bool = False
