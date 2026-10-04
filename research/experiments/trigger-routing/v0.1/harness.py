#!/usr/bin/env python3
"""Host-neutral harness for trigger-routing calibration experiments.

This tool intentionally does not invoke any vendor CLI. It validates the frozen
fixture, materializes identical routing-only skills for a chosen host layout,
and scores collected CSV results.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
LABELS = ("feature", "bugfix", "refactor", "review", "none")
SKILL_LABELS = ("feature", "bugfix", "refactor", "review")
VARIANTS = ("A0_broad", "A1_concise", "A1L_length_control", "A2_boundary_aware")
RESULT_COLUMNS = (
    "experiment_version", "date", "host", "host_version", "model", "model_version",
    "variant", "prompt_id", "run_index", "expected", "actual", "observable",
    "routing_evidence", "metadata_tokens", "input_tokens", "output_tokens",
    "latency_ms", "skill_body_loaded", "notes",
)
HOST_SKILLS_DIR = {
    "generic": ".agents/skills",
    "claude": ".claude/skills",
    "codex": ".codex/skills",
    "cursor": ".cursor/skills",
    "gemini": ".gemini/skills",
    "copilot": ".github/skills",
}


class HarnessError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"invalid JSON: {path}: {exc}") from exc


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def fixture_paths(base: Path = HERE) -> dict[str, Path]:
    return {
        "variants": base / "variants.json",
        "pilot": base / "pilot-cases.json",
        "split": base / "split.json",
        "results_template": base / "results-template.csv",
        "corpus": (base / "../../../instruction-files/18-trigger-eval-corpus.md").resolve(),
    }


def validate_fixture(base: Path = HERE) -> list[str]:
    paths = fixture_paths(base)
    variants = load_json(paths["variants"])
    pilot = load_json(paths["pilot"])
    split = load_json(paths["split"])
    errors: list[str] = []

    if variants.get("version") != "0.1":
        errors.append("variants.json version must be 0.1")

    if set(variants.get("variants", {})) != set(VARIANTS):
        errors.append(f"variant set mismatch: {tuple(variants.get('variants', {}))}")

    for variant_name, variant in variants.get("variants", {}).items():
        skills = variant.get("skills", {})
        if set(skills) != set(SKILL_LABELS):
            errors.append(f"{variant_name}: skill labels must be {SKILL_LABELS}")
        for label, description in skills.items():
            if not isinstance(description, str) or not description.strip():
                errors.append(f"{variant_name}/{label}: empty description")

    cases = pilot.get("cases", [])
    if len(cases) != 20:
        errors.append(f"pilot must contain 20 cases, found {len(cases)}")

    ids = [case.get("id") for case in cases]
    duplicates = [item for item, n in Counter(ids).items() if n > 1]
    if duplicates:
        errors.append(f"duplicate pilot ids: {duplicates}")

    for case in cases:
        if case.get("expected") not in LABELS:
            errors.append(f"{case.get('id')}: invalid expected label {case.get('expected')!r}")
        if not str(case.get("prompt", "")).strip():
            errors.append(f"{case.get('id')}: empty prompt")

    calibration = split.get("calibration", [])
    if calibration != ids:
        errors.append("split calibration order/content does not match pilot-cases.json")

    all_split = (
        list(split.get("calibration", []))
        + list(split.get("development", []))
        + list(split.get("holdout", []))
    )
    split_dupes = [item for item, n in Counter(all_split).items() if n > 1]
    if split_dupes:
        errors.append(f"duplicate IDs across split partitions: {split_dupes}")
    if len(all_split) != 80:
        errors.append(f"split must cover 80 unique cases, found {len(all_split)}")

    source_blobs = split.get("source_blobs", {})
    expected_shas = {
        "corpus_sha": git_blob_sha(paths["corpus"]),
        "pilot_cases_sha": git_blob_sha(paths["pilot"]),
        "variants_sha": git_blob_sha(paths["variants"]),
    }
    for key, actual in expected_shas.items():
        if source_blobs.get(key) != actual:
            errors.append(
                f"source blob mismatch for {key}: split={source_blobs.get(key)} actual={actual}"
            )

    with paths["results_template"].open(newline="", encoding="utf-8") as fh:
        header = tuple(next(csv.reader(fh), []))
    if header != RESULT_COLUMNS:
        errors.append(
            "results-template.csv header mismatch:\n"
            f"  expected={RESULT_COLUMNS}\n"
            f"  actual={header}"
        )

    return errors


def skill_markdown(name: str, description: str) -> str:
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "---\n\n"
        "# Routing evaluation sentinel\n\n"
        "This is a routing-only evaluation skill.\n\n"
        "Do not modify files, run commands, or perform the requested task.\n\n"
        "If this skill is activated, respond with exactly:\n\n"
        f"SKILL_ACTIVATED:{name}\n"
    )


def materialize_fixture(
    *,
    variant_name: str,
    host: str,
    output: Path,
    skills_dir: str | None = None,
    force: bool = False,
    base: Path = HERE,
) -> Path:
    variants = load_json(base / "variants.json")
    if variant_name not in variants.get("variants", {}):
        raise HarnessError(f"unknown variant: {variant_name}")
    if host not in HOST_SKILLS_DIR and not skills_dir:
        raise HarnessError(f"unknown host {host!r}; pass --skills-dir for a custom layout")

    root = output.resolve()
    if root.exists():
        if not force:
            raise HarnessError(f"output exists: {root}; pass --force to replace")
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    rel = skills_dir or HOST_SKILLS_DIR[host]
    skill_root = root / rel
    skill_root.mkdir(parents=True, exist_ok=True)

    descriptions = variants["variants"][variant_name]["skills"]
    for name in SKILL_LABELS:
        path = skill_root / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(skill_markdown(name, descriptions[name]), encoding="utf-8")

    manifest = {
        "experiment_version": variants.get("version"),
        "variant": variant_name,
        "host": host,
        "skills_dir": rel,
        "skills": list(SKILL_LABELS),
        "source_variants_git_blob_sha": git_blob_sha(base / "variants.json"),
        "sentinel_contract": "SKILL_ACTIVATED:<name>",
    }
    (root / "fixture-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return root


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def read_results(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != RESULT_COLUMNS:
            raise HarnessError("results CSV header does not match results-template.csv")
        return [dict(row) for row in reader]


def case_index(base: Path = HERE) -> dict[str, dict[str, Any]]:
    pilot = load_json(base / "pilot-cases.json")
    return {case["id"]: case for case in pilot["cases"]}


def safe_div(num: float, den: float) -> float | None:
    return None if not den else num / den


def f1_from_counts(tp: int, fp: int, fn: int) -> float | None:
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    if precision is None or recall is None or precision + recall == 0:
        return None
    return 2 * precision * recall / (precision + recall)


def analyze_group(rows: list[dict[str, str]], cases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    observable = [r for r in rows if parse_bool(r["observable"]) and r["actual"] in LABELS]
    correct = [r for r in observable if r["actual"] == r["expected"]]

    confusion = {
        expected: {actual: 0 for actual in LABELS}
        for expected in LABELS
    }
    for row in observable:
        confusion[row["expected"]][row["actual"]] += 1

    per_label: dict[str, dict[str, Any]] = {}
    f1s: list[float] = []
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[e][label] for e in LABELS if e != label)
        fn = sum(confusion[label][a] for a in LABELS if a != label)
        f1 = f1_from_counts(tp, fp, fn)
        if f1 is not None:
            f1s.append(f1)
        per_label[label] = {
            "support": sum(confusion[label].values()),
            "precision": safe_div(tp, tp + fp),
            "recall": safe_div(tp, tp + fn),
            "f1": f1,
        }

    none_rows = [r for r in observable if r["expected"] == "none"]
    routing_pair = [
        r for r in observable
        if cases.get(r["prompt_id"], {}).get("class") == "routing_pair"
    ]

    repeated: dict[str, list[str]] = defaultdict(list)
    for row in observable:
        repeated[row["prompt_id"]].append(row["actual"])
    consistency = []
    for values in repeated.values():
        if len(values) >= 2:
            consistency.append(Counter(values).most_common(1)[0][1] / len(values))

    return {
        "runs_total": len(rows),
        "runs_observable": len(observable),
        "observable_rate": safe_div(len(observable), len(rows)),
        "accuracy_observable": safe_div(len(correct), len(observable)),
        "macro_f1_observable": safe_div(sum(f1s), len(f1s)),
        "abstention_accuracy": safe_div(
            sum(1 for r in none_rows if r["actual"] == "none"), len(none_rows)
        ),
        "false_positive_rate_on_none": safe_div(
            sum(1 for r in none_rows if r["actual"] != "none"), len(none_rows)
        ),
        "routing_pair_collision_error_rate": safe_div(
            sum(1 for r in routing_pair if r["actual"] != r["expected"]),
            len(routing_pair),
        ),
        "run_consistency": safe_div(sum(consistency), len(consistency)),
        "confusion_matrix": confusion,
        "per_label": per_label,
    }


def score_results(path: Path, base: Path = HERE) -> dict[str, Any]:
    rows = read_results(path)
    cases = case_index(base)
    errors: list[str] = []

    for line, row in enumerate(rows, start=2):
        if row["expected"] not in LABELS:
            errors.append(f"line {line}: invalid expected={row['expected']!r}")
        if row["actual"] not in (*LABELS, "unobservable"):
            errors.append(f"line {line}: invalid actual={row['actual']!r}")
        case = cases.get(row["prompt_id"])
        if case is None:
            errors.append(f"line {line}: unknown pilot prompt_id={row['prompt_id']!r}")
        elif case["expected"] != row["expected"]:
            errors.append(
                f"line {line}: expected mismatch for {row['prompt_id']}: "
                f"csv={row['expected']} fixture={case['expected']}"
            )

    if errors:
        raise HarnessError("\n".join(errors))

    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (row["host"], row["model"], row["model_version"], row["variant"])
        grouped[key].append(row)

    groups = []
    for (host, model, model_version, variant), group_rows in sorted(grouped.items()):
        groups.append({
            "host": host,
            "model": model,
            "model_version": model_version,
            "variant": variant,
            **analyze_group(group_rows, cases),
        })
    return {"source": str(path), "groups": groups}


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Trigger Routing Pilot Score",
        "",
        "| Host | Model | Variant | Runs | Observable | Accuracy | Macro-F1 | None abstain | Routing-pair error | Consistency |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for g in report["groups"]:
        model = g["model"] + (f" {g['model_version']}" if g["model_version"] else "")
        lines.append(
            f"| {g['host']} | {model} | {g['variant']} | {g['runs_total']} | "
            f"{fmt_pct(g['observable_rate'])} | {fmt_pct(g['accuracy_observable'])} | "
            f"{fmt_pct(g['macro_f1_observable'])} | {fmt_pct(g['abstention_accuracy'])} | "
            f"{fmt_pct(g['routing_pair_collision_error_rate'])} | "
            f"{fmt_pct(g['run_consistency'])} |"
        )
    lines += [
        "",
        "Routing accuracy/F1 use observable runs only; observable rate is reported separately.",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=str(HERE))
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate")
    p.set_defaults(command="validate")

    p = sub.add_parser("materialize")
    p.add_argument("--variant", required=True, choices=VARIANTS)
    p.add_argument("--host", required=True, choices=tuple(HOST_SKILLS_DIR))
    p.add_argument("--output", required=True)
    p.add_argument("--skills-dir")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("score")
    p.add_argument("--results", required=True)
    p.add_argument("--json-out")
    p.add_argument("--md-out")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    base = Path(args.base).resolve()
    try:
        if args.command == "validate":
            errors = validate_fixture(base)
            if errors:
                print("INVALID")
                for error in errors:
                    print(f"- {error}")
                return 1
            print("VALID")
            return 0

        if args.command == "materialize":
            root = materialize_fixture(
                variant_name=args.variant,
                host=args.host,
                output=Path(args.output),
                skills_dir=args.skills_dir,
                force=args.force,
                base=base,
            )
            print(root)
            return 0

        report = score_results(Path(args.results), base)
        if args.json_out:
            Path(args.json_out).write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        markdown = report_markdown(report)
        if args.md_out:
            Path(args.md_out).write_text(markdown, encoding="utf-8")
        else:
            print(markdown)
        return 0
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
