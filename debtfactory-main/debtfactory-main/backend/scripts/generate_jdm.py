"""CLI: build the GoRules JDM artifact from the eligibility matrix.

Usage:
    python scripts/generate_jdm.py [--matrix PATH] [--out PATH]

Runs the Rule Engine pipeline (parse -> validate -> build) and writes
``decisions/bank_eligibility.jdm.json``. This is the only sanctioned way to
(re)generate the JDM — never hand-edit the JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make ``src`` importable when run as a plain script.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from app.services.rule_engine.config import RuleEngineSettings  # noqa: E402
from app.services.rule_engine.constants import JDM_OUTPUT_FILENAME  # noqa: E402
from app.services.rule_engine.service import build_jdm_from_matrix  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Parse args and regenerate the JDM artifact."""
    settings = RuleEngineSettings()
    parser = argparse.ArgumentParser(description="Generate the bank eligibility JDM.")
    parser.add_argument(
        "--matrix", type=Path, default=settings.matrix_path, help="Path to matrix .xlsx"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=settings.decisions_dir / JDM_OUTPUT_FILENAME,
        help="Output .jdm.json path",
    )
    args = parser.parse_args(argv)

    graph, row_count = build_jdm_from_matrix(args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"Wrote JDM ({row_count} rules) -> {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
