# pstack 项目规范

本项目是 Claude Code Skills 的维护仓库。

## Skill 结构规范

每个 skill 位于 `skills/<skill-name>/` 下，必须包含 `SKILL.md`。

### SKILL.md 格式要求

1. 以 YAML frontmatter 开头，包含 `name` 和 `description` 字段
2. `description` 要覆盖触发关键词，让 Claude Code 能准确匹配意图
3. 正文定义完整的工作流程、参数说明和示例
4. 脚本引用使用相对于 SKILL.md 所在目录的路径

### 辅助文件

- 可执行脚本 → `scripts/`
- 参考文档、模板 → `references/`
- 不要在 skill 目录下放与该 skill 无关的文件

## 改进 Skill

使用 `document-skills:skill-creator` skill 来创建、修改和评估 skill：

- 新建 skill：描述需求，用 skill-creator 生成初始结构
- 改进 skill：用 skill-creator 的 eval 能力测试触发准确度和输出质量
- 优化 description：确保触发词覆盖用户的自然表达方式

## 质量要点

- SKILL.md 指令应具体、可操作，避免空泛描述
- 示例 prompt 要贴近真实使用场景
- 脚本需要有清晰的参数说明和错误处理
- 每个 skill 职责单一，不要把不相关的功能塞进同一个 skill
