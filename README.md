# api-blackbox-tester

> 用于阶段化接口黑盒测试的 Codex 插件：编码前出方案，编码后执行真实 HTTP/gRPC 验证，最后生成基于证据的测试报告。

[![许可证：MIT](https://img.shields.io/badge/%E8%AE%B8%E5%8F%AF%E8%AF%81-MIT-yellow.svg)](LICENSE)
[![版本](https://img.shields.io/badge/version-0.2.3-0F766E.svg)](.codex-plugin/plugin.json)

## 项目定位

接口变更经常能通过单元测试，却仍然破坏客户端契约、数据库副作用或多接口业务链路。`api-blackbox-tester` 为 Codex 提供一套可重复的接口黑盒测试流程，把测试方案、执行证据和最终报告串联起来。

它适合用于需要验证兼容性、边界条件、安全输入、数据库状态或跨多个接口编排链路的接口需求。

## 功能组成

本仓库包含 4 个 Codex Skill：

| Skill | 作用 |
| --- | --- |
| `api-blackbox-tester` | 统一入口，根据用户意图选择并串联三个测试阶段。 |
| `api-blackbox-test-planner` | 输出编码前或执行前的接口黑盒测试方案，并写入 `测试方案.md`。 |
| `api-blackbox-test-executor` | 执行真实接口请求，使用 [`db-mcp`](https://github.com/xiu86/db-mcp) 准备或校验数据，并写入 `执行记录.md`。 |
| `api-blackbox-test-reporter` | 汇总方案和执行证据，输出覆盖率、风险和发布建议，并写入 `测试报告.md`。 |

## 快速开始

将本插件安装或复制到支持本地插件和 Skill 的 Codex 环境中，然后在 Codex 会话中调用：

```text
使用 $api-blackbox-tester 为当前接口需求编排完整黑盒测试流程。
```

如果只需要某个阶段：

```text
使用 $api-blackbox-test-planner 输出接口黑盒测试范围、用例、数据计划和编排链路。
使用 $api-blackbox-test-executor 按已有测试用例执行真实接口请求并用 db-mcp 校验。
使用 $api-blackbox-test-reporter 根据测试方案和执行证据输出覆盖率评估和测试报告。
```

## 标准流程

1. 使用 `api-blackbox-test-planner` 分析需求和项目上下文。
2. 审核生成的测试用例、数据计划、边界测试、安全测试和接口编排链路。
3. 实现完成后，使用 `api-blackbox-test-executor` 执行真实 HTTP 或 gRPC 请求。
4. 将 planner 输出和 executor 证据提供给 `api-blackbox-test-reporter`。
5. 根据最终报告判断变更是通过、阻塞、部分通过还是失败。

## 文件输出规范

三个阶段必须生成对应 Markdown 文件，默认保存在项目根目录：

```text
tests/【需求】_YYYYMMDD/测试方案.md
tests/【需求】_YYYYMMDD/执行记录.md
tests/【需求】_YYYYMMDD/测试报告.md
```

- `【需求】` 使用用户需求的简短标题；未提供时由 Skill 根据需求内容提炼。
- `YYYYMMDD` 使用执行当天日期，例如 `20260428`。
- 同一需求的 planner、executor、reporter 必须复用同一个目录。
- 每个阶段完成后必须在回复中说明已写入的文件路径。

## 使用要求

- 支持 Skill/plugin 的 Codex 环境。
- 用于规划阶段的项目源码或 API 文档。
- 用于执行阶段的可访问测试环境。
- 受保护接口所需的凭证或 token。
- 需要数据库准备或校验时，配置 [`db-mcp`](https://github.com/xiu86/db-mcp)。
- HTTP 接口通常使用 `curl`，gRPC 接口通常使用 `grpcurl`。

执行阶段不得在未确认安全的环境中运行破坏性测试，也不得默认修改生产或疑似生产数据。

## 仓库结构

```text
.
├── .codex-plugin/plugin.json
├── skills/
│   ├── api-blackbox-tester/
│   ├── api-blackbox-test-planner/
│   ├── api-blackbox-test-executor/
│   └── api-blackbox-test-reporter/
└── docs/
    ├── architecture.md
    ├── release.md
    └── usage.md
```

## 文档

- [使用指南](docs/usage.md)
- [架构说明](docs/architecture.md)
- [发布流程](docs/release.md)
- [贡献指南](CONTRIBUTING.md)
- [安全策略](SECURITY.md)
- [变更日志](CHANGELOG.md)

## 开发说明

当前项目以文档和配置为主，没有应用构建步骤。

修改 Skill 时请检查：

1. `SKILL.md` 的 front matter 中 `name` 和 `description` 是否准确。
2. 对应 `agents/openai.yaml` 的默认提示词和依赖声明是否同步。
3. 面向用户的行为变化是否已经更新 README 或 docs。
4. planner -> executor -> reporter 的交付物是否仍能衔接。
5. 三个阶段是否仍按 `tests/【需求】_YYYYMMDD/阶段.md` 规则写入文件。

## 许可证

本项目使用 MIT 许可证，详见 [LICENSE](LICENSE)。
