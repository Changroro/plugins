import json
from pathlib import Path
import re
import sys

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


if __name__ == '__main__':
    try:
        core.main(discover, 'claude')
    except (ValueError, OSError) as error:
        print(f'claude-project-rename: {error}', file=sys.stderr)
        raise SystemExit(1)
