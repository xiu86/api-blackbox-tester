#!/usr/bin/env python3
"""Validate api-blackbox-tester Markdown artifacts.

This is a conservative gate. It catches missing sections, obvious missing
required execution evidence, and summary count conflicts before a report is
allowed to claim success.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FILES = ["测试方案.md", "测试用例评审.md", "执行记录.md", "测试报告.md"]

PLAN_SECTIONS = [
    "业务场景拆解",
    "场景 x 边界/异常覆盖矩阵",
    "接口 x 字段语义等价类矩阵",
    "测试用例",
    "边界测试",
    "安全测试",
]

REVIEW_SECTIONS = [
    "业务场景拆解评审",
    "场景 x 边界/异常覆盖矩阵评审",
    "接口 x 字段语义等价类矩阵评审",
    "Anti-Happy-Path Gate",
    "最终评审结果",
]

EXECUTION_SECTIONS = [
    "单接口请求记录",
    "接口 x 字段语义等价类矩阵执行状态",
    "DB 验证记录",
]

REPORT_SECTIONS = [
    "测试执行汇总",
    "接口 x 字段语义等价类矩阵执行完整性",
    "场景 x 边界/异常覆盖完整性",
    "覆盖率评估",
    "测试结果可信度评分",
    "最终总结",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_section(text: str, title: str) -> bool:
    return bool(re.search(rf"(^|\n)#+\s*{re.escape(title)}\s*(\n|$)", text)) or f"**{title}**" in text


def table_rows_after(text: str, title: str) -> list[str]:
    marker_positions = [m.end() for m in re.finditer(re.escape(title), text)]
    if not marker_positions:
        return []
    rest = text[marker_positions[0] :]
    rows: list[str] = []
    in_table = False
    for line in rest.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            if not re.fullmatch(r"\|[\s:\-|\u2014]+\|", stripped):
                rows.append(stripped)
        elif in_table and stripped:
            break
    return rows[1:] if rows and "---" in rows[0] else rows


def parse_summary_counts(report: str) -> dict[str, int]:
    labels = {
        "计划用例总数": "planned",
        "已执行用例数": "executed",
        "通过用例数": "passed",
        "未通过用例数": "failed",
        "跳过用例数": "skipped",
        "阻塞用例数": "blocked",
        "未执行用例数": "not_executed",
    }
    counts: dict[str, int] = {}
    for cn, key in labels.items():
        match = re.search(rf"\|\s*{re.escape(cn)}\s*\|\s*(\d+)\s*\|", report)
        if match:
            counts[key] = int(match.group(1))
    return counts


def find_final_conclusion(report: str) -> str:
    patterns = [
        r"最终结论[:：]\s*(通过|失败|部分通过|阻塞)",
        r"最终测试结论[:：]\s*(通过|失败|部分通过|阻塞)",
        r"本次需求测试是否通过[:：]\s*(通过|失败|部分通过|阻塞|是|否)",
    ]
    for pattern in patterns:
        match = re.search(pattern, report)
        if match:
            value = match.group(1)
            return "通过" if value == "是" else ("失败" if value == "否" else value)
    return ""


def validate(test_dir: Path) -> list[str]:
    errors: list[str] = []
    files = {name: test_dir / name for name in REQUIRED_FILES}

    for name, path in files.items():
        if not path.exists():
            errors.append(f"缺少阶段文件: {name}")

    texts = {name: read(path) for name, path in files.items() if path.exists()}

    for section in PLAN_SECTIONS:
        if "测试方案.md" in texts and not has_section(texts["测试方案.md"], section):
            errors.append(f"测试方案缺少章节: {section}")

    for section in REVIEW_SECTIONS:
        if "测试用例评审.md" in texts and not has_section(texts["测试用例评审.md"], section):
            errors.append(f"测试用例评审缺少章节: {section}")

    for section in EXECUTION_SECTIONS:
        if "执行记录.md" in texts and not has_section(texts["执行记录.md"], section):
            errors.append(f"执行记录缺少章节: {section}")

    for section in REPORT_SECTIONS:
        if "测试报告.md" in texts and not has_section(texts["测试报告.md"], section):
            errors.append(f"测试报告缺少章节: {section}")

    report = texts.get("测试报告.md", "")
    execution = texts.get("执行记录.md", "")
    if report:
        counts = parse_summary_counts(report)
        required = {"planned", "executed", "passed", "failed", "skipped", "blocked", "not_executed"}
        missing = sorted(required - counts.keys())
        if missing:
            errors.append(f"测试报告执行汇总缺少统计字段: {', '.join(missing)}")
        elif counts["planned"] != counts["passed"] + counts["failed"] + counts["skipped"] + counts["blocked"] + counts["not_executed"]:
            errors.append("测试报告用例统计不守恒: 计划数 != 通过+未通过+跳过+阻塞+未执行")
        elif counts["executed"] != counts["passed"] + counts["failed"]:
            errors.append("测试报告执行统计不守恒: 已执行 != 通过+未通过")

        conclusion = find_final_conclusion(report)
        if conclusion == "通过":
            for key in ("failed", "skipped", "blocked", "not_executed"):
                if counts.get(key, 0) > 0:
                    errors.append(f"报告结论为通过但 {key} 数量为 {counts[key]}")
            if re.search(r"\|\s*[^|\n]*必测[^|\n]*\|\s*(跳过|阻塞|未执行)\s*\|", report):
                errors.append("报告结论为通过但存在未执行/跳过/阻塞的必测单元")
            if "测试结果可信度评分" in report:
                score_match = re.search(r"(?:总分|可信度评分)[:：]\s*(\d+)", report)
                if score_match and int(score_match.group(1)) < 85:
                    errors.append("报告结论为通过但测试结果可信度评分低于 85")

    if execution:
        for section in ["接口 x 字段语义等价类矩阵执行状态", "场景 x 边界/异常覆盖完整性"]:
            rows = table_rows_after(execution, section)
            for row in rows:
                if "必测" in row and "已执行" in row and ("|  |" in row or "||" in row):
                    errors.append(f"{section} 存在已执行必测单元但字段为空: {row}")
                if "必测" in row and ("跳过" in row or "阻塞" in row):
                    errors.append(f"{section} 存在未完成必测单元: {row}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("test_dir", type=Path, help="tests/【需求】_YYYYMMDD directory")
    args = parser.parse_args()

    errors = validate(args.test_dir)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
