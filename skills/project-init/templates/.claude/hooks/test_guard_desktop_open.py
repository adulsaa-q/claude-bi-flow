"""Portable, write-free guard regression tests."""
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location("guard", Path(__file__).with_name("guard_desktop_open.py"))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardTests(unittest.TestCase):
    def test_tool_matrix(self):
        cases = [
            ("Edit", {"file_path": "x/Demo.SemanticModel/definition/tables/A.tmdl"}, "deny"),
            ("Write", {"file_path": "x/Demo.Report/definition/report.json"}, "deny"),
            ("Edit", {"file_path": "x/Demo.Report/definition/bookmarks/a.json"}, "deny"),
            ("Edit", {"file_path": "AGENTS.md"}, None),
            ("Bash", {"command": "python scripts/fix.py"}, "ask"),
            ("PowerShell", {"command": "Set-Content x.tmdl 'fixture'"}, "ask"),
            ("Bash", {"command": "pbi database export-tmdl ./definition"}, "ask"),
            ("Bash", {"command": "pbi visual list"}, None),
            ("Bash", {"command": "git status"}, None),
        ]
        for running in (True, False, None):
            for tool, ti, expected in cases:
                with self.subTest(running=running, tool=tool, ti=ti):
                    self.assertEqual(guard.decision({"tool_name": tool, "tool_input": ti}, running),
                                     None if running is False else expected)

    def test_process_failure_is_unknown(self):
        for result in [SimpleNamespace(returncode=1, stdout=""),
                       subprocess.TimeoutExpired("tasklist", 10), OSError("missing")]:
            kw = {"side_effect": result} if isinstance(result, Exception) else {"return_value": result}
            with patch.object(guard.subprocess, "run", **kw):
                self.assertIsNone(guard.desktop_running())


env_spec = importlib.util.spec_from_file_location("envguard", Path(__file__).with_name("block_env_access.py"))
envguard = importlib.util.module_from_spec(env_spec)
env_spec.loader.exec_module(envguard)
PROJECT = Path(__file__).resolve().parents[2]


class EnvGuardTests(unittest.TestCase):
    def test_decision_matrix(self):
        cases = [
            ("Read", {"file_path": "D:/x/.env"}, "deny"),
            ("Edit", {"file_path": "x\\.env"}, "deny"),
            ("Read", {"file_path": "x/.env.example"}, None),
            ("Grep", {"pattern": "PASS", "path": ".env"}, "deny"),
            ("Grep", {"pattern": "PASS", "glob": ".env"}, "deny"),
            ("Grep", {"pattern": "PASS", "path": "scripts"}, None),
            ("Bash", {"command": "cat .env"}, "ask"),
            ("PowerShell", {"command": "Get-Content \"$root/.env\""}, "ask"),
            ("Bash", {"command": "cp .env.example .env.bak"}, None),
            ("Bash", {"command": "git status"}, None),
        ]
        for tool, ti, expected in cases:
            with self.subTest(tool=tool, ti=ti):
                self.assertEqual(envguard.decision({"tool_name": tool, "tool_input": ti}), expected)


class HookWiringTests(unittest.TestCase):
    """Run the exact settings.json commands the client runs, including without python."""

    def commands(self):
        import json
        settings = json.loads((PROJECT / ".claude/settings.json").read_text(encoding="utf-8"))
        return [h["command"] for group in settings["hooks"]["PreToolUse"] for h in group["hooks"]]

    def run_hook(self, command, payload, path=None):
        import os, shutil
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash not available")
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(PROJECT))
        if path is not None:
            env["PATH"] = path
        return subprocess.run([bash, "-c", command], input=payload, capture_output=True, text=True, env=env)

    def test_blocking_guards_fail_closed(self):
        read_env = '{"tool_name":"Read","tool_input":{"file_path":"x/.env"}}'
        harmless = '{"tool_name":"Bash","tool_input":{"command":"git status"}}'
        for command in self.commands():
            with self.subTest(command=command):
                self.assertTrue(command.endswith("|| exit 2"), command)
                self.assertEqual(self.run_hook(command, "not json").returncode, 2)
                self.assertEqual(self.run_hook(command, read_env, path="/nonexistent").returncode, 2)
        env_cmd = next(c for c in self.commands() if "block_env_access" in c)
        self.assertEqual(self.run_hook(env_cmd, read_env).returncode, 2)
        self.assertEqual(self.run_hook(env_cmd, harmless).returncode, 0)


if __name__ == "__main__":
    unittest.main()
