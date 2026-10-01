import argparse
from contextlib import closing, ExitStack
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sqlite3
import sys
import tempfile

PROCESS_ROOT = Path('/proc')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def packed(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def under(path, root):
    return path == root or path.startswith(root + os.sep)


def relocated(path, old, new):
    return Path(new + path[len(old):] if under(path, old) else path)


def mapped_file(path, data, after):
    if after:
        for move in sorted(data['moves'], key=lambda item: len(item['source']), reverse=True):
            if under(path, move['source']):
                return relocated(path, move['source'], move['destination'])
    return Path(path)


def path_value(value, old, new):
    return new + value[len(old):] if isinstance(value, str) and under(value, old) else value


def json_patch_text(text, updated):
    decoder = json.JSONDecoder()
    original = json.loads(text)
    changes = []

    def whitespace(position):
        while position < len(text) and text[position].isspace():
            position += 1
        return position

    def visit(before, after, position):
        position = whitespace(position)
        if before == after:
            return decoder.raw_decode(text, position)[1]
        if isinstance(before, dict) and isinstance(after, dict):
            require(len(before) == len(after), '메타데이터 변경이 키 개수를 바꿨습니다')
            removed = [key for key in before if key not in after]
            added = [key for key in after if key not in before]
            mapping = dict(zip(removed, added))
            position += 1
            for key, value in before.items():
                position = whitespace(position)
                _, end = decoder.raw_decode(text, position)
                target = key if key in after else mapping[key]
                if target != key:
                    changes.append((position, end, json.dumps(target, ensure_ascii=False)))
                position = whitespace(end)
                require(text[position] == ':', 'JSON 메타데이터 키 형식 오류')
                position = visit(value, after[target], position + 1)
                position = whitespace(position)
                if text[position] == ',':
                    position += 1
            require(text[position] == '}', 'JSON 메타데이터 객체 형식 오류')
            return position + 1
        if isinstance(before, list) and isinstance(after, list):
            require(len(before) == len(after), '메타데이터 변경이 배열 길이를 바꿨습니다')
            position += 1
            for old_value, new_value in zip(before, after):
                position = whitespace(visit(old_value, new_value, position))
                if text[position] == ',':
                    position += 1
            require(text[position] == ']', 'JSON 메타데이터 배열 형식 오류')
            return position + 1
        end = decoder.raw_decode(text, position)[1]
        changes.append((position, end, json.dumps(after, ensure_ascii=False)))
        return end

    visit(original, updated, 0)
    for start, end, replacement in reversed(changes):
        text = text[:start] + replacement + text[end:]
    require(json.loads(text) == updated, 'JSON 메타데이터 수정 결과 불일치')
    return text


def patch_metadata(obj, old, new):
    protected_keys = {'message', 'content', 'text', 'prompt', 'firstPrompt', 'userPrompt', 'summary', 'preview', 'title', 'input', 'output', 'arguments', 'display', 'toolUseResult', 'toolResult', 'toolResults', 'toolInput', 'toolOutput', 'base_instructions', 'developer_instructions', 'user_instructions'}
    if isinstance(obj, dict):
        for key in list(obj):
            if key in protected_keys or 'history' in key.lower() and key != 'file-history':
                continue
            child = obj[key]
            if isinstance(child, str):
                obj[key] = path_value(child, old, new)
            else:
                patch_metadata(child, old, new)
            target = path_value(key, old, new)
            if target != key:
                require(target not in obj, '경로 키 충돌')
                obj[target] = obj.pop(key)
    elif isinstance(obj, list):
        for index, child in enumerate(obj):
            if isinstance(child, str):
                obj[index] = path_value(child, old, new)
            else:
                patch_metadata(child, old, new)


def jsonl_paths(raw, old, new, kind):
    result = []
    for line in raw.decode().splitlines(keepends=True):
        if not line.strip():
            result.append(line)
            continue
        obj = json.loads(line)
        require(isinstance(obj, dict), '세션 레코드 형식 오류')
        before = packed(obj)
        if kind == 'claude':
            patch_metadata(obj, old, new)
        elif kind == 'history':
            if 'project' in obj:
                obj['project'] = path_value(obj['project'], old, new)
        elif obj.get('type') in {'session_meta', 'turn_context'}:
            patch_metadata(obj.get('payload', {}), old, new)
        elif obj.get('type') == 'event_msg' and obj.get('payload', {}).get('type') == 'thread_settings_applied':
            patch_metadata(obj['payload'].get('thread_settings', {}), old, new)
        result.append(json_patch_text(line, obj) if packed(obj) != before else line)
    return ''.join(result).encode()


def ensure_idle(data):
    require(PROCESS_ROOT.is_dir(), '현재 자동 수정의 활성 writer 검사는 Linux에서 지원합니다')
    paths = {f['path'] for f in data['files'] if f.get('metadata')}
    paths.update(str(mapped_file(f['path'], data, True)) for f in data['files'] if f.get('metadata'))
    if not paths:
        return
    busy = set()
    for proc in PROCESS_ROOT.iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if proc.stat().st_uid != os.getuid():
                continue
            status = (proc / 'status').read_text().splitlines()
            state = next(line.split(':', 1)[1].strip() for line in status if line.startswith('State:'))
            if state.startswith(('Z', 'X')):
                continue
            name = (proc / 'comm').read_text().strip().lower()
            if not name.startswith(('codex', 'claude', 'chatgpt', 'node', 'electron', 'python', 'sqlite')):
                continue
            for fd in (proc / 'fd').iterdir():
                try:
                    target = os.readlink(fd)
                    if target not in paths:
                        continue
                    lines = (proc / 'fdinfo' / fd.name).read_text().splitlines()
                    flags = next(line.split(':', 1)[1].strip() for line in lines if line.startswith('flags:'))
                    if int(flags, 8) & os.O_ACCMODE != os.O_RDONLY:
                        busy.add(target)
                except FileNotFoundError:
                    continue
        except FileNotFoundError:
            continue
        except PermissionError as error:
            raise ValueError('활성 writer 확인 권한이 없습니다; 데이터는 수정하지 않았습니다') from error
    require(not busy, '현재 기록 중인 데이터라 적용하지 않았습니다. 실행을 대신 종료하지 않습니다: ' + ', '.join(sorted(busy)))


def connect_db(path):
    return closing(sqlite3.connect(Path(path).as_uri() + '?mode=ro', uri=True, timeout=1))


def update_db(item, reverse=False):
    with closing(sqlite3.connect(item['path'], timeout=1)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        for session_id, old, new in item['rows']:
            before, after = (new, old) if reverse else (old, new)
            row = db.execute('SELECT cwd FROM threads WHERE id=?', (session_id,)).fetchone()
            if reverse and row == (after,):
                continue
            require(row == (before,), '계획 이후 DB 경로 변경: ' + session_id)
            require(db.execute('UPDATE threads SET cwd=? WHERE id=? AND cwd=?', (after, session_id, before)).rowcount == 1, 'DB 갱신 행 불일치')


def read_file(path):
    require(path.is_file() and not path.is_symlink() and path.resolve() == path, f'실제 일반 파일이 아님: {path}')
    require(path.stat().st_nlink == 1, f'하드링크는 별도 검토 필요: {path}')
    return path.read_bytes()


def protected(path):
    home = Path.home()
    roots = [home / '.codex', home / '.claude', home / '.config/Codex']
    roots.extend(Path(os.environ[key]).absolute() for key in ('CODEX_HOME', 'CLAUDE_CONFIG_DIR') if os.environ.get(key))
    return path.suffix.lower() in {'.jsonl', '.db', '.sqlite', '.sqlite3', '.db-wal', '.db-shm', '.sqlite-wal', '.sqlite-shm'} or path == home / '.claude.json' or '.git' in path.parts or any(under(str(path), str(root)) for root in roots)


def atomic(path, raw, mode=0o600):
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def transform(raw, old, new):
    require(b'\0' not in raw, '바이너리 참조 수정은 지원하지 않습니다')
    require('/' in old and old != new, '변경할 구체적인 경로가 필요합니다')
    require(not any(char in old + new for char in '\n\r\"\x27`$\\;|&<>*?[]{}()!'), '특수문자 경로는 형식별 검토가 필요합니다')
    pattern = r'(?<![\w./\\-])' + re.escape(old) + r'(?=$|[/\\]|[^\w./\\-])'
    text, count = re.subn(pattern, lambda _: new, raw.decode())
    require(count, '일치하는 경로 참조가 없습니다')
    return text.encode()


def plan(args, adapter=None):
    source, target = Path(args.source).absolute(), Path(args.destination).absolute()
    sessions_only = getattr(args, 'sessions_only', False)
    if sessions_only:
        require(not os.path.lexists(source) and target.is_dir() and target.resolve() == target, 'sessions-only는 폴더 rename 이후에만 사용하세요')
    else:
        require(source.is_dir() and source.resolve() == source and not source.is_symlink(), '원본은 실제 절대 디렉터리여야 합니다')
    require(source not in {Path.home(), Path('/')}, '홈/루트 rename 금지')
    require(target.parent.is_dir() and target.parent.resolve() == target.parent, '목적지 부모가 실제 디렉터리가 아님')
    require(sessions_only or not os.path.lexists(target), '목적지가 이미 존재합니다; 덮어쓰지 않습니다')
    require(not under(str(target), str(source)) and not under(str(source), str(target)), '중첩된 경로 rename 금지')
    require(sessions_only or source.stat().st_dev == target.parent.stat().st_dev, '다른 파일시스템은 rename할 수 없습니다')
    require(not (source / '.git').is_file(), 'worktree/submodule은 Git 전용 절차가 필요합니다')
    require(not (source / '.git/worktrees').exists(), '연결된 worktree가 있는 저장소는 Git 전용 절차가 필요합니다')
    info = (target if sessions_only else source).stat()
    moves = [] if sessions_only else [{'source':str(source), 'destination':str(target), 'identity':[info.st_dev, info.st_ino]}]
    data = {'version': 5, 'engine':getattr(args, 'engine', None), 'source': str(source), 'destination': str(target), 'identity': [info.st_dev, info.st_ino], 'moves':moves, 'files': [], 'databases': []}
    staged = []
    for filename, previous, following in args.reference_map:
        path = Path(filename).absolute()
        require(not protected(path), f'세션 기록·DB·에이전트 공유 상태·Git 내부는 자동 수정하지 않습니다: {path}')
        before = read_file(path)
        after = transform(before, previous, following)
        if path.suffix == '.json':
            json.loads(after)
        item = {'path': str(path), 'before': digest(before), 'after': digest(after), 'mode': stat.S_IMODE(path.stat().st_mode), 'blob': len(staged)}
        data['files'].append(item)
        staged.append((before, after))
    if adapter:
        metadata_files, metadata_moves, databases = adapter(args, str(source), str(target))
        for path, after in metadata_files:
            before = read_file(Path(path))
            if before != after:
                data['files'].append({'path':str(path), 'before':digest(before), 'after':digest(after), 'mode':stat.S_IMODE(Path(path).stat().st_mode), 'blob':len(staged), 'metadata':True})
                staged.append((before, after))
        for old, new in metadata_moves:
            require(not os.path.lexists(new), '세션 디렉터리 목적지 충돌')
            require(Path(old).resolve() == Path(old), '세션 디렉터리 심링크는 별도 검토 필요')
            identity = Path(old).stat()
            data['moves'].append({'source':str(old), 'destination':str(new), 'identity':[identity.st_dev, identity.st_ino]})
        data['databases'] = databases
    require(len({f['path'] for f in data['files']}) == len(data['files']), '같은 파일의 중복 참조 수정은 하나의 형식별 변경으로 정리하세요')
    out = Path(args.out).absolute()
    require(out.parent.is_dir() and out.parent.resolve() == out.parent and not os.path.lexists(out), '계획은 실제 부모 아래 새 디렉터리여야 합니다')
    require(not under(str(out), str(source)) and not under(str(out), str(target)), '계획·백업은 rename 대상 밖에 두세요')
    out.mkdir(mode=0o700)
    for index, (before, after) in enumerate(staged):
        atomic(out / f'{index}.before', before)
        atomic(out / f'{index}.after', after)
    atomic(out / 'plan.json', packed(data))
    for index, item in enumerate(data['databases']):
        with connect_db(item['path']) as db, sqlite3.connect(out / f'db-{index}.backup.sqlite') as backup:
            db.backup(backup)
    print(json.dumps({'plan': str(out / 'plan.json'), 'approve': digest(packed(data)), 'moves':data['moves'], 'references':[f['path'] for f in data['files']], 'database_rows':sum(len(d['rows']) for d in data['databases'])}, ensure_ascii=False, indent=2))


def check_payload(item, out):
    for kind in ('before', 'after'):
        require(digest(read_file(out / f"{item['blob']}.{kind}")) == item[kind], '참조 백업 또는 계획 내용이 변조되었습니다')


def check_directory(path, data):
    require(path.is_dir() and not path.is_symlink() and path.resolve() == path, f'rename 디렉터리 누락/교체: {path}')
    info = path.stat()
    require([info.st_dev, info.st_ino] == data['identity'], '계획한 디렉터리가 다른 디렉터리로 바뀌었습니다')


def verify(data, out):
    old, new = data['source'], data['destination']
    require(not os.path.lexists(old), '이전 경로가 다시 생성되었습니다')
    check_directory(Path(new), data)
    for item in data['files']:
        check_payload(item, out)
        path = mapped_file(item['path'], data, True)
        require(digest(read_file(path)) == item['after'], f'변경 후 참조 불일치: {path}')
    for item in data['databases']:
        with connect_db(item['path']) as db:
            for session_id, _, new in item['rows']:
                require(db.execute('SELECT cwd FROM threads WHERE id=?', (session_id,)).fetchone() == (new,), 'DB 세션 경로 검증 실패')
    print('검증 통과: 폴더·세션 경로 갱신, 세션 ID·대화 내용 유지; 프로세스 제어 없음')


def rollback(data, out, state):
    old, new = data['source'], data['destination']
    require(state['status'] in {'applying', 'applied', 'restoring'}, '되돌릴 작업이 없습니다')
    ensure_idle(data)
    for item in data['files']:
        check_payload(item, out)
        path = mapped_file(item['path'], data, True)
        if not path.exists():
            path = Path(item['path'])
        require(digest(read_file(path)) in {item['before'], item['after']}, f'외부 변경이 있어 자동 복구하지 않습니다: {path}')
    state['status'] = 'restoring'
    atomic(out / 'state.json', packed(state))
    for number in reversed(state.get('db_pending', [])):
        update_db(data['databases'][number], reverse=True)
    for item in reversed(data['files']):
        path = mapped_file(item['path'], data, True)
        if not path.exists():
            path = Path(item['path'])
        atomic(path, read_file(out / f"{item['blob']}.before"), item['mode'])
    for move in reversed(data['moves']):
        exists_old, exists_new = os.path.lexists(move['source']), os.path.lexists(move['destination'])
        require(exists_old != exists_new, '복구 경로 충돌/누락')
        path = Path(move['destination'] if exists_new else move['source'])
        check_directory(path, {'identity':move['identity']})
        if exists_new:
            os.rename(move['destination'], move['source'])
    state['status'] = 'restored'
    atomic(out / 'state.json', packed(state))
    print('원래 폴더 이름과 참조를 복구했습니다; 백업은 보존했습니다')


def apply(data, out, raw):
    require(not (out / 'state.json').exists(), '이미 실행한 계획입니다; verify/rollback으로 확인하세요')
    ensure_idle(data)
    for move in data['moves']:
        check_directory(Path(move['source']), {'identity':move['identity']})
        require(not os.path.lexists(move['destination']), '목적지가 생겼습니다; 덮어쓰지 않습니다')
    for item in data['files']:
        check_payload(item, out)
        require(digest(read_file(Path(item['path']))) == item['before'], f'계획 이후 참조 변경: {item["path"]}')
    with ExitStack() as stack:
        connections = []
        for item in data['databases']:
            db = stack.enter_context(closing(sqlite3.connect(item['path'], timeout=1)))
            db.execute('BEGIN IMMEDIATE')
            for session_id, old, _ in item['rows']:
                require(db.execute('SELECT cwd FROM threads WHERE id=?', (session_id,)).fetchone() == (old,), '계획 이후 DB 경로 변경: ' + session_id)
            connections.append(db)
        state = {'status': 'applying', 'plan_hash': digest(raw), 'db_pending': []}
        atomic(out / 'state.json', packed(state))
        try:
            for move in data['moves']:
                os.rename(move['source'], move['destination'])
            for item in data['files']:
                path = mapped_file(item['path'], data, True)
                require(digest(read_file(path)) == item['before'], '적용 중 참조가 변경되었습니다: ' + str(path))
                atomic(path, read_file(out / f"{item['blob']}.after"), item['mode'])
            for number, (database, db) in enumerate(zip(data['databases'], connections)):
                state['db_pending'].append(number)
                atomic(out / 'state.json', packed(state))
                for session_id, old, new in database['rows']:
                    require(db.execute('UPDATE threads SET cwd=? WHERE id=? AND cwd=?', (new, session_id, old)).rowcount == 1, 'DB 갱신 행 불일치')
                db.commit()
            state['status'] = 'applied'
            atomic(out / 'state.json', packed(state))
            verify(data, out)
        except Exception:
            for db in connections:
                db.rollback()
            rollback(data, out, state)
            raise


def main(adapter=None, kind=None):
    parser = argparse.ArgumentParser(description=f'{kind or "로컬"} 프로젝트·세션 경로 자동 수정; 프로세스 제어 없음')
    commands = parser.add_subparsers(dest='command', required=True)
    planning = commands.add_parser('plan')
    planning.set_defaults(engine=kind)
    for flag in ('source', 'destination', 'out'):
        planning.add_argument('--' + flag, required=True)
    planning.add_argument('--reference-map', nargs=3, action='append', default=[], metavar=('FILE', 'OLD', 'NEW'))
    planning.add_argument('--sessions-only', action='store_true')
    if kind == 'claude':
        planning.add_argument('--claude-home', required=True)
        planning.add_argument('--claude-config')
    if kind == 'codex':
        planning.add_argument('--codex-home', required=True)
        planning.add_argument('--codex-db')
    for name in ('apply', 'verify', 'rollback'):
        command = commands.add_parser(name)
        command.add_argument('--plan', required=True)
        if name != 'verify':
            command.add_argument('--approve', required=True)
    args = parser.parse_args()
    if args.command == 'plan':
        plan(args, adapter)
        return
    path = Path(args.plan).absolute()
    raw = read_file(path)
    data = json.loads(raw)
    require(data.get('version') == 5, '폐기된 계획입니다. 도구별 계획을 새로 만드세요')
    require(data.get('engine') == kind, '다른 도구용 계획을 이 스크립트에서 적용할 수 없습니다')
    if args.command != 'verify':
        require(args.approve == digest(raw), '검토한 계획 SHA256이 필요합니다')
    with (path.parent / '.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.command == 'apply':
            apply(data, path.parent, raw)
        else:
            state = json.loads(read_file(path.parent / 'state.json'))
            require(state['plan_hash'] == digest(raw), '적용한 계획과 다릅니다')
            if args.command == 'verify':
                require(state['status'] == 'applied', '적용이 완료되지 않았습니다')
                verify(data, path.parent)
            else:
                rollback(data, path.parent, state)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print(f'project-rename: {error}', file=sys.stderr)
        raise SystemExit(1)
