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


def discover(args, old, new):
    home = Path(args.codex_home).absolute()
    core.require(home.is_dir() and home.resolve() == home and not core.under(str(home), old), 'Codex 홈은 프로젝트 밖의 실제 경로여야 합니다')
    files, databases, selected = [], [], {}
    existing = list(home.glob('state_*.sqlite'))
    core.require(args.codex_db or not existing, '실제 sqlite_home의 Codex 상태 DB를 --codex-db로 명시하세요')
    if args.codex_db:
        path = Path(args.codex_db).absolute()
        core.read_file(path)
        with core.connect_db(path) as db:
            columns = {row[1] for row in db.execute('PRAGMA table_info(threads)')}
            core.require({'id', 'cwd', 'rollout_path'} <= columns, '지원하지 않는 Codex 세션 DB 스키마')
            cwd_triggers_safe(db)
            rows = []
            for session_id, cwd, rollout in db.execute('SELECT id,cwd,rollout_path FROM threads'):
                if isinstance(cwd, str) and core.under(cwd, old):
                    transcript = Path(rollout)
                    core.require(any(core.under(str(transcript), str(home / directory)) for directory in ('sessions', 'archived_sessions')), 'DB의 세션 파일이 지정한 Codex 홈 밖에 있습니다')
                    core.require(rollout not in selected, 'Codex DB 세션 파일 중복')
                    selected[rollout] = session_id
                    rows.append([session_id, cwd, core.path_value(cwd, old, new)])
            if rows:
                databases.append({'path':str(path), 'rows':rows})
        transcripts = [Path(path) for path in selected]
    else:
        transcripts = []
        for directory in ('sessions', 'archived_sessions'):
            folder = home / directory
            if folder.exists():
                core.require(not folder.is_symlink(), 'Codex 세션 디렉터리 심링크는 별도 검토 필요')
                transcripts.extend(folder.rglob('*.jsonl'))
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
        files.append((transcript, core.jsonl_paths(raw, old, new, 'codex')))
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


if __name__ == '__main__':
    try:
        core.main(discover, 'codex')
    except (ValueError, OSError, sqlite3.Error) as error:
        print(f'codex-project-rename: {error}', file=sys.stderr)
        raise SystemExit(1)
