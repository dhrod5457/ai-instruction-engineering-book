#!/usr/bin/env python3
"""Materialize and grade Experiment B scope-placement fixtures.

This harness compares:
- S0: monolithic root AGENTS.md containing all rules
- S1: root global AGENTS.md + nested subsystem AGENTS.md files

It uses only the Python standard library and creates a synthetic repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
VARIANTS = ("S0_monolithic_root", "S1_nested_agents")
WORKLOAD_ROOTS = ("backend", "frontend", "deploy", "docs")


class ScopeHarnessError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ScopeHarnessError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ScopeHarnessError(f"invalid JSON: {path}: {exc}") from exc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rule_map(rules: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for group in ("global", "backend", "frontend", "deploy", "docs"):
        for item in rules.get(group, []):
            out[item["id"]] = item["text"]
    return out


def validate_definition(base: Path = HERE) -> list[str]:
    errors: list[str] = []
    rules = load_json(base / "rules.json")
    tasks = load_json(base / "pilot-tasks.json")

    if rules.get("version") != "0.1":
        errors.append("rules.json version must be 0.1")
    if tasks.get("version") != "0.1":
        errors.append("pilot-tasks.json version must be 0.1")

    ids: list[str] = []
    known_rules = set(rule_map(rules))
    for task in tasks.get("tasks", []):
        task_id = task.get("id")
        ids.append(task_id)
        if not task_id:
            errors.append("task with empty id")
        if not str(task.get("prompt", "")).strip():
            errors.append(f"{task_id}: empty prompt")
        if task.get("working_dir") is None:
            errors.append(f"{task_id}: missing working_dir")
        if not task.get("allowed_files"):
            errors.append(f"{task_id}: allowed_files must not be empty")
        unknown = sorted(set(task.get("required_rules", [])) - known_rules)
        if unknown:
            errors.append(f"{task_id}: unknown required_rules {unknown}")
        overlap = set(task.get("required_validation", [])) & set(task.get("forbidden_validation", []))
        if overlap:
            errors.append(f"{task_id}: validation target both required and forbidden: {sorted(overlap)}")

    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append(f"duplicate task ids: {duplicates}")
    if len(ids) != 12:
        errors.append(f"pilot must contain 12 tasks, found {len(ids)}")

    return errors


def baseline_files() -> dict[str, str]:
    return {
        "backend/src/main/java/com/example/order/OrderController.java": """package com.example.order;

public final class OrderController {
    private final OrderService service;

    public OrderController(OrderService service) {
        this.service = service;
    }

    public String getOrder(String id) {
        return service.findOrder(id);
    }
}
""",
        "backend/src/main/java/com/example/order/OrderService.java": """package com.example.order;

public final class OrderService {
    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }

    public String findOrder(String id) {
        return repository.findById(id);
    }

    public String normalizeStatus(String status) {
        return status == null ? "UNKNOWN" : status;
    }
}
""",
        "backend/src/main/java/com/example/order/OrderRepository.java": """package com.example.order;

public final class OrderRepository {
    public String findById(String id) {
        return "ORDER-" + id;
    }
}
""",
        "backend/src/test/java/com/example/order/OrderServiceTest.java": """package com.example.order;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class OrderServiceTest {
    @Test
    void findsOrder() {
        var service = new OrderService(new OrderRepository());
        assertEquals("ORDER-1", service.findOrder("1"));
    }
}
""",
        "frontend/src/OrderPage.tsx": """import { loadOrders } from "./orderApi";

export function OrderPage() {
  const orders = loadOrders();
  return <main>{orders.length} orders</main>;
}
""",
        "frontend/src/orderApi.ts": """export function loadOrders(): string[] {
  return ["ORDER-1"];
}
""",
        "frontend/test/OrderPage.test.tsx": """import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { OrderPage } from "../src/OrderPage";

describe("OrderPage", () => {
  it("shows the order count", () => {
    render(<OrderPage />);
    expect(screen.getByText("1 orders")).toBeTruthy();
  });
});
""",
        "deploy/deployment.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders
spec:
  template:
    spec:
      containers:
        - name: orders
          image: example/orders:1.0.0
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
""",
        "deploy/values.yaml": """replicaCount: 2
environment: production
""",
        "docs/api.md": """# Orders API

The service exposes order endpoints under /api/orders.
""",
        "docs/operations.md": """# Operations

Deploy manifests live under deploy/.
""",
    }


def render_rules(title: str, items: list[dict[str, str]]) -> str:
    lines = [f"# {title}", "", "Follow these repository instructions.", ""]
    for item in items:
        lines.append(f"- [{item['id']}] {item['text']}")
    lines.append("")
    return "\n".join(lines)


def instruction_files(variant: str, rules: dict[str, Any]) -> dict[str, str]:
    if variant == "S0_monolithic_root":
        sections = [
            "# Scope Placement Experiment — Monolithic Root",
            "",
            "All repository rules are intentionally centralized here.",
            "",
            "## Global",
        ]
        for item in rules["global"]:
            sections.append(f"- [{item['id']}] {item['text']}")
        for group, heading in (
            ("backend", "Backend"),
            ("frontend", "Frontend"),
            ("deploy", "Deploy"),
            ("docs", "Docs"),
        ):
            sections += ["", f"## {heading}"]
            for item in rules[group]:
                sections.append(f"- [{item['id']}] {item['text']}")
        sections.append("")
        return {"AGENTS.md": "\n".join(sections)}

    if variant == "S1_nested_agents":
        return {
            "AGENTS.md": render_rules("Scope Placement Experiment — Global", rules["global"])
            + "\nSubsystem-specific rules are stored in nested AGENTS.md files.\n",
            "backend/AGENTS.md": render_rules("Backend Rules", rules["backend"]),
            "frontend/AGENTS.md": render_rules("Frontend Rules", rules["frontend"]),
            "deploy/AGENTS.md": render_rules("Deploy Rules", rules["deploy"]),
            "docs/AGENTS.md": render_rules("Docs Rules", rules["docs"]),
        }

    raise ScopeHarnessError(f"unknown variant: {variant}")


def verifier_script() -> str:
    return r'''#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / ".experiment" / "validation-log.jsonl"


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def record(target, ok, failures):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"target": target, "ok": ok, "failures": failures}) + "\n")


def check(target):
    failures = []
    if target == "backend":
        controller = text("backend/src/main/java/com/example/order/OrderController.java")
        test = text("backend/src/test/java/com/example/order/OrderServiceTest.java")
        if "OrderRepository" in controller:
            failures.append("controller-direct-repository")
        if "org.junit.jupiter.api.Test" not in test:
            failures.append("not-junit5")
    elif target == "frontend":
        page = text("frontend/src/OrderPage.tsx")
        test = text("frontend/test/OrderPage.test.tsx")
        if "fetch(" in page:
            failures.append("direct-fetch-in-page")
        if "vitest" not in test or "@testing-library/react" not in test:
            failures.append("frontend-test-framework")
    elif target == "deploy":
        manifest = text("deploy/deployment.yaml")
        if ":latest" in manifest:
            failures.append("latest-image-tag")
        if "requests:" not in manifest or "limits:" not in manifest:
            failures.append("resources-removed")
        suspicious = ("value: super-secret", "value: token123", "password: plaintext")
        if any(item in manifest for item in suspicious):
            failures.append("plaintext-secret")
    elif target == "docs":
        api = text("docs/api.md")
        operations = text("docs/operations.md")
        if not api.startswith("#") or not operations.startswith("#"):
            failures.append("invalid-doc-heading")
    else:
        failures.append("unknown-target")
    return failures


def main():
    if len(sys.argv) != 2:
        print("usage: verify.py backend|frontend|deploy|docs|all", file=sys.stderr)
        return 2
    target = sys.argv[1]
    if target == "all":
        failures = []
        for child in ("backend", "frontend", "deploy", "docs"):
            failures.extend(f"{child}:{item}" for item in check(child))
    else:
        failures = check(target)
    record(target, not failures, failures)
    if failures:
        for item in failures:
            print(item, file=sys.stderr)
        return 1
    print(f"{target}: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def write_text(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def workload_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for name in WORKLOAD_ROOTS:
        base = root / name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.name != "AGENTS.md":
                paths.append(path)
    return sorted(paths)


def make_manifest(root: Path, variant: str) -> dict[str, Any]:
    files = {
        str(path.relative_to(root)): sha256_file(path)
        for path in workload_paths(root)
    }
    instructions = {}
    for path in sorted(root.rglob("AGENTS.md")):
        instructions[str(path.relative_to(root))] = {
            "bytes": len(path.read_bytes()),
            "sha256": sha256_file(path),
        }
    return {
        "version": "0.1",
        "variant": variant,
        "workload_files": files,
        "instruction_files": instructions,
    }


def materialize(variant: str, output: Path, force: bool = False, base: Path = HERE) -> Path:
    errors = validate_definition(base)
    if errors:
        raise ScopeHarnessError("definition invalid:\n" + "\n".join(errors))
    if output.exists():
        if not force:
            raise ScopeHarnessError(f"output exists: {output}; pass --force")
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    for relative, data in baseline_files().items():
        write_text(output, relative, data)

    rules = load_json(base / "rules.json")
    for relative, data in instruction_files(variant, rules).items():
        write_text(output, relative, data)

    write_text(output, "scripts/verify.py", verifier_script())
    (output / ".experiment").mkdir(parents=True, exist_ok=True)
    manifest = make_manifest(output, variant)
    write_text(
        output,
        ".experiment/baseline-manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )
    write_text(
        output,
        ".experiment/variant.json",
        json.dumps({"variant": variant}, ensure_ascii=False, indent=2) + "\n",
    )
    return output


def task_index(base: Path = HERE) -> dict[str, dict[str, Any]]:
    tasks = load_json(base / "pilot-tasks.json")
    return {task["id"]: task for task in tasks["tasks"]}


def validation_targets(workspace: Path) -> list[str]:
    log = workspace / ".experiment" / "validation-log.jsonl"
    if not log.exists():
        return []
    targets: list[str] = []
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        target = obj.get("target")
        if isinstance(target, str):
            targets.append(target)
    return targets


def current_workload_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha256_file(path)
        for path in workload_paths(root)
    }


def grade(workspace: Path, task_id: str, base: Path = HERE) -> dict[str, Any]:
    tasks = task_index(base)
    if task_id not in tasks:
        raise ScopeHarnessError(f"unknown task: {task_id}")
    task = tasks[task_id]

    manifest_path = workspace / ".experiment" / "baseline-manifest.json"
    if not manifest_path.exists():
        raise ScopeHarnessError("workspace has no baseline manifest")
    manifest = load_json(manifest_path)

    baseline = manifest["workload_files"]
    current = current_workload_hashes(workspace)
    changed = sorted(
        path for path in set(baseline) | set(current)
        if baseline.get(path) != current.get(path)
    )
    allowed = set(task["allowed_files"])
    out_of_scope = sorted(set(changed) - allowed)

    assertions: list[dict[str, Any]] = []
    for relative, needles in task.get("must_contain", {}).items():
        path = workspace / relative
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for needle in needles:
            assertions.append({
                "type": "must_contain",
                "file": relative,
                "value": needle,
                "passed": needle in text,
            })
    for relative, needles in task.get("must_not_contain", {}).items():
        path = workspace / relative
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for needle in needles:
            assertions.append({
                "type": "must_not_contain",
                "file": relative,
                "value": needle,
                "passed": needle not in text,
            })

    targets = validation_targets(workspace)
    missing_validation = [
        target for target in task.get("required_validation", [])
        if target not in targets
    ]
    forbidden_validation = [
        target for target in task.get("forbidden_validation", [])
        if target in targets
    ]

    invariant_failures: list[str] = []
    controller = workspace / "backend/src/main/java/com/example/order/OrderController.java"
    if controller.exists() and "OrderRepository" in controller.read_text(encoding="utf-8"):
        invariant_failures.append("controller-direct-repository")
    page = workspace / "frontend/src/OrderPage.tsx"
    if page.exists() and "fetch(" in page.read_text(encoding="utf-8"):
        invariant_failures.append("direct-fetch-in-page")
    deploy = workspace / "deploy/deployment.yaml"
    if deploy.exists():
        deploy_text = deploy.read_text(encoding="utf-8")
        if ":latest" in deploy_text:
            invariant_failures.append("latest-image-tag")
        if "requests:" not in deploy_text or "limits:" not in deploy_text:
            invariant_failures.append("resources-removed")
        if any(s in deploy_text for s in ("value: super-secret", "value: token123", "password: plaintext")):
            invariant_failures.append("plaintext-secret")

    assertion_failures = [a for a in assertions if not a["passed"]]
    passed = not (
        out_of_scope
        or missing_validation
        or forbidden_validation
        or invariant_failures
        or assertion_failures
    )

    instruction_bytes = sum(
        item["bytes"] for item in manifest.get("instruction_files", {}).values()
    )

    return {
        "experiment_version": manifest.get("version"),
        "variant": manifest.get("variant"),
        "task_id": task_id,
        "class": task.get("class"),
        "working_dir": task.get("working_dir"),
        "passed": passed,
        "changed_files": changed,
        "allowed_files": task["allowed_files"],
        "out_of_scope_files": out_of_scope,
        "validation_targets": targets,
        "missing_required_validation": missing_validation,
        "forbidden_validation_observed": forbidden_validation,
        "invariant_failures": invariant_failures,
        "assertions": assertions,
        "required_rules": task.get("required_rules", []),
        "fixture_instruction_bytes": instruction_bytes,
    }


def report_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# Scope Placement Grade — {result['task_id']}",
        "",
        f"- variant: {result['variant']}",
        f"- class: {result['class']}",
        f"- passed: {str(result['passed']).lower()}",
        f"- fixture instruction bytes: {result['fixture_instruction_bytes']}",
        f"- changed files: {', '.join(result['changed_files']) or '(none)'}",
        f"- out-of-scope files: {', '.join(result['out_of_scope_files']) or '(none)'}",
        f"- validation targets: {', '.join(result['validation_targets']) or '(none)'}",
        f"- missing validation: {', '.join(result['missing_required_validation']) or '(none)'}",
        f"- forbidden validation observed: {', '.join(result['forbidden_validation_observed']) or '(none)'}",
        f"- invariant failures: {', '.join(result['invariant_failures']) or '(none)'}",
        "",
        "## Assertions",
        "",
    ]
    for item in result["assertions"]:
        mark = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {mark} {item['type']} {item['file']} -> {item['value']}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=str(HERE))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate")

    p = sub.add_parser("materialize")
    p.add_argument("--variant", choices=VARIANTS, required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("grade")
    p.add_argument("--workspace", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--json-out")
    p.add_argument("--md-out")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    base = Path(args.base).resolve()
    try:
        if args.command == "validate":
            errors = validate_definition(base)
            if errors:
                print("INVALID")
                for error in errors:
                    print(f"- {error}")
                return 1
            print("VALID")
            return 0

        if args.command == "materialize":
            path = materialize(
                args.variant,
                Path(args.output).resolve(),
                force=args.force,
                base=base,
            )
            print(path)
            return 0

        result = grade(Path(args.workspace).resolve(), args.task, base=base)
        if args.json_out:
            Path(args.json_out).write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        markdown = report_markdown(result)
        if args.md_out:
            Path(args.md_out).write_text(markdown, encoding="utf-8")
        else:
            print(markdown)
        return 0 if result["passed"] else 1

    except ScopeHarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
