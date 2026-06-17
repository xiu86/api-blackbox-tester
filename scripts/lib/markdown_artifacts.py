from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


EMPTY_VALUES = {"", "-", "无", "N/A", "n/a", "不适用"}


@dataclass
class MarkdownTable:
    title: str
    headers: list[str]
    rows: list[dict[str, str]]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_section(text: str, title: str) -> bool:
    return bool(re.search(rf"(^|\n)#+\s*{re.escape(title)}\s*(\n|$)", text)) or f"**{title}**" in text


def section_text(text: str, title: str) -> str:
    patterns = [
        rf"(^|\n)#+\s*{re.escape(title)}\s*\n",
        rf"(^|\n)\*\*{re.escape(title)}\*\*\s*\n",
    ]
    starts: list[int] = []
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            starts.append(match.end())
    if not starts:
        return ""
    start = min(starts)
    rest = text[start:]
    next_heading = re.search(r"\n(?:#+\s+|\*\*[^*\n]+\*\*\s*\n)", rest)
    return rest[: next_heading.start()] if next_heading else rest


def _split_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def _is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?[\s:\-|]+\|?\s*", line))


def table_after(text: str, title: str) -> MarkdownTable | None:
    body = section_text(text, title)
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        if index + 1 >= len(lines) or not _is_separator(lines[index + 1]):
            continue
        headers = _split_row(line)
        rows: list[dict[str, str]] = []
        for row_line in lines[index + 2 :]:
            if not row_line.strip().startswith("|"):
                break
            cells = _split_row(row_line)
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            rows.append(dict(zip(headers, cells)))
        return MarkdownTable(title=title, headers=headers, rows=rows)
    return None


def meaningful_rows(table: MarkdownTable | None) -> list[dict[str, str]]:
    if table is None:
        return []
    result = []
    for row in table.rows:
        values = [value.strip() for value in row.values()]
        if any(value not in EMPTY_VALUES for value in values):
            result.append(row)
    return result


def find_conclusion(text: str) -> str:
    for pattern in [
        r"最终结论[:：]\s*(通过|失败|部分通过|阻塞)",
        r"最终测试结论[:：]\s*(通过|失败|部分通过|阻塞)",
        r"本次需求测试是否通过[:：]\s*(通过|失败|部分通过|阻塞|是|否)",
    ]:
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            return "通过" if value == "是" else ("失败" if value == "否" else value)
    return ""


def parse_report_counts(report: str) -> dict[str, int]:
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


def score(report: str) -> int | None:
    match = re.search(r"(?:综合可信度|总分|可信度评分)[:：]\s*(\d+)", report)
    return int(match.group(1)) if match else None
