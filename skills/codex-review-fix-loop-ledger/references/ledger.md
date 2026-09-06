# 台账细节参考

本文件是 codex-review-fix-loop-ledger 的细节层:字段 schema、分类表、fallback 模板、提交机制命令序列、报告模板。

**权威口径**:项目有自己的台账模板时(如 practical-education 的 `CodexReviewFindings记录模板.md`),以项目模板的结构与分类定义为准,本文的结构、字段及证据策略仅补充项目未定义部分；项目的门禁和授权边界同样优先。

## 1. 文件命名

```text
{ledger_dir}/{yyyy-mm-dd-HHmm}-{scope}-{change-slug}.md
{ledger_dir}/raw/{yyyy-mm-dd-HHmm}-{scope}-{change-slug}-commands-raw.md
```

`ledger_dir` 严格按 `../SKILL.md` 的“前置检查与位置”解析；此处不另设 fallback 顺序。root-docs 只有在项目将其指定为审计 owner 时才可采用，普通 fallback 必须在任何 Git 工作树之外。

## 2. raw 记录

无项目证据策略时，每次执行以下命令后追加一条 raw 记录:codex review(每轮 + final clean)、测试 / lint / typecheck / build、`git diff --check` 等收口判断命令。

| 字段 | 说明 |
| --- | --- |
| RAW ID | `RAW-001` 起递增 |
| 时间 | 命令执行时间 |
| 命令 | 实际命令 |
| 工作目录 | 实际 cwd |
| 退出码 | exit code |
| stdout/stderr | 原始输出 |

台账正文只索引 RAW ID,不粘贴大段原始输出。两个例外:

- **过大**:记录裁剪版(命令、cwd、退出码、摘要)+ 指向本地完整 dump 的路径和抽取方式,不塞整块 blob。
- **敏感**:输出可能含 token / env / 密钥时,脱敏后入库,原件仅留本地指针;不原样提交。

## 3. finding 条目字段

| 字段 | 取值或说明 |
| --- | --- |
| ID | `CR-001` 起递增 |
| 轮次 | `R1`、`R2`… |
| 严重级别 | `P0/P1/P2/P3`;review 未给级别时由 agent 按影响判断 |
| finding 摘要 | 一句话 |
| 合理性判断 | `真实问题` / `误报` / `重复` / `超出本阶段范围` / `待确认` |
| 归因 | 见第 4 节,每条真实 finding 至少一个 |
| 判断依据 | 代码、spec、测试、接口契约、SQL、配置或阶段边界 |
| 处理方式 | 已修复 / 不采纳 / 后续处理 / 阻塞 |
| 验证证据 | 测试/构建/lint 的 RAW ID |
| 文档回写 | 无需回写 / 已回写 / 待回写 |
| 预防动作 | 见第 5 节 |
| 状态 | 待处理 / 已关闭 / 阻塞 / 暂缓 |

`误报`、`历史遗留`、`超出本阶段范围` 仍需写清反证依据或后续落点,不能只贴标签。

## 4. 归因分类(fallback,10 类)

| 归因 | 说明 |
| --- | --- |
| 指令不清 | 用户目标、约束或优先级没有明确表达 |
| spec 缺失 | 需求、技术方案或任务 spec 没有覆盖该规则 |
| spec 冲突 | 多份文档、章节或接口口径互相矛盾 |
| 实现遗漏 | 已有信息足够,但 agent 没有实现完整 |
| 范围误判 | agent 把当前阶段应做或不应做的内容判断错 |
| 测试缺口 | 现有测试未覆盖该边界或回归路径 |
| 文档同步遗漏 | 代码、接口或行为变化后未同步事实源文档 |
| review 误报 | finding 不成立 |
| 历史遗留 | 问题存在于本次变更前,不属于本轮引入 |
| 环境/数据缺口 | 需要环境、权限、数据或日志才能确认 |

## 5. 预防动作(fallback,7 类)

每条 `真实问题` 记录直接修复 + 预防动作:

| 预防动作 | 适用情况 |
| --- | --- |
| 补 spec | finding 暴露需求或任务边界缺失 |
| 补规则矩阵 | 涉及状态、操作、权限、数量、排序、审批、回调、历史数据等规则 |
| 补测试 | 代码行为遗漏且可自动化验证 |
| 补 checklist | 反复出现的 review 检查项 |
| 补 runbook | 依赖环境、权限、数据、上线配置或联调步骤 |
| 补 AGENTS 或 skill | 源于 agent 稳定执行问题或流程漏项 |
| 无需预防 | 一次性问题,需写明理由 |

## 6. 台账章节结构(fallback 模板)

```markdown
# Review Findings 台账 — {change-slug}

## 1. 基本信息
<!-- 项目、日期、改动意向 X、执行人/agent、台账与 raw 路径 -->

## 2. Review 输入边界
<!-- 被审 diff 范围、停止条件、预存 stage 说明(如有) -->

## 3. Review 轮次
<!-- 每轮一行:轮次 / 时间 / RAW ID / findings 数 / 结果 -->

## 4. Findings 台账
<!-- 每条 finding 一行,字段见参考第 3 节 -->

## 5. Raw 命令输出索引
<!-- RAW ID → 命令 → 位置(raw 文件内锚点) -->

## 6. 处理明细
<!-- 需要展开的 CR:修复内容、涉及文件、取舍 -->

## 7. 归因复盘
<!-- 按归因聚合:归因 | findings | 复盘结论 | 预防动作 | 状态 -->

## 8. 预防动作
<!-- 动作 | 对应 CR | 落点(spec/测试/checklist/...) | 状态 -->

## 9. 验证记录
<!-- 命令 | 结果 | RAW ID -->

## 10. 文档回写检查
<!-- 受影响事实源 | 是否回写 | 位置 -->

## 11. 未关闭项
<!-- CR/动作 | 原因 | 建议落点 -->

## 12. 收口结论
<!-- final clean review(RAW ID)或台账自引用收口结论(含前置条件核对) -->
```

## 7. 可选提交机制与证据收口

仅在 SKILL.md 的授权、目标和 Git 前提全满足时使用；不满足则按位置策略保留文件，不执行本节 Git 修改。

### 前提核对

```bash
git -C <repo> rev-parse --verify HEAD
git -C <repo> symbolic-ref -q HEAD
git -C <repo> status --porcelain=v1
git -C <repo> diff --cached --name-only
```

通过 `git rev-parse --git-path <name>` 解析 `rebase-merge`、`rebase-apply`、`MERGE_HEAD`、`CHERRY_PICK_HEAD` 和 `REVERT_HEAD` 并检查是否存在；worktree 的 `.git` 可能是文件，不能硬编码 `<repo>/.git/...`。

记录原 HEAD、非台账业务 diff 和暂存状态。确认台账/raw 是本轮新建路径，且当前 Git 授权覆盖拟执行操作。

### 首轮提交（仅已获授权时）

```bash
git add -- <台账路径> <raw路径>
git commit --only -m "chore(review): 评审台账 [review-ledger]" -- <台账路径> <raw路径>
git show --pretty="" --name-only HEAD
git rev-parse HEAD
```

核对提交文件仅为台账/raw，并记录新 SHA；核对 hooks 没有改动非台账内容或预存 stage。hook 失败时诊断原因或禁用提交机制，不自动加 `--no-verify`，不清空 index 重试。

### 每轮更新（仅已获 amend 授权时）

```bash
git rev-parse HEAD                              # 必须等于本轮记录的台账 SHA
git show --pretty="" --name-only HEAD           # 仅台账/raw
git log -1 --format=%s                          # 含 [review-ledger]
git branch -r --contains HEAD                   # 辅助检查，空输出不足以证明未发布
```

结合本轮创建记录、发布操作及远程状态确认未发布；存在并发发布或来源不明等不确定性时，不 amend。全通过后才运行：

```bash
git commit --amend --only --no-edit -- <台账路径> <raw路径>
git show --pretty="" --name-only HEAD
git rev-parse HEAD
```

记录新的专用台账 SHA，并再次核对业务 diff 和预存 stage。`--no-verify` 不在默认命令中；单独明确授权绕过 hook 时才可追加。

### 失败处理

- 提交失败或前提断言失败：禁用该机制，用允许的非提交方式继续记录。项目没有合规替代方式时，报告具体审计阻塞。
- 提交掺入业务文件、hook 改动业务/index 或 HEAD 意外变化：先停止 Git 修改，保留证据并重新核对受审对象；准备恢复方案，不自动 `reset`、stash、改写历史或创建另一个台账 commit。受审输入未确认前不能继续宣称 clean。

### 纯证据自引用收口

只有全部满足时可不因最终记账再跑 review：

1. 项目允许该收口方式，实质受审内容未在 final review 后改变。
2. 业务代码、需求、接口、SQL、上线流程等无未处理的真实相关 finding，也无待决项。
3. 最后一轮 review 完整原始结论已保留；如仍有台账自引用 finding，报告原文和判定依据，不声称原始输出为 no findings。
4. 台账的格式、引用、路径和状态一致性检查通过；真实审计缺陷已修正。
5. 必要业务验证与项目审计门槛已满足。未满足时仍报告 blocked。

## 8. 最终报告模板

```text
完成状态:clean / scoped-clean / paused / blocked
项目:<project-path>
改动意向 X:<one sentence>
台账:<path>
Raw 输出:<path>
Review 轮次:<n>
Findings 归因摘要:
- spec 缺失:2,已补规则矩阵
- 实现遗漏:1,已补测试
修复摘要:
- ...
验证:
- <command>: passed/failed/not run,证据 RAW-xxx
未关闭项:
- ...
预防动作:
- ...
收尾指引:
- 隔离方式:<repo 外 / 同 repo 未提交 / 已授权提交机制>
- Git 状态:<实际 HEAD、台账及业务是否提交/推送>
- 长期归档:<已完成 / 项目无要求 / 待完成及原因>
```
