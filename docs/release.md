# 发布流程

当前仓库没有构建流水线。一次发布代表插件元数据、Skill 文件和文档的一个版本化更新。

## 版本规则

使用语义化版本：

- `MAJOR`：不兼容的 Skill 行为变化，或公开 Skill 名称变更。
- `MINOR`：新增能力、输出章节或兼容性的流程变化。
- `PATCH`：文字修正、问题修复、元数据修正或文档更新。

当前版本记录在 `.codex-plugin/plugin.json`。

## 发布检查清单

1. 更新 `.codex-plugin/plugin.json` 中的版本号。
2. 更新 `CHANGELOG.md`。
3. 检查所有变更过的 `SKILL.md` front matter 是否准确。
4. 检查所有变更过的 `agents/openai.yaml` 中的提示词和依赖声明是否一致。
5. 验证三阶段交付物仍然可以衔接：
   - planner 输出包含用例 ID 和链路 ID。
   - executor 输出包含请求证据和数据库证据。
   - reporter 输出能引用 planner 范围和 executor 证据。
6. 验证三个阶段都明确写入对应文件：
   - `tests/【需求】_YYYYMMDD/测试方案.md`
   - `tests/【需求】_YYYYMMDD/执行记录.md`
   - `tests/【需求】_YYYYMMDD/测试报告.md`
7. 确认 README 和 docs 已描述新的行为。
8. 按目标 Codex 插件分发方式打包或发布。

## 手工验证场景

使用一个小型接口变更依次运行：

```text
使用 $api-blackbox-test-planner 输出测试方案。
使用 $api-blackbox-test-executor 按测试方案执行真实请求。
使用 $api-blackbox-test-reporter 根据方案和证据输出报告。
```

如果 reporter 无法将 executor 证据关联回 planner 的用例 ID 或链路 ID，则不应发布。

如果任一阶段只在对话中输出结果、没有写入对应 Markdown 文件，也不应发布。
