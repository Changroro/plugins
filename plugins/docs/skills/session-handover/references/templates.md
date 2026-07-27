# Templates

Read when creating a file from scratch, or when an existing file's shape has drifted.

## AGENTS.md

```markdown
# <Project Name>

> Persistent project memory for AI coding agents (Claude Code, Codex, Cursor, etc.).
> When starting a new session, also read HANDOFF.md before doing any work.
> Plans, specs, and other session docs live under docs/ — read the relevant one on demand.

## Purpose

<What this project is for and who it's for, in 1–2 sentences.>

## Rules & conventions

- <Explicit rules the user has given across sessions.>

## Cautions

- <Known landmines and things the user has told the agent to stop doing.>

## Environment (non-obvious only)

- <Setup facts not visible in package.json, pyproject.toml, or similar.>
```

- **Purpose = intent and audience, not implementation.** A tech-stack summary is not a purpose; a feature list belongs in a `docs/` topic doc.
- **Rules & conventions**: project-specific only. Global work-style rules stay in global memory.
- Drop the `docs/` pointer line while no topic docs exist.
- Omit empty sections rather than filling them with placeholders.

## CLAUDE.md

```markdown
@AGENTS.md
```

The entire file — no heading, no prose, no second line. `@<path>` is Claude Code's inline-include syntax. Under the upstream fallback the file is `CLAUDE.local.md` and/or the line is `@AGENTS.local.md`.

## HANDOFF.md

```markdown
# HANDOFF — <Project Name>

<!-- For the next AI session. Not a history log. ≤15 lines. -->

## Just done
- <The single step literally just completed, with its concrete result. 1–2 lines.>

## Next up
1. <Concrete action the next session can start on without guessing.>
2. ...

## Blockers
- <Only if something genuinely gates the next step. Omit the section otherwise.>
```

- **Just done**: only the immediately preceding step. Older entries are deleted on update — they live in `git log`.
- **Next up**: actionable without guessing. "Improve the UX" is useless; "add pagination to the posts list" is not.
- **Blockers**: omit the section entirely when empty.
- No date headers, no command output, no narrative paragraphs.
