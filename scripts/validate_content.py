#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from lib.markdown_artifacts import EMPTY_VALUES, meaningful_rows, parse_report_counts, read_text, table_after


def validate(test_dir: Path) -> list[str]:
    errors: list[str] = []
    plan = read_text(test_dir / "测试方案.md") if (test_dir / "测试方案.md").exists() else ""
    review = read_text(test_dir / "测试用例评审.md") if (test_dir / "测试用例评审.md").exists() else ""
    report = read_text(test_dir / "测试报告.md") if (test_dir / "测试报告.md").exists() else ""

    impact_table = table_after(plan, "变更代码影响接口清单")
    for row in meaningful_rows(impact_table):
        included = row.get("是否纳入测试范围", "").strip()
        coverage = row.get("覆盖方式", "").strip()
        if included == "否" and coverage in EMPTY_VALUES:
            errors.append("变更代码影响接口清单存在未纳入测试范围但缺少豁免/覆盖方式的接口")
        if included in {"是", "部分"} and coverage in EMPTY_VALUES:
            errors.append("变更代码影响接口清单存在已纳入接口但缺少覆盖方式")

    role_table = table_after(review, "多角色评审结论矩阵")
    required_roles = {"资深测试工程师", "资深产品经理", "资深软件工程师", "安全工程师", "测试证据审计员"}
    seen_roles = {row.get("角色", "").strip() for row in meaningful_rows(role_table)}
    missing_roles = sorted(required_roles - seen_roles)
    if missing_roles:
        errors.append(f"多角色评审缺少角色: {', '.join(missing_roles)}")
    for row in meaningful_rows(role_table):
        blocker = row.get("阻塞项", "").strip()
        result = row.get("结论", "").strip()
        if blocker not in EMPTY_VALUES and result in {"通过", "有条件通过"}:
            errors.append(f"角色 {row.get('角色', '')} 存在阻塞项但结论为 {result}")

    counts = parse_report_counts(report)
    required = {"planned", "executed", "passed", "failed", "skipped", "blocked", "not_executed"}
    missing = sorted(required - counts.keys())
    if missing:
        errors.append(f"测试报告执行汇总缺少统计字段: {', '.join(missing)}")
    elif counts["planned"] != counts["passed"] + counts["failed"] + counts["skipped"] + counts["blocked"] + counts["not_executed"]:
        errors.append("测试报告用例统计不守恒: 计划数 != 通过+未通过+跳过+阻塞+未执行")
    elif counts["executed"] != counts["passed"] + counts["failed"]:
        errors.append("测试报告执行统计不守恒: 已执行 != 通过+未通过")

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
