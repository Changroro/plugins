import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import shutil

import rename_core as core


def discover(args, old, new):
    home = Path(args.claude_home).absolute()
    core.require(home.is_dir() and home.resolve() == home and not core.under(str(home), old), 'Claude 홈은 프로젝트 밖의 실제 경로여야 합니다')
    files, moves = [], []
    session_ids = set()
    projects = home / 'projects'
    encode = lambda path: re.sub(r'[^a-zA-Z0-9]', '-', path)
    if projects.exists():
        for folder in sorted(projects.iterdir()):
            core.require(folder.is_dir() and not folder.is_symlink(), 'Claude 프로젝트 디렉터리 형식 오류')
            owners = set()
            index = folder / 'sessions-index.json'
            if index.exists():
                path = json.loads(core.read_file(index)).get('originalPath')
                if isinstance(path, str) and encode(path) == folder.name:
                    owners.add(path)
            for transcript in folder.glob('*.jsonl'):
                for line in core.read_file(transcript).decode().splitlines():
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    core.require(isinstance(obj, dict), 'Claude 세션 레코드 형식 오류')
                    path = obj.get('cwd')
                    if isinstance(path, str) and encode(path) == folder.name:
                        owners.add(path)
            matched = {p for p in owners if core.under(p, old)}
            core.require(not (folder.name == encode(old) and not matched), 'Claude 세션 디렉터리의 실제 소속을 확인할 수 없습니다')
            if not matched:
                continue
            core.require(len(matched) == 1 and owners == matched, 'Claude 경로 인코딩 충돌')
            path = next(iter(matched))
            session_ids.update(file.stem for file in folder.glob('*.jsonl'))
            target = projects / encode(core.path_value(path, old, new))
            if target != folder:
                moves.append((folder, target))
            for transcript in folder.rglob('*.jsonl'):
                files.append((transcript, core.jsonl_paths(core.read_file(transcript), old, new, 'claude')))
            if index.exists():
                obj = json.loads(core.read_file(index))
                before = core.packed(obj)
                core.patch_metadata(obj, old, new)
                core.patch_metadata(obj, str(folder), str(target))
                files.append((index, core.packed(obj) if core.packed(obj) != before else core.read_file(index)))
    history = home / 'history.jsonl'
    if history.exists():
        files.append((history, core.jsonl_paths(core.read_file(history), old, new, 'history')))
    if args.claude_config:
        config = Path(args.claude_config).absolute()
        obj = json.loads(core.read_file(config))
        before = core.packed(obj)
        core.patch_metadata(obj.get('projects', {}), old, new)
        files.append((config, core.packed(obj) if core.packed(obj) != before else core.read_file(config)))
    else:
        candidates = [home / '.claude.json', home.parent / '.claude.json']
        core.require(not any(p.exists() for p in candidates), '프로젝트 설정 파일이 있습니다. 실제 파일을 --claude-config로 명시하세요')
    for name in ('settings.json', 'settings.local.json'):
        path = home / name
        if path.exists() and (not args.claude_config or path != Path(args.claude_config).absolute()):
            raw = core.read_file(path)
            obj = json.loads(raw)
            before = core.packed(obj)
            core.patch_metadata(obj, old, new)
            files.append((path, core.packed(obj) if core.packed(obj) != before else raw))
    for name in ('session-env', 'file-history', 'todos', 'tasks'):
        folder = home / name
        if not folder.exists():
            continue
        for path in folder.rglob('*.json'):
            if not any(Path(part).stem in session_ids or Path(part).stem.split('-agent-')[0] in session_ids for part in path.relative_to(folder).parts):
                continue
            raw = core.read_file(path)
            obj = json.loads(raw)
            before = core.packed(obj)
            core.patch_metadata(obj, old, new)
            files.append((path, core.packed(obj) if core.packed(obj) != before else raw))
    return files, moves, []


def move_session(args):
    home = Path(args.claude_home).absolute()
    source = Path(args.source).absolute()
    destination = Path(args.destination).absolute()
    transcript = Path(args.session_file).absolute()
    out = Path(args.out).absolute()
    encode = lambda path: re.sub(r'[^a-zA-Z0-9]', '-', str(path))
    source_dir = home / 'projects' / encode(source)
    target_dir = home / 'projects' / encode(destination)
    core.require(source.is_dir() and destination.is_dir() and source != destination, '원본·목적지 프로젝트가 실제 디렉터리여야 합니다')
    core.require(source.resolve() == source and destination.resolve() == destination and home.resolve() == home, '프로젝트와 Claude 홈은 실제 경로여야 합니다')
    core.require(transcript.parent == source_dir and transcript.suffix == '.jsonl', '지정한 프로젝트의 실제 주 세션 JSONL만 복사할 수 있습니다')
    core.require(not os.path.lexists(target_dir) and not os.path.lexists(out), '목적지 세션 디렉터리·백업이 이미 존재합니다')
    core.require(out.parent.is_dir() and out.parent.resolve() == out.parent and not core.under(str(out), str(home)) and not core.under(str(out), str(destination)), '백업은 Claude 홈·목적지 밖의 새 디렉터리여야 합니다')
    raw = core.read_file(transcript)
    records = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    core.require(all(isinstance(record, dict) for record in records), 'Claude 세션 레코드 형식 오류')
    core.require({record['sessionId'] for record in records if record.get('sessionId')} == {transcript.stem}, '세션 ID와 파일명 불일치')
    core.require(any(record.get('cwd') == str(source) for record in records), '세션의 원본 프로젝트 소속 불일치')
    files = [(transcript, raw)]
    sidecars = source_dir / transcript.stem
    if sidecars.exists():
        core.require(sidecars.is_dir() and not sidecars.is_symlink(), '세션 부속 디렉터리 형식 오류')
        files.extend((path, core.read_file(path)) for path in sorted(sidecars.rglob('*')) if path.is_file())
    index_path = source_dir / 'sessions-index.json'
    index_before = core.read_file(index_path) if index_path.exists() else None
    guard = {'files':[{'path':str(path), 'metadata':True} for path, _ in files], 'moves':[]}
    if index_before is not None:
        guard['files'].append({'path':str(index_path), 'metadata':True})
    core.ensure_idle(guard)
    core.require(out.parent.stat().st_dev == source_dir.parent.stat().st_dev, '백업·세션 저장소는 같은 파일시스템이어야 합니다')
    out.mkdir(mode=0o700)
    entries = []
    target_index_digest = None
    with tempfile.TemporaryDirectory(dir=out) as temporary:
        staged = Path(temporary) / 'session'
        staged.mkdir()
        for index, (path, before) in enumerate(files):
            after = core.jsonl_paths(before, str(source), str(destination), 'claude') if path.suffix == '.jsonl' else before
            target = staged / path.relative_to(source_dir)
            target.parent.mkdir(parents=True, exist_ok=True)
            core.atomic(out / f'{index}.before', before)
            core.atomic(target, after, path.stat().st_mode & 0o777)
            entries.append({'source':str(path), 'target':str(target_dir / path.relative_to(source_dir)), 'before':core.digest(before), 'after':core.digest(after)})
        if index_before is not None:
            index = json.loads(index_before)
            index['entries'] = [entry for entry in index.get('entries', []) if entry.get('sessionId') == transcript.stem]
            core.patch_metadata(index, str(source_dir), str(target_dir))
            core.patch_metadata(index, str(source), str(destination))
            core.atomic(out / 'sessions-index.before', index_before)
            target_index = core.packed(index)
            core.atomic(staged / 'sessions-index.json', target_index)
            target_index_digest = core.digest(target_index)
        core.ensure_idle(guard)
        for path, before in files:
            core.require(core.read_file(path) == before, '복사 도중 원본 세션이 변경됐습니다')
        core.require(not os.path.lexists(target_dir), '복사 도중 목적지 세션 디렉터리가 생성됐습니다')
        os.rename(staged, target_dir)
    for entry in entries:
        core.require(core.digest(core.read_file(Path(entry['source']))) == entry['before'], '원본 세션 변경 발견')
        core.require(core.digest(core.read_file(Path(entry['target']))) == entry['after'], '복사한 세션 검증 실패')
    core.ensure_idle(guard)
    if index_before is not None:
        core.require(core.read_file(index_path) == index_before, '검증 중 원본 인덱스 변경 발견')
    sidecar_backup = out / 'sidecars-original'
    remaining_raw = None
    if index_before is not None:
        remaining = json.loads(index_before)
        remaining['entries'] = [entry for entry in remaining.get('entries', []) if entry.get('sessionId') != transcript.stem]
        remaining_raw = core.packed(remaining)
    try:
        if sidecars.exists():
            core.require({p for p in sidecars.rglob('*') if p.is_file()} == {p for p, _ in files[1:]}, '검증 중 원본 세션 부속 파일 변경 발견')
            os.rename(sidecars, sidecar_backup)
        if index_before is not None:
            core.atomic(index_path, remaining_raw, index_path.stat().st_mode & 0o777)
        core.require(core.read_file(transcript) == raw, '삭제 전에 원본 세션 변경 발견')
        os.replace(transcript, out / '0.before')
    except Exception:
        if sidecar_backup.exists() and not sidecars.exists():
            os.rename(sidecar_backup, sidecars)
        if not transcript.exists():
            core.atomic(transcript, raw)
        if index_before is not None:
            core.require(core.read_file(index_path) in (index_before, remaining_raw), '외부 인덱스 변경이 있어 덮어쓰지 않습니다; 백업을 확인하세요')
            core.atomic(index_path, index_before)
        expected = {Path(entry['target']) for entry in entries}
        if target_index_digest is not None:
            expected.add(target_dir / 'sessions-index.json')
            core.require(core.digest(core.read_file(target_dir / 'sessions-index.json')) == target_index_digest, '목적지 인덱스가 변경되어 제거하지 않습니다')
        core.require({p for p in target_dir.rglob('*') if p.is_file()} == expected, '목적지에 다른 파일이 생겨 제거하지 않습니다')
        for entry in entries:
            core.require(core.digest(core.read_file(Path(entry['target']))) == entry['after'], '목적지 세션이 변경되어 제거하지 않습니다')
        shutil.rmtree(target_dir)
        raise
    core.require(not transcript.exists() and not sidecars.exists(), '원본 세션 제거 검증 실패')
    for entry in entries:
        core.require(core.digest(core.read_file(Path(entry['target']))) == entry['after'], '이동 후 목적지 세션 검증 실패')
    audit = {'status':'verified', 'mode':'mv-session', 'session_id':transcript.stem, 'source_project':str(source), 'destination_project':str(destination), 'source_removed':True, 'files':entries}
    core.atomic(out / 'audit.json', core.packed(audit))
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'mv-session':
            parser = argparse.ArgumentParser(description='Claude 세션을 복사·검증한 뒤 원본에서 제거해 목적지 하나로 이동')
            for flag in ('source', 'destination', 'session-file', 'claude-home', 'out'):
                parser.add_argument('--' + flag, required=True)
            move_session(parser.parse_args(sys.argv[2:]))
        elif len(sys.argv) > 1 and sys.argv[1] == 'mv-project':
            del sys.argv[1]
            core.main(discover, 'claude')
        else:
            raise ValueError('mv-session 또는 mv-project를 지정하세요')
    except (ValueError, OSError) as error:
        print(f'project-rename/claude: {error}', file=sys.stderr)
        raise SystemExit(1)
