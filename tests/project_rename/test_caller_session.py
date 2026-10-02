import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tomllib
import unittest
from unittest.mock import patch

import test_rename_project as fixtures
import codex_rename
import rename_core as core


class CallerSessionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.MetadataTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.runtime = patch.dict(os.environ, {'CODEX_THREAD_ID':'caller-id'})
        self.runtime.start()
        self.addCleanup(self.runtime.stop)

    def test_current_session_blocks_before_plan_or_any_write(self):
        f = self.fixture
        transcript, _, _, _, database = f.codex()
        original = transcript.read_bytes()
        os.environ['CODEX_THREAD_ID'] = 'same-id'
        with self.assertRaisesRegex(ValueError, '다른 세션'):
            f.agent_plan(codex_rename)
        self.assertFalse(f.out.exists())
        self.assertTrue(f.old.is_dir())
        self.assertFalse(f.new.exists())
        self.assertEqual(transcript.read_bytes(), original)
        with core.connect_db(database) as db:
            self.assertEqual(db.execute('SELECT cwd FROM threads WHERE id="same-id"').fetchone(), (str(f.old),))

    def test_apply_rechecks_current_caller_after_plan(self):
        f = self.fixture
        f.codex()
        data, raw = f.agent_plan(codex_rename)
        os.environ['CODEX_THREAD_ID'] = 'same-id'
        with self.assertRaisesRegex(ValueError, '다른 세션'):
            core.apply(data, f.out, raw)
        self.assertTrue(f.old.is_dir())
        self.assertFalse((f.out / 'state.json').exists())

    def test_empty_session_database_fails_before_folder_rename(self):
        f = self.fixture
        _, _, _, _, database = f.codex()
        with sqlite3.connect(database) as db:
            db.execute('DELETE FROM threads')
        with self.assertRaisesRegex(ValueError, '세션을 찾지 못했습니다'):
            f.agent_plan(codex_rename)
        self.assertFalse(f.out.exists())
        self.assertTrue(f.old.is_dir())

    def test_missing_or_forged_caller_is_rejected(self):
        f = self.fixture
        f.codex()
        os.environ.pop('CODEX_THREAD_ID')
        with self.assertRaisesRegex(ValueError, '현재 세션 ID'):
            f.agent_plan(codex_rename)
        os.environ['CODEX_THREAD_ID'] = 'same-id'
        f.args.caller_thread_id = 'caller-id'
        with self.assertRaisesRegex(ValueError, '실행 환경과 다릅니다'):
            f.agent_plan(codex_rename)
        self.assertFalse(f.out.exists())

    def test_other_caller_gets_verified_ids_and_reversible_migration(self):
        f = self.fixture
        transcript, _, _, _, _ = f.codex()
        original = transcript.read_bytes()
        data, raw = f.agent_plan(codex_rename)
        state = f.run_apply(data, raw)
        with patch('builtins.print') as output:
            core.verify(data, f.out)
        result = json.loads(output.call_args.args[0])
        self.assertEqual(result['status'], 'verified')
        self.assertEqual(set(result['session_ids']), {'same-id', 'archived-id'})
        self.assertEqual(result['database_rows'], 2)
        with patch('builtins.print'):
            core.rollback(data, f.out, state)
        self.assertEqual(transcript.read_bytes(), original)

    def test_luna_role_is_read_only_and_does_not_execute_migration(self):
        path = Path(__file__).resolve().parents[2] / 'plugins/project-rename/codex/agents/codex-renamer.toml'
        role = tomllib.loads(path.read_text())
        self.assertEqual(role['sandbox_mode'], 'read-only')
        self.assertIn('메인 에이전트가 맡는다', role['developer_instructions'])

    def test_cli_blocks_self_and_migrates_other_session_with_verify_and_rollback(self):
        f = self.fixture
        transcript, _, _, _, database = f.codex()
        original = transcript.read_bytes()
        script = Path(codex_rename.__file__)
        env = dict(os.environ, CODEX_THREAD_ID='same-id')
        args = [sys.executable, '-B', str(script), 'mv-project', 'plan', '--source', str(f.old), '--destination', str(f.new), '--out', str(f.out), '--codex-home', str(f.home), '--codex-db', str(database)]
        blocked = subprocess.run(args, capture_output=True, text=True, env=env)
        self.assertEqual(blocked.returncode, 1, blocked.stderr)
        self.assertIn('다른 세션', blocked.stderr)
        self.assertFalse(f.out.exists())
        env['CODEX_THREAD_ID'] = 'caller-id'
        planned = subprocess.run(args, capture_output=True, text=True, env=env, check=True)
        approval = json.loads(planned.stdout)['approve']
        def command(name):
            command_args = [sys.executable, '-B', str(script), 'mv-project', name, '--plan', str(f.out / 'plan.json')]
            if name != 'verify':
                command_args += ['--approve', approval]
            return subprocess.run(command_args, capture_output=True, text=True, env=env, check=True)
        command('apply')
        verified = json.loads(command('verify').stdout)
        self.assertEqual(verified['database_rows'], 2)
        self.assertFalse(f.old.exists())
        self.assertTrue(f.new.is_dir())
        with core.connect_db(database) as db:
            self.assertEqual(db.execute('SELECT cwd FROM threads WHERE id="same-id"').fetchone(), (str(f.new),))
        command('rollback')
        self.assertTrue(f.old.is_dir())
        self.assertEqual(transcript.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
