#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_REQUIRED_TERMS = [
    "结构化路由影响分析",
    "变更代码影响接口清单",
    "风险驱动用例生成矩阵",
    "断言计划",
    "多角色评审",
    "测试证据审计员",
    "证据包",
    "覆盖可信度",
    "证据可信度",
    "综合可信度",
    "非通过闭环",
]
FILES = {
    ROOT / "README.md": GLOBAL_REQUIRED_TERMS,
    ROOT / "docs" / "usage.md": GLOBAL_REQUIRED_TERMS,
    ROOT / "docs" / "architecture.md": GLOBAL_REQUIRED_TERMS,
    ROOT / "docs" / "release.md": GLOBAL_REQUIRED_TERMS,
    ROOT / ".codex-plugin" / "plugin.json": GLOBAL_REQUIRED_TERMS,
    ROOT / "skills" / "api-blackbox-tester" / "SKILL.md": GLOBAL_REQUIRED_TERMS,
    ROOT / "skills" / "api-blackbox-tester" / "agents" / "openai.yaml": GLOBAL_REQUIRED_TERMS,
    ROOT / "skills" / "api-blackbox-tester" / "references" / "artifact-contract.md": GLOBAL_REQUIRED_TERMS,
    ROOT / "skills" / "api-blackbox-test-planner" / "SKILL.md": [
        "结构化路由影响分析",
        "变更代码影响接口清单",
        "风险驱动用例生成矩阵",
        "断言计划",
        "证据采集计划",
    ],
    ROOT / "skills" / "api-blackbox-test-reviewer" / "SKILL.md": [
        "结构化路由影响分析",
        "变更代码影响接口清单",
        "多角色评审",
        "测试证据审计员",
        "断言计划",
        "证据包",
    ],
    ROOT / "skills" / "api-blackbox-test-executor" / "SKILL.md": [
        "结构化路由分析工具",
        "多角色评审",
        "断言计划",
        "证据采集计划",
        "证据包",
        "DB/副作用",
    ],
    ROOT / "skills" / "api-blackbox-test-reporter" / "SKILL.md": [
        "多角色评审",
        "证据包",
        "覆盖可信度",
        "证据可信度",
        "综合可信度",
    ],
}
FORBIDDEN_PATTERNS = [
    "四角色",
    "reporter，reporter",
    "scripts/validate_test_artifacts.py 检查本契约",
]


def validate() -> list[str]:
    errors: list[str] = []
    for path, required_terms in FILES.items():
        if not path.exists():
            errors.append(f"缺少文档/入口文件: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in required_terms:
            if term not in text:
                errors.append(f"{path.relative_to(ROOT)} 缺少关键术语: {term}")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                errors.append(f"{path.relative_to(ROOT)} 存在旧口径: {pattern}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
