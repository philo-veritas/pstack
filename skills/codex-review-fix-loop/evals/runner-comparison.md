# Python wrapper 与直接 `codex review` 对照评估（历史）

## 当前决策

自 2026-08-31 起，`codex-review-fix-loop` 按用户确认改为直接使用原生 `codex review`，并删除 `scripts/codex_review.py`。本文件保留 2026-07-20 的对照数据，作为输出噪声与维护成本的历史证据；原先“默认保留 wrapper”的建议已被本次决策取代。

本次取舍接受原生 CLI 输出较长的代价，换取不再维护文本解析器、vendored 副本和 wrapper 专属参数。review 质量与耗时不是决定因素；历史样本中两种方案的 verdict 一致。

## 评估范围

- 日期：2026-07-20
- Codex CLI：`0.144.6`
- 项目：`/Users/philoveritas/Projects/x-proj/pstack`
- 固定审查目标：commit `7877f55a00facdd50675fe1833b7896f14021d66`
- 每种方案运行 3 次
- 所有运行只读，运行前后 `git status --short` 一致

两个方案审查同一个 commit：

```bash
python skills/codex-review-fix-loop/scripts/codex_review.py \
  --cd /Users/philoveritas/Projects/x-proj/pstack \
  --commit 7877f55a00facdd50675fe1833b7896f14021d66
```

```bash
codex review --commit 7877f55a00facdd50675fe1833b7896f14021d66
```

## 结果

| 指标 | Python wrapper | 直接 CLI |
|---|---:|---:|
| 成功退出 | 3/3 | 3/3 |
| verdict 一致 | 3/3 clean | 3/3 clean |
| wall time | 46.94s / 51.33s / 71.56s | 38.07s / 45.32s / 53.45s |
| wall time 中位数 | 51.33s | 45.32s |
| 返回输出 | 每次 1 行，169–246 字符 | 已完整计量的运行分别为 238 行和 296 行 |
| 中间工具日志 | 无 | 有；详细运行包含 6 个完整工具区块和完整 diff |
| 最终结论重复 | 无 | 有；详细运行重复 2 次 |
| 非致命 stderr 警告 | 成功时被隐藏 | 可见 |

direct CLI 的两个完整计量样本分别产生 12,255 UTF-8 bytes 和 17,666 个 Unicode 字符。两者计量单位不同，不把它们合并成伪精确的字符范围；它们都远大于 wrapper 的 169–246 字符。

耗时差不能解释为 Python 带来了约 6 秒固定开销。`codex review` 每次都会重新执行非确定性的模型审查和工具调用，本次样本量也不足以隔离包装层成本。wrapper 的额外本地工作只是启动子进程并在完成后解析文本，选择方案时不应使用这组耗时差作为主要依据。

## 能力与代价

### Python wrapper（已移除）

收益：

- 只把最终 review 结论返回给上层 agent，显著减少循环每轮的上下文噪声。
- 提供 skill 内部可移植的 `--cd` 和 15 分钟 timeout。
- 把缺少命令、目录无效、超时、无 review 输出等失败转换成明确非零退出。

代价：

- 依赖 `codex review` 的文本标记（`codex`、`Review comment:`、`Full review comments:`）；CLI 输出格式变化时可能误解析。
- 使用 `capture_output=True`，运行期间没有进度输出，并在内存中保留完整原始输出直到进程结束。
- 成功退出时不展示 stderr，因此会隐藏本次 direct CLI 暴露的 models cache 警告。
- 与 `codex-collab` 维护 vendored 副本，需要同步两处。

### 直接 CLI（当前方案）

收益：

- 没有自维护文本解析器，CLI 输出格式变化时更容易诊断。
- 可直接观察进度、工具调用和非致命 stderr。
- 项目路径和 timeout 可以由调用工具的 `workdir` 与 timeout 参数提供。

代价：

- 把审查过程、完整 diff 和重复最终结论全部返回上层 agent；review/fix 多轮运行时重复放大上下文成本。
- 最终 verdict 可能淹没在长输出中，依赖工具截断策略时还有丢失关键尾部输出的风险。

## 建议

1. 默认直接运行 `codex review`；通过调用工具的 `workdir` 或原生 `codex -C <project-path> review ...` 指定项目。
2. 外层执行工具保留至少 15 分钟 timeout，并为原生输出提供足够的输出预算；结论被截断时不能视为 clean。
3. 读取最后一份完整 reviewer 结论，并把重复 verdict 视为同一轮结果；不要为压缩输出重新引入自维护文本解析器。
4. 后续若 CLI 提供稳定的 quiet、JSON 或仅输出 final message 的选项，优先采用原生能力。

## 评估限制

- 使用一个小型文档 commit，未覆盖大量 findings、review 失败和 timeout 场景。
- 两种方案由不同的独立 review 会话执行，模型输出非确定，不能比较逐字一致性。
- direct CLI 第一次确认运行只记录了时间，没有记录输出规模；输出规模结论基于另外两次完整计量运行。
