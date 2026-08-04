# Edge cases

Read when the target files are not in the plain state (untracked, project root, one project).

## Upstream-tracked files

If `AGENTS.md` or `CLAUDE.md` is tracked in git, it belongs to the upstream project — never overwrite. Detect with `git ls-files --error-unmatch <file>` (exit 0 = tracked).

- Upstream `AGENTS.md` tracked → write `AGENTS.local.md`; the shim line becomes `@AGENTS.local.md`.
- Upstream `CLAUDE.md` tracked → write the shim to `CLAUDE.local.md`. Claude Code reads both.
- A tracked doc occupies a topic-doc name you need → pick a different untracked name. Never append session content to a tracked file.

## Gitignore

Gitignore every file this skill wrote, as whole-line entries: the fixed set plus each `docs/` topic doc by **exact path** (`docs/plan.md`). A blanket `docs/*` would swallow the project's real docs.

```
AGENTS.md
CLAUDE.md
HANDOFF.md
```

Under the `.local` fallback, ignore those variants instead.

- **Never gitignore a file already tracked in git.**
- No `.gitignore` → create it with the entries you wrote.
- Existing `.gitignore` → append only the missing entries. Do not reorder, dedupe, or reformat the rest.

## Ambiguous target directory

Wrong-project writes are silent corruption that surfaces late. If the current directory is ambiguous — a monorepo package vs its root, a worktree vs its main checkout — confirm before writing. This is the one case where asking beats acting.

## Not a git repo

Skip the tracked/gitignore checks and write the files. `audit.py` degrades the same way.

## Foreign tool blocks

Other tools inject their own banners and auto-generated markers into these files (memory-bank headers, `<!-- BEGIN ... -->` fences). Remove them from files this skill owns — they are another tool's state, not project memory.
