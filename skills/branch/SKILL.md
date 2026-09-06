---
name: branch
description: |
  创建 git 分支。按照“类型/简短英文描述”规范从当前分支或指定基线创建新分支。
  支持从用户描述推断分支名，或分析未提交改动自动生成。
  当用户说"创建分支"、"新建 branch"、"切个分支"、"开分支"、"建个分支"、
  "create branch"、"new branch"时使用此 skill。
---

# Branch - 创建 Git 分支

默认按照 `<type>/<short-english-description>` 规范推断新分支名；用户明确指定的名称优先。

## 分支类型

| type       | 适用场景                         |
| ---------- | -------------------------------- |
| `feature`  | 新功能、新模块                   |
| `fix`      | 修复已知 bug                     |
| `hotfix`   | 线上紧急修复                     |
| `refactor` | 重构，不改变外部行为             |
| `chore`    | 构建、CI、依赖更新等杂务         |
| `docs`     | 文档新增或修改                   |

## 默认命名约束

以下格式用于 agent 推断名称。用户明确给定名称时，以该名称为准，但必须通过 `git check-ref-format --branch <name>` 校验且不能覆盖已有分支；不要仅为符合默认格式再次要求用户改名。

- 格式：`<type>/<kebab-case-description>`
- description 使用英文，kebab-case，最多 5 个单词
- 总长度（含 type/）不超过 50 字符

## 工作流程

### 第一步：检查环境

运行 `git status` 和 `git branch --show-current`，确认：

- 当前分支名
- 是否有未提交的改动（uncommitted changes）

基线优先采用用户指定的分支或 commit，否则默认当前 HEAD 并告知；不要仅因当前分支不是 main 就询问是否切回 main。先验证基线可解析、目标分支名合法且不存在。基线无法确定、名称冲突或 Git 操作进行中时，只询问具体缺口，不覆盖或重置现有分支。

### 第二步：推断分支名

根据输入来源选择模式：

**模式 A — 用户给出描述**：从用户的需求描述中推断 type 和 description。

**模式 B — 分析未提交改动**：如果用户没有给出描述且有未提交改动，运行 `git diff` 和 `git diff --cached` 分析改动内容，推断 type 和 description。

如果信息不足以推断，主动询问用户要做什么。

### 第三步：复用授权或确认推断名称

用户已给出合法分支名并要求创建时，直接使用，不重复确认。由 agent 推断名称时，展示基线和建议名称，请求一次确认；已有明确确认则直接继续。没有答复不视为批准。

> 将从 `<base>` 创建 `feature/user-export-module`，请确认名称或给出调整。

### 第四步：创建分支

1. 通常执行 `git switch -c <branch-name>`；指定其他基线时使用 `git switch -c <branch-name> <base>`。
2. 从当前 HEAD 创建分支时保留工作区及暂存区，不例行 `stash` / `stash pop`。
3. 其他基线可能改变带有未提交改动的工作区时，先检查影响；只有能保留现有内容和暂存状态、且符合用户意图时才执行。否则准备可审阅的隔离方案并询问，不自动 stash、强制切换、覆盖文件或改写历史。
4. 核对当前分支和 Git 状态。本任务不自动 commit 或 push。

创建完成后输出确认信息。

## 示例

**用户**：创建一个分支，我要给用户模块加个导出功能

> 推断：`feature/user-export`

**用户**：切个 hotfix 分支，线上支付回调报错了

> 推断：`hotfix/payment-callback-error`

**用户**：帮我建个分支（有 uncommitted changes：修改了 README.md 和 docs/ 下的文件）

> 推断：`docs/update-readme`

**用户**：开个分支重构一下认证中间件

> 推断：`refactor/auth-middleware`
