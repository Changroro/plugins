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

Two filters, applied line by line — a line must survive both:

1. **Rediscoverable?** Learnable from the code, `ls`, or `git log` → out. Directory layouts, file paths, tech stack summaries, architecture diagrams fail.
2. **Load-bearing?** Would removing it cause the next session to make a mistake? No → cut, even if not rediscoverable. Restating the user's global memory (`~/.claude/CLAUDE.md` + imports) fails this test.

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

"Non-obvious environment facts" = a service running inside a specific container, a port not in `package.json`, an env var not documented elsewhere. Standard commands like `npm run dev` do not qualify; a command does qualify when it carries flags or env vars a session could not guess.

**AGENTS.md budget: target ≤60 lines, hard ceiling ~100.** Over target → prune before writing. Long memory files degrade adherence.

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

AGENTS.md may contain hand-edited content not in this conversation. Read it first and **merge** — preserve still-true rules/cautions/env facts; only add/refine/remove in response to something explicit in this session.

**"Still true" is a verdict, not an assumption.** Verify each preserved entry against the code, environment, and this session. An unconfirmable fact (limit, size, URL, workflow) is a stale candidate: update it if this session shows the current value, else keep it and list it as unverified in the post-write report. Hand-edits are not exempt from the checklist.

HANDOFF.md is regenerable — replace wholesale with the new "just done + next up" snapshot.

CLAUDE.md (or `.local` fallback) is exactly one line: `@AGENTS.md` or `@AGENTS.local.md`. If anything else accumulated there, replace the whole file with the single import line.

### 4. Filter, then write

Run every drafted line through the two filters (rediscoverable? load-bearing?), then run the pre-write checklist below and auto-correct every violation found. Write directly — do not ask "작성할까요?" / "shall I write this?". After the write, output the post-write report defined below — the report is the proof that the checklist actually ran.

#### Pre-write checklist

Scan the drafted AGENTS.md / HANDOFF.md / CLAUDE.md and silently fix every violation. No separate audit mode, no quality score, no report-first, no approval prompt — corrections happen inline and are summarized in the post-write report.

- **Code-discoverable content leaked in** — architecture, directory trees, tech-stack summaries, file paths, commit SHAs in AGENTS.md or HANDOFF.md → remove.
- **HANDOFF bloat** — "Just done" holds more than the single immediately-preceding step → keep only the latest, delete the rest.
- **HANDOFF pollution** — date headers, command outputs, narrative paragraphs, `(none)` placeholder blockers → remove.
- **CLAUDE.md pollution** — anything beyond the single `@AGENTS.md` (or `@AGENTS.local.md`) import line → replace the whole file with the one line.
- **git log conflict** — HANDOFF contradicts `git log --oneline -10` → rebuild HANDOFF from current reality.
- **Missing session learnings** — a rule or caution the user gave in this session is absent from AGENTS.md → add it.
- **Human-facing prose** — AGENTS.md written as narrative for a human reader → compress to AI-facing form.
- **Global-memory duplication** — a rule already in the user's global memory (`~/.claude/CLAUDE.md` + imports) restated in AGENTS.md → remove.
- **Volatile facts** — IPs, resource IDs, versions, sizes/counts, dates in AGENTS.md → remove or generalize ("SSH ingress is IP-whitelisted", not the IP). HANDOFF may carry a literal only when the next step needs it.
- **Foreign tool blocks** — content injected by other tools (memory banners, auto-generated headers) → remove from all three files.
- **Caution narration** — a caution longer than one line, or telling a past bug's story instead of the standing constraint → compress to the invariant.

#### Post-write report (mandatory)

Replaces free-form "what changed" narration:

- One line per checklist item: `pass` or `fixed: <what>`. A missing item means the checklist did not run.
- Final line counts vs the ≤60-line AGENTS.md target.
- Unverified stale candidates from the merge, if any.

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

Notes:

- **Purpose = intent and audience, not implementation.** A tech-stack summary is not a purpose.
- **Rules & conventions**: project-specific only — global work-style rules (commit style, planning workflow, tooling) stay in global memory.
- Empty sections are omitted, not filled with placeholders.

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

- **Preserve hand-edited AGENTS.md content.** Read before write, merge — never blind-overwrite. The file is gitignored, so overwrites are not git-recoverable. Preservation still requires the still-true verification (workflow §3).
- **AGENTS.md stays within budget** — ≤60 target, ~100 ceiling.
- **CLAUDE.md is a shim, not a memory file.** It must remain a single line.
- **Trust `git log` over prose.** When HANDOFF and `git log` disagree, rebuild HANDOFF from current reality.
- **Leave upstream-tracked `AGENTS.md` / `CLAUDE.md` alone.** Use `.local` fallback (see workflow §2).
- **Verify the target directory** when ambiguous. Wrong-project writes surface late.
- **Gitignore is mandatory for files you wrote, never for tracked files.**
- **The pre-write checklist runs on every invocation; the post-write report proves it.** Violations auto-corrected inline — no audit mode, no quality score, no approval prompt.
