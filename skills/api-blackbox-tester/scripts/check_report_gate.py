#!/usr/bin/env python3
"""Compatibility wrapper for pass-gate and lifecycle validation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(script: Path, test_dir: str) -> int:
    result = subprocess.run([sys.executable, str(script), test_dir], text=True)
    return result.returncode


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_report_gate.py <tests/需求目录>")
        return 2
    root = Path(__file__).resolve().parents[3]
    scripts = root / "scripts"
    pass_code = run(scripts / "validate_pass_gate.py", sys.argv[1])
    lifecycle_code = run(scripts / "validate_lifecycle.py", sys.argv[1])
    return 1 if pass_code or lifecycle_code else 0


if __name__ == "__main__":
    raise SystemExit(main())
