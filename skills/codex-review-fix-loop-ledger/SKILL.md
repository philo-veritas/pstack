---
name: codex-review-fix-loop-ledger
description: |
  在 codex-review-fix-loop 循环上叠加可审计的 findings 台账：首轮 review 前准备证据位置，逐轮记录 finding 判断、归因、修复和验证，保留 final review 结论。用户要求“带台账的 review 循环”、“review 并记录 findings 台账”、“可审计/可复盘地修到 clean”，或项目规则要求 review 台账时使用。依赖 codex-review-fix-loop；台账不隐含 commit、amend、push 或绕过 hook 的权限。
---

# Codex Review Fix Loop — Ledger

## 定位与依赖

本 skill 只定义审计记录与隔离方式。意向 X、目标 R、review/evaluate/fix/verify、停止条件和结果判断由 `codex-review-fix-loop` 定义；台账规则不扩大 base 的修复或 Git 授权。

1. 读取本文件及 `references/ledger.md`；项目规定的台账结构、证据保留策略、位置和准入门槛优先，reference 仅补未定义部分。
2. 读取并遵循 `codex-review-fix-loop/SKILL.md`。有 Skill 工具时可用它加载，没有时直接读文件，不因缺少名为 Skill 的工具而停止。
3. base 未发现时，先查已安装位置及同源相邻 skill；确实缺失才报告依赖阻塞，不凭记忆另造 loop。

## 前置检查与位置

1. 按 base 对 R 做预检。只有当前改动审查要求存在未提交改动；`--base`、`--commit` 和其他自定义目标分别沿用各自前提。
2. 解析台账位置，取首个适用项：
   - 项目已指定位置：使用该位置，不为省事移动到别处或跳过门禁。
   - 项目已将 root-docs 指定为审计 owner，但未给出具体文件路径：在其 docs 区选择不冲突的位置，并核对真实路径和 R。不能仅凭存在父仓库就把它当成已授权的审计位置，也不能仅凭 cwd 声称 reviewer 无法读取这些文件。
   - 无项目位置约束：选择不属于任何 Git 工作树的持久目录，例如用户数据目录下的 `review-findings/<repo-path-id>/<session-id>/`；repo-path-id 区分完整仓库路径，不能仅使用可能重名的 basename。创建前解析真实路径，并对最近已存在的父目录运行 `git -C <parent> rev-parse --show-toplevel`，确认不存在所属 Git 工作树；若属于其他仓库或检查因权限等原因不确定，改选位置后重新检查。选择不冲突且可写的目录，核对不在 R 的输入范围，不污染嵌套仓库或父仓库。报告实际路径，不能只保存在易清理的临时目录。
3. 同 repo 位置不等于必须提交：优先保留台账为工作区文件，并如实处理 review 看到的台账 findings。仅在满足下方条件时启用可选提交机制。
4. 位置不可写或机制不可用时，先检查项目允许的替代位置；没有合规位置才报告审计阻塞。只暂停依赖该审计门槛的工作，不自动豁免项目门禁。

首次 review 前声明 X、R，并追加：

```text
台账与证据：<实际路径>（项目模板 / fallback）
隔离方式：repo 外 / 同 repo 未提交 / 已授权的台账提交机制
授权范围：<已授权的 Git 操作；没有则写无>
```

## 初始化与逐轮记录

创建任何台账文件前，记录初始 HEAD、R、业务 diff 和预存 stage/untracked 范围。首轮 review 前创建台账并准备 raw 位置；项目要求预建 raw 时同步创建，不能事后伪造记录。`--commit` 且项目要求同 repo 台账时，按 base 的精确台账路径例外核对首次修复前的干净条件；只有创建前已干净、本轮新建且不属于目标 commit 的台账/raw 可以排除，不能将其他脏路径归为证据。

| 阶段 | 台账动作 |
| --- | --- |
| review / 验证后 | 按项目策略记录命令、cwd、退出码及必要原始证据；无项目策略时沿用 reference |
| Evaluate 后 | 逐条记录相关性、判断依据、处理方式、归因和所需决定 |
| Fix / Verify 后 | 回填修复、验证证据、文档回写和状态；待决项不阻塞其他独立已授权工作 |
| 下一轮前 | 记录本轮结果；仅已启用提交机制时按 reference 的断言更新台账 commit |
| final review 后 | 保留完整结论并完成记录；由该结论派生的纯证据更新只做确定性校验，不因新增记账重启循环 |

新改业务、接口、权限、SQL 或其他实质受审内容必须重新 review。台账本身真实的证据缺失、错误结论或敏感信息问题仍需修正，不能归为“自引用”忽略。

## 可选同 repo 提交机制

仅用于 **当前未提交改动审查**，且以下条件全部满足：

- 用户授权或适用项目规则已明确覆盖台账 commit；若使用 amend，还须明确覆盖对本轮专用台账 commit 的 amend。普通“review/fix/记录台账”不是该授权。
- 受审业务改动保持未提交；仓库有 HEAD、非 detached HEAD，且没有 merge/rebase 等进行中的 Git 操作。
- 台账/raw 是本轮新建的独立路径，不能把既有业务或文档改动夹入台账提交。

`--base` 的台账 commit 仍在分支 diff 中，`--commit` 的目标不可变，因此不能套用此机制声称已隔离；使用前述位置策略即可。台账条件不满足只禁用该机制，不把它变成 base 审查的通用前提。

- 只提交精确台账路径，保留预存 stage；默认运行 hooks。绕过 hook 须单独已有明确授权，不能由此 skill 自动推出。
- commit 后验证仅含台账/raw，且业务 diff 和预存 stage 未被改变。异常时停止 Git 修改，保存证据并重新核对 R；不自动 reset/stash 或宣称 clean。
- amend 必须同时满足：HEAD 是本轮记录的专用台账 commit、只含台账/raw、带 `[review-ledger]`、能够确认未发布。远程跟踪引用查询为空不是未发布的充分证明；发布状态不明时不 amend。
- 断言失败后禁用 amend，保留记录。优先用允许的非提交方式继续，不自动另造提交或恢复历史。需要用户决定时先准备具体恢复方案。

完整操作提示见 `references/ledger.md` 第 7 节。证据文件最终入库若是项目交付要求，必须完成该要求或报告未完成；repo 外保存不等于长期归档已完成。

## 收口与报告

沿用 base 的 `clean / scoped-clean / paused / blocked` 状态和验证边界。报告台账/raw 路径、未关闭项及实际 commit/push/归档状态，不固定声称“HEAD 为台账 commit”。需要用户决定时指出具体问题，不能只要求“确认继续”。

仅剩纯台账自引用时按 reference 条件记录“实质受审对象已收口，纯证据更新已校验”，不能冒充 reviewer 原文无 findings；未满足的验证或审计门槛仍报告 blocked。

## 示例

- `对 /path/to/repo 的未提交改动做带台账的 review/fix，不要提交`
- `以 main 为 base 审查功能分支，工作树干净，台账遵循项目规范`
- `审查 commit abc123 并记录 findings，修复补丁继续审查，不 amend`
