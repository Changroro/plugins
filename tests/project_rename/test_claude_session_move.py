import argparse
import json
from pathlib import Path
import unittest
import subprocess
import sys
from unittest.mock import patch

import test_rename_project as fixtures
import claude_rename
import rename_core as core


class ClaudeSessionMoveTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.MetadataTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.folder, self.file, self.record, _, _ = self.f.claude()
        self.original = self.file.read_bytes()
        self.index = self.folder / 'sessions-index.json'
        self.index_original = self.index.read_bytes()
        self.sidecar = self.folder / 'same-id/subagents/agent.jsonl'
        self.sidecar.parent.mkdir(parents=True)
        self.sidecar.write_bytes(self.original)
        self.f.new.mkdir()
        self.args = argparse.Namespace(source=str(self.f.old), destination=str(self.f.new), session_file=str(self.file), claude_home=str(self.f.home), out=str(self.f.out))
        self.target = self.f.home / 'projects' / core.re.sub(r'[^a-zA-Z0-9]', '-', str(self.f.new))

    def test_move_leaves_one_session_with_verified_conversation_and_backup(self):
        with patch('builtins.print'):
            claude_rename.move_session(self.args)
        audit = json.loads((self.f.out / 'audit.json').read_text())
        self.assertEqual(audit['mode'], 'mv-session')
        self.assertTrue(audit['source_removed'])
        copied = Path(audit['files'][0]['target'])
        self.assertFalse(self.file.exists())
        self.assertFalse(self.sidecar.exists())
        self.assertEqual((self.f.out / '0.before').read_bytes(), self.original)
        self.assertEqual(copied.read_bytes(), core.jsonl_paths(self.original, str(self.f.old), str(self.f.new), 'claude'))
        actual = json.loads(copied.read_text())
        for key in ('sessionId', 'uuid', 'timestamp', 'message', 'toolUseResult'):
            self.assertEqual(actual[key], self.record[key])
        self.assertEqual(actual['cwd'], str(self.f.new))
        self.assertEqual(json.loads(self.index.read_text())['entries'], [])
        self.assertEqual(len(list(self.f.home.glob('projects/*/same-id.jsonl'))), 1)
        self.assertTrue((self.folder / 'memory/MEMORY.md').exists())
        self.assertTrue(self.f.old.is_dir())

    def test_failed_source_removal_restores_original_index_and_sidecars(self):
        replace = claude_rename.os.replace
        def fail(path, target):
            if Path(path) == self.file:
                raise OSError('injected source removal failure')
            return replace(path, target)
        with patch.object(claude_rename.os, 'replace', fail):
            with self.assertRaisesRegex(OSError, 'source removal'):
                claude_rename.move_session(self.args)
        self.assertEqual(self.file.read_bytes(), self.original)
        self.assertEqual(self.sidecar.read_bytes(), self.original)
        self.assertEqual(self.index.read_bytes(), self.index_original)
        self.assertFalse(self.target.exists())

    def test_claude_cli_uses_same_mv_session_name_and_removes_original(self):
        result = subprocess.run([sys.executable, '-B', str(Path(claude_rename.__file__)), 'mv-session', '--source', self.args.source, '--destination', self.args.destination, '--session-file', self.args.session_file, '--claude-home', self.args.claude_home, '--out', self.args.out], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        audit = json.loads(result.stdout)
        self.assertEqual(audit['mode'], 'mv-session')
        self.assertTrue(audit['source_removed'])
        self.assertFalse(self.file.exists())
        self.assertTrue(self.target.joinpath('same-id.jsonl').exists())


if __name__ == '__main__':
    unittest.main()
