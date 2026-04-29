# 变更日志

本文件记录项目的重要变更。

本项目遵循语义化版本。

## [未发布]

### 新增

- 新增 `api-blackbox-test-reviewer` Skill，在 planner 和 executor 之间增加测试用例评审门禁。
- 评审由资深测试工程师、资深产品经理、资深软件工程师、安全工程师四个角色分别提出意见，再通过小组讨论形成最终结论。
- 新增 `tests/【需求】_YYYYMMDD/测试用例评审.md` 阶段交付物。
- reviewer 增加风险分级覆盖矩阵、需求追踪、可执行性 preflight、安全建模、Anti-Happy-Path 检测和量化判定依据。

### 变更

- 完整流程调整为 `planner -> reviewer -> executor -> reporter`。
- executor 必须在评审结果为通过或有条件通过后才执行；不通过或阻塞时退回 planner 完善。
- reviewer 的异常路径、安全评审和评分规则按接口风险等级适用，避免机械套用固定配额。
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
