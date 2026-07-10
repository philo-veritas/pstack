---
name: codex-review-fix-loop-ledger
description: |
  在 codex-review-fix-loop 循环上叠加可审计的 findings 台账:首轮 review 前创建台账与 raw 输出文件,逐轮记录 finding 判断、归因、修复、验证证据,final clean review 入账,并用"单一台账 commit + amend"机制让台账不进 codex 待审 diff、避免自引用循环。用户要求"带台账的 review 循环"、"review 并记录 findings 台账"、"可审计/可复盘地修到 clean",或项目规则(AGENTS.md)要求 review 循环留存台账时使用。依赖已安装的 codex-review-fix-loop skill;轻量、无需审计的场景直接用 codex-review-fix-loop。
---

# Codex Review Fix Loop — Ledger

## 定位

本 skill 是 codex-review-fix-loop 的台账叠加层:loop 的全部逻辑(意向 X 推断、review、evaluate、fix、verify、停止条件、输出判断、失败处理)由 base skill 定义,本文只定义在哪些阶段记录什么,以及如何让台账不污染 review。

执行方式:

1. 读完本文,再读 `references/ledger.md`(字段 schema、归因/预防分类、fallback 模板、提交机制命令序列、报告模板)。
2. 通过 Skill tool 调用 `codex-review-fix-loop`,按其流程跑 loop。
3. 在 loop 各阶段叠加下方台账动作;台账相关行为与 base 冲突时以本文为准。

依赖:`codex-review-fix-loop` 已安装(两个 skill 由 pstack 成对维护、成对分发)。未安装则停下说明,不要自行复述 loop。

## 前置检查(并入 base 的"建立边界"阶段)

1. base 前置照常:项目路径、存在未提交改动。
2. **台账位置解析**(确定性顺序,取第一个命中):
   1. 项目规则/模板指明位置(项目 AGENTS.md、方法论文档、模板)→ 用项目的路径和文件模板。
   2. 工作区为跨 repo / root-docs 结构 → 台账放 root docs 区(被 review repo 之外)。codex `--cd <业务repo>` 看不到台账,**无需提交机制**,台账随 docs 区正常管理。
   3. 单体 repo → `<repo>/docs/review-findings/`,走提交机制。
3. **同 repo 台账的 git 前提**,任一不满足即停下说明、不猜:是 git 仓库(或 worktree);HEAD 存在(非空仓库);非 detached HEAD;无 rebase / merge 进行中。
4. **预存 stage 检查**:`git diff --cached --name-only` 非空 → 向用户说明"index 已有预存内容,台账将用 pathspec 提交,不 unstage、不带走这些内容"。
5. 在 base 的边界声明中追加:

```text
台账:<路径>(模板:项目模板 / 内置 fallback)
提交机制:同 repo 单一台账 commit([review-ledger])/ repo 外无需
```

## 台账初始化(首轮 review 前,不能事后补录)

1. 创建台账 + raw 文件(命名与模板见 references/ledger.md)。
2. 同 repo:`git add <台账> <raw>`(只 add 这些精确路径)→ `git commit --only --no-verify -m "chore(review): 评审台账 [review-ledger]" -- <台账> <raw>` → 立即断言 `git show --pretty="" --name-only HEAD` 只含台账/raw。
3. repo 外:按 docs 区惯例正常提交。

## 各阶段台账动作

| base 阶段 | 叠加动作 |
| --- | --- |
| 每次 review / 测试 / lint / 收口命令后 | 追加 raw 记录(RAW-xxx:时间、命令、cwd、退出码、原始输出) |
| Evaluate 逐条判断后 | 写 finding 条目(CR-xxx:轮次、严重级别、合理性判断、归因、判断依据、处理方式、验证证据、文档回写、预防动作、状态) |
| Fix / Verify 后 | 回填对应 CR 的处理方式、验证证据(RAW ID)、状态 |
| 每轮结束(下一轮 review 前) | 同 repo:三断言通过 → `git commit --amend --only --no-verify --no-edit -- <台账> <raw>`;任一断言失败走兜底 |
| final clean review | 作为一轮入账:追加 raw + 写收口证据;这轮之后的台账更新照常 amend,无需再触发 review |

字段取值、归因 10 类、预防 7 类、台账章节结构见 `references/ledger.md`。

## 提交机制红线(同 repo 台账)

核心不变量:**业务改动全程不提交**(留在工作区给 codex review),HEAD 始终是台账 commit。

- 绝不 `git add -A` / `git add .` / 直接 `git commit` 整个 index;只用精确路径 add + `--only -- <路径>` 提交。
- 台账 commit 一律 `--no-verify`:hook 可能失败,或自动 stage 业务文件(lint-staged 类)。
- 每次 commit 后立即断言文件列表恰为台账/raw;掺入其他文件 → `git reset --soft HEAD^` 回滚并停下报错。致命坑:业务改动被卷进台账 commit → `--uncommitted` 变空 → codex 报无 findings → 假 clean。
- amend 前三断言(全过才 amend):① HEAD 只动台账/raw 路径;② message 含 `[review-ledger]`;③ HEAD 未 push(`git branch -r --contains HEAD` 为空)。任一不成立 → 绝不 amend,改为在 HEAD 之上新建台账 commit,或暂停交用户决定。正确性优先于历史整洁。
- raw 原样入库;单次输出过大或含敏感信息时,按 references 的例外处理(裁剪记录 / 脱敏 + 指针),不原样塞入。

完整命令序列见 `references/ledger.md`。

## 收口与最终报告

- 使用 references/ledger.md 的 ledger 版报告格式(含台账/raw 路径、归因摘要、未关闭项、预防动作)。
- 报告必须含收尾指引:HEAD 为台账 commit(未 push);业务改动仍未提交,用户后续业务 commit 会落在台账 commit 之上,可按需 squash / reorder。
- **台账自引用收口结论**仅作兜底:提交机制与 repo 外台账都不可用、且确认剩余 finding 只针对台账自身时才能使用;绝不能用于跳过业务、接口契约、权限、SQL、数据类 finding。前置条件见 references。

## 示例触发

- `对 /path/to/repo 跑带台账的 codex review fix loop,修到 clean 并留审计记录`
- `review 并记录 findings 台账,归因和预防动作都要写`
- `这个项目要求 review 台账,用 ledger 版循环修到 clean`
