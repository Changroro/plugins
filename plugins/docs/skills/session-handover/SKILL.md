---
name: session-handover
description: Maintains AGENTS.md (durable cross-tool project memory readable by Claude Code, Codex, Cursor, Gemini CLI, and other agents that follow the AGENTS.md open standard) plus a one-line CLAUDE.md `@AGENTS.md` import shim and a rolling HANDOFF.md, so a fresh session in any agent can resume work without re-explanation. Runs automatically without asking for confirmation, and ensures all per-user files are gitignored. Use whenever the user asks to write, update, sync, or refresh project memory or the next-step log — including Korean phrasings like "agents.md 최신화", "agents.md 적어놔", "agents.md 정리", "claude.md 최신화", "claude.local.md 최신화", "claude.local.md 적어놔", "handoff 업데이트", "handoff 갱신", "핸드오프 작성", "인수인계", "세션 인계", and English phrasings like "update agents md", "update claude md", "refresh agents md", "write handoff", "session handover", "sync memory bank". Handles single-file and combined requests, and the full-set pattern "README / AGENTS.md / HANDOFF before PR".
---

# Session Handover

Maintains three files at the project root so a fresh AI session (Claude Code, Codex, Cursor, etc.) can resume work without re-explanation:

- **AGENTS.md** — durable project memory. Holds all content.
- **CLAUDE.md** — a single line `@AGENTS.md`. Claude Code imports AGENTS.md through this shim. Never holds content of its own.
- **HANDOFF.md** — rolling "just done / next up" log.

All three are written for the next AI session, not for humans. If a human is the only reader who benefits from a line, cut it.

## What goes where

Decision rule: **if a future session could learn it by reading the code, running `ls`, or running `git log`, it does not belong in either file.** Directory layouts, file paths, tech stack summaries, architecture diagrams fail this test.

| Content                                             | AGENTS.md   | HANDOFF.md     |
| --------------------------------------------------- | ----------- | -------------- |
| Project purpose, intent, target users               | core        | —              |
| User-given rules, conventions, cautions             | core        | —              |
| Non-obvious environment facts (hidden setup)        | yes         | —              |
| Label of the step just finished                     | —           | core           |
| Concrete next steps                                 | —           | core           |
| Unresolved blocker that gates the next step         | —           | if real        |
| Tech stack, architecture, implementation narrative  | —           | —              |
| File paths, directory trees, commit SHAs            | —           | —              |
| Historical log of every past step                   | —           | —              |
| Narration written for the human to read             | —           | —              |

"Non-obvious environment facts" = a service running inside a specific container, a port not in `package.json`, an env var not documented elsewhere. Standard commands like `npm run dev` do not qualify.

## HANDOFF is not a history log

HANDOFF.md is intentionally short. It answers exactly two questions for the next session:

1. **What was just done?** — only the immediately preceding step. Not every step in the session, not a narrative of the whole project, not command outputs or explanations written for a human reader. One or two short lines.
2. **What should happen next?** — concrete, actionable items the next session can start on without guessing.

When updating HANDOFF.md, delete older "just done" entries. Only the step that was *literally just completed* survives; anything older lives in `git log`.

## Workflow

### 1. Understand the request

Most requests touch AGENTS.md and HANDOFF.md. CLAUDE.md is touched only when missing or its single line is corrupted. If the current directory is ambiguous, confirm before writing — wrong-project writes are a silent corruption. Everything else runs without asking.

### 2. Gather context

Read existing files but treat them as potentially stale. Verify against `git status` and `git log --oneline -10`.

Scan the conversation for: user's explicit instructions/intent (→ AGENTS.md), and the step just finished + concrete next actions (→ HANDOFF.md). If conversation is fresh (e.g., initializing AGENTS.md), draft AGENTS.md from stated intent and a minimal HANDOFF.md with only "next up".

All files live at the project root. Do not scatter into `docs/handoff/` or `.claude/handoff/` subdirectories.

#### Upstream-tracked fallback

If `AGENTS.md` or `CLAUDE.md` is tracked in git, it belongs to the upstream project — never overwrite. Detect with `git ls-files --error-unmatch <file>` (exit 0 = tracked):

- Upstream `AGENTS.md` tracked → write to `AGENTS.local.md`; shim becomes `@AGENTS.local.md`.
- Upstream `CLAUDE.md` tracked → write the shim to `CLAUDE.local.md` (Claude Code reads both).

### 3. Merge, don't overwrite

AGENTS.md may contain hand-edited content not in this conversation. Read it first and **merge** — preserve every still-true rule/caution/env fact; only add/refine/remove in response to something explicit in this session.

HANDOFF.md is regenerable — replace wholesale with the new "just done + next up" snapshot.

CLAUDE.md (or `.local` fallback) is exactly one line: `@AGENTS.md` or `@AGENTS.local.md`. If anything else accumulated there, replace the whole file with the single import line.

### 4. Filter, then write

Drop anything rediscoverable from the code. Run the pre-write checklist below and auto-correct every violation found. Write directly — do not ask "작성할까요?" / "shall I write this?". After the write, report what changed, including any checklist corrections.

#### Pre-write checklist

Scan the drafted AGENTS.md / HANDOFF.md / CLAUDE.md and silently fix every violation. No separate audit mode, no quality score, no report-first, no approval prompt — corrections happen inline and are summarized in the post-write report.

- **Code-discoverable content leaked in** — architecture, directory trees, tech-stack summaries, file paths, commit SHAs in AGENTS.md or HANDOFF.md → remove.
- **HANDOFF bloat** — "Just done" holds more than the single immediately-preceding step → keep only the latest, delete the rest.
- **HANDOFF pollution** — date headers, command outputs, narrative paragraphs, `(none)` placeholder blockers → remove.
- **CLAUDE.md pollution** — anything beyond the single `@AGENTS.md` (or `@AGENTS.local.md`) import line → replace the whole file with the one line.
- **git log conflict** — HANDOFF contradicts `git log --oneline -10` → rebuild HANDOFF from current reality.
- **Missing session learnings** — a rule or caution the user gave in this session is absent from AGENTS.md → add it.
- **Human-facing prose** — AGENTS.md written as narrative for a human reader → compress to AI-facing form.

### 5. Gitignore the files you wrote

Default set:

```
AGENTS.md
CLAUDE.md
HANDOFF.md
```

If you fell back to `.local` variants, gitignore those instead. **Never gitignore a file already tracked in git.**

- No `.gitignore` → create it with the entries you wrote.
- Existing `.gitignore` → append only missing whole-line entries. Don't reorder/dedupe/reformat the rest.

## AGENTS.md template

```markdown
# <Project Name>

> Persistent project memory for AI coding agents (Claude Code, Codex, Cursor, etc.).
> When starting a new session, also read HANDOFF.md before doing any work.

## Purpose

<What this project is for and who it's for, in 1–3 sentences.>
<Reference services or benchmarks the user has explicitly pointed to, if any.>

## Rules & conventions

- <Explicit rules the user has given across sessions.>
- <Work-style directives and tooling preferences.>

## Cautions

- <Known landmines and things the user has told the agent to stop doing.>

## Environment (non-obvious only)

- <Setup facts that are not visible in package.json, pyproject.toml, or similar.>
```

## CLAUDE.md template

```markdown
@AGENTS.md
```

The entire file. No headings, no prose, no second line. `@<path>` is Claude Code's inline-include syntax. With the upstream fallback, the file is `CLAUDE.local.md` and/or the line is `@AGENTS.local.md`.

## HANDOFF.md template

```markdown
# HANDOFF — <Project Name>

<!-- For the next AI session. Not a history log. Only "just done" and "next up". -->

## Just done
- <Label of the single step that was literally just completed. One short line.>

## Next up
1. <Concrete action the next session can start on without guessing.>
2. ...

## Blockers
- <Only if something genuinely gates the next step. Omit the section otherwise.>
```

Notes:

- **Just done**: only the immediately preceding step. Older entries get deleted on update.
- **Next up**: each item must be concrete enough to act on without guessing. "Improve the UX" → useless; "add pagination to the posts list" → actionable.
- **Blockers**: omit the section entirely when empty. No `(none)` placeholders.
- No date headers, no command outputs, no narrative paragraphs.

## Safety

- **Preserve hand-edited AGENTS.md content.** Read before write, merge — never blind-overwrite. The file is gitignored, so overwrites are not git-recoverable.
- **CLAUDE.md is a shim, not a memory file.** It must remain a single line.
- **Trust `git log` over prose.** When HANDOFF and `git log` disagree, rebuild HANDOFF from current reality.
- **Leave upstream-tracked `AGENTS.md` / `CLAUDE.md` alone.** Use `.local` fallback (see workflow §2).
- **Verify the target directory** when ambiguous. Wrong-project writes surface late.
- **Gitignore is mandatory for files you wrote, never for tracked files.**
- **The pre-write checklist runs on every invocation.** Violations are auto-corrected inline — no audit mode, no quality score, no approval prompt.
