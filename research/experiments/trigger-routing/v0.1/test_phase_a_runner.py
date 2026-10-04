import importlib.util
import json
import sys
import unittest
from pathlib import Path

SPEC_H = importlib.util.spec_from_file_location("harness", Path(__file__).with_name("harness.py"))
harness = importlib.util.module_from_spec(SPEC_H)
assert SPEC_H.loader is not None
SPEC_H.loader.exec_module(harness)
sys.modules["harness"] = harness

SPEC_R = importlib.util.spec_from_file_location("phase_a_runner", Path(__file__).with_name("phase_a_runner.py"))
runner = importlib.util.module_from_spec(SPEC_R)
assert SPEC_R.loader is not None
SPEC_R.loader.exec_module(runner)


class PhaseARunnerTests(unittest.TestCase):
    def test_gemini_native_activation(self):
        text = json.dumps({
            "type": "tool_use",
            "name": "activate_skill",
            "arguments": {"name": "bugfix"},
        }) + "\n"
        actual, observable, evidence, body_loaded = runner.extract_result("gemini", text, 0)
        self.assertEqual("bugfix", actual)
        self.assertTrue(observable)
        self.assertEqual("activate_skill:bugfix", evidence)
        self.assertTrue(body_loaded)

    def test_sentinel_fallback(self):
        actual, observable, evidence, body_loaded = runner.extract_result(
            "codex",
            '{"type":"item.completed","item":{"type":"agent_message","text":"SKILL_ACTIVATED:refactor"}}\n',
            0,
        )
        self.assertEqual("refactor", actual)
        self.assertTrue(observable)
        self.assertEqual("sentinel:refactor", evidence)
        self.assertTrue(body_loaded)

    def test_claude_absence_is_unobservable(self):
        actual, observable, evidence, body_loaded = runner.extract_result(
            "claude",
            '{"type":"result","result":"no skill"}\n',
            0,
        )
        self.assertEqual("unobservable", actual)
        self.assertFalse(observable)
        self.assertFalse(body_loaded)

    def test_tool_output_is_not_activation(self):
        event = {"type": "item.completed", "item": {
            "type": "command_execution", "aggregated_output": "SKILL_ACTIVATED:feature"}}
        self.assertFalse(runner.extract_result("codex", json.dumps(event), 0)[1])

    def test_failed_host_cannot_supply_activation(self):
        event = {"type": "result", "result": "SKILL_ACTIVATED:feature"}
        self.assertFalse(runner.extract_result("claude", json.dumps(event), 124)[1])

    def test_gemini_requires_completed_success_for_none(self):
        self.assertFalse(runner.extract_result("gemini", "", 0)[1])
        event = {"type": "result", "status": "success"}
        self.assertEqual("none", runner.extract_result("gemini", json.dumps(event), 0)[0])

    def test_multiple_sentinels_are_ambiguous(self):
        events = [{"type": "result", "result": f"SKILL_ACTIVATED:{name}"}
                  for name in ("feature", "bugfix")]
        text = "\n".join(json.dumps(e) for e in events)
        self.assertFalse(runner.extract_result("claude", text, 0)[1])

    def test_timeout_bytes_preserved(self):
        self.assertEqual("partial trace", runner.partial_text(b"partial trace"))

    def test_codex_routing_has_explicit_read_only_boundary(self):
        command = runner.build_command("codex", "task", "model")
        self.assertEqual("read-only", command[command.index("--sandbox") + 1])
        self.assertEqual("never", command[command.index("--ask-for-approval") + 1])

    def test_claude_command_uses_safe_mode(self):
        command = runner.build_command("claude", "hello", "claude-opus-x")
        self.assertIn("--permission-mode", command)
        self.assertIn("plan", command)
        self.assertIn("--no-session-persistence", command)


if __name__ == "__main__":
    unittest.main()
