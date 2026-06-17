#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from lib.markdown_artifacts import meaningful_rows, read_text, table_after


def _split_items(value: str) -> list[str]:
    return [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]


def _evidence_refs(value: str) -> list[str]:
    normalized = value.replace("；", ";").replace("\n", ";")
    return [item.strip() for item in normalized.split(";") if item.strip()]


def validate(test_dir: Path) -> list[str]:
    errors: list[str] = []
    plan = read_text(test_dir / "测试方案.md") if (test_dir / "测试方案.md").exists() else ""
    execution = read_text(test_dir / "执行记录.md") if (test_dir / "执行记录.md").exists() else ""

    matrix_rows = meaningful_rows(table_after(plan, "接口 x 字段语义等价类矩阵"))
    execution_matrix_rows = meaningful_rows(table_after(execution, "接口 x 字段语义等价类矩阵执行状态"))
    executed_matrix_by_id = {row.get("矩阵单元 ID", "").strip(): row for row in execution_matrix_rows}
    for row in matrix_rows:
        matrix_id = row.get("矩阵单元 ID", "").strip()
        level = row.get("必测级别", "")
        case_id = row.get("关联用例 ID", "").strip()
        if "必测" in level and not case_id:
            errors.append(f"必测矩阵单元缺少关联用例: {matrix_id}")
        execution_row = executed_matrix_by_id.get(matrix_id)
        if "必测" in level and matrix_id and execution_row is None:
            errors.append(f"必测矩阵单元缺少执行回填: {matrix_id}")
        elif "必测" in level and execution_row is not None:
            status = execution_row.get("执行状态", "").strip()
            evidence = execution_row.get("证据路径", "").strip()
            if status != "已执行":
                errors.append(f"必测矩阵单元未执行: {matrix_id} 状态={status}")
            if not evidence:
                errors.append(f"必测矩阵单元缺少证据路径: {matrix_id}")

    scene_rows = meaningful_rows(table_after(plan, "场景 x 边界/异常覆盖矩阵"))
    execution_scene_rows = meaningful_rows(table_after(execution, "场景 x 边界/异常覆盖完整性"))
    executed_scene_by_id = {row.get("覆盖单元 ID", "").strip(): row for row in execution_scene_rows}
    for row in scene_rows:
        scene_id = row.get("覆盖单元 ID", "").strip()
        level = row.get("必测级别", "")
        execution_row = executed_scene_by_id.get(scene_id)
        if "必测" in level and scene_id and execution_row is None:
            errors.append(f"必测场景覆盖单元缺少执行回填: {scene_id}")
        elif "必测" in level and execution_row is not None:
            status = execution_row.get("执行状态", "").strip()
            evidence = execution_row.get("证据路径", "").strip()
            if status != "已执行":
                errors.append(f"必测场景覆盖单元未执行: {scene_id} 状态={status}")
            if not evidence:
                errors.append(f"必测场景覆盖单元缺少证据路径: {scene_id}")

    consistency_rows = meaningful_rows(table_after(execution, "跨接口一致性执行记录"))
    for row in consistency_rows:
        group = row.get("逻辑类似接口组", "")
        evidence = row.get("各接口证据路径", "")
        participants = _split_items(group)
        refs = _evidence_refs(evidence)
        if len(participants) > 1 and len(refs) < len(participants):
            errors.append(f"跨接口一致性缺少每个参与接口的独立证据: {row.get('一致性 ID', '')}")
        for participant in participants:
            name = participant.split()[0].rstrip(":：") if participant else ""
            if name and not any(name in ref for ref in refs):
                errors.append(f"跨接口一致性证据未标明参与接口: {row.get('一致性 ID', '')} {participant}")

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
