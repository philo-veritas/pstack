---
name: codex-collab
description: |
  让 Claude Code 与 OpenAI Codex CLI 协作完成编码任务。通过内置脚本调用 codex exec，
  支持多轮会话、需求分析、代码原型获取和代码审查。
  当用户提到"用 codex"、"让 codex 看看"、"codex review"时触发此 skill。
  在以下场景也应主动建议使用：
  - 复杂编码任务需要第二意见来完善需求分析和实施计划时
  - plan mode 下生成计划后需要独立审查时（"让 codex review plan"、"codex 看下计划"）
  - 编码完成后需要进行代码审查时
  - 排查棘手 bug 或精准定位问题时
  - 需要快速获取代码实现原型时
  即使用户没有明确提到 codex，只要任务复杂度足以受益于双 AI 协作，就应考虑使用。
---

# Codex 协作 Skill

## 核心理念

在任何编码过程中，始终思考当前任务是否可以借助 codex 获得更全面、更客观的分析。Claude 负责架构设计与全局把控，Codex 负责代码生成细节和独立审查视角——两个独立推理路径交叉验证，暴露单一视角的盲区。

## 前置要求

- Python 3.12+
- [Codex CLI](https://developers.openai.com/codex/quickstart) 已安装且 `codex` 命令可用（版本 >= v0.61.0）

## 调用 Codex

通过 Bash 执行内置脚本 `scripts/codex_exec.py`，脚本路径相对于此 SKILL.md 所在目录。

```bash
python <skill-dir>/scripts/codex_exec.py \
  --prompt "你的指令" \
  --cd /path/to/repo \
  [--sandbox read-only] \
  [--session-id <uuid>] \
  [--all-messages]
```

### 参数

| 参数 | 必选 | 默认值 | 说明 |
|------|------|--------|------|
| `--prompt` | 是 | - | 发送给 codex 的任务指令 |
| `--cd` | 是 | - | 工作目录根路径（必须存在，否则静默失败） |
| `--sandbox` | 否 | `read-only` | `read-only` / `workspace-write` / `danger-full-access` |
| `--session-id` | 否 | 空（新会话） | 传入上次返回的 session_id 可继续对话 |
| `--all-messages` | 否 | false | 包含完整推理过程（用于追踪 codex 的推理和工具调用） |
| `--model` | 否 | 空 | 仅在用户明确指定时使用 |
| `--profile` | 否 | 空 | 仅在用户明确指定时使用 |
| `--yolo` | 否 | false | 跳过沙箱，慎用 |
| `--image` | 否 | 空 | 逗号分隔的图片路径 |

### 安全约束

默认且推荐使用 `--sandbox read-only`。严禁 codex 对代码进行实际修改——需要代码时只让它给出 unified diff patch。这是整个协作模式的安全基石：codex 提供思路，你来执行。

### 返回值

脚本输出 JSON 到 stdout：

```json
{"success": true, "session_id": "uuid-string", "agent_messages": "codex 的回复"}
```
```json
{"success": false, "error": "错误描述"}
```

每次调用后检查 `success` 字段做错误处理。

### 会话管理

每次成功调用都会返回 `session_id`。在对话中维护一个变量 `CODEX_SESSION_ID`：
- 首次调用：不传 `--session-id`，从返回值中提取并记住 `session_id`
- 后续调用：传入 `--session-id <CODEX_SESSION_ID>` 以延续上下文
- 切换到不相关的新任务时：丢弃旧 session_id，开启新会话

始终追踪 `CODEX_SESSION_ID`，避免会话混乱。

## 协作工作流

### 1. 需求分析 — 让 codex 补充你的盲区

对用户需求形成初步分析后，将需求和初始思路告知 codex，要求它完善需求分析和实施计划。

**示例 prompt：**
```
用户需求：{需求描述}

我的初步分析：{你的分析}

请从以下角度补充：
1. 我的分析是否有遗漏的边界情况？
2. 实施计划是否合理？有什么更优方案？
3. 有哪些潜在风险？
```

### 2. Plan 审查 — 让 codex 审查实施计划

在 plan mode 下生成计划后，可以让 codex 从独立视角审查。codex 运行在独立进程中，无法访问你的对话上下文，所以发送给 codex 的 prompt **必须内嵌完整的 plan 内容**，不能只说"请审查当前计划"。

构建 prompt 的步骤：
1. 从当前对话上下文中提取完整的 plan 文本
2. 将 plan 文本嵌入 prompt，连同项目背景一起发送
3. 明确要求 codex 从哪些角度审查

**示例 prompt：**
```
请审查以下实施计划，给出你的评估和改进建议。

## 项目背景
{项目简要描述和当前需求}

## 实施计划
{完整的 plan 内容，逐条列出}

## 审查要点
1. 步骤顺序是否合理？是否有依赖关系被忽略？
2. 是否有遗漏的关键步骤？
3. 各步骤的技术方案是否恰当？有无更优选择？
4. 是否存在潜在的风险或副作用？
5. 预估的改动范围是否准确？
```

codex 反馈后，批判性地评估其意见，合理的建议更新到 plan 中，不合理的说明理由忽略。

### 3. 代码原型 — 用 codex 的实现作为参考（可选）

编码前向 codex 索要代码实现原型。这不是"让 codex 写代码然后直接用"，而是获取一个独立的实现思路，然后你重写为生产级代码。

- 要求 codex 仅给出 unified diff patch，严禁对代码做任何真实修改
- 使用 `--sandbox read-only` 确保安全
- 拿到原型后，以此为逻辑参考，重写为高可读性、高可维护性的生产代码

**示例 prompt：**
```
请为以下需求给出代码实现原型，仅输出 unified diff patch，不要做任何真实修改：

{需求描述}

涉及文件：{文件列表}
```

### 4. 代码审查 — 编码完成后立即执行

每次完成编码后，立即让 codex 审查改动。独立的 AI 审查视角能捕获你自己不容易发现的问题。

通过 Bash 执行内置包装脚本 `scripts/codex_review.py` 调用 `codex review`。脚本会自动过滤 codex 输出中 2000+ 行的工具日志和中间推理，只返回审查摘要和 "Full review comments" 区块。审查标准参考 `references/review_guidelines.md`。

codex review 通常需要 2-5 分钟。调用时务必设置 Bash timeout 为 300000（5 分钟），避免被自动转为后台任务。

**常用命令：**
```bash
# 审查未提交改动（staged + unstaged + untracked）
python <skill-dir>/scripts/codex_review.py --uncommitted

# 审查未提交改动，附加自定义审查要求
python <skill-dir>/scripts/codex_review.py --uncommitted "只关注安全性和并发问题"

# 审查相对于某分支的改动
python <skill-dir>/scripts/codex_review.py --base main

# 审查某次提交
python <skill-dir>/scripts/codex_review.py --commit <sha>
```

所有参数直接透传给 `codex review`，可通过 prompt 参数传入自定义审查要求。

**`codex review` vs `codex exec` 的区别：**
- `codex review`（通过 `scripts/codex_review.py` 调用）是专用审查命令，自动获取 diff 内容，输出已过滤
- `codex review` 不返回 `session_id`，不支持多轮对话
- 需要多轮讨论审查意见时，仍用 `codex exec`（通过 `codex_exec.py` 脚本）继续对话

**续接审查讨论：**

拿到审查结果后，如需追问细节，用 `codex_exec.py` 开启新会话，将审查结论嵌入 prompt：

```
以下是 codex review 对本次改动的审查意见：

{粘贴 review 输出}

我想针对以下问题深入讨论：
{具体问题}
```

### 5. 独立思考 — 尽信书则不如无书

codex 只能给出参考，你必须有自己的判断，甚至需要对 codex 的回答提出质疑。你与 codex 的最终使命是达成全面、精准的意见，所以要通过不断争辩来逼近更好的方案：

- 批判性评估每一条建议——它可能遗漏了上下文，也可能过度谨慎
- 不同意就说明理由，把你的反驳再发给 codex 继续讨论（利用 session_id 保持上下文）
- 最终决策权在你这里

## 何时主动建议使用 Codex

不必等用户开口。在以下场景应主动提议：

- **复杂架构决策**：涉及多模块的改动、API 设计、数据模型变更
- **Plan 审查**：在 plan mode 下完成计划后，建议让 codex 审查步骤完整性和技术方案
- **编码完成后的审查**：任何超过 50 行的代码改动都值得让 codex 看一眼
- **数据密集型脚本**：包含大量硬编码数据、统计数字或测试 fixture 的文件——人容易对数字脱敏，AI 不会
- **棘手的 bug**：单独排查无果时，让 codex 从不同角度分析
- **精准定位问题**：需要快速缩小排查范围时
- **代码原型快速获取**：需要在多种实现方案中做选择时

主动建议时简洁说明原因，比如："这个改动涉及 3 个模块的联动，建议让 codex 从另一个角度审查一下，要不要试试？"

## 错误处理

- 如果脚本返回 `success: false`，检查 `error` 字段并告知用户
- 常见问题：codex CLI 未安装、API key 未配置、网络超时
- 遇到 `session_id` 获取失败时，不要重试同一个 session，直接开新会话
