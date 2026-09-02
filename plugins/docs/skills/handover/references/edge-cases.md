# Edge cases

## Tracked files and external ownership

Git tracking proves repository ownership, not upstream/external ownership. Update a tracked memory or canonical document when the user's request includes it, and never add it to gitignore.

Treat a repository as external/upstream-owned only when the repository context, remote ownership, contribution instructions, or the user establishes that fact. If changing its memory files is outside the task, leave them intact and create a local override only when local instructions are needed.

Use `AGENTS.override.md`, not `AGENTS.local.md`, because Codex recognizes the override name. Pair it with a Claude import, normally `CLAUDE.local.md` containing `@AGENTS.override.md`.

## Existing Claude instructions

Do not overwrite a populated CLAUDE file. Add the effective AGENTS import as a standalone line while preserving Claude-specific instructions. A newly created CLAUDE file may remain a one-line import.

When both `AGENTS.md` and `AGENTS.override.md` exist in a directory, import the override because it is the effective Codex file for that scope.

## Gitignore

For each new local AI-only file, add an exact path or a narrowly scoped pattern. Keep repository-canonical documents trackable. Never ignore a tracked file or blanket-ignore a real documentation tree.

Examples:

```gitignore
/AGENTS.override.md
/CLAUDE.local.md
/HANDOFF.md
/services/api/docs/local-operations.md
```

Do not reorder, deduplicate, or reformat unrelated gitignore entries.

## Nested scopes

Put a rule in the nearest directory that covers every place it applies. A component rule goes in that component's AGENTS file and gets a same-scope Claude import. Do not repeat ancestor rules.

Put durable non-rule knowledge in that component's existing documentation area. A root-level index may link to it when the project already maintains such an index, but AGENTS must not enumerate documents.

## Ambiguous target

Confirm before writing when the current directory could mean a monorepo root versus a package, or a worktree versus its main checkout. Wrong-scope memory silently affects later sessions.

## Non-git projects

Skip tracking and gitignore checks. Preserve the same role and scope boundaries.

## Foreign generated blocks

Remove third-party generated banners and memory-bank fences only during a restart of files the task authorizes. A handover does not clean unrelated old content.
