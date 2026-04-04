#!/usr/bin/env python3
"""codex review 输出过滤器。

codex review 会输出 2000+ 行的工具执行日志、diff 和中间推理，
但有用信息只在末尾的审查结论。本脚本运行 codex review 后自动提取
摘要和 "Full review comments:" 区块，大幅减少 token 消耗。

用法（参数直接透传给 codex review）：
    python codex_review.py --uncommitted
    python codex_review.py --uncommitted "只关注安全性"
    python codex_review.py --base main
    python codex_review.py --commit <sha>
"""

from __future__ import annotations

import subprocess
import sys


_REVIEW_FALLBACK = "Reviewer failed to output a response."

_REVIEW_HEADERS = ("Full review comments:", "Review comment:")


def _deduplicate(text: str) -> str:
    """codex 会将审查结论输出两遍（流式 + 最终），尝试去重。"""
    text_lines = text.splitlines()
    n = len(text_lines)
    if n < 2:
        return text
    for mid in range(max(1, n // 2 - 2), min(n, n // 2 + 3)):
        first = "\n".join(text_lines[:mid]).strip()
        second = "\n".join(text_lines[mid:]).strip()
        if first and first == second:
            return first
    return text


def extract_review(output: str) -> str:
    """从 codex review 完整输出中提取审查结论。

    codex review 的输出结构（render_review_output_text）：
    - 有 findings：explanation + "Full review comments:"/"Review comment:" + 逐条评论
    - 无 findings：仅 explanation
    - 完全无输出："Reviewer failed to output a response."

    原始输出中结论会出现两遍（流式 + 最终），本函数取最后一份并去重。
    """
    lines = output.splitlines()

    # 策略 1：有 findings — 找最后一个审查区块 header，连同前面的摘要段落一起提取
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() in _REVIEW_HEADERS:
            start = i
            j = i - 1
            # 跳过 header 前的空行
            while j >= 0 and lines[j].strip() == "":
                j -= 1
            # 向上收集摘要行：非缩进、非审查条目的行，遇到 "codex" 响应标记停止
            while j >= 0:
                line = lines[j]
                if line.strip() == "codex":
                    break
                if line and not line[0].isspace() and not line.startswith("- [P"):
                    start = j
                    j -= 1
                else:
                    break
            return "\n".join(lines[start:]).strip()

    # 策略 2：完全无输出 — 匹配 codex 的回退消息
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == _REVIEW_FALLBACK:
            return _REVIEW_FALLBACK

    # 策略 3：无 findings 但有 explanation — 找最后一个 "codex" 响应标记，取其后内容并去重
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "codex" and i < len(lines) - 1:
            return _deduplicate("\n".join(lines[i + 1 :]).strip())

    # 兜底：返回最后 30 行
    return "\n".join(lines[-30:]).strip() if len(lines) > 30 else output.strip()


def main() -> None:
    cmd = ["codex", "review"] + sys.argv[1:]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        print("Error: codex review 超时（10 分钟）", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 未找到 codex 命令", file=sys.stderr)
        sys.exit(1)

    if not result.stdout and result.returncode != 0:
        print(f"codex review 失败（exit {result.returncode}）", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    review = extract_review(result.stdout or "")
    if review:
        print(review)
    else:
        print("未捕获到审查输出", file=sys.stderr)
        sys.exit(1)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
