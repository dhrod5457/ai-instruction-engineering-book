#!/usr/bin/env python3
"""Run Experiment B S0/S1 pilot against Claude Code or Codex CLI.

Each task gets a fresh synthetic workspace. The real repository is never used
as the agent workspace. Results are graded by scope_harness.py.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import scope_harness as scope

HERE = Path(__file__).resolve().parent
HOSTS = ("claude", "codex")
RESULT_COLUMNS = (
    "experiment_version",
    "date",
    "host",
    "host_version",
    "model",
    "variant",
    "task_id",
    "task_class",
    "run_index",
    "agent_exit_code",
    "latency_ms",
    "passed",
    "changed_file_count",
    "out_of_scope_count",
    "missing_validation_count",
    "forbidden_validation_count",
    "invariant_failure_count",
    "assertion_failure_count",
    "fixture_instruction_bytes",
    "raw_dir",
    "notes",
)


class RunnerError(RuntimeError):
    pass


def utc_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def command_version(binary: str) -> str:
    try:
        result = subprocess.run(
            [binary, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=15,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RunnerError(f"{binary!r} is not installed or not on PATH") from exc
    line = (result.stdout or "").strip().splitlines()
    return line[0] if line else f"exit={result.returncode}"


def preflight(host: str) -> dict[str, str]:
    binary = {"claude": "claude", "codex": "codex"}[host]
    path = shutil.which(binary)
    if not path:
        raise RunnerError(f"{binary!r} is not installed or not on PATH")
    version = command_version(binary)
    if host == "claude":
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", version)
        if not match or tuple(map(int, match.groups())) < (2, 1, 277):
            raise RunnerError("native AGENTS.md smoke requires Claude Code >= 2.1.277; check PATH")
    return {"binary": path, "host_version": version}


def init_git_repo(path: Path) -> None:
    git = shutil.which("git")
    if not git:
        raise RunnerError("git is required for the scope-placement fixture")
    result = subprocess.run(
        [git, "init", "-q"],
        cwd=path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RunnerError(f"git init failed: {result.stderr.strip()}")


def claude_settings_json() -> str:
    return json.dumps({
        "pluginConfigs": {
            "agents-md@builtin": {
                "options": {
                    "instructionFiles": "claude-md-and-agents-md"
                }
            }
        }
    }, separators=(",", ":"))


def build_command(host: str, prompt: str, model: str | None, workspace: Path | None = None) -> list[str]:
    if host == "claude":
        command = [
            "claude",
            "-p",
            prompt,
            "--output-format",
            "stream-json",
            "--verbose",
            "--no-session-persistence",
            "--permission-mode",
            "acceptEdits",
            "--permission-prompts",
            "none",
            "--tools",
            "Bash,Edit,Read,Glob,Grep",
            "--allowedTools",
            "Bash(python3 *scripts/verify.py*)",
            "Bash(git status *)",
            "Bash(git diff *)",
            "--disallowedTools",
            "mcp__*",
            "--setting-sources",
            "project",
            "--settings",
            claude_settings_json(),
            "--no-chrome",
        ]
        if model:
            command += ["--model", model]
        return command

    if host == "codex":
        command = [
            "codex",
            "--sandbox",
            "workspace-write",
            "--ask-for-approval",
            "never",
        ]
        if model:
            command += ["--model", model]
        if workspace is not None:
            command += ["--add-dir", str(workspace.resolve())]
        command += ["exec", "--json", prompt]
        return command

    raise RunnerError(f"unsupported host: {host}")


def tasks_by_id() -> dict[str, dict[str, Any]]:
    data = scope.load_json(HERE / "pilot-tasks.json")
    return {task["id"]: task for task in data["tasks"]}


def select_tasks(ids: list[str] | None) -> list[dict[str, Any]]:
    index = tasks_by_id()
    if not ids:
        return list(index.values())
    missing = [task_id for task_id in ids if task_id not in index]
    if missing:
        raise RunnerError(f"unknown task IDs: {missing}")
    return [index[task_id] for task_id in ids]


def safe_slug(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in value)


def run_one(
    *,
    host: str,
    variant: str,
    task: dict[str, Any],
    run_index: int,
    root: Path,
    model: str | None,
    timeout: int,
    host_version: str,
) -> dict[str, str]:
    run_name = f"{variant}__{task['id']}__r{run_index:02d}"
    run_root = root / run_name
    workspace = run_root / "workspace"
    raw = run_root / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    scope.materialize(variant, workspace, base=HERE)
    init_git_repo(workspace)

    working_dir = workspace if task["working_dir"] == "." else workspace / task["working_dir"]
    if not working_dir.is_dir():
        raise RunnerError(f"task {task['id']} working_dir missing: {working_dir}")

    command = build_command(host, str(task["prompt"]), model, workspace)
    (raw / "command.json").write_text(
        json.dumps(command, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (raw / "task.json").write_text(
        json.dumps(task, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    started = time.monotonic()
    notes: list[str] = []
    try:
        proc = subprocess.run(
            command,
            cwd=working_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env=os.environ.copy(),
            stdin=subprocess.DEVNULL,
        )
        exit_code = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        if exit_code != 0:
            notes.append(f"agent-exit={exit_code}")
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        notes.append(f"timeout>{timeout}s")

    latency_ms = int((time.monotonic() - started) * 1000)
    (raw / "stdout.jsonl").write_text(stdout, encoding="utf-8")
    (raw / "stderr.txt").write_text(stderr, encoding="utf-8")

    grade = scope.grade(workspace, task["id"], base=HERE)
    (raw / "grade.json").write_text(
        json.dumps(grade, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (raw / "grade.md").write_text(
        scope.report_markdown(grade),
        encoding="utf-8",
    )

    assertion_failures = sum(1 for item in grade["assertions"] if not item["passed"])
    row = {column: "" for column in RESULT_COLUMNS}
    row.update({
        "experiment_version": str(grade["experiment_version"]),
        "date": utc_date(),
        "host": host,
        "host_version": host_version,
        "model": model or "host-default",
        "variant": variant,
        "task_id": task["id"],
        "task_class": task["class"],
        "run_index": str(run_index),
        "agent_exit_code": str(exit_code),
        "latency_ms": str(latency_ms),
        "passed": str(bool(grade["passed"])).lower(),
        "changed_file_count": str(len(grade["changed_files"])),
        "out_of_scope_count": str(len(grade["out_of_scope_files"])),
        "missing_validation_count": str(len(grade["missing_required_validation"])),
        "forbidden_validation_count": str(len(grade["forbidden_validation_observed"])),
        "invariant_failure_count": str(len(grade["invariant_failures"])),
        "assertion_failure_count": str(assertion_failures),
        "fixture_instruction_bytes": str(grade["fixture_instruction_bytes"]),
        "raw_dir": str(raw),
        "notes": ";".join(notes),
    })
    return row


def write_results(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def as_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def summarize(rows: list[dict[str, str]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["host"], row["variant"])].append(row)

    result_groups = []
    for (host, variant), items in sorted(groups.items()):
        n = len(items)
        passed = sum(as_bool(item["passed"]) for item in items)
        result_groups.append({
            "host": host,
            "variant": variant,
            "runs": n,
            "pass_rate": passed / n if n else None,
            "out_of_scope_rate": sum(as_int(i["out_of_scope_count"]) > 0 for i in items) / n if n else None,
            "validation_miss_rate": sum(as_int(i["missing_validation_count"]) > 0 for i in items) / n if n else None,
            "over_verification_rate": sum(as_int(i["forbidden_validation_count"]) > 0 for i in items) / n if n else None,
            "invariant_failure_rate": sum(as_int(i["invariant_failure_count"]) > 0 for i in items) / n if n else None,
            "assertion_failure_rate": sum(as_int(i["assertion_failure_count"]) > 0 for i in items) / n if n else None,
            "mean_latency_ms": sum(as_int(i["latency_ms"]) for i in items) / n if n else None,
        })
    return {"groups": result_groups}


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Scope Placement Pilot Summary",
        "",
        "| Host | Variant | Runs | Pass | Scope leak | Validation miss | Over-verify | Invariant fail | Assertion fail |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for group in summary["groups"]:
        lines.append(
            f"| {group['host']} | {group['variant']} | {group['runs']} | "
            f"{fmt_pct(group['pass_rate'])} | {fmt_pct(group['out_of_scope_rate'])} | "
            f"{fmt_pct(group['validation_miss_rate'])} | {fmt_pct(group['over_verification_rate'])} | "
            f"{fmt_pct(group['invariant_failure_rate'])} | {fmt_pct(group['assertion_failure_rate'])} |"
        )
    lines += [
        "",
        "These are calibration metrics. They are not publication-level claims.",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, choices=HOSTS)
    parser.add_argument("--variant", action="append", choices=scope.VARIANTS)
    parser.add_argument("--task", action="append")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--out", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        errors = scope.validate_definition(HERE)
        if errors:
            raise RunnerError("fixture invalid:\n" + "\n".join(errors))
        if args.runs < 1:
            raise RunnerError("--runs must be >= 1")
        if args.timeout < 1:
            raise RunnerError("--timeout must be >= 1")

        info = preflight(args.host)
        print(json.dumps(info, ensure_ascii=False))
        if args.preflight_only:
            return 0

        variants = args.variant or list(scope.VARIANTS)
        tasks = select_tasks(args.task)
        out = Path(args.out).resolve()
        rows: list[dict[str, str]] = []

        for variant in variants:
            for task in tasks:
                for run_index in range(1, args.runs + 1):
                    print(
                        f"[{args.host}] {variant} {task['id']} run={run_index}",
                        flush=True,
                    )
                    row = run_one(
                        host=args.host,
                        variant=variant,
                        task=task,
                        run_index=run_index,
                        root=out / "runs",
                        model=args.model,
                        timeout=args.timeout,
                        host_version=info["host_version"],
                    )
                    rows.append(row)
                    write_results(out / "results.csv", rows)

        summary = summarize(rows)
        (out / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (out / "summary.md").write_text(
            summary_markdown(summary),
            encoding="utf-8",
        )
        return 0

    except (RunnerError, scope.ScopeHarnessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
