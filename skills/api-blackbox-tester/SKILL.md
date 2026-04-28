---
name: api-blackbox-tester
description: 作为接口黑盒测试插件的统一编排入口使用。当用户需要完整接口黑盒测试流程，或不确定应该做编码前测试方案、编码后接口执行还是最终覆盖率报告时使用本技能。本技能负责选择并串联 api-blackbox-test-planner、api-blackbox-test-executor、api-blackbox-test-reporter 三个阶段 Skill。
---

# 接口黑盒测试编排入口

## 目标

这个 Skill 只负责阶段判断和流程编排，不承载具体测试细节。根据用户意图选择一个或多个阶段 Skill：

- `api-blackbox-test-planner`：编码前分析，输出测试范围、兼容性验证、测试用例、接口编排链路和测试数据计划。
- `api-blackbox-test-executor`：编码后执行，使用 db-mcp 准备或获取数据，真实请求接口，执行编排链路，记录 curl 和 DB 验证。
- `api-blackbox-test-reporter`：最终总结，汇总计划和执行证据，评估覆盖率、通过结论、失败原因和剩余风险，输出报告。

## 阶段选择

- 用户说“编码前、先分析、先出方案、测试范围、测试用例、数据准备、接口编排设计”：使用 `api-blackbox-test-planner`。
- 用户说“编码完成后、执行测试、真实请求、curl、db-mcp 校验、按用例跑、接口编排执行”：使用 `api-blackbox-test-executor`。
- 用户说“总结、覆盖率、是否通过、测试报告、失败原因、发布建议”：使用 `api-blackbox-test-reporter`。
- 用户说“完整黑盒测试、全流程、从方案到报告”：按 `planner -> executor -> reporter` 顺序执行。
- 用户已有某阶段输出时，复用已有输出作为下一阶段输入，不重复生成无关内容。

## 编排规则

- 三个阶段的交付物必须可衔接：planner 的用例 ID、链路 ID 和数据计划要被 executor 沿用；executor 的 curl 记录、响应、DB 验证要被 reporter 汇总。
- 三个阶段必须写入对应 Markdown 文件，默认保存在当前项目根目录下的 `tests/【需求】_YYYYMMDD/` 目录中：
  - planner 阶段：`tests/【需求】_YYYYMMDD/测试方案.md`
  - executor 阶段：`tests/【需求】_YYYYMMDD/执行记录.md`
  - reporter 阶段：`tests/【需求】_YYYYMMDD/测试报告.md`
- `【需求】` 应取用户需求的简短标题；如果用户未提供标题，应根据需求内容提炼 8 到 20 个中文字符。文件名中的 `/`、空格、冒号、引号等不适合作为路径的字符应替换为 `_`。
- `YYYYMMDD` 使用执行当天日期，例如 `20260428`。如果用户明确指定日期，以用户指定日期为准。
- 每个阶段完成后，除在对话中给出摘要外，必须说明已写入的文件路径。无法写文件时必须明确标记为阻塞，并给出原因。
- 如果缺少执行环境、凭证、base URL 或安全测试库确认，执行阶段应先阻塞并说明缺口，不要跳到报告结论。
- 复杂需求默认询问或判断是否需要接口编排；如果不需要，planner 必须说明原因。
- 最终报告不能只基于计划输出，必须基于 executor 的真实请求和 DB 验证证据；没有执行证据时，只能输出计划覆盖评估或阻塞结论。

## 快速输出

当用户只要求“怎么用”或“下一步怎么做”时，直接给出应使用的阶段 Skill 和示例 prompt。

示例：

```text
使用 $api-blackbox-test-planner 为当前需求输出接口黑盒测试方案。
使用 $api-blackbox-test-executor 按已有测试用例执行真实接口请求并用 db-mcp 校验。
使用 $api-blackbox-test-reporter 根据测试方案和执行证据输出覆盖率评估和测试报告。
```
