#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from lib.markdown_artifacts import find_conclusion, parse_report_counts, read_text, score


def validate(test_dir: Path) -> list[str]:
    report_path = test_dir / "测试报告.md"
    if not report_path.exists():
        return ["缺少测试报告.md"]
    report = read_text(report_path)
    if find_conclusion(report) != "通过":
        return []
    errors: list[str] = []
    counts = parse_report_counts(report)
    for key in ["failed", "skipped", "blocked", "not_executed"]:
        if counts.get(key, 0) > 0:
            errors.append(f"报告结论为通过但 {key} 数量为 {counts[key]}")
    current_score = score(report)
    if current_score is None:
        errors.append("报告结论为通过但缺少综合可信度/可信度评分")
    elif current_score < 85:
        errors.append(f"报告结论为通过但可信度评分低于 85: {current_score}")
    deny_patterns = [
        ("必测[^|\\n]*\\|\\s*(跳过|阻塞|未执行)\\s*\\|", "存在未完成必测单元"),
        ("证据完整性[^\\n]*(缺失|部分完整)", "存在证据完整性不足"),
        ("只有\\s*HTTP\\s*200|仅\\s*HTTP\\s*200", "存在只有 HTTP 200 无业务断言风险"),
        ("兼容性.*证据不足.*通过", "兼容性证据不足却判定通过"),
    ]
    for pattern, message in deny_patterns:
        if re.search(pattern, report, re.IGNORECASE):
            errors.append(message)
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
