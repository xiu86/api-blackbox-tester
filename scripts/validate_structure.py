#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from lib.markdown_artifacts import has_section, meaningful_rows, read_text, table_after


ROOT = Path(__file__).resolve().parents[1]
FALLBACK_SCHEMA = {
    "测试方案.md": {
        "结构化路由影响分析": {"min_rows": 1, "columns": ["分析方式", "工具或来源", "是否可用", "结构化输出", "置信度", "兜底方式"]},
        "变更代码影响接口清单": {"min_rows": 1, "columns": ["变更文件/符号", "直接影响接口", "是否纳入测试范围", "覆盖方式"]},
        "测试范围": {},
        "影响范围初判": {"min_rows": 1},
        "业务场景拆解": {"min_rows": 1},
        "风险驱动用例生成矩阵": {"min_rows": 1},
        "接口 x 字段语义等价类矩阵": {"min_rows": 1},
        "场景 x 边界/异常覆盖矩阵": {"min_rows": 1},
        "测试用例": {"min_rows": 1},
        "断言计划": {"min_rows": 1},
        "测试数据计划": {},
        "跨接口一致性测试": {},
        "接口编排/集成测试": {},
    },
    "测试用例评审.md": {
        "结构化路由影响分析评审": {"min_rows": 1},
        "变更代码影响接口清单评审": {"min_rows": 1},
        "多角色评审结论矩阵": {"min_rows": 5, "columns": ["角色", "结论", "阻塞项", "executor 关注项"]},
        "角色冲突与裁决": {},
        "业务场景拆解评审": {},
        "场景 x 边界/异常覆盖矩阵评审": {},
        "接口 x 字段语义等价类矩阵评审": {},
        "Anti-Happy-Path Gate": {},
        "最终评审结果": {},
    },
    "执行记录.md": {
        "影响范围覆盖核对": {},
        "单接口请求记录": {"min_rows": 1},
        "断言执行记录": {"min_rows": 1},
        "证据包": {"min_rows": 1, "columns": ["证据包ID", "用例ID", "请求证据", "响应断言", "DB断言", "证据完整性"]},
        "接口 x 字段语义等价类矩阵执行状态": {"min_rows": 1},
        "场景 x 边界/异常覆盖完整性": {"min_rows": 1},
        "跨接口一致性执行记录": {},
        "接口编排链路执行记录": {},
        "DB 验证记录": {},
        "阻塞前自动补救记录": {},
    },
    "测试报告.md": {
        "测试执行汇总": {},
        "编码前测试方案摘要": {},
        "多角色评审摘要": {},
        "证据完整性评估": {},
        "接口 x 字段语义等价类矩阵执行完整性": {},
        "场景 x 边界/异常覆盖完整性": {},
        "覆盖率评估": {},
        "覆盖与证据可信度评分": {},
        "最终总结": {},
    },
}


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value.isdigit():
        return int(value)
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def _load_contract_schema() -> dict[str, dict[str, dict[str, Any]]]:
    path = ROOT / "contracts" / "artifact_schema.yaml"
    if not path.exists():
        return FALLBACK_SCHEMA

    schema: dict[str, dict[str, dict[str, Any]]] = {}
    current_file: str | None = None
    current_section: str | None = None
    current_list: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if indent == 2 and stripped.endswith(":"):
            current_file = stripped[:-1].strip('"')
            schema[current_file] = {}
            current_section = None
            current_list = None
        elif indent == 6 and stripped.endswith(":") and current_file:
            current_section = stripped[:-1].strip('"')
            schema[current_file][current_section] = {}
            current_list = None
        elif indent == 8 and ":" in stripped and current_file and current_section:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                schema[current_file][current_section][key] = _parse_scalar(value)
                current_list = None
            else:
                schema[current_file][current_section][key] = []
                current_list = key
        elif indent == 10 and stripped.startswith("- ") and current_file and current_section and current_list:
            schema[current_file][current_section][current_list].append(_parse_scalar(stripped[2:]))

    return schema or FALLBACK_SCHEMA


def validate(test_dir: Path) -> list[str]:
    errors: list[str] = []
    schema = _load_contract_schema()
    for filename, sections in schema.items():
        path = test_dir / filename
        if not path.exists():
            errors.append(f"缺少阶段文件: {filename}")
            continue
        text = read_text(path)
        for section, spec in sections.items():
            if not has_section(text, section):
                errors.append(f"{filename} 缺少章节: {section}")
                continue
            if spec.get("min_rows") is not None or spec.get("columns"):
                table = table_after(text, section)
                if table is None:
                    errors.append(f"{filename} 章节缺少表格: {section}")
                    continue
                for column in spec.get("columns", []):
                    if column not in table.headers:
                        errors.append(f"{filename} {section} 缺少列: {column}")
                min_rows = spec.get("min_rows")
                if min_rows is not None and len(meaningful_rows(table)) < min_rows:
                    errors.append(f"{filename} {section} 有效数据行少于 {min_rows}")
    return errors


def main() -> int:
    test_dir = Path(sys.argv[1])
    errors = validate(test_dir)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
