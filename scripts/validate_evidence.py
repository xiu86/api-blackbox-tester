#!/usr/bin/env python3
from __future__ import annotations

import sys
import re
from pathlib import Path

from lib.markdown_artifacts import EMPTY_VALUES, meaningful_rows, read_text, table_after


WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _request_method(request: str) -> str:
    upper = request.upper()
    match = re.search(r"(?:-X|--REQUEST)\s+([A-Z]+)", upper)
    if match:
        return match.group(1)
    if any(token in upper for token in [" -D ", " --DATA", "--DATA-RAW", "--DATA-BINARY", "--FORM", " -F "]):
        return "POST"
    grpc_match = re.search(r"\b(CREATE|UPDATE|DELETE|REMOVE|PATCH|UPSERT)[A-Z0-9_./-]*", upper)
    if grpc_match:
        return grpc_match.group(1)
    return "GET"


def validate(test_dir: Path) -> list[str]:
    execution_path = test_dir / "执行记录.md"
    if not execution_path.exists():
        return ["缺少执行记录.md"]
    text = read_text(execution_path)
    errors: list[str] = []

    assertion_rows = meaningful_rows(table_after(text, "断言执行记录"))
    if not assertion_rows:
        errors.append("缺少断言执行记录有效数据")
    for row in assertion_rows:
        if row.get("结果", "").strip() != "通过":
            errors.append(f"断言未通过或缺失: {row.get('断言ID', '')}")
        if row.get("证据路径", "").strip() in EMPTY_VALUES:
            errors.append(f"断言缺少证据路径: {row.get('断言ID', '')}")

    packet_rows = meaningful_rows(table_after(text, "证据包"))
    if not packet_rows:
        errors.append("缺少证据包有效数据")
    for row in packet_rows:
        if row.get("请求证据", "").strip() in EMPTY_VALUES:
            errors.append(f"证据包缺少请求证据: {row.get('证据包ID', '')}")
        if row.get("响应断言", "").strip() in EMPTY_VALUES:
            errors.append(f"证据包缺少响应断言: {row.get('证据包ID', '')}")
        if row.get("证据完整性", "").strip() not in {"完整", "不适用"}:
            errors.append(f"证据包完整性不足: {row.get('证据包ID', '')}")

    request_rows = meaningful_rows(table_after(text, "单接口请求记录"))
    write_case_ids = set()
    for row in request_rows:
        request = row.get("curl 请求", "")
        if _request_method(request) in WRITE_METHODS or _request_method(request) in {"CREATE", "UPDATE", "REMOVE", "UPSERT"}:
            write_case_ids.add(row.get("用例 ID", "").strip())
    db_rows = meaningful_rows(table_after(text, "DB 验证记录"))
    db_case_refs = " ".join(row.get("用例/链路ID", "") for row in db_rows)
    for case_id in write_case_ids:
        if case_id and case_id not in db_case_refs:
            errors.append(f"写接口用例缺少 DB/副作用验证: {case_id}")

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
