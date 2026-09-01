---
name: codex-review-fix-loop
description: |
  使用 Codex 原生 `codex review` 对指定 Git 项目执行 review → evaluate → fix 循环。用户提出“review and fix until clean”、“循环 codex review”、“根据改动意向修复 review findings”、“审查分支/commit/未提交改动并修到没有 findings”、或要求反复审查与修复时使用本 skill。必须拿到项目路径；初始改动意向 X 默认从当前对话、最近任务和 diff 中推断。根据场景选择 `--uncommitted`、`--base`、`--commit` 或自定义 `PROMPT`，评估每条 finding 是否与 X 相关，只修复相关问题，并循环到 clean 或需要用户决策。
---

# Codex Review Fix Loop

## 目标

把一次“请 review 并修复”的开放任务收敛成可验证循环：

1. 从上下文推断初始改动意向 X。
2. 为审查目标选择稳定且可重复的原生 `codex review` 命令。
3. 对每条 review finding 判断是否属于 X 的变更范围。
4. 只修复与 X 相关且判断明确的问题。
5. 运行必要验证。
6. 使用同一审查目标继续 review，直到没有 findings。

这个 skill 解决循环控制和决策边界；`codex review` 只提供独立审查结果，最终判断和代码修改由当前 agent 负责。

需要可审计的 findings 台账时，使用 `codex-review-fix-loop-ledger`，它在本 loop 上叠加台账层。

## 输入要求

开始前确认三个输入：

- `项目路径`：要 review 的 Git repository 根目录。
- `初始改动意向 X`：本轮改动原本想完成什么。用户可以显式提供；没有提供时，从上下文推断。
- `审查目标 R`：未提交改动、相对基线分支的改动、指定 commit，或自定义审查指令。

推断 X 的优先级：

1. 当前对话中用户最近提出的实现 / 修复 / 重构目标。
2. 当前 agent 本轮或上一轮实际修改过的文件和说明。
3. 与 R 对应的 `git diff` / `git show` 所呈现的改动主题。
4. 最近一次相关 review 输出或用户反馈中的问题描述。

推断后用一句话写出 X 并继续。只有在以下情况才先问用户：

- 同时存在多个互不相关的候选 X，且选择错误会导致修错范围。
- 用户要求 `--base`，但基线分支无法从上下文或 Git 状态确定。
- diff 很大但上下文没有明确目标。
- 修复可能改变公共 API、数据迁移、权限模型、持久化格式或提交历史。

## 原生 CLI 命令

直接使用 Codex CLI，不调用 Python wrapper，也不自行维护 `codex review` 输出解析脚本。

优先把工具调用的 `workdir` 设置为项目路径。需要在命令中显式指定路径时，使用 Codex 全局 `-C`，并把它放在 `review` 子命令之前：

```bash
codex -C <project-path> review --uncommitted
```

### 命令与适用场景

| 命令 | 审查内容 | 适用场景 | 循环注意事项 |
|---|---|---|---|
| `codex review --uncommitted` | staged、unstaged、untracked 改动 | 提交前检查；当前工作区 review/fix；本 skill 默认场景 | 修复会直接更新同一目标，最适合循环到 clean |
| `codex review --base <branch>` | 当前分支相对指定基线分支 merge-base 的改动 | PR/MR 风格审查；整个功能分支验收 | 每轮保持同一 base；修复后分支 diff 会随之更新 |
| `codex review --commit <sha>` | 指定 commit 引入的改动 | 已提交 change set 的一次性审查；定位某次提交的问题 | commit 是不可变目标；不改写历史时，修复工作区后不能宣称原 commit 已 clean |
| `codex review "<instructions>"` | 完全由 instructions 定义 | 内置目标不能表达的专项范围或审查准则 | prompt 必须自行写清审查对象；每轮原样复用，避免目标漂移 |
| `codex review -` | 从 stdin 读取自定义 instructions | 指令很长，或由上游命令提供 | 与 positional prompt 语义相同 |

审查指定 commit 时，可以提供仅用于该 commit 的标题：

```bash
codex review --commit <sha> --title "<commit-title>"
```

原生 CLI 的四种 target `--uncommitted`、`--base`、`--commit`、自定义 `PROMPT` 两两互斥。`--title` 的语义是 commit 标题，只在 `--commit` 场景使用，即使某个 CLI 版本没有拒绝其他组合也不要依赖该行为。不要写：

```bash
codex review --uncommitted "只检查与 X 相关的问题"
```

目标是未提交改动但只允许修复 X 范围内的问题时，仍使用 `--uncommitted`，把 X 作为 Evaluate 阶段的过滤边界，而不是附加到 review 命令。

交互式 TUI 的 `/review` 也提供 base、uncommitted、commit、自定义指令四种预设，适合用户手动发起一次审查；本 skill 的自动循环使用非交互 `codex review`，不要为了执行 loop 启动 TUI。

`codex review` 没有公开的 review 总时限参数。外层执行工具的 timeout 设置为至少 900000 ms（15 分钟）；这是调用器超时，不是 CLI 参数。原生输出可能包含工具日志、完整 diff 和重复的最终结论，读取最后一份完整 reviewer 结论，不要因为前段输出很长就提前判定结果。

## 选择审查目标

按以下顺序选择 R：

1. 用户显式指定 target 时，使用该 target。
2. 用户说“当前改动”“未提交改动”“提交前”或只要求把刚完成的修改审到 clean，使用 `--uncommitted`。
3. 用户说“相对 main/develop”“PR/MR”“整个分支”，使用 `--base <branch>`。
4. 用户给出 SHA 或要求审查某个已提交 change set，使用 `--commit <sha>`。
5. 只有内置 target 无法表达审查对象时才使用自定义 `PROMPT`；prompt 必须包含稳定、可复现的目标描述。

不要为了使用自定义标准而放弃已经明确的结构化 target。比如“审查未提交改动，只修复登录回调相关问题”仍选择 `--uncommitted`，再用 X 限制修复范围。

### `--commit` 的修复边界

`--commit <sha>` 每次都会审查同一个不可变提交。发现问题后：

- 进入自动修复前，要求工作树干净，且当前 HEAD 等于目标 commit 或包含该 commit。否则只交付 commit findings，并暂停确认要在哪个分支或独立 worktree 中修复；不要自动 stash、切分支或覆盖已有改动。
- 未得到改写历史授权时，可以把修复写入工作区，并用 `--uncommitted` 审查修复补丁；如果已知 base，也可用 `--base` 审查包含原 commit 和修复的整体分支。
- 不要在未授权时自动 `commit --amend`、rebase 或移动分支。
- 最终报告要区分“原 commit 的 findings”“修复补丁已 clean”和“原 commit 是否被改写”。

## 循环流程

### 1. 建立边界

先按 R 做只读预检：

- `--uncommitted`：检查 `git status`、`git diff`、`git diff --staged`。没有未提交改动就停止，不要空跑 review。
- `--base <branch>`：确认 branch 可解析，并确认当前分支相对 merge-base 存在待审改动。
- `--commit <sha>`：确认 SHA 可解析，并用 `git show --stat --oneline <sha>` 核对目标；同时记录工作树是否干净、HEAD 是否等于或包含目标 commit。只读 review 不要求工作树干净，但自动修复必须满足前述 commit 修复边界。
- 自定义 `PROMPT`：确认 prompt 已写清审查对象和完成标准。

在第一次 review 前，向用户简短说明边界：

```text
项目：<project-path>
改动意向 X：<one sentence>
审查目标 R：<uncommitted / base branch / commit / custom>
命令：<exact codex review command>
停止条件：review 没有 findings；或修复需要改变 X、扩大范围、改写历史；或多轮未收敛（最多 10 轮）。
```

如果目标中包含多个明显无关的改动主题，且无法从上下文判断 X 对应哪个主题，先暂停并建议用户选择或拆分；不要在一个 loop 里混合修复无关主题。

### 2. Review

在项目路径运行已选择的原生命令。每轮保持 R 不变；只有 `--commit` 按前述不可变目标规则切换到修复补丁 target 时例外，并记录切换原因。

保留每轮 review 的关键信息：

- 轮次编号
- 实际命令和 target
- finding 标题和优先级
- 涉及文件
- 是否与 X 相关
- 处理决定

原生 CLI 输出较长时，以最后一份完整 reviewer 结论为准。如果外层工具仍显示进程在运行，继续轮询而不是启动第二个 review；如果输出在结论前被截断，使用更大的输出预算重新取得结果。没有取得完整结论不能视为 clean。

### 3. Evaluate

逐条评估 finding：

- `相关`：finding 指向 X 引入或修改路径上的正确性、安全性、性能、兼容性、可维护性问题。
- `不相关`：finding 指向 X 之前已经存在的问题，或属于另一个改动主题。
- `不确定`：需要业务意图、兼容性承诺、发布策略或用户偏好才能判断。

处理规则：

- 修复 `相关` 且修复方案明确的问题。
- 不修复 `不相关` 问题，但在最终报告中列出。
- `不确定` 问题不要猜测；把本轮所有需用户决策的项攒在一起一次性问，拿到答复再继续。
- finding 明显误判时，记录理由并继续下一条。

### 4. Fix

修复时保持 surgical：

- 只改与 finding 和 X 直接相关的文件。
- 不重构无关代码。
- 不顺手修历史问题。
- 不扩大 X 的功能范围。
- 不因 `--commit` review 自动改写提交历史。

如果修复会改变 X 的行为、公共 API、数据迁移、权限模型、持久化格式或提交历史，先暂停并说明取舍。

### 5. Verify

每轮修复后运行与改动风险匹配的验证：

- 优先使用项目已有测试、lint、typecheck。
- 没有明确验证命令时，至少运行针对被改模块的最小可用检查。
- 验证无法运行时记录原因并继续下一轮 review；最终报告必须说明未验证项。

### 6. Repeat

再次运行与当前 R 对应的原生命令。循环直到：

- review 输出明确表示没有 findings；或
- 连续两轮只剩误判 / 不相关问题；或
- 出现需要用户决策的问题，且本轮相关项已汇总；或
- 修复需要扩大 X、改变审查目标或改写历史，必须由用户确认；或
- 已经跑满 10 轮但仍不断出现新 finding：暂停并汇报当前状态，交用户决定是否继续。

不要因为“已经修了几处”就停止。停止条件必须和 review 结果绑定。

## Codex 输出判断

不同版本的 `codex review` 可能用不同措辞表示没有发现问题。以下都可以作为 clean 信号：

- `No findings`
- `no findings`
- `did not find any discrete functional regression`
- `I did not find any ... regression`
- 最终 reviewer 摘要明确表示没有可执行问题

如果最后一份完整结论含有 `Review comment:`、`Full review comments:` 或明确列出的 findings，按有 findings 处理。原生 CLI 可能把最终结论打印两次，重复内容只计为一份 review 结果。

### Review 失败（不是 clean）

以下情况表示 review 本身没跑成功：

- `codex review` 非零退出。
- 输出 `Reviewer failed to output a response.`。
- 进程被外层 timeout 终止。
- 输出被截断，或结束时没有完整 reviewer 结论。

遇到失败先重试一轮；仍失败则暂停并报告。不要把“没有捕获到 findings”误判为“没有 findings”。

## 最终报告

结束时用简短报告交付：

```text
完成状态：clean / paused / blocked
项目：<project-path>
改动意向 X：<one sentence>
审查目标 R：<target>
Review 轮次：<n>
修复摘要：
- ...
验证：
- <command>: passed/failed/not run
未修复 findings：
- <finding>: <不相关/误判/等待用户决策>，原因...
```

如果使用 `--commit` 后把修复留在工作区，明确报告原 commit 未变，以及最终 clean 结论对应的是修复补丁还是整个分支。最终状态不是 `clean` 时，说明下一步需要用户做什么决定。

## 示例触发

- `对 /path/to/repo 的未提交改动做 codex review，自动判断改动意向并循环修到 clean`
- `以 main 为 base 审查当前分支，只修这次支付重试相关 findings，直到没有问题`
- `审查 commit abc123；发现问题就修，但不要 amend，修复补丁继续 review 到 clean`
- `用自定义 review 指令检查这个并发修复，反复修到没有可执行 findings`
