import json
import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "gitwf"


class GitCommitContractTest(unittest.TestCase):
    def test_identity_rules_live_in_commit_skill(self):
        skill = (PLUGIN_ROOT / "skills" / "git-commit" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("## Git Identity", skill)
        self.assertIn("chbae@gcsc.co.kr", skill)
        self.assertIn("chbae624@gmail.com", skill)
        self.assertIn("Keep `user.name` as `Bae-ChangHyun`", skill)
        self.assertIn("Use `Changroro` in current GitHub remote URLs", skill)

    def test_codex_adapters_point_to_canonical_skills(self):
        for name in (
            "git-commit",
            "github-pr-creation",
            "github-pr-merge",
            "github-pr-review",
        ):
            canonical = PLUGIN_ROOT / "skills" / name
            adapter = PLUGIN_ROOT / "codex" / name

            self.assertTrue(adapter.is_symlink())
            self.assertEqual(canonical, Path(os.path.realpath(adapter)))

    def test_gitwf_version_is_1_3_1(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual("1.3.1", manifest["version"])


if __name__ == "__main__":
    unittest.main()
