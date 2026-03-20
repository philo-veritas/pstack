#!/usr/bin/env python3
"""Execute a Codex CLI session and return structured JSON results.

Usage:
    python codex_exec.py --prompt "..." --cd /path/to/repo [options]

Options:
    --prompt        Task instruction for codex (required)
    --cd            Workspace root directory (required)
    --sandbox       read-only | workspace-write | danger-full-access (default: read-only)
    --session-id    Resume a previous session by UUID
    --image         Comma-separated image file paths
    --model         Model override (only when user explicitly specifies)
    --profile       Config profile from ~/.codex/config.toml
    --yolo          Skip sandbox, run all commands without approval
    --skip-git-repo-check  Allow running outside a Git repository
    --all-messages  Include full reasoning trace in output

Output: JSON to stdout
    {"success": true, "session_id": "uuid", "agent_messages": "..."}
    {"success": false, "error": "..."}
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from typing import Any, Generator, Optional


def run_shell_command(cmd: list[str]) -> Generator[str, None, None]:
    popen_cmd = cmd.copy()
    codex_path = shutil.which("codex") or cmd[0]
    popen_cmd[0] = codex_path

    process = subprocess.Popen(
        popen_cmd,
        shell=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding="utf-8",
    )

    output_queue: queue.Queue[str | None] = queue.Queue()
    GRACEFUL_SHUTDOWN_DELAY = 0.3

    def is_turn_completed(line: str) -> bool:
        try:
            data = json.loads(line)
            return data.get("type") == "turn.completed"
        except (json.JSONDecodeError, AttributeError, TypeError):
            return False

    def read_output() -> None:
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                stripped = line.strip()
                output_queue.put(stripped)
                if is_turn_completed(stripped):
                    time.sleep(GRACEFUL_SHUTDOWN_DELAY)
                    process.terminate()
                    break
            process.stdout.close()
        output_queue.put(None)

    thread = threading.Thread(target=read_output)
    thread.start()

    while True:
        try:
            line = output_queue.get(timeout=0.5)
            if line is None:
                break
            yield line
        except queue.Empty:
            if process.poll() is not None and not thread.is_alive():
                break

    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    thread.join(timeout=5)

    while not output_queue.empty():
        try:
            line = output_queue.get_nowait()
            if line is not None:
                yield line
        except queue.Empty:
            break


def windows_escape(prompt: str) -> str:
    result = prompt.replace("\\", "\\\\")
    result = result.replace('"', '\\"')
    result = result.replace("\n", "\\n")
    result = result.replace("\r", "\\r")
    result = result.replace("\t", "\\t")
    result = result.replace("\b", "\\b")
    result = result.replace("\f", "\\f")
    result = result.replace("'", "\\'")
    return result


def run_codex(args: argparse.Namespace) -> dict[str, Any]:
    cmd = ["codex", "exec", "--sandbox", args.sandbox, "--cd", args.cd, "--json"]

    if args.image:
        cmd.extend(["--image", args.image])
    if args.model:
        cmd.extend(["--model", args.model])
    if args.profile:
        cmd.extend(["--profile", args.profile])
    if args.yolo:
        cmd.append("--yolo")
    if args.skip_git_repo_check:
        cmd.append("--skip-git-repo-check")
    if args.session_id:
        cmd.extend(["resume", args.session_id])

    prompt = args.prompt
    if os.name == "nt":
        prompt = windows_escape(prompt)
    cmd += ["--", prompt]

    all_messages: list[dict[str, Any]] = []
    agent_messages = ""
    success = True
    err_message = ""
    thread_id: Optional[str] = None

    for line in run_shell_command(cmd):
        try:
            line_dict = json.loads(line.strip())
            all_messages.append(line_dict)
            item = line_dict.get("item", {})
            if item.get("type") == "agent_message":
                agent_messages += item.get("text", "")
            if line_dict.get("thread_id") is not None:
                thread_id = line_dict.get("thread_id")
            if "fail" in line_dict.get("type", ""):
                if not agent_messages:
                    success = False
                err_message += "\n\n[codex error] " + line_dict.get("error", {}).get("message", "")
            if "error" in line_dict.get("type", ""):
                error_msg = line_dict.get("message", "")
                is_reconnecting = bool(re.match(r"^Reconnecting\.\.\.\s+\d+/\d+", error_msg))
                if not is_reconnecting:
                    if not agent_messages:
                        success = False
                    err_message += "\n\n[codex error] " + error_msg
        except json.JSONDecodeError:
            err_message += "\n\n[json decode error] " + line
            continue
        except Exception as error:
            err_message += f"\n\n[unexpected error] {error}. Line: {line!r}"
            success = False
            break

    if thread_id is None:
        success = False
        err_message = "Failed to get SESSION_ID from codex.\n\n" + err_message
    if not agent_messages:
        success = False
        err_message = "Failed to get agent_messages from codex.\n\n" + err_message

    if success:
        result: dict[str, Any] = {
            "success": True,
            "session_id": thread_id,
            "agent_messages": agent_messages,
        }
    else:
        result = {"success": False, "error": err_message}

    if args.all_messages:
        result["all_messages"] = all_messages

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute a Codex CLI session")
    parser.add_argument("--prompt", required=True, help="Task instruction for codex")
    parser.add_argument("--cd", required=True, help="Workspace root directory")
    parser.add_argument("--sandbox", default="read-only",
                        choices=["read-only", "workspace-write", "danger-full-access"])
    parser.add_argument("--session-id", default="", help="Resume a previous session")
    parser.add_argument("--image", default="", help="Comma-separated image paths")
    parser.add_argument("--model", default="", help="Model override")
    parser.add_argument("--profile", default="", help="Config profile name")
    parser.add_argument("--yolo", action="store_true", help="Skip sandbox")
    parser.add_argument("--skip-git-repo-check", action="store_true", default=True)
    parser.add_argument("--all-messages", action="store_true", help="Include full trace")
    args = parser.parse_args()

    result = run_codex(args)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
