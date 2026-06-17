#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECKS = [
    "validate_structure.py",
    "validate_route_analysis.py",
    "validate_content.py",
    "validate_review_gate.py",
    "validate_traceability.py",
    "validate_evidence.py",
    "validate_pass_gate.py",
    "validate_lifecycle.py",
]


def load_validate(script: str):
    path = ROOT / script
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_all.py <tests/需求目录>")
        return 2
    test_dir = Path(sys.argv[1])
    failed = False
    for script in CHECKS:
        validate = load_validate(script)
        errors = validate(test_dir)
        label = script.removeprefix("validate_").removesuffix(".py")
        if errors:
            failed = True
            print(f"{label}: FAIL")
            for error in errors:
                print(f"- {error}")
        else:
            print(f"{label}: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
