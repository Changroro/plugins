import json
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

    def test_gitwf_version_is_1_3_0(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual("1.3.0", manifest["version"])


if __name__ == "__main__":
    unittest.main()
