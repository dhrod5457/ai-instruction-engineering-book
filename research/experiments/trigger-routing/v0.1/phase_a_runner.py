#!/usr/bin/env python3
"""Run Phase A trigger-routing calibration against an installed coding-agent CLI.

Supported defaults:
- Claude Code
- Codex CLI
- Gemini CLI

Each prompt runs in a fresh materialized workspace. The runner never evaluates
the user's real repository and uses routing-only sentinel skills.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import harness

HERE = Path(__file__).resolve().parent
SENTINEL_RE = re.compile(r"SKILL_ACTIVATED:(feature|bugfix|refactor|review)")
PHASE_A_HOSTS = ("claude", "codex", "gemini")


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
    lines = (result.stdout or "").strip().splitlines()
    return lines[0] if lines else f"exit={result.returncode}"


def build_command(host: str, prompt: str, model: str | None) -> list[str]:
    if host == "claude":
        command = [
            "claude", "-p", prompt,
            "--output-format", "stream-json",
            "--verbose",
            "--no-session-persistence",
            "--permission-mode", "plan",
            "--setting-sources", "project",
            "--tools", "Skill,Read,Glob,Grep",
            "--strict-mcp-config",
            "--mcp-config", '{"mcpServers":{}}',
            "--no-chrome",
        ]
        if model:
            command += ["--model", model]
        return command

    if host == "codex":
        command = ["codex", "--sandbox", "read-only", "--ask-for-approval", "never", "exec", "--json"]
        if model:
            command += ["--model", model]
        command.append(prompt)
        return command

    if host == "gemini":
        command = [
            "gemini", "-p", prompt,
            "--output-format", "stream-json",
            "--approval-mode", "plan",
        ]
        if model:
            command += ["--model", model]
        return command

    raise RunnerError(f"unsupported Phase A host: {host}")


def recursive_activate_skill(value: Any) -> str | None:
    if isinstance(value, dict):
        tool_name = value.get("name") or value.get("tool_name") or value.get("tool")
        if tool_name == "activate_skill":
            args = (
                value.get("arguments")
                or value.get("args")
                or value.get("input")
                or value.get("parameters")
            )
            if isinstance(args, dict):
                name = args.get("name") or args.get("skill_name")
                if name in harness.SKILL_LABELS:
                    return str(name)
        for child in value.values():
            found = recursive_activate_skill(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = recursive_activate_skill(child)
            if found:
                return found
    return None


def parse_json_lines(text: str) -> list[Any]:
    values: list[Any] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            values.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return values


def extract_result(host: str, stdout: str, returncode: int) -> tuple[str, bool, str, bool]:
    # Commands, tool output and echoed skill bodies are not activation evidence.
    if returncode != 0:
        return "unobservable", False, "host-did-not-complete", False
    events = parse_json_lines(stdout)
    texts: list[str] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if host == "gemini":
            native = recursive_activate_skill(event)
            if native:
                return native, True, f"activate_skill:{native}", True
            if event.get("type") == "message" and event.get("role") == "assistant":
                texts.append(str(event.get("content", "")))
        elif host == "claude":
            if event.get("type") == "result" and not event.get("is_error", False):
                texts.append(str(event.get("result", "")))
            if event.get("type") == "assistant":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "text":
                        texts.append(str(block.get("text", "")))
        elif host == "codex" and event.get("type") == "item.completed":
            item = event.get("item", {})
            if item.get("type") == "agent_message":
                texts.append(str(item.get("text", "")))
    labels = {match.group(1) for text in texts
              if (match := SENTINEL_RE.fullmatch(text.strip()))}
    if len(labels) == 1:
        name = labels.pop()
        return name, True, f"sentinel:{name}", True
    if len(labels) > 1:
        return "unobservable", False, "multiple-activation-sentinels", True
    if host == "gemini" and any(
        isinstance(e, dict) and e.get("type") == "result"
        and e.get("status") == "success" for e in events
    ):
        return "none", True, "no-activate_skill-event", False
    return "unobservable", False, "no-reliable-activation-evidence", False


def partial_text(value: str | bytes | None) -> str:
    """TimeoutExpired carries bytes even when subprocess text mode is enabled."""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def init_git_repo(path: Path) -> None:
    git = shutil.which("git")
    if not git:
        return
    subprocess.run(
        [git, "init", "-q"],
        cwd=path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def run_one(
    *,
    host: str,
    variant: str,
    case: dict[str, Any],
    run_index: int,
    root: Path,
    model: str | None,
    timeout: int,
    host_version: str,
) -> dict[str, str]:
    run_id = f"{variant}__{case['id']}__r{run_index:02d}"
    run_root = root / run_id
    workspace = run_root / "workspace"
    raw = run_root / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    harness.materialize_fixture(
        variant_name=variant,
        host=host,
        output=workspace,
        force=False,
        base=HERE,
    )
    init_git_repo(workspace)

    command = build_command(host, str(case["prompt"]), model)
    (raw / "command.json").write_text(
        json.dumps(command, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    started = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            cwd=workspace,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env=os.environ.copy(),
            stdin=subprocess.DEVNULL,
        )
        returncode = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        note = "" if returncode == 0 else f"host-exit={returncode}"
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout = partial_text(exc.stdout)
        stderr = partial_text(exc.stderr)
        note = f"timeout>{timeout}s"

    latency_ms = int((time.monotonic() - started) * 1000)
    (raw / "stdout.jsonl").write_text(stdout, encoding="utf-8")
    (raw / "stderr.txt").write_text(stderr, encoding="utf-8")

    actual, observable, evidence, body_loaded = extract_result(host, stdout, returncode)
    row = {column: "" for column in harness.RESULT_COLUMNS}
    row.update({
        "experiment_version": "0.1",
        "date": utc_date(),
        "host": host,
        "host_version": host_version,
        "model": model or "host-default",
        "model_version": "",
        "variant": variant,
        "prompt_id": str(case["id"]),
        "run_index": str(run_index),
        "expected": str(case["expected"]),
        "actual": actual,
        "observable": str(observable).lower(),
        "routing_evidence": evidence,
        "latency_ms": str(latency_ms),
        "skill_body_loaded": str(body_loaded).lower(),
        "notes": note,
    })
    (raw / "result-row.json").write_text(
        json.dumps(row, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return row


def write_results(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=harness.RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def select_cases(ids: list[str] | None) -> list[dict[str, Any]]:
    cases = harness.load_json(HERE / "pilot-cases.json")["cases"]
    if not ids:
        return cases
    index = {case["id"]: case for case in cases}
    missing = [case_id for case_id in ids if case_id not in index]
    if missing:
        raise RunnerError(f"unknown pilot case IDs: {missing}")
    return [index[case_id] for case_id in ids]


def preflight(host: str) -> dict[str, str]:
    if host not in PHASE_A_HOSTS:
        raise RunnerError(f"host must be one of {PHASE_A_HOSTS}")
    binary = {"claude": "claude", "codex": "codex", "gemini": "gemini"}[host]
    path = shutil.which(binary)
    if not path:
        raise RunnerError(f"{binary!r} is not installed or not on PATH")
    return {"binary": path, "host_version": command_version(binary)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, choices=PHASE_A_HOSTS)
    parser.add_argument("--variant", action="append", choices=harness.VARIANTS)
    parser.add_argument("--case", action="append", help="pilot case ID; repeat to select multiple")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--model", help="exact model name; recommended for reproducible results")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--out", required=True, help="output directory for raw artifacts and results.csv")
    parser.add_argument("--preflight-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        errors = harness.validate_fixture(HERE)
        if errors:
            raise RunnerError("fixture validation failed:\n" + "\n".join(errors))

        info = preflight(args.host)
        print(json.dumps(info, ensure_ascii=False))

        if args.preflight_only:
            return 0
        if args.runs < 1:
            raise RunnerError("--runs must be >= 1")
        if args.timeout < 1:
            raise RunnerError("--timeout must be >= 1")

        variants = args.variant or list(harness.VARIANTS)
        cases = select_cases(args.case)
        out = Path(args.out).resolve()
        rows: list[dict[str, str]] = []

        for variant in variants:
            for case in cases:
                for run_index in range(1, args.runs + 1):
                    print(f"[{args.host}] {variant} {case['id']} run={run_index}", flush=True)
                    row = run_one(
                        host=args.host,
                        variant=variant,
                        case=case,
                        run_index=run_index,
                        root=out / "raw",
                        model=args.model,
                        timeout=args.timeout,
                        host_version=info["host_version"],
                    )
                    rows.append(row)
                    write_results(out / "results.csv", rows)

        report = harness.score_results(out / "results.csv", HERE)
        (out / "score.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (out / "score.md").write_text(
            harness.report_markdown(report),
            encoding="utf-8",
        )
        return 0
    except (RunnerError, harness.HarnessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
