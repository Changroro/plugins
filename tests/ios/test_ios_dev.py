import json
import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "ios"


class IosDevContractTest(unittest.TestCase):
    def test_skill_routes_through_xcode_bridge_device_hub_and_asc(self):
        skill = (PLUGIN_ROOT / "skills" / "ios-dev" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: ios-dev", skill)
        self.assertIn("claude mcp add -s project xcode -- xcrun mcpbridge", skill)
        self.assertIn("Never open `Simulator.app`", skill)
        self.assertIn("simslim verify", skill)
        self.assertIn("only with the user's approval", skill)
        self.assertIn("iPhone Mirroring", skill)
        self.assertIn("asc publish appstore", skill)
        self.assertIn("--unsafe-always-allow-all-agents", skill)

    def test_codex_adapter_points_to_canonical_skill(self):
        canonical = PLUGIN_ROOT / "skills" / "ios-dev"
        adapter = PLUGIN_ROOT / "codex" / "ios-dev"

        self.assertTrue(adapter.is_symlink())
        self.assertEqual(canonical, Path(os.path.realpath(adapter)))

    def test_plugin_is_registered_in_marketplace(self):
        manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        entry = next(p for p in marketplace["plugins"] if p["name"] == "ios")

        self.assertEqual("1.0.0", manifest["version"])
        self.assertEqual("./plugins/ios", entry["source"])


if __name__ == "__main__":
    unittest.main()
