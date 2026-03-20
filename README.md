# pstack

个人维护的 Claude Code Skills 集合。封装常用工作流，提升日常开发效率。

## Skills 列表

| Skill | 说明 |
|-------|------|
| [think-clarify](skills/think-clarify/) | 深度思考重构工具。将散乱的想法打散、梳理关系、输出清晰的逻辑骨架。适用于头脑风暴整理、复杂问题拆解等场景 |
| [codex-collab](skills/codex-collab/) | Claude Code 与 OpenAI Codex CLI 协作。支持需求分析、代码原型获取、代码审查，通过双 AI 交叉验证提升代码质量 |

## 安装

将 skill 目录软链接或复制到 `~/.claude/skills/` 下即可使用：

```bash
# 软链接单个 skill
ln -s "$(pwd)/skills/think-clarify" ~/.claude/skills/think-clarify

# 或软链接全部
for skill in skills/*/; do
  ln -s "$(pwd)/$skill" ~/.claude/skills/"$(basename "$skill")"
done
```

## Skill 目录结构

每个 skill 遵循以下结构：

```
skills/<skill-name>/
├── SKILL.md              # skill 定义（必须）
├── scripts/              # 辅助脚本（可选）
└── references/           # 参考资料（可选）
```

- `SKILL.md` 包含 YAML frontmatter（name + description）和详细的工作流指令
- `scripts/` 放可执行脚本，供 SKILL.md 中通过 Bash 调用
- `references/` 放审查标准、模板等参考文档
