---
name: branch
description: |
  创建 git 分支。按照 <type>/<short-english-description> 规范从当前分支创建新分支。
  支持从用户描述推断分支名，或分析未提交改动自动生成。
  当用户说"创建分支"、"新建 branch"、"切个分支"、"开分支"、"建个分支"、
  "create branch"、"new branch"时使用此 skill。
---

# Branch - 创建 Git 分支

按照 `<type>/<short-english-description>` 规范创建新分支。

## 分支类型

| type       | 适用场景                         |
| ---------- | -------------------------------- |
| `feature`  | 新功能、新模块                   |
| `fix`      | 修复已知 bug                     |
| `hotfix`   | 线上紧急修复                     |
| `refactor` | 重构，不改变外部行为             |
| `chore`    | 构建、CI、依赖更新等杂务         |
| `docs`     | 文档新增或修改                   |

## 命名约束

- 格式：`<type>/<kebab-case-description>`
- description 使用英文，kebab-case，最多 5 个单词
- 总长度（含 type/）不超过 50 字符

## 工作流程

### 第一步：检查环境

运行 `git status` 和 `git branch --show-current`，确认：

- 当前分支名
- 是否有未提交的改动（uncommitted changes）

如果当前不在 main 分支，提醒用户："当前在 `<branch>` 分支，新分支将从此处创建。是否要先切回 main？"

### 第二步：推断分支名

根据输入来源选择模式：

**模式 A — 用户给出描述**：从用户的需求描述中推断 type 和 description。

**模式 B — 分析未提交改动**：如果用户没有给出描述且有未提交改动，运行 `git diff` 和 `git diff --cached` 分析改动内容，推断 type 和 description。

如果信息不足以推断，主动询问用户要做什么。

### 第三步：确认

向用户展示建议的分支名，等待确认：

> 建议分支名：`feature/user-export-module`
>
> 确认创建？或告诉我调整方向。

用户确认后才执行创建。

### 第四步：创建分支

1. 如果有未提交改动：先 `git stash`
2. 执行 `git checkout -b <branch-name>`
3. 如果第 1 步做了 stash：执行 `git stash pop`

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
