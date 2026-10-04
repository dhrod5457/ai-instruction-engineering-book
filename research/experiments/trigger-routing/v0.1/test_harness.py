import csv
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("harness", Path(__file__).with_name("harness.py"))
harness = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(harness)


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


class HarnessTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> Path:
        base = root / "research" / "experiments" / "trigger-routing" / "v0.1"
        base.mkdir(parents=True)
        corpus = root / "research" / "instruction-files" / "18-trigger-eval-corpus.md"
        corpus.parent.mkdir(parents=True)
        corpus.write_text("# corpus\n", encoding="utf-8")

        variants = {
            "version": "0.1",
            "variants": {
                name: {"skills": {label: f"{name} {label}" for label in harness.SKILL_LABELS}}
                for name in harness.VARIANTS
            },
        }
        pilot_cases = []
        for i in range(20):
            label = harness.LABELS[i % len(harness.LABELS)]
            pilot_cases.append({
                "id": f"C{i:02d}",
                "class": "routing_pair" if i < 5 else "explicit",
                "prompt": f"prompt {i}",
                "expected": label,
            })

        variants_path = base / "variants.json"
        pilot_path = base / "pilot-cases.json"
        variants_path.write_text(json.dumps(variants, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        pilot_path.write_text(json.dumps({"version": "0.1", "cases": pilot_cases}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        remaining = [f"D{i:02d}" for i in range(44)] + [f"H{i:02d}" for i in range(16)]
        split = {
            "calibration": [c["id"] for c in pilot_cases],
            "development": remaining[:44],
            "holdout": remaining[44:],
            "source_blobs": {
                "corpus_sha": blob_sha(corpus.read_bytes()),
                "pilot_cases_sha": blob_sha(pilot_path.read_bytes()),
                "variants_sha": blob_sha(variants_path.read_bytes()),
            },
        }
        (base / "split.json").write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")
        (base / "results-template.csv").write_text(",".join(harness.RESULT_COLUMNS) + "\n", encoding="utf-8")
        return base

    def test_validate_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = self.make_fixture(Path(tmp))
            self.assertEqual([], harness.validate_fixture(base))

    def test_materialize(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self.make_fixture(root)
            out = root / "out"
            harness.materialize_fixture(
                variant_name="A1_concise",
                host="generic",
                output=out,
                base=base,
            )
            skill = out / ".agents" / "skills" / "feature" / "SKILL.md"
            text = skill.read_text(encoding="utf-8")
            self.assertIn("name: feature", text)
            self.assertIn("SKILL_ACTIVATED:feature", text)

    def test_score_observable_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self.make_fixture(root)
            cases = json.loads((base / "pilot-cases.json").read_text())["cases"]
            results = base / "results.csv"
            with results.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=harness.RESULT_COLUMNS)
                writer.writeheader()
                for case in cases[:5]:
                    row = {col: "" for col in harness.RESULT_COLUMNS}
                    row.update({
                        "experiment_version": "0.1",
                        "date": "2026-10-03",
                        "host": "test",
                        "model": "m",
                        "model_version": "1",
                        "variant": "A1_concise",
                        "prompt_id": case["id"],
                        "run_index": "1",
                        "expected": case["expected"],
                        "actual": case["expected"],
                        "observable": "true",
                        "routing_evidence": "sentinel",
                    })
                    writer.writerow(row)
            report = harness.score_results(results, base)
            group = report["groups"][0]
            self.assertEqual(1.0, group["accuracy_observable"])
            self.assertEqual(1.0, group["observable_rate"])
            self.assertEqual(0.0, group["routing_pair_collision_error_rate"])


if __name__ == "__main__":
    unittest.main()
