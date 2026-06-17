#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from lib.markdown_artifacts import find_conclusion, has_section, read_text


def validate(test_dir: Path) -> list[str]:
    report_path = test_dir / "测试报告.md"
    if not report_path.exists():
        return ["缺少测试报告.md"]
    report = read_text(report_path)
    conclusion = find_conclusion(report)
    if conclusion == "通过":
        return []
    errors: list[str] = []
    required = ["失败项", "开发修复与复验计划", "闭环执行状态"]
    if conclusion == "阻塞":
        required.append("阻塞解除计划")
    for section in required:
        if not has_section(report, section):
            errors.append(f"非通过报告缺少闭环章节: {section}")
    if "复验范围" not in report:
        errors.append("非通过报告缺少复验范围")
    return errors


def main() -> int:
    errors = validate(Path(sys.argv[1]))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
