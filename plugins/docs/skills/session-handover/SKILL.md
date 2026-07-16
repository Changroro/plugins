---
name: session-handover
description: Maintains AGENTS.md (durable cross-tool project memory readable by Claude Code, Codex, Cursor, Gemini CLI, and other agents that follow the AGENTS.md open standard) plus a one-line CLAUDE.md `@AGENTS.md` import shim, a rolling HANDOFF.md, and on-demand topic docs under docs/, so a fresh session in any agent can resume work without re-explanation. Routes content by kind — durable rules to AGENTS.md, planning/design/spec and other topical content to docs/<topic>.md files it creates as needed, just-done/next-up to HANDOFF.md — and audits existing files on every run, relocating misplaced content automatically. Runs without asking for confirmation and keeps all per-user files gitignored. Use whenever the user asks to write, update, sync, clean up, or refresh project memory, the next-step log, or session docs — including Korean phrasings like "agents.md 최신화", "agents.md 적어놔", "agents.md 정리", "agents.md 다이어트", "claude.md 최신화", "claude.local.md 최신화", "handoff 업데이트", "핸드오프 작성", "인수인계", "세션 인계", "기획 문서로 옮겨", "plan 문서 갱신", and English phrasings like "update agents md", "clean up agents md", "refresh agents md", "write handoff", "session handover", "update plan doc", "sync memory bank". Handles single-file and combined requests, and the full-set pattern "README / AGENTS.md / HANDOFF before PR".
---

# Session Handover

Maintains project files so a fresh AI session (Claude Code, Codex, Cursor, etc.) can resume work without re-explanation. Each file has one job:

| File | Job | Loaded |
| --- | --- | --- |
| **AGENTS.md** | Durable rules only: user-given rules, conventions, cautions, non-obvious env facts. | Every session, every tool → most expensive file. |
| **CLAUDE.md** | One line: `@AGENTS.md`. Never holds content of its own. | Every Claude session. |
| **HANDOFF.md** | Rolling "just done / next up" log. | Read at session start. |
| **docs/<topic>.md** | Everything durable that is *not* a rule: planning, specs, design decisions, troubleshooting knowledge, backlogs — one topic per file, created as the project needs them. | On demand only. |

AGENTS.md is loaded into every session of every tool — every line there costs context forever. HANDOFF and docs/ files are read on demand. That asymmetry drives all routing: **when in doubt, route away from AGENTS.md.**

All files are written for the next AI session, not for humans. If a human is the only reader who benefits from a line, cut it.

## What goes where

First **route by kind**, then filter. The table applies both to new session content and to lines already sitting in the files (see workflow §3–4).

| Content | Destination |
| --- | --- |
| Project purpose, intent, target users — 1–2 sentences | AGENTS.md |
| User-given rules, conventions, cautions | AGENTS.md |
| Non-obvious environment facts (hidden setup) | AGENTS.md |
| Planning, feature design, specs, roadmap, reference-service detail, troubleshooting lore, or other durable topical knowledge | a `docs/<topic>.md` that fits — create or extend one, named by topic |
| Label of the step just finished | HANDOFF.md |
| Concrete next steps (≤5 items) | HANDOFF.md |
| Unresolved blocker that gates the next step | HANDOFF.md, if real |
| Task backlog larger than next-up | the project's existing task file (e.g. a root TODO.md) if it has one, else a docs/ topic doc |
| Incident story ("X broke when we did Y, rolled back") | compress to a one-line rule in AGENTS.md: "Do not Y (breaks X)." |
| Tech stack, architecture summaries, file paths, directory trees, commit SHAs | nowhere — rediscoverable |
| Historical log of past steps, command outputs, narration for humans | nowhere |

Then two filters, applied line by line to AGENTS.md and HANDOFF.md — a line must survive both:

1. **Rediscoverable?** Learnable from the code, `ls`, or `git log` → out. Directory layouts, file paths, tech stack summaries, architecture diagrams fail.
2. **Load-bearing?** Would removing it cause the next session to make a mistake? No → cut, even if not rediscoverable. Restating the user's global memory (`~/.claude/CLAUDE.md` + imports) fails this test.

"Non-obvious environment facts" = a service running inside a specific container, a port not in `package.json`, an env var not documented elsewhere. Standard commands like `npm run dev` do not qualify; a command does qualify when it carries flags or env vars a session could not guess.

**Budgets: AGENTS.md target ≤60 lines, hard ceiling ~100. HANDOFF.md ≤15 lines.** Over target → prune before writing. Long memory files degrade adherence — a bloated AGENTS.md makes agents ignore the rules that matter.

## docs/ topic files

- Decide the set of docs yourself, per project, by topic — no fixed list. One topic per file, short names that say what's inside.
- AGENTS.md carries only a **brief pointer** to docs/ (one line in its header — see template). Do not enumerate or summarize the docs inside AGENTS.md; the pointer line is what makes them discoverable.
- A topic doc holds intent, design, and knowledge for its topic. It is not a rules file (rules → AGENTS.md), not a next-step log (→ HANDOFF.md), and not a history log. It may grow, but when a plan is fully implemented, compress it to its surviving decisions.
- Start each doc with a one-line HTML comment stating its job, e.g. `<!-- Planning memory for AI sessions. Read on demand. -->`.
- Never write session content into a git-tracked doc — skill-created topic docs are separate, untracked, and gitignored.

## HANDOFF is not a history log

HANDOFF.md is intentionally short. It answers exactly two questions for the next session:

1. **What was just done?** — only the immediately preceding step, with its concrete result. Not every step in the session, not a narrative of the whole project, not command outputs or explanations written for a human reader. One or two short lines.
2. **What should happen next?** — concrete, actionable items the next session can start on without guessing.

When updating HANDOFF.md, delete older "just done" entries. Only the step that was *literally just completed* survives; anything older lives in `git log`. No tech-stack sections, no page-structure tables — those belong in docs/ or nowhere.

## Workflow

### 1. Understand the request

Most requests touch AGENTS.md and HANDOFF.md; docs/ topic files are touched when the session produced topical content or the audit relocates some. CLAUDE.md is touched only when missing or its single line is corrupted. If the current directory is ambiguous, confirm before writing — wrong-project writes are a silent corruption. Everything else runs without asking.

### 2. Gather context

Read existing AGENTS.md / HANDOFF.md / CLAUDE.md and any session-support docs under docs/, but treat them as potentially stale. Verify against `git status` and `git log --oneline -10`.

Scan the conversation and route by the table: rules/cautions → AGENTS.md; planning/design/spec or other topical discussion → the fitting docs/ topic doc; step finished + concrete next actions → HANDOFF.md. If conversation is fresh (e.g., initializing AGENTS.md), draft AGENTS.md from stated intent and a minimal HANDOFF.md with only "next up".

AGENTS.md, CLAUDE.md, and HANDOFF.md live at the project root; topic docs live under `docs/`. Do not scatter into other subdirectories.

#### Upstream-tracked fallback

If `AGENTS.md` or `CLAUDE.md` is tracked in git, it belongs to the upstream project — never overwrite. Detect with `git ls-files --error-unmatch <file>` (exit 0 = tracked):

- Upstream `AGENTS.md` tracked → write to `AGENTS.local.md`; shim becomes `@AGENTS.local.md`.
- Upstream `CLAUDE.md` tracked → write the shim to `CLAUDE.local.md` (Claude Code reads both).
- A tracked doc occupies a topic-doc name you need → pick a different untracked name; never append session content to tracked files.

### 3. Merge, don't overwrite — by meaning, not text

AGENTS.md and docs/ topic files may contain hand-edited content not in this conversation. Read first and **merge** — preserve the meaning of still-true rules/cautions/env facts/plans; only add/refine/remove meaning in response to something explicit in this session. Text is not sacred; content is: relocation and compression per the checklist are required, not optional.

**"Still true" is a verdict, not an assumption.** Verify each preserved entry against the code, environment, and this session. An unconfirmable fact (limit, size, URL, workflow) is a stale candidate: update it if this session shows the current value, else keep it and list it as unverified in the post-write report. Hand-edits are not exempt from the checklist.

HANDOFF.md is regenerable — replace wholesale with the new "just done + next up" snapshot.

CLAUDE.md (or `.local` fallback) is exactly one line: `@AGENTS.md` or `@AGENTS.local.md`. If anything else accumulated there, replace the whole file with the single import line.

### 4. Filter, then write

Run every line of the merged result — pre-existing lines included — through the routing table and the two filters, then run the pre-write checklist below and auto-correct every violation found. Write directly — do not ask "작성할까요?" / "shall I write this?". End with the compact post-write report defined below — nothing else.

#### Pre-write checklist

Scan the merged AGENTS.md / HANDOFF.md / CLAUDE.md and silently fix every violation. No separate audit mode, no quality score, no report-first, no approval prompt — corrections happen inline and are summarized in the post-write report.

- **Misrouted topical content** — planning, feature design, page/screen structures, specs, roadmaps, reference-service detail, troubleshooting lore in AGENTS.md or HANDOFF.md → **move** to a fitting docs/ topic doc, creating it if none fits. Moving, never silent deletion.
- **Code-discoverable content leaked in** — architecture, directory trees, tech-stack summaries, file paths, commit SHAs in AGENTS.md or HANDOFF.md → remove.
- **Caution narration** — a caution longer than one line, or telling a past bug's story instead of the standing constraint → compress to the invariant.
- **Over budget** — AGENTS.md >100 lines or HANDOFF.md >15 → merge overlapping rules, shorten the longest, re-apply the filters until within budget.
- **HANDOFF bloat** — "Just done" holds more than the single immediately-preceding step → keep only the latest, delete the rest.
- **HANDOFF pollution** — date headers, command outputs, narrative paragraphs, `(none)` placeholder blockers → remove.
- **CLAUDE.md pollution** — anything beyond the single `@AGENTS.md` (or `@AGENTS.local.md`) import line → replace the whole file with the one line.
- **git log conflict** — HANDOFF contradicts `git log --oneline -10` → rebuild HANDOFF from current reality.
- **Missing session learnings** — a rule or caution the user gave in this session is absent from AGENTS.md → add it.
- **Human-facing prose** — AGENTS.md written as narrative for a human reader → compress to AI-facing form.
- **Global-memory duplication** — a rule already in the user's global memory (`~/.claude/CLAUDE.md` + imports) restated in AGENTS.md → remove.
- **Volatile facts** — IPs, resource IDs, versions, sizes/counts, dates in AGENTS.md → remove or generalize ("SSH ingress is IP-whitelisted", not the IP). HANDOFF may carry a literal only when the next step needs it.
- **Foreign tool blocks** — content injected by other tools (memory banners, auto-generated headers) → remove from all files.

#### Post-write report (compact)

The entire user-facing output after writing. This shape and nothing else — target ~6 lines; only the `moved`/`cut` listing may extend it:

```
AGENTS.md 58줄 · HANDOFF.md 12줄 · checklist 13/13 (fixed 3)
fixed: <item> — <half-line: what was cut>     ← fixed 항목만, 한 줄씩
moved: docs/<file> ← <n>줄 (<half-line gist>)  ← 재배치가 있을 때만, 대상 파일별 한 줄
cut: "<deleted line, verbatim>"                ← 기존 파일에서 삭제된 줄만, 줄마다
stale 유지: <unverified entries>               ← 있을 때만
```

- Passing items are silent. Report `fixed` only; the `n/n` count proves the full checklist ran.
- `moved` names the destination; the content survives there, so no quoting. `cut` lines from **pre-existing** file content are quoted verbatim — the files are gitignored, so the report is the only recovery path. Draft-stage cuts of this session's own content are not quoted.
- Over budget → one clause ("100줄 초과, 잔여 전부 필터 통과"), not a defense essay.
- **Never mention this skill, its version, or its rules.** The report is about the files, not the tooling.
- No closing narration: no gitignore status, no "다음 세션은 …하면 됩니다", no explaining what the files are for.

### 5. Gitignore the files you wrote

Gitignore every file this skill wrote, as whole-line entries — the fixed set plus each docs/ topic doc you created (exact paths, e.g. `docs/plan.md`; never a blanket `docs/*` that would swallow real project docs). **Never gitignore a file already tracked in git.**

```
AGENTS.md
CLAUDE.md
HANDOFF.md
```

If you fell back to `.local` variants, gitignore those instead.

- No `.gitignore` → create it with the entries you wrote.
- Existing `.gitignore` → append only missing whole-line entries. Don't reorder/dedupe/reformat the rest.

## AGENTS.md template

```markdown
# <Project Name>

> Persistent project memory for AI coding agents (Claude Code, Codex, Cursor, etc.).
> When starting a new session, also read HANDOFF.md before doing any work.
> Plans, specs, and other session docs live under docs/ — read the relevant one on demand.

## Purpose

<What this project is for and who it's for, in 1–2 sentences.>

## Rules & conventions

- <Explicit rules the user has given across sessions.>
- <Work-style directives and tooling preferences.>

## Cautions

- <Known landmines and things the user has told the agent to stop doing.>

## Environment (non-obvious only)

- <Setup facts that are not visible in package.json, pyproject.toml, or similar.>
```

Notes:

- **Purpose = intent and audience, not implementation.** A tech-stack summary is not a purpose; a feature list or reference-service walkthrough belongs in a docs/ topic doc.
- **Rules & conventions**: project-specific only — global work-style rules (commit style, planning workflow, tooling) stay in global memory.
- The docs/ pointer line is dropped while no topic docs exist yet.
- Empty sections are omitted, not filled with placeholders.

## CLAUDE.md template

```markdown
@AGENTS.md
```

The entire file. No headings, no prose, no second line. `@<path>` is Claude Code's inline-include syntax. With the upstream fallback, the file is `CLAUDE.local.md` and/or the line is `@AGENTS.local.md`.

## HANDOFF.md template

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

Notes:

- **Just done**: only the immediately preceding step. Older entries get deleted on update.
- **Next up**: each item must be concrete enough to act on without guessing. "Improve the UX" → useless; "add pagination to the posts list" → actionable.
- **Blockers**: omit the section entirely when empty. No `(none)` placeholders.
- No date headers, no command outputs, no narrative paragraphs.

## Safety

- **Nothing pre-existing disappears unreported.** Every moved line names its destination; every deleted pre-existing line is quoted verbatim in the report. The files are gitignored, so the report is the only recovery path.
- **Preserve hand-edited content by meaning.** Read before write; relocate and compress rather than blind-overwrite or blind-preserve. Preservation still requires the still-true verification (workflow §3).
- **Budgets are hard** — AGENTS.md ≤60 target / ~100 ceiling, HANDOFF.md ≤15 lines.
- **CLAUDE.md is a shim, not a memory file.** It must remain a single line.
- **Trust `git log` over prose.** When HANDOFF and `git log` disagree, rebuild HANDOFF from current reality.
- **Leave upstream-tracked files alone.** Use `.local` fallbacks (see workflow §2).
- **Verify the target directory** when ambiguous. Wrong-project writes surface late.
- **Gitignore is mandatory for files you wrote, never for tracked files.**
- **The pre-write checklist runs on every invocation; the post-write report proves it.** Violations auto-corrected inline — no audit mode, no quality score, no approval prompt.
