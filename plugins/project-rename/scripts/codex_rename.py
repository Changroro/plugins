import argparse
import json
from pathlib import Path
import re
import sqlite3
import sys
import tomllib

import rename_core as core


def cwd_triggers_safe(db):
    for name, sql in db.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger' AND tbl_name='threads'"):
        header = re.split(r'\bBEGIN\b', sql, maxsplit=1, flags=re.IGNORECASE)[0]
        if re.search(r'\b(?:BEFORE|AFTER)\s+(?:INSERT|DELETE)\s+ON\s+threads\b', header, re.IGNORECASE):
            continue
        update = re.search(r'\b(?:BEFORE|AFTER)\s+UPDATE\s+OF\s+(.+?)\s+ON\s+threads\b', header, re.IGNORECASE | re.DOTALL)
        columns = {column.strip().strip('"`[]').lower() for column in update[1].split(',')} if update else {'cwd'}
        core.require('cwd' not in columns, 'cwd 갱신에 영향을 주는 DB 트리거는 별도 검토 필요: ' + name)


def config_paths(raw, old, new):
    text = raw.decode()
    before = tomllib.loads(text)
    desired = json.loads(json.dumps(before, default=str))
    core.patch_metadata(desired.get('projects', {}), old, new)
    pattern = r'(?m)^(\s*\[projects\.)("(?:[^"\\]|\\.)*"|\x27[^\x27]*\x27)(\]\s*(?:#.*)?$)'
    def replace(match):
        path = tomllib.loads('v=' + match[2])['v']
        target = core.path_value(path, old, new)
        return match[1] + json.dumps(target, ensure_ascii=False) + match[3] if target != path else match[0]
    text = re.sub(pattern, replace, text)
    core.require(json.loads(json.dumps(tomllib.loads(text), default=str)) == desired, '지원하지 않는 Codex 프로젝트 설정 형식')
    return text.encode()


def session_cwd_paths(raw, previous, target):
    result = []
    for line in raw.decode().splitlines(keepends=True):
        if not line.strip():
            result.append(line)
            continue
        obj = json.loads(line)
        payload = obj.get('payload', {})
        settings = None
        if obj.get('type') in {'session_meta', 'turn_context'}:
            settings = payload
        elif obj.get('type') == 'event_msg' and payload.get('type') == 'thread_settings_applied':
            settings = payload.get('thread_settings', {})
        if isinstance(settings, dict) and settings.get('cwd') == previous:
            settings['cwd'] = target
            line = core.json_patch_text(line, obj)
        result.append(line)
    return ''.join(result).encode()


def discover(args, old, new):
    home = Path(args.codex_home).absolute()
    session_move = getattr(args, 'session_move', False)
    core.require(home.is_dir() and home.resolve() == home and (session_move or not core.under(str(home), old)), 'Codex 홈은 프로젝트 밖의 실제 경로여야 합니다')
    files, databases, selected = [], [], {}
    session_ids = set(getattr(args, 'session_id', []))
    if session_ids:
        core.require(args.sessions_only and args.codex_db, '세션 ID 선택에는 --sessions-only와 실제 --codex-db가 필요합니다')
    current_cwds = {}
    core.require(args.codex_db, '실제 sqlite_home의 Codex 상태 DB를 --codex-db로 명시하세요')
    if args.codex_db:
        path = Path(args.codex_db).absolute()
        core.read_file(path)
        with core.connect_db(path) as db:
            columns = {row[1] for row in db.execute('PRAGMA table_info(threads)')}
            core.require({'id', 'cwd', 'rollout_path'} <= columns, '지원하지 않는 Codex 세션 DB 스키마')
            cwd_triggers_safe(db)
            rows = []
            for session_id, cwd, rollout in db.execute('SELECT id,cwd,rollout_path FROM threads'):
                if (session_id in session_ids if session_ids else isinstance(cwd, str) and core.under(cwd, old)):
                    core.require(isinstance(cwd, str) and Path(cwd).is_absolute(), '세션 ID의 cwd가 올바른 절대 경로가 아닙니다')
                    transcript = Path(rollout)
                    core.require(any(core.under(str(transcript), str(home / directory)) for directory in ('sessions', 'archived_sessions')), 'DB의 세션 파일이 지정한 Codex 홈 밖에 있습니다')
                    core.require(rollout not in selected, 'Codex DB 세션 파일 중복')
                    selected[rollout] = session_id
                    current_cwds[rollout] = cwd
                    rows.append([session_id, cwd, new if session_ids else core.path_value(cwd, old, new)])
            core.require(not session_ids or session_ids == set(selected.values()), '요청한 세션 ID를 DB에서 모두 찾지 못했습니다')
            if rows:
                databases.append({'path':str(path), 'rows':rows})
        core.require_other_session({'engine':'codex', 'databases':databases}, getattr(args, 'caller_thread_id', None))
        transcripts = [Path(path) for path in selected]
    for transcript in sorted(transcripts):
        raw = core.read_file(transcript)
        ids = []
        for line in raw.decode().splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            core.require(isinstance(obj, dict), 'Codex 세션 레코드 형식 오류: ' + str(transcript))
            if obj.get('type') == 'session_meta':
                ids.append(obj.get('payload', {}).get('id'))
        if args.codex_db:
            core.require(ids == [selected[str(transcript)]], 'Codex DB와 세션 파일 ID 불일치: ' + str(transcript))
        after = raw if session_move else core.jsonl_paths(raw, old, new, 'codex')
        if session_ids:
            after = session_cwd_paths(after, current_cwds[str(transcript)], new)
        files.append((transcript, after))
    if session_move:
        return files, [], databases
    config = home / 'config.toml'
    if config.exists():
        files.append((config, config_paths(core.read_file(config), old, new)))
    state = home / '.codex-global-state.json'
    if state.exists():
        raw = core.read_file(state)
        obj = json.loads(raw)
        core.patch_metadata(obj, old, new)
        for project in obj.get('local-projects', {}).values():
            if project.get('name') == Path(old).name and new in project.get('rootPaths', []):
                project['name'] = Path(new).name
        files.append((state, core.packed(obj) if obj != json.loads(raw) else raw))
    return files, [], databases


def move_session(args):
    with core.connect_db(Path(args.codex_db).absolute()) as db:
        rows = db.execute('SELECT id,cwd FROM threads WHERE id=?', (args.session_id,)).fetchall()
    core.require(len(rows) == 1, '이관할 세션 ID를 DB에서 찾지 못했습니다')
    core.require_other_session({'engine':'codex', 'databases':[{'rows':[[rows[0][0], rows[0][1], args.destination]]}]}, args.caller_thread_id)
    args.source = rows[0][1]
    args.session_id = [args.session_id]
    args.sessions_only = True
    args.session_move = True
    args.reference_map = []
    args.engine = 'codex'
    core.plan(args, discover)
    path = Path(args.out).absolute() / 'plan.json'
    raw = core.read_file(path)
    data = json.loads(raw)
    with (path.parent / '.lock').open('a') as stream:
        core.fcntl.flock(stream, core.fcntl.LOCK_EX | core.fcntl.LOCK_NB)
        core.apply(data, path.parent, raw, args.caller_thread_id)


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'mv-session':
            parser = argparse.ArgumentParser(description='프로젝트 폴더를 유지하고 Codex 세션 ID 하나만 목적지로 이관·검증')
            for flag in ('session-id', 'destination', 'codex-home', 'codex-db', 'out'):
                parser.add_argument('--' + flag, required=True)
            parser.add_argument('--caller-thread-id')
            move_session(parser.parse_args(sys.argv[2:]))
        elif len(sys.argv) > 1 and sys.argv[1] == 'mv-project':
            del sys.argv[1]
            core.main(discover, 'codex')
        else:
            raise ValueError('mv-session 또는 mv-project를 지정하세요')
    except (ValueError, OSError, sqlite3.Error) as error:
        print(f'project-rename/codex: {error}', file=sys.stderr)
        raise SystemExit(1)
