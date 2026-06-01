#!/usr/bin/env python3
"""Decide whether a test report is allowed to conclude PASS."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def conclusion(report: str) -> str:
    for pattern in [
        r"最终结论[:：]\s*(通过|失败|部分通过|阻塞)",
        r"最终测试结论[:：]\s*(通过|失败|部分通过|阻塞)",
    ]:
        match = re.search(pattern, report)
        if match:
            return match.group(1)
    return ""


def score(report: str) -> int | None:
    match = re.search(r"(?:总分|可信度评分)[:：]\s*(\d+)", report)
    return int(match.group(1)) if match else None


def gate(test_dir: Path) -> list[str]:
    errors: list[str] = []
    report_path = test_dir / "测试报告.md"
    if not report_path.exists():
        return ["缺少测试报告.md"]

    report = read(report_path)
    final = conclusion(report)
    if final != "通过":
        return []

    validator = Path(__file__).with_name("validate_test_artifacts.py")
    result = subprocess.run(
        [sys.executable, str(validator), str(test_dir)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        errors.append("artifact 校验失败，报告不得结论为通过")
        errors.extend(f"  {line}" for line in result.stdout.splitlines() if line.strip())

    low_score = score(report)
    if low_score is None:
        errors.append("报告结论为通过但缺少测试结果可信度评分")
    elif low_score < 85:
        errors.append(f"报告结论为通过但测试结果可信度评分为 {low_score}，低于 85")

    deny_patterns = [
        (r"未通过用例数\s*\|\s*[1-9]\d*", "存在未通过用例"),
        (r"阻塞用例数\s*\|\s*[1-9]\d*", "存在阻塞用例"),
        (r"未执行用例数\s*\|\s*[1-9]\d*", "存在未执行用例"),
        (r"必测[^|\n]*\|\s*(跳过|阻塞|未执行)\s*\|", "存在未完成必测单元"),
        (r"只有\s*Happy Path|仅\s*Happy Path", "存在仅 Happy Path 风险描述"),
        (r"DB\s*验证.*(缺失|无|未执行)", "存在 DB 验证缺失风险"),
    ]
    for pattern, message in deny_patterns:
        if re.search(pattern, report, re.IGNORECASE):
            errors.append(message)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("test_dir", type=Path, help="tests/【需求】_YYYYMMDD directory")
    args = parser.parse_args()

    errors = gate(args.test_dir)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
