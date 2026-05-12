# 变更日志

本文件记录项目的重要变更。

本项目遵循语义化版本。

## [0.4.0] - 2026-05-12

### 新增

- planner 增加影响范围初判，要求记录直接影响、潜在扩散影响、证据来源和高/中/低置信度。
- reviewer 增加独立评审模板 `references/review-template.md`，集中维护评分模型、Must Pass、Reject If 和输出结构。
- executor 增加执行记录模板 `references/execution-template.md`，集中维护请求记录、矩阵回填、跨接口一致性、编排链路、DB 验证和清理状态格式。
- tester 增加共享闭环状态文件 `references/loop-state.md`，统一闭环优先级、状态机和最新 artifact 判定算法。

### 变更

- 非通过报告闭环调整为自动进入 `开发修复 -> 最小验证/单测 -> 自动编译/重启最多 3 次 -> executor 复验 -> reporter 再评估`，仅在自动编译/重启失败或缺少权限时进入 `FIXED_WAIT_RESTART`。
- executor 发现测试范围缺口时，不再直接执行原方案；关键范围缺口回 planner 完整补方案，非关键补证项回 reviewer 评审。
- reporter 和 tester 共用闭环状态定义，避免 artifact 判定和状态机逻辑分叉。
- reviewer 主 Skill 精简为流程和规则摘要，详细评分与模板下沉到 reference，降低维护成本。

## [0.3.0] - 2026-04-29

### 新增

- 新增 `api-blackbox-test-reviewer` Skill，在 planner 和 executor 之间增加测试用例评审门禁。
- 评审由资深测试工程师、资深产品经理、资深软件工程师、安全工程师四个角色分别提出意见，再通过小组讨论形成最终结论。
- 新增 `tests/【需求】_YYYYMMDD/测试用例评审.md` 阶段交付物。
- reviewer 增加风险分级覆盖矩阵、需求追踪、可执行性 preflight、安全建模、Anti-Happy-Path 检测和量化判定依据。
- reporter 增加非通过结论的根因分析、解决建议、责任阶段和复验计划要求。

### 变更

- 完整流程调整为 `planner -> reviewer -> executor -> reporter`。
- executor 必须在评审结果为通过或有条件通过后才执行；不通过或阻塞时退回 planner 完善。
- reviewer 的异常路径、安全评审和评分规则按接口风险等级适用，避免机械套用固定配额。
- 测试报告结论不是通过时，完整流程必须回到开发修复或解除阻塞，并在修复后执行接口复验和报告再评估。
- README、使用指南、架构说明、发布检查和插件提示词同步四阶段流程。

## [0.2.3] - 2026-04-28

### 变更

- 明确三个测试阶段必须写入对应 Markdown 文件。
- 默认输出目录调整为 `tests/【需求】_YYYYMMDD/`。
- 约定 planner 写入 `测试方案.md`，executor 写入 `执行记录.md`，reporter 写入 `测试报告.md`。
- 更新 README、使用指南、架构说明、发布流程和插件默认提示词。

## [0.2.2] - 2026-04-27

### 新增

- 新增项目文档：README、使用指南、架构说明、发布流程、贡献指南、行为准则、安全策略和许可证。

### 既有能力

- 通过 `api-blackbox-tester` 编排接口黑盒测试流程。
- 通过 `api-blackbox-test-planner` 输出编码前测试方案。
- 通过 `api-blackbox-test-executor` 执行真实请求和数据库验证。
- 通过 `api-blackbox-test-reporter` 输出基于证据的覆盖率报告。
