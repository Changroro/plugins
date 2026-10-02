import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest

import test_rename_project as fixtures
import codex_rename
import rename_core as core


class SessionModeTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.MetadataTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.transcript, records, self.other, self.state, self.database = self.f.codex()
        for record in records:
            if record.get('type') in ('session_meta', 'turn_context'):
                record['payload']['cwd'] = str(self.f.root)
        self.transcript.write_text(''.join(json.dumps(r) + '\n' for r in records))
        with sqlite3.connect(self.database) as db:
            db.execute('UPDATE threads SET cwd=? WHERE id="same-id"', (str(self.f.root),))
        self.f.new.mkdir()
        self.original = self.transcript.read_bytes()
        self.other_original = self.other.read_bytes()
        self.state_original = self.state.read_bytes()
        self.config = self.f.home / 'config.toml'
        self.config_original = self.config.read_bytes()

    def run_cli(self, caller):
        return subprocess.run([sys.executable, '-B', str(Path(codex_rename.__file__)), 'mv-session', '--session-id', 'same-id', '--destination', str(self.f.new), '--codex-home', str(self.f.home), '--codex-db', str(self.database), '--out', str(self.f.out)], capture_output=True, text=True, env=dict(os.environ, CODEX_THREAD_ID=caller))

    def test_session_cli_preserves_folders_other_threads_and_shared_settings(self):
        result = self.run_cli('caller-id')
        self.assertEqual(result.returncode, 0, result.stderr)
        verified = json.loads(result.stdout.splitlines()[-1])
        self.assertEqual(verified['session_ids'], ['same-id'])
        self.assertEqual(verified['directory_moves'], 0)
        self.assertTrue(self.f.old.is_dir())
        self.assertTrue(self.f.new.is_dir())
        self.assertTrue(self.f.root.is_dir())
        self.assertEqual(self.other.read_bytes(), self.other_original)
        self.assertEqual(self.state.read_bytes(), self.state_original)
        self.assertEqual(self.config.read_bytes(), self.config_original)
        with core.connect_db(self.database) as db:
            self.assertEqual(db.execute('SELECT cwd FROM threads WHERE id="same-id"').fetchone(), (str(self.f.new),))
        after = [json.loads(line) for line in self.transcript.read_text().splitlines()]
        before = [json.loads(line) for line in self.original.decode().splitlines()]
        self.assertEqual(after[2:4], before[2:4])
        self.assertEqual(after[0]['payload']['cwd'], str(self.f.new))
        plan = self.f.out / 'plan.json'
        restored = subprocess.run([sys.executable, '-B', str(Path(codex_rename.__file__)), 'mv-project', 'rollback', '--plan', str(plan), '--approve', core.digest(plan.read_bytes())], capture_output=True, text=True, env=dict(os.environ, CODEX_THREAD_ID='caller-id'))
        self.assertEqual(restored.returncode, 0, restored.stderr)
        self.assertEqual(self.transcript.read_bytes(), self.original)

    def test_session_cli_blocks_current_caller_before_backups_or_writes(self):
        result = self.run_cli('same-id')
        self.assertEqual(result.returncode, 1)
        self.assertIn('다른 세션', result.stderr)
        self.assertFalse(self.f.out.exists())
        self.assertEqual(self.transcript.read_bytes(), self.original)


if __name__ == '__main__':
    unittest.main()
