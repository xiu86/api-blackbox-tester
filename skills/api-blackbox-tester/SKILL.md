---
name: api-blackbox-tester
description: 作为接口黑盒测试插件的统一编排入口使用。当用户需要完整接口黑盒测试流程，或不确定应该做编码前测试方案、测试用例评审、编码后接口执行还是最终覆盖率报告时使用本技能。本技能负责选择并串联 api-blackbox-test-planner、api-blackbox-test-reviewer、api-blackbox-test-executor、api-blackbox-test-reporter 四个阶段 Skill。
---

# 接口黑盒测试编排入口

## 目标

这个 Skill 只负责阶段判断和流程编排，不承载具体测试细节。根据用户意图选择一个或多个阶段 Skill：

- `api-blackbox-test-planner`：编码前分析，输出测试范围、兼容性验证、测试用例、接口编排链路和测试数据计划。
- `api-blackbox-test-reviewer`：执行前测试用例评审，由资深测试工程师、资深产品经理、资深软件工程师、安全工程师四个角色评审 planner 输出；通过或有条件通过后才允许 executor 执行，不通过则退回 planner 完善。
- `api-blackbox-test-executor`：编码后执行，使用 db-mcp 准备或获取数据，真实请求接口，执行编排链路，记录 curl 和 DB 验证。
- `api-blackbox-test-reporter`：最终总结，汇总计划和执行证据，评估覆盖率、通过结论、失败原因、根因分析、解决建议和剩余风险，输出报告。

## 阶段选择

- 用户说“编码前、先分析、先出方案、测试范围、测试用例、数据准备、接口编排设计”：使用 `api-blackbox-test-planner`。
- 用户说“评审测试用例、用例审核、执行前把关、测试方案是否完善、四角色评审”：使用 `api-blackbox-test-reviewer`。
- 用户说“编码完成后、执行测试、真实请求、curl、db-mcp 校验、按用例跑、接口编排执行”：使用 `api-blackbox-test-executor`。
- 用户说“总结、覆盖率、是否通过、测试报告、失败原因、发布建议”：使用 `api-blackbox-test-reporter`。
- 用户说“完整黑盒测试、全流程、从方案到报告”：按 `planner -> reviewer -> executor -> reporter` 顺序执行；如果 reporter 结论不是 `通过`，必须进入 `开发修复 -> executor 复验 -> reporter 再评估` 闭环，直到报告结论为 `通过` 或明确阻塞无法继续。
- 用户已有某阶段输出时，复用已有输出作为下一阶段输入，不重复生成无关内容。

## 编排规则

- 四个阶段的交付物必须可衔接：planner 的用例 ID、链路 ID 和数据计划要被 reviewer 评审；reviewer 的最终结果决定是否允许 executor 执行；executor 的 curl 记录、响应、DB 验证要被 reporter 汇总。
- 四个阶段必须写入对应 Markdown 文件，默认保存在当前项目根目录下的 `tests/【需求】_YYYYMMDD/` 目录中：
  - planner 阶段：`tests/【需求】_YYYYMMDD/测试方案.md`
  - reviewer 阶段：`tests/【需求】_YYYYMMDD/测试用例评审.md`
  - executor 阶段：`tests/【需求】_YYYYMMDD/执行记录.md`
  - reporter 阶段：`tests/【需求】_YYYYMMDD/测试报告.md`
- `【需求】` 应取用户需求的简短标题；如果用户未提供标题，应根据需求内容提炼 8 到 20 个中文字符。文件名中的 `/`、空格、冒号、引号等不适合作为路径的字符应替换为 `_`。
- `YYYYMMDD` 使用执行当天日期，例如 `20260428`。如果用户明确指定日期，以用户指定日期为准。
- 每个阶段完成后，除在对话中给出摘要外，必须说明已写入的文件路径。无法写文件时必须明确标记为阻塞，并给出原因。
- reviewer 阶段最终结果为 `通过` 或 `有条件通过` 时，才允许进入 executor；结果为 `不通过` 或 `阻塞` 时，必须退回 planner 完善测试方案或补充输入后重新评审。
- executor 阶段开始前必须读取或确认 `测试用例评审.md`；如果没有评审记录，或评审结果不是 `通过` / `有条件通过`，应阻塞并说明需要先完成评审。
- 如果缺少执行环境、凭证、base URL 或安全测试库确认，执行阶段应先阻塞并说明缺口，不要跳到报告结论。
- 复杂需求默认询问或判断是否需要接口编排；如果不需要，planner 必须说明原因。
- 最终报告不能只基于计划输出，必须基于 executor 的真实请求和 DB 验证证据；没有执行证据时，只能输出计划覆盖评估或阻塞结论。
- reporter 结论为 `失败`、`部分通过` 或 `阻塞` 时，全流程不得视为完成；必须把所有未通过、部分通过、阻塞和剩余风险整理成开发修复输入，包含问题根因分析、解决建议、复验范围和再次执行的用例/链路 ID。
- 开发修复完成后，必须回到 executor 执行 HTTP/gRPC 接口复验，并由 reporter 基于新的复验证据重新评估测试报告；循环直到最终结论为 `通过`，或因环境、凭证、依赖等不可解决因素明确标记为阻塞。

## 快速输出

当用户只要求“怎么用”或“下一步怎么做”时，直接给出应使用的阶段 Skill 和示例 prompt。

示例：

```text
使用 $api-blackbox-test-planner 为当前需求输出接口黑盒测试方案。
使用 $api-blackbox-test-reviewer 对测试方案和测试用例做执行前评审。
使用 $api-blackbox-test-executor 在评审通过后按已有测试用例执行真实接口请求并用 db-mcp 校验。
使用 $api-blackbox-test-reporter 根据测试方案、评审结论和执行证据输出覆盖率评估和测试报告。
如果测试报告结论不是通过，先按报告中的根因分析和解决建议回到开发修复，再执行接口复验和报告再评估。
```
