---
name: harness-audit-existing
description: 为已经存在的项目(无论是否已经接入 Claude Code / Codex)做一次完整的 harness 诊断与改造处方。当用户提到 "评估 / audit 现有 CLAUDE.md / AGENTS.md"、"我的 .claude/ 或 Codex 配置怎么改"、"这个老项目要不要加 hook"、"docs/ 结构合理吗"、"agent 在这个项目老犯同一个错"、"接入 Claude Code 或 Codex 该怎么起步"、"现有的 CLAUDE.md / AGENTS.md 优化",或者展示一个仓库希望从 agent 工程角度评估时,使用本 skill。CLAUDE.md / AGENTS.md 是 Claude Code 与 Codex 两个工具对应的 always-on 提示词文件,本 skill 对两者一视同仁。本 skill 只交付诊断和改造处方(分层路线图 + 反决策清单 + 改造建议报告),不直接生成脚手架文件——具体的 CLAUDE.md / AGENTS.md / hook / skill 模板由用户基于处方自行实现或在后续 skill 中处理。Use this skill aggressively whenever the user mentions auditing, improving, or onboarding agent tooling (Claude Code or Codex) on an existing codebase, even if they don't use the word "harness" explicitly.
---

# Harness Audit & Refactor(历史项目诊断与处方)

## 这个 skill 做什么

为一个已存在的代码库出一份 **harness 诊断报告 + 改造路线图**。覆盖范围:

- 现有 CLAUDE.md / AGENTS.md / .claude/ 配置(以及 Codex 对应配置)的评估与改造建议
- docs/ 结构的评估(是否承担了知识库"记录系统"的角色)
- Hooks 现状与建议配置(Claude Code 与 Codex 各自的 hook 体系)
- Permission tier 的现状与缺口
- Sub-agent / skill 体系的引入建议
- 度量与 entropy 治理的优先级

**关于工具与文件的对称约定**:本 skill 所述"CLAUDE.md"和"AGENTS.md"指代同一个抽象——always-on 提示词文件,分别对应 Claude Code 与 Codex。所有诊断与处方逻辑对两者对称适用;只在涉及具体 hook 事件覆盖范围、配置目录路径等平台差异时,才区分讨论。出现"Claude Code"的地方默认也适用 Codex,反之亦然,除非显式说明平台差异。

**明确不做的事情**:不直接生成 CLAUDE.md / AGENTS.md、不写 hook 脚本、不创建 docs/ 目录、不修改任何项目文件。所有改造由用户基于本 skill 的处方自行实施。这条边界很重要——脚手架生成需要项目特有判断,本 skill 只到"该做什么、按什么优先级、为什么"。

## 什么时候用 / 什么时候不用

**用本 skill 的场景**:

- 项目已经在用 Claude Code / Codex 但 agent 行为不稳定、反复出错
- 团队想给一个老项目正式接入 agent 工作流(无论是 Claude Code 还是 Codex),需要起步方案
- 现有 CLAUDE.md / AGENTS.md 膨胀到几百行,想精简
- docs/ 散乱,想重新组织成 agent 可导航的形态
- 要给某个项目做 harness 评审,作为引入更多 agent 工作的前置

**不要用本 skill**:

- **新项目**:用 `harness-bootstrap-new` skill,工作流完全不同(从零搭 vs 改存量)
- **只想要模板**:本 skill 不交付文件,只交付方案
- **agent 行为正常但用户想"再优化一下"**:大概率不该投资 harness,符合 v2 doc 第 6 章的反决策条件
- **跨项目的 harness 标准制定**:那是组织层的工作,本 skill 范围只到单项目

## 工作流总览

两阶段,严格按顺序执行。诊断阶段不出建议,处方阶段不再补诊断。

```
Phase 1: 诊断 (Diagnose)
  └─ 1a. 现状扫描(silent,读项目)
  └─ 1b. 交互式访谈(问用户)
  └─ 1c. 分层定位(在 v2 矩阵中定位)

Phase 2: 处方 (Prescribe)
  └─ 2a. Gap 分析(现状 vs 目标)
  └─ 2b. 投资优先级(哪一层先做)
  └─ 2c. 改造路线图(分阶段)
  └─ 2d. 反决策清单(明确不做什么)
  └─ 2e. 输出报告(标准格式)
```

每个子阶段的详细执行指引见 `workflows/` 目录(下面只给意图,不给细节)。

## Phase 1: 诊断

### 1a. 现状扫描(silent)

在向用户提问之前,先把能从仓库读出来的东西全部读完。目的是问问题之前已经有 80% 的 context,避免问用户已经在仓库里写明的事。

扫描清单:

- 根目录:CLAUDE.md / AGENTS.md / ARCHITECTURE.md / README.md
- 工具配置目录:.claude/(Claude Code)或 Codex 对应配置目录,内含 settings.json、hooks、commands、agents 等
- docs/ 整体结构:有没有、深度多少、是否有 index
- 最近 30 次 commit / PR:有没有 agent-generated 痕迹、是否有 revert
- 测试 / lint / type check 配置:覆盖率与执行频率
- 是否有 ADR 类长决策记录

输出:一份内部的 **现状结构图**,不给用户看,作为后续提问的依据。

详细扫描步骤见 `workflows/01-scan.md`。

### 1b. 交互式访谈

问 5-8 个问题,**一次一个**,根据回答动态调整下一个问题。不要一口气把问题清单倒给用户。

核心问题分布在三个维度:

- **阶段判断**:项目处于个人 / 小团队 / 生产级哪个阶段?目标是什么?
- **痛点识别**:最近 agent 反复出错的场景?返工最多的 PR 类型?
- **约束确认**:团队风险偏好?哪些操作绝对不允许 agent 自动做?是否有合规 / 安全硬约束?

问题模板和追问策略见 `workflows/02-interview.md`。

### 1c. 分层定位

把诊断结果映射到 v2 doc 的 **四层 × 三阶段矩阵**(见 references/harness-engineering-v2.md 的 1.2 节)。输出:

- 当前项目位于哪一格
- 当前 harness 的"实际所在层级"vs"应在层级"的差距
- 主要 gap 在四层中哪一层(机制 / 上下文策略 / 流程 / 组织)

## Phase 2: 处方

### 2a. Gap 分析

按四层逐层对比:

| 层 | 现状 | 目标(对应矩阵格子) | Gap |
|---|---|---|---|
| 机制层 | … | … | … |
| 上下文策略层 | … | … | … |
| 流程层 | … | … | … |
| 组织 / 度量层 | … | … | … |

对每个 gap,标记三种状态:
- 🔴 关键缺口(影响 agent 基本可用性)
- 🟡 应该补但不紧急
- 🟢 锦上添花,可以暂不处理

### 2b. 投资优先级

按 ROI 给出投资顺序。规则:

1. 红色 gap 优先于黄色优先于绿色
2. 同色 gap 之间,**低层优先**(测试 / lint 改造优先于 hook 优先于 prompt 规则改造)
3. **依赖关系**:某些改造需要前置(比如先建 docs/ 结构,再让 CLAUDE.md / AGENTS.md 变地图)
4. 单次改造的预估工作量必须合理(2 人日内能完成,否则继续拆)

详细优先级判断逻辑见 `workflows/03-prioritize.md`。

### 2c. 改造路线图

分阶段输出。每个阶段必须包含:

- 阶段目标(一句话)
- 具体改造项清单
- 验证标准(怎么知道这个阶段做完了)
- 预估时间
- 风险与回滚方案

典型阶段切分:
- **Sprint 1(1-2 周)**:止血,解决最频繁的 agent 失败
- **Sprint 2(2-4 周)**:结构化,docs/ 与分层规则
- **Sprint 3(后续)**:深化,sub-agent / 度量 / entropy 治理

### 2d. 反决策清单

明确告诉用户 **不要做** 的事情。这一段不能省。常见反决策来自 v2 doc 第 6 章,需要根据本项目实际情况筛选哪些适用。例如:

- 当前阶段不要建 sub-agent 体系(原因)
- 不要给 X 类操作加 hook(原因)
- 不要把现有 CLAUDE.md / AGENTS.md 直接精简到 30 行(原因:还没建 docs/)
- ……

### 2e. 输出报告

标准报告结构见 `references/report-template.md`。核心结构:

```
# Harness Audit Report: <项目名>

## 1. 现状摘要
## 2. 分层诊断(四层 × Gap)
## 3. 改造路线图
   - Sprint 1
   - Sprint 2
   - Sprint 3+
## 4. 反决策清单
## 5. 度量与 follow-up 建议
## 附录 A: 现状扫描结果
## 附录 B: 关键对话访谈记录
```

## 核心原则(执行时坚守)

引自 `references/harness-engineering-v2.md`,执行处方时反复对照:

- **能用 L4(测试 / lint)拦的,不要进 context**——见 v2 doc 2.2.2 规则分层架构
- **CLAUDE.md / AGENTS.md 是地图,不是手册**——见 v2 doc 2.2.3 知识库结构与导航
- **从低层优先**——测试 > skill > 规则 > prompt 提醒
- **模型变强 → harness 应该变薄**——见 v2 doc 8.3
- **可追溯性**:每条建议必须能追溯到一个诊断阶段的具体发现,不要凭空给规则

## 关键边界与拒绝条件

遇到以下情况,主动停止并告知用户:

- **诊断信息不足以出处方**:扫描+访谈仍无法判断关键约束(团队规模、风险偏好等)时,明确告诉用户"需要补充 X 信息才能出处方",不要凭直觉硬出
- **真正的痛点不在 harness 层**:有时候用户问 harness,实际问题是测试覆盖率、CI 不稳定、文档缺失等。这种情况要诚实指出:"你描述的问题更适合用 X 方式解决,加 harness 不会改善"
- **过度工程信号**:如果用户描述的项目落在 v2 doc 第 6 章的反决策条件里,建议不做改造而不是出方案
- **跨项目泄漏风险**:如果用户的诊断信息混进了其他项目的内容,要明确隔离,不要把项目 A 的方案套到项目 B

## 诊断时要警惕的反模式

扫描时主动识别以下信号,出现就标红:

| 信号 | 说明 | 处方方向 |
|---|---|---|
| CLAUDE.md / AGENTS.md > 200 行 | 通常是规则爆炸 | 重构为地图 + 下沉到 L1/L2 |
| 没有 docs/ 但 README 巨大 | 知识没有结构化 | 建立 docs/ 记录系统 |
| 有 hook 但没有 hook 日志 | 静默失败风险 | 加 hook 自身的健康检查 |
| 测试覆盖率低 + 规则文档多 | 该机制化的没机制化 | 把 L0 规则下沉到 L4 |
| Permission tier 全 auto 或全 ask | 边界设计缺失 | 重新设计三档矩阵 |
| 有 sub-agent 但没有 context handoff 协议 | 流程层埋雷 | 明确 handoff schema |
| docs/ 里有 active 但没有 completed | 没有案例库 | 引入 active/completed 分离 |
| 引入了 agent 但没度量 | 不知道有没有效果 | 起步先追三个指标 |

完整反模式目录见 `references/harness-engineering-v2.md` 第 7 章。

## 引用文档

- `references/harness-engineering-v2.md` — 完整方法论参考。**必读章节**:1.2(定位矩阵)、2.2(上下文策略层四个子节)、第 6 章(反决策)、第 7 章(失败模式目录)
- `references/report-template.md` — 输出报告标准模板(待补充)
- `workflows/01-scan.md` — 现状扫描详细步骤(待补充)
- `workflows/02-interview.md` — 访谈问题模板与追问策略(待补充)
- `workflows/03-prioritize.md` — 投资优先级判断逻辑(待补充)

## 维护信息

- **Last reviewed**: 2026-05
- **适用平台版本**: Claude Code(截至 2026-05 的 hook 体系)、Codex(实验性 hook 阶段)
- **审查触发**:CC 或 Codex 的 hook 体系变更、v2 doc 更新、积累 5 个以上 pilot 反馈
- **Owner**: (待填)
