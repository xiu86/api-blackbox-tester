#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from lib.markdown_artifacts import read_text


def validate(test_dir: Path) -> list[str]:
    path = test_dir / "测试用例评审.md"
    if not path.exists():
        return ["缺少测试用例评审.md"]
    text = read_text(path)
    errors: list[str] = []
    result = ""
    match = re.search(r"结果[:：]\s*(通过|有条件通过|不通过|阻塞)", text)
    if match:
        result = match.group(1)
    if not result:
        errors.append("最终评审结果缺少明确结果")
    if result in {"通过", "有条件通过"}:
        risky_patterns = [
            "未完成变更影响接口评估",
            "核心场景 Happy Path 偏置未补充",
            "受保护接口安全评估缺失",
            "核心用例缺少证据路径",
            "DB 断言缺失",
        ]
        for pattern in risky_patterns:
            if pattern in text:
                errors.append(f"评审结论为 {result} 但存在未解决门禁问题: {pattern}")
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
