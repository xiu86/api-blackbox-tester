from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_all.py"
FIXTURES = ROOT / "tests" / "fixtures"


def run_fixture(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIXTURES / name)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_pass_full_fixture_passes() -> None:
    result = run_fixture("pass_full")
    assert result.returncode == 0, result.stdout


def test_structured_route_analysis_fixture_passes() -> None:
    result = run_fixture("pass_structured_route_analysis")
    assert result.returncode == 0, result.stdout


def test_invalid_fixtures_fail() -> None:
    invalid = [
        "fail_missing_structured_route_analysis",
        "fail_structured_route_not_in_impact",
        "fail_missing_change_impact_list",
        "fail_missing_role_review",
        "fail_required_matrix_skipped",
        "fail_only_http_200_no_assertions",
        "fail_no_db_for_write_api",
        "fail_no_db_for_implicit_post",
        "fail_cross_interface_missing_independent_evidence",
        "fail_non_pass_without_closure_plan",
    ]
    for name in invalid:
        result = run_fixture(name)
        assert result.returncode != 0, f"{name} unexpectedly passed\n{result.stdout}"
