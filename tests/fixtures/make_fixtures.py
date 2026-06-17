from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent


PLAN = """# 测试方案

**结构化路由影响分析**
| 分析方式 | 工具或来源 | 是否可用 | 结构化输出 | 置信度 | 兜底方式 |
| --- | --- | --- | --- | --- | --- |
| 结构化路由分析工具优先 | 当前项目未提供可用结构化路由分析工具 | 否 | 不适用 | 中 | 代码 diff + 路由定义 + API 文档 + Agent 推理 |

**变更代码影响接口清单**
| 变更文件/符号 | 变更类型 | 直接影响接口 | 间接受影响接口/逻辑类似接口 | 调用方/消费者/任务 | 影响依据 | 是否纳入测试范围 | 覆盖方式 | 置信度 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| api/user.go:updateUser | 修改 | POST /api/users | GET /api/users/{id} | Web 用户中心 | diff+route | 是 | API-001/MATRIX-001/SCENE-001 | 高 |

**测试范围**
- 范围内：POST /api/users、GET /api/users/{id}
- 范围外：无
- 假设：测试环境可访问

**影响范围初判**
| 影响ID | 来源 | 证据来源 | 置信度 | 影响类型 | 影响对象 | 风险等级 | 测试覆盖方式 | 关联用例/矩阵/链路 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-001 | 代码变更 | api/user.go | 高 | 接口契约 | POST /api/users | 高 | API-001 | MATRIX-001 |

**业务场景拆解**
| 场景ID | 需求/业务规则来源 | 业务场景 | 用户/角色 | 前置状态/数据 | 主流程 | 分支/异常/边界点 | 风险等级 | 关联接口/链路 | 关联用例/矩阵 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCN-001 | REQ-001 | 创建用户 | 管理员 | token 有效 | 提交用户资料 | 缺失 name、重复提交 | 高 | POST /api/users | API-001/MATRIX-001 |

**风险驱动用例生成矩阵**
| 场景ID | 风险类型 | 是否适用 | 用例ID | 不适用依据 | 风险等级 |
| --- | --- | --- | --- | --- | --- |
| SCN-001 | 正常路径 | 是 | API-001 | - | 高 |

**接口 x 字段语义等价类矩阵**
| 矩阵单元 ID | 接口 | 字段 | 字段语义 | 等价类/取值类别 | 代表值或构造方式 | 必测级别 | 关联用例 ID | 预期响应/错误 | DB/副作用预期 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MATRIX-001 | POST /api/users | name | 用户名 | 有效字符串 | codex_api_test_user | 必测 | API-001 | 201 | users 新增 |

**场景 x 边界/异常覆盖矩阵**
| 覆盖单元 ID | 场景ID | 覆盖类型 | 输入/状态组合 | 边界值或反例 | 必测级别 | 关联用例 ID | 预期响应/错误 | DB/副作用预期 | 豁免依据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCENE-001 | SCN-001 | 正常 | 合法 name | codex_api_test_user | 必测 | API-001 | 201 | users 新增 | - |

**测试用例**
| ID | 场景 | 前置数据 | 请求 | 预期响应 | 预期数据库状态 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 创建用户 | 管理员 token | POST /api/users | 201 | users 存在 |

**断言计划**
| 用例ID | 断言ID | 断言类型 | 预期 | 证据要求 |
| --- | --- | --- | --- | --- |
| API-001 | ASSERT-001 | 状态码 | 201 | curl 响应 |

**测试数据计划**
| 数据用途 | 表/集合 | 必填字段 | 构造或获取方式 | 清理方式 |
| --- | --- | --- | --- | --- |
| 创建用户 | users | name | codex_api_test_user | 逻辑删除 |

**跨接口一致性测试**
| 一致性 ID | 逻辑类似接口组 | 字段/业务规则 | 等价类覆盖 | 对比方式 | 关联用例 ID | 预期一致性 |
| --- | --- | --- | --- | --- | --- | --- |
| CONS-001 | POST /api/users, GET /api/users/{id} | name | 有效字符串 | 创建后查询 | API-001 | name 一致 |

**接口编排/集成测试**
| 链路 ID | 场景 | 接口顺序/依赖 | 是否包含非本次变更接口 | 数据提取与传递 | 预期结果 | DB 验证 |
| --- | --- | --- | --- | --- | --- | --- |
| FLOW-001 | 创建后查询 | POST -> GET | 是 | id | 查询到用户 | users 存在 |
"""


REVIEW = """# 测试用例评审

**结构化路由影响分析评审**
| 分析方式 | 工具或来源 | 是否可用 | 结构化输出 | 兜底方式 | 置信度 | 评审结论 | 缺口或退回项 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 结构化路由分析工具优先 | 当前项目未提供可用结构化路由分析工具 | 否 | 不适用 | 代码 diff + 路由定义 + API 文档 + Agent 推理 | 中 | 通过 | 无 |

**变更代码影响接口清单评审**
| 变更文件/符号 | 变更类型 | 直接影响接口 | 间接受影响接口/逻辑类似接口 | 调用方/消费者/任务 | 是否纳入测试范围 | 覆盖用例/矩阵/链路 | 评审结论 | 缺口或豁免依据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| api/user.go:updateUser | 修改 | POST /api/users | GET /api/users/{id} | Web 用户中心 | 是 | API-001/MATRIX-001/FLOW-001 | 通过 | 无 |

**多角色评审结论矩阵**
| 角色 | 评审领域 | 结论 | 阻塞项 | 有条件通过项 | 必须退回 planner 项 | executor 关注项 |
| --- | --- | --- | --- | --- | --- | --- |
| 资深测试工程师 | 场景/边界 | 通过 | 无 | 无 | 无 | 执行 API-001 |
| 资深产品经理 | 需求/兼容 | 通过 | 无 | 无 | 无 | 校验 name 语义 |
| 资深软件工程师 | 变更影响/契约 | 通过 | 无 | 无 | 无 | 校验 DB |
| 安全工程师 | 鉴权/权限 | 通过 | 无 | 无 | 无 | 使用管理员 token |
| 测试证据审计员 | 证据/断言 | 通过 | 无 | 无 | 无 | 记录证据包 |

**角色冲突与裁决**
| 议题 | 分歧角色 | 分歧点 | 裁决结论 | 处理方式 | 责任阶段 |
| --- | --- | --- | --- | --- | --- |
| 无 | 无 | 无 | 无 | 无 | 无 |

**业务场景拆解评审**
| 场景ID | 评审结论 |
| --- | --- |
| SCN-001 | 通过 |

**场景 x 边界/异常覆盖矩阵评审**
| 覆盖单元 ID | 评审结论 |
| --- | --- |
| SCENE-001 | 通过 |

**接口 x 字段语义等价类矩阵评审**
| 矩阵单元 ID | 评审结论 |
| --- | --- |
| MATRIX-001 | 通过 |

**Anti-Happy-Path Gate**
| 接口/链路 | 风险等级 | 正常用例数 | 异常用例数 | 安全用例数 | 异常占比 | 是否达标 | 豁免理由 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| POST /api/users | 高 | 1 | 1 | 1 | 50% | 是 | 无 |

**最终评审结果**
- 结果：通过
- 是否允许进入 executor：是
"""


EXECUTION = """# 执行记录

**影响范围覆盖核对**
| 影响ID | 影响对象 | 覆盖状态 | 覆盖用例/矩阵/链路 | 缺口 | 处理方式 |
| --- | --- | --- | --- | --- | --- |
| IMP-001 | POST /api/users | 已覆盖 | API-001/MATRIX-001 | 无 | 执行 |

**单接口请求记录**
| 用例 ID | curl 请求 | 请求参数 | 返回数据 | 是否通过 | 不通过原因 |
| --- | --- | --- | --- | --- | --- |
| API-001 | `curl -sS -X POST http://127.0.0.1/api/users -d '{\"name\":\"codex_api_test_user\"}'` | body.name | 201 {id:1,name:codex_api_test_user} | 通过 | 无 |

**断言执行记录**
| 用例ID | 断言ID | 断言类型 | 预期 | 实际 | 结果 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| API-001 | ASSERT-001 | 状态码 | 201 | 201 | 通过 | 执行记录.md#单接口请求记录 |

**证据包**
| 证据包ID | 用例ID | 请求证据 | 响应断言 | DB断言 | 副作用断言 | 环境证据 | 清理证据 | 证据完整性 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EVI-001 | API-001 | 执行记录.md#单接口请求记录 | ASSERT-001 | DB-001 | 审计日志不适用 | test | CLEAN-001 | 完整 |

**接口 x 字段语义等价类矩阵执行状态**
| 矩阵单元 ID | 接口 | 字段 | 等价类/取值类别 | 必测级别 | 关联用例 ID | 执行状态 | 证据路径 | 失败/跳过/阻塞原因 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MATRIX-001 | POST /api/users | name | 有效字符串 | 必测 | API-001 | 已执行 | EVI-001 | 无 |

**场景 x 边界/异常覆盖完整性**
| 覆盖单元 ID | 场景ID | 覆盖类型 | 输入/状态组合 | 边界值或反例 | 必测级别 | 关联用例 ID | 执行状态 | 证据路径 | 失败/跳过/阻塞原因 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCENE-001 | SCN-001 | 正常 | 合法 name | codex_api_test_user | 必测 | API-001 | 已执行 | EVI-001 | 无 |

**跨接口一致性执行记录**
| 一致性 ID | 逻辑类似接口组 | 字段/业务规则 | 等价类 | 各接口证据路径 | 对比结果 | 是否通过 | 失败/跳过/阻塞原因 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CONS-001 | POST /api/users, GET /api/users/{id} | name | 有效字符串 | POST: 执行记录.md#单接口请求记录; GET: 执行记录.md#单接口请求记录 | 一致 | 通过 | 无 |

**接口编排链路执行记录**
| 链路 ID | 步骤 | curl 请求 | 提取数据 | 传递到 | 步骤结果 | 失败原因 |
| --- | --- | --- | --- | --- | --- | --- |
| FLOW-001 | 1 | POST /api/users | id=1 | GET path | 通过 | 无 |

**DB 验证记录**
| 验证ID | 用例/链路ID | 查询或写入验证 | 预期结果 | 实际结果 | 结论 |
| --- | --- | --- | --- | --- | --- |
| DB-001 | API-001 | select * from users where name='codex_api_test_user' | 1 行 | 1 行 | 通过 |

**阻塞前自动补救记录**
| 阻塞ID | 阻塞类型 | 自动补救动作 | 命令或工具 | 结果 | 证据路径 | 是否解除 | 最小缺口 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 无 | 无 | 无 | 无 | 无 | 无 | 是 | 无 |
"""


REPORT = """# 测试报告

**测试执行汇总**
| 指标 | 数量 | 说明 |
| --- | --- | --- |
| 计划用例总数 | 1 | planner/reviewer 确认 |
| 已执行用例数 | 1 | 有真实请求 |
| 通过用例数 | 1 | 响应和 DB 均通过 |
| 未通过用例数 | 0 | 无 |
| 跳过用例数 | 0 | 无 |
| 阻塞用例数 | 0 | 无 |
| 未执行用例数 | 0 | 无 |

**编码前测试方案摘要**
| 类别 | 摘要 | 备注 |
| --- | --- | --- |
| 变更代码影响接口清单 | POST /api/users 已覆盖 | API-001 |

**多角色评审摘要**
| 角色 | 结论 | 说明 |
| --- | --- | --- |
| 资深测试工程师 | 通过 | 无阻塞 |
| 资深产品经理 | 通过 | 无阻塞 |
| 资深软件工程师 | 通过 | 无阻塞 |
| 安全工程师 | 通过 | 无阻塞 |
| 测试证据审计员 | 通过 | 无阻塞 |

**证据完整性评估**
| 证据包ID | 用例ID | 证据完整性 | 结论影响 |
| --- | --- | --- | --- |
| EVI-001 | API-001 | 完整 | 不影响 |

**接口 x 字段语义等价类矩阵执行完整性**
| 矩阵单元 ID | 接口 | 字段 | 等价类/取值类别 | 必测级别 | 关联用例 ID | 执行状态 | 证据路径 | 失败/跳过/阻塞原因 | 报告结论影响 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MATRIX-001 | POST /api/users | name | 有效字符串 | 必测 | API-001 | 已执行 | EVI-001 | 无 | 不影响 |

**场景 x 边界/异常覆盖完整性**
| 覆盖单元 ID | 场景ID | 覆盖类型 | 输入/状态组合 | 边界值或反例 | 必测级别 | 关联用例 ID | 执行状态 | 证据路径 | 失败/跳过/阻塞原因 | 报告结论影响 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCENE-001 | SCN-001 | 正常 | 合法 name | codex_api_test_user | 必测 | API-001 | 已执行 | EVI-001 | 无 | 不影响 |

**覆盖率评估**
| 覆盖维度 | 已覆盖 | 总数 | 覆盖率 | 未覆盖项和原因 |
| --- | --- | --- | --- | --- |
| 需求覆盖率 | 1 | 1 | 100% | 无 |

**覆盖与证据可信度评分**
- 覆盖可信度：90/100
- 证据可信度：90/100
- 综合可信度：90
- 可信度等级：高
- 是否允许作为发布门禁依据：是

**最终总结**
- 最终结论：通过
- 本次需求测试是否通过：通过
- 通过依据：真实请求、断言、DB 验证、证据包完整
- 复验范围：API-001
"""


def write_fixture(name: str, plan: str = PLAN, review: str = REVIEW, execution: str = EXECUTION, report: str = REPORT) -> None:
    directory = ROOT / name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "测试方案.md").write_text(plan, encoding="utf-8")
    (directory / "测试用例评审.md").write_text(review, encoding="utf-8")
    (directory / "执行记录.md").write_text(execution, encoding="utf-8")
    (directory / "测试报告.md").write_text(report, encoding="utf-8")


def main() -> None:
    for child in ROOT.iterdir():
        if child.is_dir() and child.name != "__pycache__":
            shutil.rmtree(child)

    write_fixture("pass_full")
    write_fixture(
        "fail_missing_structured_route_analysis",
        plan=PLAN.replace("**结构化路由影响分析**", "**缺失结构化分析**", 1),
    )
    structured_plan = PLAN.replace(
        "| 结构化路由分析工具优先 | 当前项目未提供可用结构化路由分析工具 | 否 | 不适用 | 中 | 代码 diff + 路由定义 + API 文档 + Agent 推理 |",
        "| 结构化路由分析工具优先 | 项目可用结构化路由分析工具 | 是 | 代码影响分析.json | 高 | 不适用 |",
    )
    write_fixture("pass_structured_route_analysis", plan=structured_plan)
    (ROOT / "pass_structured_route_analysis" / "代码影响分析.json").write_text(
        '{"direct_routes":[{"method":"POST","path":"/api/users"}],"indirect_routes":[{"method":"GET","path":"/api/users/{id}"}],"similar_routes":[]}',
        encoding="utf-8",
    )
    write_fixture("fail_structured_route_not_in_impact", plan=structured_plan)
    (ROOT / "fail_structured_route_not_in_impact" / "代码影响分析.json").write_text(
        '{"direct_routes":[{"method":"DELETE","path":"/api/users/{id}"}],"indirect_routes":[],"similar_routes":[]}',
        encoding="utf-8",
    )
    write_fixture("fail_missing_change_impact_list", plan=PLAN.replace("**变更代码影响接口清单**", "**缺失清单**", 1))
    write_fixture("fail_missing_role_review", review=REVIEW.replace("| 测试证据审计员 | 证据/断言 | 通过 | 无 | 无 | 无 | 记录证据包 |\n", ""))
    write_fixture("fail_required_matrix_skipped", execution=EXECUTION.replace("| MATRIX-001 | POST /api/users | name | 有效字符串 | 必测 | API-001 | 已执行 | EVI-001 | 无 |", "| MATRIX-001 | POST /api/users | name | 有效字符串 | 必测 | API-001 | 跳过 |  | 未执行 |"))
    write_fixture("fail_only_http_200_no_assertions", execution=EXECUTION.replace("**断言执行记录**", "**断言执行记录**\n| 用例ID | 断言ID | 断言类型 | 预期 | 实际 | 结果 | 证据路径 |\n| --- | --- | --- | --- | --- | --- | --- |\n", 1).replace("| API-001 | ASSERT-001 | 状态码 | 201 | 201 | 通过 | 执行记录.md#单接口请求记录 |\n", ""), report=REPORT.replace("- 通过依据：真实请求、断言、DB 验证、证据包完整", "- 通过依据：仅 HTTP 200"))
    write_fixture("fail_no_db_for_write_api", execution=EXECUTION.replace("| DB-001 | API-001 | select * from users where name='codex_api_test_user' | 1 行 | 1 行 | 通过 |", "| 无 | 无 | 无 | 无 | 无 | 无 |"))
    write_fixture(
        "fail_no_db_for_implicit_post",
        execution=EXECUTION
        .replace("-X POST ", "")
        .replace("| DB-001 | API-001 | select * from users where name='codex_api_test_user' | 1 行 | 1 行 | 通过 |", "| 无 | 无 | 无 | 无 | 无 | 无 |"),
    )
    write_fixture(
        "fail_cross_interface_missing_independent_evidence",
        execution=EXECUTION.replace(
            "POST: 执行记录.md#单接口请求记录; GET: 执行记录.md#单接口请求记录",
            "POST: 执行记录.md#单接口请求记录",
        ),
    )
    non_pass_report = REPORT.replace("- 最终结论：通过", "- 最终结论：失败").replace("- 本次需求测试是否通过：通过", "- 本次需求测试是否通过：失败")
    write_fixture("fail_non_pass_without_closure_plan", report=non_pass_report)


if __name__ == "__main__":
    main()
