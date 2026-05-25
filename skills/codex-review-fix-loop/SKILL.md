---
name: codex-review-fix-loop
description: |
  基于 codex review 对指定项目的未提交改动执行 review -> evaluate -> fix 循环。用户提出“review and fix until clean”、“循环 codex review”、“根据改动意向修复 review findings”、“审查未提交改动直到没有 findings”、或要求在指定项目上反复 review/evaluate/fix 时使用本 skill。必须拿到项目路径；初始改动意向 X 默认从当前对话、最近任务和未提交 diff 中推断。运行 codex review --uncommitted，评估每条 finding 是否与 X 相关，只修复相关问题，然后继续循环直到 review findings 为空或遇到需要用户决策的问题。单次 review 用 codex-collab；需要 review→fix 反复迭代到 clean 时用本 skill。
---

# Codex Review Fix Loop

## 目标

把一次“请 review 并修复”的开放任务收敛成可验证循环：

1. 从上下文推断初始改动意向 X。
2. 在指定项目上 review uncommitted changes。
3. 对每条 review finding 判断是否属于 X 的变更范围。
4. 只修复与 X 相关且判断明确的问题。
5. 运行必要验证。
6. 继续 review，直到没有 findings。

这个 skill 解决的是循环控制和决策边界；Codex 只提供独立 review 结果，最终判断和代码修改由当前 agent 负责。

## 输入要求

开始前确认项目路径，并推断改动意向：

- `项目路径`：要 review 的 repository 根目录。
- `初始改动意向 X`：本轮未提交改动原本想完成什么。用户可以显式提供；如果没有提供，默认自动从上下文推断。

推断 X 的优先级：

1. 当前对话中用户最近提出的实现 / 修复 / 重构目标。
2. 当前 agent 本轮或上一轮实际修改过的文件和说明。
3. `git diff` / `git diff --staged` 显示的未提交改动主题。
4. 最近一次相关 review 输出或用户反馈中的问题描述。

推断后用一句话写出 X 并继续，不要为了让用户复述已经明显存在的上下文而停下来。只有在以下情况才先问用户：

- 同时存在多个互不相关的候选 X，且选择错误会导致修错范围。
- diff 很大但上下文没有明确目标。
- 用户要求的行为可能需要扩大、改变或覆盖原始意图。

## 依赖

使用本 skill 内置的 review 包装脚本（vendored 自 codex-collab，便于独立打包）。路径相对本 SKILL.md 所在目录：

```bash
python scripts/codex_review.py \
  --cd <project-path> \
  --uncommitted \
  "只报告本次未提交改动引入的实际 bug，忽略琐碎风格问题。每个问题标注优先级 [P0]-[P3]。"
```

把命令 timeout 设置为至少 900000 ms（15 分钟）。`codex review` 实测可能持续 10-12 分钟，外层 timeout 必须留足，否则会在脚本完成前被杀掉。

## 循环流程

### 1. 建立边界

先确认工作区存在未提交改动（`git status` / `git diff`）。若没有任何未提交改动，`codex review --uncommitted` 无内容可审，直接停下告知用户，不要空跑 codex。

在第一次 review 前，向用户简短说明推断出的本轮边界：

```text
项目：<project-path>
推断的改动意向 X：<one sentence>
停止条件：codex review 没有 findings；或出现需要改变 X、扩大范围、风险较高的修复；或多轮未收敛（最多 5 轮）。
```

如果工作区包含多个明显无关的未提交主题，且无法从上下文判断本轮 X 对应哪个主题，先暂停并建议用户选择或拆分；不要在一个 loop 里混合修复无关主题。

### 2. Review

运行 `python scripts/codex_review.py --cd <project-path> --uncommitted`。保留每轮 review 的关键信息：

- 轮次编号
- finding 标题和优先级
- 涉及文件
- 是否与 X 相关
- 处理决定

### 3. Evaluate

逐条评估 finding：

- `相关`：finding 指向的是 X 引入或修改路径上的正确性、安全性、性能、兼容性、可维护性问题。
- `不相关`：finding 指向 X 之前已经存在的问题，或属于另一个未提交主题。
- `不确定`：需要业务意图、兼容性承诺、发布策略或用户偏好才能判断。

处理规则：

- 修复 `相关` 且修复方案明确的问题。
- 不修复 `不相关` 问题，但在最终报告中列出。
- `不确定` 问题不要猜测；把本轮所有 `不确定` / 需用户决策的项攒在一起一次性问，拿到答复再继续，不要每条单独暂停——每次重跑 review 要 10-12 分钟，逐条打断会反复拖住用户。
- 如果 finding 本身明显误判，说明理由并继续下一条。

### 4. Fix

修复时保持 surgical：

- 只改与 finding 和 X 直接相关的文件。
- 不重构无关代码。
- 不顺手修历史问题。
- 不扩大 X 的功能范围。

如果修复会改变 X 的行为、公共 API、数据迁移、权限模型或持久化格式，先暂停并说明取舍。

### 5. Verify

每轮修复后运行与改动风险匹配的验证：

- 优先使用项目已有测试、lint、typecheck。
- 如果没有明确验证命令，至少运行针对被改模块的最小可用检查。
- 如果验证无法运行，记录原因并继续下一轮 review；最终报告必须说明未验证项。

### 6. Repeat

再次运行 codex review。循环直到：

- review 输出明确表示没有 findings；或
- 连续两轮只剩误判 / 不相关 / 需要用户决策的问题；或
- 修复需要扩大 X，必须由用户确认；或
- 已经跑满 5 轮但仍不断冒出新 finding（未收敛）：暂停并汇报当前状态，交用户决定是否继续。codex review 结果不确定，没有这个上限循环可能发散，每轮 10-12 分钟成本很高。

不要因为“已经修了几处”就停止。停止条件必须和 review 结果绑定。

## Codex 输出判断

不同版本的 `codex review` 可能用不同措辞表示没有发现问题。以下都视为 clean：

- `No findings`
- `no findings`
- `did not find any discrete functional regression`
- `I did not find any ... regression`
- 没有 `Review comment:` 或 `Full review comments:` 区块，且摘要明确表示无问题

如果输出含有 `Review comment:` 或 `Full review comments:`，按有 findings 处理。

### Review 失败（不是 clean）

以下情况表示 review 本身没跑成功，绝不能当作 clean：

- 输出 `Reviewer failed to output a response.`
- 脚本非零退出，或打印 `未捕获到审查输出` / `codex review 失败` / `codex review 超时`

遇到失败先重试一轮；若仍失败，暂停并向用户报告。不要把“没看到 findings”误判为“没有 findings”。

## 最终报告

结束时用简短报告交付：

```text
完成状态：clean / paused / blocked
项目：<project-path>
改动意向 X：<one sentence>
Review 轮次：<n>
修复摘要：
- ...
验证：
- <command>: passed/failed/not run
未修复 findings：
- <finding>: <不相关/误判/等待用户决策>，原因...
```

如果最终状态不是 `clean`，明确下一步需要用户做什么决定。

## 示例触发

- `对 /path/to/repo 的未提交改动做 codex review，自动根据上下文判断本轮改动意向并循环修到 clean`
- `对 /path/to/repo 的未提交改动做 codex review，按“修复登录回调错误”这个意向循环修到 clean`
- `review & evaluate & fix loop，项目是当前目录，X 是给 codex_review 增加 --cd 参数`
- `帮我反复跑 codex review，只修跟这次支付重试改动相关的问题，直到没有 findings`
