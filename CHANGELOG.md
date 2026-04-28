# 变更日志

本文件记录项目的重要变更。

本项目遵循语义化版本。

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
