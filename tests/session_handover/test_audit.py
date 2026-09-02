import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HANDOVER_ROOT = REPO_ROOT / "plugins" / "docs" / "skills" / "handover"
RESTART_ROOT = REPO_ROOT / "plugins" / "docs" / "skills" / "restart"
AUDIT = HANDOVER_ROOT / "scripts" / "audit.py"


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def write(self, relative, content):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def init_git(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def run_audit(self, mode="routine"):
        result = subprocess.run(
            [
                "python3",
                str(AUDIT),
                "--root",
                str(self.root),
                "--mode",
                mode,
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def write_valid_memory(self, agents="## Rules\n\n- Keep the project convention."):
        self.write("AGENTS.md", agents + "\n")
        self.write("CLAUDE.md", "@AGENTS.md\n")
        self.write(
            "HANDOFF.md",
            "# HANDOFF — Demo\n\n"
            "## Just done\n\n"
            "- Refined the memory policy.\n\n"
            "## Next up\n\n"
            "- Validate the policy against fixtures.\n",
        )
        self.write(".gitignore", "AGENTS.md\nCLAUDE.md\nHANDOFF.md\n")

    def violation_ids(self, payload):
        return {item["id"] for item in payload["violations"]}

    def test_line_count_is_not_a_policy(self):
        rules = "## Rules\n\n" + "\n".join(
            f"- Required project behavior {index}." for index in range(120)
        )
        self.write_valid_memory(rules)

        code, payload = self.run_audit("full")

        self.assertEqual(0, code, payload)
        self.assertNotIn("budget-agents", self.violation_ids(payload))

    def test_compatibility_versions_are_allowed_in_agents(self):
        self.write_valid_memory(
            "## Constraints\n\n- The project must remain compatible with Python 3.9."
        )

        code, payload = self.run_audit("full")

        self.assertEqual(0, code, payload)

    def test_tracked_memory_is_repository_owned(self):
        self.init_git()
        self.write_valid_memory()
        self.write(".gitignore", "")
        subprocess.run(
            ["git", "add", "AGENTS.md", "CLAUDE.md", "HANDOFF.md"],
            cwd=self.root,
            check=True,
        )

        code, payload = self.run_audit("full")

        self.assertEqual(0, code, payload)
        self.assertNotIn("upstream-tracked", self.violation_ids(payload))

    def test_nested_memory_scope_is_audited(self):
        self.init_git()
        self.write(
            "services/api/AGENTS.md", "## Rules\n\n- Bind the API to port 3002.\n"
        )
        self.write("services/api/CLAUDE.md", "@AGENTS.md\n")
        self.write(
            ".gitignore",
            "services/api/AGENTS.md\nservices/api/CLAUDE.md\n",
        )

        code, payload = self.run_audit("full")

        self.assertEqual(0, code, payload)
        self.assertEqual(1, payload["counts"]["agents"])
        self.assertEqual(1, payload["counts"]["scopes"])

    def test_agents_rejects_topical_knowledge_sections(self):
        self.write_valid_memory(
            "## Architecture\n\nThe API calls the worker.\n\n"
            "## Rules\n\n- Keep the project convention."
        )

        code, payload = self.run_audit("full")

        self.assertEqual(1, code)
        self.assertIn("agents-topical-section", self.violation_ids(payload))

    def test_agents_rejects_command_blocks(self):
        self.write_valid_memory(
            "## Rules\n\n- Keep the project convention.\n\n```sh\nnpm run dev\n```"
        )

        code, payload = self.run_audit("full")

        self.assertEqual(1, code)
        self.assertIn("agents-code-fence", self.violation_ids(payload))

    def test_routine_mode_does_not_reclassify_old_agents_content(self):
        self.write_valid_memory(
            "## Architecture\n\nThe API calls the worker.\n\n"
            "## Rules\n\n- Keep the project convention."
        )

        code, payload = self.run_audit("routine")

        self.assertEqual(0, code, payload)
        self.assertNotIn("agents-topical-section", self.violation_ids(payload))

    def test_handoff_rejects_volatile_history(self):
        self.write_valid_memory()
        self.write(
            "HANDOFF.md",
            "# HANDOFF — Demo\n\n"
            "## Just done\n\n"
            "- On 2026-09-01 deployed commit f1c1285 with sha256:abcdef123456 and processed 42 items.\n\n"
            "## Next up\n\n"
            "- The dev server is currently running.\n",
        )

        code, payload = self.run_audit()

        self.assertEqual(1, code)
        self.assertIn("handoff-volatile", self.violation_ids(payload))
        self.assertIn("handoff-live-state", self.violation_ids(payload))

    def test_handoff_allows_current_product_behavior(self):
        self.write_valid_memory()
        self.write(
            "HANDOFF.md",
            "# HANDOFF — Demo\n\n"
            "## Just done\n\n"
            "- Export now reflects the currently filtered results.\n\n"
            "## Next up\n\n"
            "- Validate the export columns.\n",
        )

        code, payload = self.run_audit()

        self.assertEqual(0, code, payload)
        self.assertNotIn("handoff-live-state", self.violation_ids(payload))

    def test_handoff_allows_only_one_just_done_item(self):
        self.write_valid_memory()
        self.write(
            "HANDOFF.md",
            "# HANDOFF — Demo\n\n"
            "## Just done\n\n"
            "- Updated the policy.\n"
            "- Updated the templates.\n\n"
            "## Next up\n\n"
            "- Validate fixtures.\n",
        )

        code, payload = self.run_audit()

        self.assertEqual(1, code)
        self.assertIn("handoff-just-done-count", self.violation_ids(payload))

    def test_existing_claude_instructions_must_import_agents(self):
        self.write_valid_memory()
        self.write("CLAUDE.md", "# Claude instructions\n\nKeep responses concise.\n")

        code, payload = self.run_audit()

        self.assertEqual(1, code)
        self.assertIn("claude-import", self.violation_ids(payload))

    def test_existing_claude_instructions_can_keep_their_content(self):
        self.write_valid_memory()
        self.write(
            "CLAUDE.md",
            "@AGENTS.md\n\n# Claude instructions\n\nKeep responses concise.\n",
        )

        code, payload = self.run_audit()

        self.assertEqual(0, code, payload)

    def test_legacy_agents_local_is_rejected(self):
        self.write("AGENTS.local.md", "## Rules\n\n- Keep the project convention.\n")
        self.write("CLAUDE.local.md", "@AGENTS.local.md\n")
        self.write(".gitignore", "AGENTS.local.md\nCLAUDE.local.md\n")

        code, payload = self.run_audit()

        self.assertEqual(1, code)
        self.assertIn("legacy-agents-local", self.violation_ids(payload))

    def test_agents_override_is_the_effective_scope_file(self):
        self.init_git()
        self.write("AGENTS.md", "## Rules\n\n- Use repository defaults.\n")
        self.write("AGENTS.override.md", "## Rules\n\n- Use local defaults.\n")
        self.write("CLAUDE.local.md", "@AGENTS.override.md\n")
        self.write(
            ".gitignore",
            "AGENTS.md\nAGENTS.override.md\nCLAUDE.local.md\n",
        )

        code, payload = self.run_audit("routine")

        self.assertEqual(0, code, payload)
        self.assertEqual(1, payload["counts"]["scopes"])

    def test_handoff_rejects_old_line_budget_markers(self):
        self.write_valid_memory()
        self.write(
            "HANDOFF.md",
            "# HANDOFF — Demo\n\n"
            "<!-- For the next session. ≤15 lines. -->\n\n"
            "## Just done\n\n"
            "- Refined the memory policy.\n\n"
            "## Next up\n\n"
            "- Validate the policy against fixtures.\n",
        )

        code, payload = self.run_audit("routine")

        self.assertEqual(1, code)
        self.assertIn("handoff-budget-marker", self.violation_ids(payload))

    def test_tracked_memory_must_not_be_ignored(self):
        self.init_git()
        self.write_valid_memory()
        subprocess.run(
            ["git", "add", "-f", "AGENTS.md", "CLAUDE.md", "HANDOFF.md"],
            cwd=self.root,
            check=True,
        )

        code, payload = self.run_audit()

        self.assertEqual(1, code)
        self.assertIn("gitignore-tracked", self.violation_ids(payload))


class DistributionTests(unittest.TestCase):
    def test_codex_adapters_point_to_canonical_skills(self):
        adapters = {
            "handover": HANDOVER_ROOT,
            "restart": RESTART_ROOT,
        }

        for name, canonical in adapters.items():
            adapter = REPO_ROOT / "plugins" / "docs" / "codex" / name
            self.assertTrue(adapter.is_symlink())
            self.assertEqual(canonical, Path(os.path.realpath(adapter)))

    def test_session_handover_is_removed(self):
        source = REPO_ROOT / "plugins" / "docs" / "skills" / "session-handover"
        adapter = REPO_ROOT / "plugins" / "docs" / "codex" / "session-handover"

        self.assertFalse(source.exists())
        self.assertFalse(source.is_symlink())
        self.assertFalse(adapter.exists())
        self.assertFalse(adapter.is_symlink())

    def test_restart_reuses_handover_auditor_and_references(self):
        self.assertEqual(
            HANDOVER_ROOT / "scripts",
            Path(os.path.realpath(RESTART_ROOT / "scripts")),
        )
        self.assertEqual(
            HANDOVER_ROOT / "references",
            Path(os.path.realpath(RESTART_ROOT / "references")),
        )

    def test_handover_and_restart_contracts_are_separate(self):
        handover = (HANDOVER_ROOT / "SKILL.md").read_text(encoding="utf-8")
        restart = (RESTART_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: handover", handover)
        self.assertIn("Update AGENTS", handover)
        self.assertNotIn("full memory audit", handover.lower())
        self.assertIn("name: restart", restart)
        self.assertIn("rebuild", restart.lower())
        self.assertIn("--mode full", restart)

    def test_docs_plugin_version_is_4_0_0(self):
        manifest = REPO_ROOT / "plugins" / "docs" / ".claude-plugin" / "plugin.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))

        self.assertEqual("4.0.0", payload["version"])


if __name__ == "__main__":
    unittest.main()
