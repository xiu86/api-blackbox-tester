#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from lib.markdown_artifacts import EMPTY_VALUES, meaningful_rows, read_text, table_after


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _route_text(route: Any) -> str:
    if isinstance(route, str):
        return route
    if isinstance(route, dict):
        method = str(route.get("method") or route.get("http_method") or "").strip()
        path = str(route.get("path") or route.get("route") or route.get("name") or "").strip()
        return f"{method} {path}".strip()
    return ""


def _routes_from_json(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    routes: list[str] = []
    for key in ["direct_routes", "indirect_routes", "similar_routes"]:
        for item in data.get(key, []) if isinstance(data, dict) else []:
            route = _route_text(item)
            if route:
                routes.append(route)
    return routes


def validate(test_dir: Path) -> list[str]:
    plan_path = test_dir / "测试方案.md"
    if not plan_path.exists():
        return ["缺少测试方案.md"]

    plan = read_text(plan_path)
    errors: list[str] = []

    analysis_rows = meaningful_rows(table_after(plan, "结构化路由影响分析"))
    if not analysis_rows:
        return ["测试方案.md 缺少结构化路由影响分析有效数据"]

    available_rows = []
    fallback_rows = []
    for row in analysis_rows:
        available = row.get("是否可用", "").strip()
        output = row.get("结构化输出", "").strip()
        fallback = row.get("兜底方式", "").strip()
        confidence = row.get("置信度", "").strip()

        if available in {"是", "可用", "已使用"}:
            available_rows.append(row)
            if output in EMPTY_VALUES:
                errors.append("结构化路由分析工具可用但缺少结构化输出位置")
        else:
            fallback_rows.append(row)
            if fallback in EMPTY_VALUES:
                errors.append("结构化路由分析工具不可用时必须说明兜底方式")
            if confidence in EMPTY_VALUES:
                errors.append("结构化路由分析工具不可用时必须标明兜底分析置信度")
            if fallback not in EMPTY_VALUES and not any(
                token in fallback
                for token in ["代码 diff", "路由", "API", "代码搜索", "文档", "Agent", "人工"]
            ):
                errors.append("兜底方式必须包含代码 diff、路由、API 文档、代码搜索、项目文档、Agent 推理或人工补证之一")

    impact_table = table_after(plan, "变更代码影响接口清单")
    impact_text = _norm(" ".join(" ".join(row.values()) for row in meaningful_rows(impact_table)))

    for row in available_rows:
        output = row.get("结构化输出", "").strip()
        if not output.endswith(".json"):
            continue
        output_path = test_dir / output
        if not output_path.exists():
            errors.append(f"结构化路由分析输出不存在: {output}")
            continue
        try:
            routes = _routes_from_json(output_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"结构化路由分析输出无法解析: {output} ({exc})")
            continue
        for route in routes:
            normalized = _norm(route)
            if normalized and normalized not in impact_text:
                errors.append(f"结构化路由分析发现的接口未进入变更代码影响接口清单: {route}")

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
