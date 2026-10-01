import argparse
import ast
from pathlib import Path
import json
import sqlite3
import sys
from contextlib import closing
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / 'plugins/project-rename/scripts/rename_core.py'
sys.path.insert(0, str(SCRIPT.parent))
import rename_core as rename
import claude_rename
import codex_rename


class RenameTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.old, self.new = self.root / 'a', self.root / 'b'
        self.old.mkdir()
        (self.old / '.hidden').write_text('keep')
        self.history = self.old / 'history.jsonl'
        self.history.write_text('{"id":"same-id","text":"original conversation","cwd":"/old"}\n')
        self.internal = self.old / 'settings.json'
        self.internal.write_text(json.dumps({'path':str(self.old / 'src'),'other':str(self.old)+'-other'}))
        self.external = self.root / 'workspace.txt'
        self.external.write_text('project="' + str(self.old) + '"\n')
        self.external.chmod(0o640)
        self.out = self.root / 'plan'
        self.args = argparse.Namespace(source=str(self.old), destination=str(self.new), out=str(self.out), reference_map=[[str(self.internal),str(self.old),str(self.new)],[str(self.external),str(self.old),str(self.new)]])
        self.signal_guard = patch.object(rename.os, 'kill', side_effect=AssertionError('프로세스 종료 금지'))
        self.signal_guard.start()
        self.addCleanup(self.signal_guard.stop)

    def plan(self):
        with patch('builtins.print'):
            rename.plan(self.args)
        raw = (self.out / 'plan.json').read_bytes()
        return json.loads(raw), raw

    def apply(self, data, raw):
        with patch('builtins.print'):
            rename.apply(data, self.out, raw)
        return json.loads((self.out / 'state.json').read_text())

    def test_rename_references_and_rollback_without_touching_history(self):
        original_inode = self.old.stat().st_ino
        history = self.history.read_bytes()
        inside = self.internal.read_bytes()
        outside = self.external.read_bytes()
        data, raw = self.plan()
        self.assertTrue(self.old.exists())
        state = self.apply(data, raw)
        self.assertFalse(self.old.exists())
        self.assertEqual(self.new.stat().st_ino, original_inode)
        self.assertEqual((self.new / '.hidden').read_text(), 'keep')
        self.assertEqual((self.new / 'history.jsonl').read_bytes(), history)
        settings = json.loads((self.new / 'settings.json').read_text())
        self.assertEqual(settings['path'], str(self.new / 'src'))
        self.assertEqual(settings['other'], str(self.old)+'-other')
        self.assertIn(str(self.new), self.external.read_text())
        self.assertEqual(self.external.stat().st_mode & 0o777, 0o640)
        with patch('builtins.print'):
            rename.rollback(data, self.out, state)
        self.assertEqual(self.old.stat().st_ino, original_inode)
        self.assertEqual(self.history.read_bytes(), history)
        self.assertEqual(self.internal.read_bytes(), inside)
        self.assertEqual(self.external.read_bytes(), outside)

    def test_existing_target_is_never_overwritten(self):
        self.new.mkdir()
        (self.new / 'keep').write_text('existing')
        with self.assertRaisesRegex(ValueError, '이미 존재'):
            self.plan()
        self.assertEqual((self.new / 'keep').read_text(), 'existing')

    def test_stale_reference_blocks_before_rename(self):
        data, raw = self.plan()
        self.external.write_text('new work')
        with self.assertRaisesRegex(ValueError, '계획 이후'):
            self.apply(data, raw)
        self.assertTrue(self.old.exists())
        self.assertFalse(self.new.exists())

    def test_failed_reference_write_restores_name_and_references(self):
        data, raw = self.plan()
        original = rename.atomic
        outside = self.external.read_bytes()
        def failure(path, raw, mode=0o600):
            if path == self.external and str(self.new).encode() in raw:
                raise OSError('injected failure')
            return original(path, raw, mode)
        with patch.object(rename, 'atomic', failure):
            with self.assertRaisesRegex(OSError, 'injected'):
                self.apply(data, raw)
        self.assertTrue(self.old.exists())
        self.assertFalse(self.new.exists())
        self.assertEqual(self.external.read_bytes(), outside)

    def test_chat_and_database_references_are_rejected(self):
        for path in [self.history, self.old / 'state.sqlite']:
            self.args.reference_map = [[str(path), '/old', '/new']]
            with self.assertRaisesRegex(ValueError, '자동 수정하지'):
                self.plan()
        self.assertTrue(self.history.exists())
        self.assertFalse(self.out.exists())

    def test_rollback_does_not_overwrite_later_user_edits(self):
        data, raw = self.plan()
        state = self.apply(data, raw)
        self.external.write_text('later work')
        with self.assertRaisesRegex(ValueError, '외부 변경'):
            rename.rollback(data, self.out, state)
        self.assertEqual(self.external.read_text(), 'later work')
        self.assertTrue(self.new.exists())

    def test_same_path_directory_replacement_is_detected(self):
        data, raw = self.plan()
        self.old.rename(self.root / 'original-backup')
        self.old.mkdir()
        with self.assertRaisesRegex(ValueError, '다른 디렉터리'):
            self.apply(data, raw)
        self.assertFalse(self.new.exists())

    def test_script_cannot_launch_or_control_processes_or_sessions(self):
        banned_imports = {'subprocess','signal','socket','ctypes'}
        for script in SCRIPT.parent.glob('*.py'):
            for node in ast.walk(ast.parse(script.read_text())):
                if isinstance(node, ast.Import):
                    self.assertFalse(banned_imports.intersection(alias.name for alias in node.names))
                if isinstance(node, ast.ImportFrom):
                    self.assertNotIn(node.module, banned_imports)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, {'kill','killpg','terminate','Popen','fork','system','execv','execve'})

class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.old, self.new = self.root / 'a', self.root / 'b'
        self.old.mkdir()
        (self.old / '.hidden').write_text('preserve')
        self.home = self.root / 'agent-home'
        self.home.mkdir()
        self.out = self.root / 'plan'
        self.process_root = self.root / 'proc'
        self.process_root.mkdir()
        self.process_guard = patch.object(rename, 'PROCESS_ROOT', self.process_root)
        self.process_guard.start()
        self.addCleanup(self.process_guard.stop)
        self.args = argparse.Namespace(source=str(self.old), destination=str(self.new), out=str(self.out), sessions_only=False, reference_map=[], claude_home=str(self.home), claude_config=None, codex_home=str(self.home), codex_db=None)
        self.kill_guard = patch.object(rename.os, 'kill', side_effect=AssertionError('프로세스 종료 금지'))
        self.kill_guard.start()
        self.addCleanup(self.kill_guard.stop)

    def agent_plan(self, adapter):
        self.args.engine = adapter.__name__.split('_')[0]
        with patch('builtins.print'):
            rename.plan(self.args, adapter.discover)
        raw = (self.out / 'plan.json').read_bytes()
        return json.loads(raw), raw

    def run_apply(self, data, raw):
        with patch('builtins.print'):
            rename.apply(data, self.out, raw)
        return json.loads((self.out / 'state.json').read_text())

    def claude(self):
        encode = lambda value: rename.re.sub(r'[^a-zA-Z0-9]', '-', str(value))
        folder = self.home / 'projects' / encode(self.old)
        folder.mkdir(parents=True)
        file = folder / 'same-id.jsonl'
        record = {'sessionId':'same-id','uuid':'message-id','timestamp':'fixed-time','cwd':str(self.old),'message':{'content':[{'text':str(self.old),'path':str(self.old)}]},'toolUseResult':{'path':str(self.old),'content':str(self.old)}}
        file.write_text(json.dumps(record)+'\n')
        (folder / 'memory').mkdir()
        (folder / 'memory/MEMORY.md').write_text('preserved memory')
        (folder / 'sessions-index.json').write_bytes(rename.packed({'originalPath':str(self.old),'entries':[{'sessionId':'same-id','fullPath':str(file),'projectPath':str(self.old),'firstPrompt':str(self.old)}]}))
        history = self.home / 'history.jsonl'
        history.write_text(json.dumps({'sessionId':'same-id','project':str(self.old),'display':str(self.old)})+'\n')
        config = self.root / 'claude.json'
        config.write_bytes(rename.packed({'projects':{str(self.old):{'allowedTools':[]},'/unrelated':{'keep':True}}}))
        self.args.claude_config = str(config)
        task = self.home / 'tasks/same-id/1.json'
        task.parent.mkdir(parents=True)
        task.write_bytes(rename.packed({'cwd':str(self.old),'content':str(self.old),'id':'task-id'}))
        return folder, file, record, config, task

    def codex(self):
        sessions = self.home / 'sessions/2026/09/30'
        sessions.mkdir(parents=True)
        file = sessions / 'rollout-same-id.jsonl'
        records = [
            {'type':'session_meta','payload':{'id':'same-id','timestamp':'fixed','cwd':str(self.old),'runtime_workspace_roots':[str(self.old),'/unrelated']}},
            {'type':'turn_context','payload':{'cwd':str(self.old / 'src'),'model':'same-model'}},
            {'type':'response_item','payload':{'type':'message','content':[{'text':str(self.old)}],'id':'message-id'}},
            {'type':'response_item','payload':{'type':'function_call_output','output':str(self.old),'call_id':'same-call'}},
            {'type':'event_msg','payload':{'type':'thread_settings_applied','thread_id':'same-id','thread_settings':{'cwd':str(self.old),'runtime_workspace_roots':[str(self.old)]}}},
        ]
        file.write_text(''.join(json.dumps(r)+'\n' for r in records))
        other = sessions / 'rollout-other.jsonl'
        other.write_text(json.dumps({'type':'session_meta','payload':{'id':'other-id','cwd':str(self.old)+'-other'}})+'\n')
        archived = self.home / 'archived_sessions/rollout-archived.jsonl'
        archived.parent.mkdir()
        archived.write_text(json.dumps({'type':'session_meta','payload':{'id':'archived-id','cwd':str(self.old / 'archive')}})+'\n')
        config = self.home / 'config.toml'
        config.write_text('[projects.'+json.dumps(str(self.old))+']\ntrust_level="trusted" # preserve\n')
        global_state = self.home / '.codex-global-state.json'
        global_state.write_bytes(rename.packed({'active-workspace-roots':[str(self.old),'/other'],'local-projects':{'same-project-id':{'name':'a','rootPaths':[str(self.old)]}},'thread-project-assignments':{'same-id':{'cwd':str(self.old),'projectId':'same-project-id'}},'prompt-history':[str(self.old)]}))
        database = self.home / 'state_5.sqlite'
        with closing(sqlite3.connect(database)) as db, db:
            db.execute('CREATE TABLE threads(id TEXT PRIMARY KEY,cwd TEXT,rollout_path TEXT,archived INTEGER)')
            db.executemany('INSERT INTO threads VALUES(?,?,?,?)', [('same-id',str(self.old),str(file),0),('archived-id',str(self.old / 'archive'),str(archived),1),('other-id',str(self.old)+'-other',str(other),0)])
        self.args.codex_db = str(database)
        return file, records, other, global_state, database

    def test_claude_updates_all_metadata_and_preserves_ids_messages_and_memory(self):
        folder, file, record, config, task = self.claude()
        originals = {path:path.read_bytes() for path in [file,config,task]}
        data, raw = self.agent_plan(claude_rename)
        state = self.run_apply(data, raw)
        moved = rename.mapped_file(str(file), data, True)
        actual = json.loads(moved.read_text())
        for key in ('sessionId','uuid','timestamp','message','toolUseResult'):
            self.assertEqual(actual[key], record[key])
        self.assertEqual(actual['cwd'],str(self.new))
        self.assertEqual((moved.parent / 'memory/MEMORY.md').read_text(),'preserved memory')
        index = json.loads((moved.parent / 'sessions-index.json').read_text())
        self.assertEqual(index['entries'][0]['fullPath'],str(moved))
        self.assertEqual(index['entries'][0]['firstPrompt'],str(self.old))
        self.assertIn(str(self.new),json.loads(config.read_text())['projects'])
        self.assertEqual(json.loads(task.read_text())['cwd'],str(self.new))
        self.assertEqual(json.loads(task.read_text())['content'],str(self.old))
        with patch('builtins.print'):
            rename.rollback(data,self.out,state)
        for path,content in originals.items():
            self.assertEqual(path.read_bytes(),content)

    def test_codex_updates_rollout_db_registration_and_trust_preserving_history(self):
        file, records, other, global_state, database = self.codex()
        original = file.read_bytes()
        other_raw = other.read_bytes()
        data, raw = self.agent_plan(codex_rename)
        state = self.run_apply(data, raw)
        actual = [json.loads(line) for line in file.read_text().splitlines()]
        self.assertEqual(actual[0]['payload']['id'],'same-id')
        self.assertEqual(actual[0]['payload']['timestamp'],'fixed')
        self.assertEqual(actual[0]['payload']['cwd'],str(self.new))
        self.assertEqual(actual[1]['payload']['cwd'],str(self.new / 'src'))
        self.assertEqual(actual[2:4],records[2:4])
        self.assertEqual(actual[4]['payload']['thread_settings']['cwd'],str(self.new))
        self.assertEqual(other.read_bytes(),other_raw)
        global_data = json.loads(global_state.read_text())
        self.assertEqual(global_data['thread-project-assignments']['same-id']['cwd'],str(self.new))
        self.assertEqual(global_data['local-projects']['same-project-id']['rootPaths'],[str(self.new)])
        self.assertEqual(global_data['prompt-history'],[str(self.old)])
        with closing(sqlite3.connect(database)) as db:
            self.assertEqual(db.execute('SELECT cwd,archived FROM threads WHERE id="archived-id"').fetchone(),(str(self.new / 'archive'),1))
            self.assertEqual(db.execute('SELECT cwd FROM threads WHERE id="other-id"').fetchone(),(str(self.old)+'-other',))
        with patch('builtins.print'):
            rename.rollback(data,self.out,state)
        self.assertEqual(file.read_bytes(),original)
        with closing(sqlite3.connect(database)) as db:
            self.assertEqual(db.execute('SELECT cwd FROM threads WHERE id="same-id"').fetchone(),(str(self.old),))

    def test_open_metadata_writer_blocks_before_any_rename(self):
        _, file, _, _, _ = self.claude()
        data, raw = self.agent_plan(claude_rename)
        proc = self.process_root / '123'
        (proc / 'fd').mkdir(parents=True)
        (proc / 'fdinfo').mkdir()
        (proc / 'comm').write_text('claude\n')
        (proc / 'status').write_text('State:\tS (sleeping)\n')
        (proc / 'fd/1').symlink_to(file)
        (proc / 'fdinfo/1').write_text('flags:\t0102001\n')
        with file.open('a'):
            with self.assertRaisesRegex(ValueError,'현재 기록 중'):
                self.run_apply(data,raw)
        self.assertTrue(self.old.exists())
        self.assertFalse(self.new.exists())

    def test_db_changed_after_plan_blocks_before_any_rename(self):
        _, _, _, _, database = self.codex()
        data, raw = self.agent_plan(codex_rename)
        with closing(sqlite3.connect(database)) as db, db:
            db.execute('UPDATE threads SET cwd="/manual" WHERE id="same-id"')
        with self.assertRaisesRegex(ValueError,'계획 이후 DB'):
            self.run_apply(data,raw)
        self.assertTrue(self.old.exists())
        self.assertFalse(self.new.exists())

    def test_bad_jsonl_stops_plan_without_touching_data(self):
        _, file, _, _, _ = self.claude()
        file.write_text('{bad json}\n')
        with self.assertRaises(json.JSONDecodeError):
            self.agent_plan(claude_rename)
        self.assertFalse(self.out.exists())
        self.assertTrue(self.old.exists())

    def test_second_engine_can_update_sessions_after_first_engine_renames_folder(self):
        self.claude()
        _, _, _, _, database = self.codex()
        data, raw = self.agent_plan(claude_rename)
        self.run_apply(data,raw)
        self.out = self.root / 'codex-plan'
        self.args.out = str(self.out)
        self.args.sessions_only = True
        data, raw = self.agent_plan(codex_rename)
        self.assertEqual(data['moves'],[])
        self.run_apply(data,raw)
        with closing(sqlite3.connect(database)) as db:
            self.assertEqual(db.execute('SELECT cwd FROM threads WHERE id="same-id"').fetchone(),(str(self.new),))

    def test_cli_rejects_another_engine_plan_before_any_change(self):
        self.claude()
        _, raw = self.agent_plan(claude_rename)
        with patch.object(sys,'argv',['codex_rename.py','apply','--plan',str(self.out/'plan.json'),'--approve',rename.digest(raw)]):
            with self.assertRaisesRegex(ValueError,'다른 도구용 계획'):
                rename.main(codex_rename.discover,'codex')
        self.assertTrue(self.old.exists())
        self.assertFalse(self.new.exists())

    def test_codex_frozen_initial_cwd_does_not_hide_current_database_owner(self):
        file, records, _, _, database = self.codex()
        records[0]['payload']['cwd']='/original-launch-directory'
        file.write_text(''.join(json.dumps(record)+'\n' for record in records))
        data, raw = self.agent_plan(codex_rename)
        self.run_apply(data, raw)
        actual=[json.loads(line) for line in file.read_text().splitlines()]
        self.assertEqual(actual[0]['payload']['cwd'],'/original-launch-directory')
        self.assertEqual(actual[4]['payload']['thread_settings']['cwd'],str(self.new))
        with closing(sqlite3.connect(database)) as db:
            self.assertEqual(db.execute('SELECT cwd FROM threads WHERE id="same-id"').fetchone(),(str(self.new),))

    def test_unrelated_broken_rollout_is_not_read_or_changed(self):
        _, _, other, _, _ = self.codex()
        other.write_text('{broken unrelated history\n')
        data, raw = self.agent_plan(codex_rename)
        self.run_apply(data, raw)
        self.assertEqual(other.read_text(),'{broken unrelated history\n')

    def test_non_cwd_triggers_remain_inactive_during_cwd_update(self):
        _, _, _, _, database = self.codex()
        with closing(sqlite3.connect(database)) as db, db:
            db.execute("CREATE TRIGGER unrelated AFTER UPDATE OF archived ON threads BEGIN UPDATE threads SET cwd='/bad' WHERE id='other-id'; END")
        data, raw = self.agent_plan(codex_rename)
        self.run_apply(data, raw)
        with closing(sqlite3.connect(database)) as db:
            self.assertEqual(db.execute('SELECT cwd FROM threads WHERE id="other-id"').fetchone(),(str(self.old)+'-other',))

    def test_cwd_trigger_is_rejected_before_changes(self):
        _, _, _, _, database = self.codex()
        with closing(sqlite3.connect(database)) as db, db:
            db.execute('CREATE TRIGGER side_effect AFTER UPDATE OF cwd ON threads BEGIN SELECT 1; END')
        with self.assertRaisesRegex(ValueError,'cwd 갱신에 영향'):
            self.agent_plan(codex_rename)
        self.assertTrue(self.old.exists())

    def test_only_path_tokens_change_in_raw_jsonl(self):
        source = '/old'
        target = '/new'
        line = '{ "cwd" : "/old", "sessionId" : "unchanged", "message" : { "content" : "\\uD55C\\uAE00 /old" } }\n'
        expected = line.replace('"cwd" : "/old"', '"cwd" : "/new"')
        self.assertEqual(rename.jsonl_paths(line.encode(),source,target,'claude'),expected.encode())

    def test_open_shared_db_connection_does_not_change_other_sessions(self):
        _, _, _, _, database = self.codex()
        data, raw = self.agent_plan(codex_rename)
        with closing(sqlite3.connect(database)) as reader:
            before=reader.execute('SELECT * FROM threads WHERE id="other-id"').fetchone()
            self.run_apply(data,raw)
            self.assertEqual(reader.execute('SELECT * FROM threads WHERE id="other-id"').fetchone(),before)

    def test_db_write_lock_stops_before_folder_or_metadata_change(self):
        file, _, _, _, database = self.codex()
        original=file.read_bytes()
        data, raw = self.agent_plan(codex_rename)
        with closing(sqlite3.connect(database)) as writer:
            writer.execute('BEGIN IMMEDIATE')
            with self.assertRaises(sqlite3.OperationalError):
                self.run_apply(data,raw)
        self.assertTrue(self.old.exists())
        self.assertFalse(self.new.exists())
        self.assertEqual(file.read_bytes(),original)
        self.assertFalse((self.out/'state.json').exists())


if __name__ == '__main__':
    unittest.main()
