#!/usr/bin/env python3
"""Compatibility wrapper for the contract-driven artifact validator."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_test_artifacts.py <tests/需求目录>")
        return 2
    root = Path(__file__).resolve().parents[3]
    validator = root / "scripts" / "validate_all.py"
    result = subprocess.run([sys.executable, str(validator), sys.argv[1]], text=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
