# 贡献指南

感谢你改进 `api-blackbox-tester`。本项目是由多个 Codex Skill 组成的插件，大多数贡献会影响提示词行为、阶段交付契约或文档。

## 贡献范围

适合提交的改进包括：

- 更清晰的测试方案规则。
- 更完整的执行证据要求。
- 更准确的报告和覆盖率规则。
- 更安全的数据库验证指导。
- 文档修正。
- `.codex-plugin/plugin.json` 或 `agents/openai.yaml` 元数据修正。

除非能直接服务接口黑盒测试流程，否则不建议加入宽泛且无关的自动化能力。

## 开发原则

- 每个 Skill 保持单一阶段职责。
- 不要把具体测试规则堆到统一编排 Skill 中。
- 保持 planner、executor、reporter 之间的输出兼容。
- 测试用例和编排链路使用稳定 ID。
- 结论必须基于证据，而不是假设。
- 环境、凭证或数据缺失时，明确标记为阻塞。
- 用户可感知行为变化时同步更新文档。

## 文件说明

| 路径 | 作用 |
| --- | --- |
| `.codex-plugin/plugin.json` | 插件元数据、版本、界面描述和 Skill 目录。 |
| `skills/api-blackbox-tester/SKILL.md` | 流程编排和阶段选择。 |
| `skills/api-blackbox-test-planner/SKILL.md` | 测试方案要求和输出格式。 |
| `skills/api-blackbox-test-executor/SKILL.md` | 执行验证和证据记录规则。 |
| `skills/api-blackbox-test-reporter/SKILL.md` | 报告和覆盖率规则。 |
| `skills/*/agents/openai.yaml` | Codex 界面元数据和默认提示词。 |
| `docs/` | 用户和维护者文档。 |

## 合并请求检查清单

- 变更过的 Skill front matter 仍然准确。
- 对应 `agents/openai.yaml` 仍然反映 Skill 行为。
- 行为变化已经更新 README 或 docs。
- `CHANGELOG.md` 已记录用户可见变化。
- planner -> executor -> reporter 的交付链路仍然清晰。

## 文风要求

- 使用直接、具体的表达。
- 下游阶段需要消费的结构化内容优先使用表格。
- 明确写出安全要求。
- 没有执行证据时，不得声称测试通过。
