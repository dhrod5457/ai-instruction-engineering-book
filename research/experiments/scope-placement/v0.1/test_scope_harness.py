import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "scope_harness", Path(__file__).with_name("scope_harness.py")
)
scope = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(scope)


class ScopeHarnessTests(unittest.TestCase):
    def test_definition_is_valid(self):
        self.assertEqual([], scope.validate_definition())

    def test_s0_s1_workload_is_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            s0 = scope.materialize("S0_monolithic_root", root / "s0")
            s1 = scope.materialize("S1_nested_agents", root / "s1")

            m0 = json.loads((s0 / ".experiment/baseline-manifest.json").read_text())
            m1 = json.loads((s1 / ".experiment/baseline-manifest.json").read_text())

            self.assertEqual(m0["workload_files"], m1["workload_files"])
            self.assertEqual({"AGENTS.md"}, set(m0["instruction_files"]))
            self.assertEqual(
                {
                    "AGENTS.md",
                    "backend/AGENTS.md",
                    "frontend/AGENTS.md",
                    "deploy/AGENTS.md",
                    "docs/AGENTS.md",
                },
                set(m1["instruction_files"]),
            )

    def test_backend_task_can_pass_deterministic_grader(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = scope.materialize(
                "S1_nested_agents", Path(tmp) / "workspace"
            )
            service = workspace / "backend/src/main/java/com/example/order/OrderService.java"
            text = service.read_text(encoding="utf-8")
            service.write_text(
                text.replace('"UNKNOWN"', '"PENDING"'),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", "scripts/verify.py", "backend"],
                cwd=workspace,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)

            grade = scope.grade(workspace, "B-01")
            self.assertTrue(grade["passed"], grade)
            self.assertEqual(
                ["backend/src/main/java/com/example/order/OrderService.java"],
                grade["changed_files"],
            )
            self.assertEqual(["backend"], grade["validation_targets"])

    def test_out_of_scope_change_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = scope.materialize(
                "S0_monolithic_root", Path(tmp) / "workspace"
            )
            api = workspace / "docs/api.md"
            api.write_text(api.read_text() + "\nextra\n", encoding="utf-8")

            grade = scope.grade(workspace, "B-01")
            self.assertFalse(grade["passed"])
            self.assertIn("docs/api.md", grade["out_of_scope_files"])


if __name__ == "__main__":
    unittest.main()
