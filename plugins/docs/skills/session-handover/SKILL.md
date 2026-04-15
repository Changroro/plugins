---
name: session-handover
description: Maintains a project's CLAUDE.local.md (durable project memory) and HANDOFF.md (append-only session log) so a fresh Claude session can resume work without re-explanation. Use whenever the user asks to write, update, sync, or refresh either file — including Korean phrasings like "claude.local.md 최신화", "claude.local.md 적어놔", "claude.local.md 정리", "handoff 업데이트", "handoff 갱신", "핸드오프 작성", "인수인계", "세션 인계", and English phrasings like "update claude local", "refresh claude md", "write handoff", "session handover", "sync memory bank". Handles single-file and combined requests, and the full-set pattern "README / claude.local.md / HANDOFF before PR".
---

# Session Handover

Maintains two files that let a fresh Claude Code session pick up work without the user re-explaining anything:

- **CLAUDE.local.md** — durable project memory. The project's intent and the rules the user has given, valid across every session.
- **HANDOFF.md** — an append-only log of what was just done and what to do next.

Both files are written **primarily for a future Claude session, not as polished human documentation**. The human already knows what they built and why; these files exist to give the next session the context it cannot recover on its own. Keeping that audience in mind is what keeps both files useful.

## What goes where

The single rule that decides what belongs in either file: **if a future session could learn it by reading the code, running `ls`, or running `git log`, it does not belong in either file.** Directory layouts, file paths, tech stack summaries, architecture diagrams, and "we use X for Y" explanations each fail this test. They waste space and grow stale within days.

The difference between the two files is temporal, not topical. CLAUDE.local.md holds what is true across every session. HANDOFF.md holds what changed in the last one.

| Content                                             | CLAUDE.local.md | HANDOFF.md     |
| --------------------------------------------------- | --------------- | -------------- |
| Project purpose, intent, target users               | core            | —              |
| User-given rules, conventions, cautions             | core            | —              |
| Non-obvious environment facts (hidden setup)        | yes             | —              |
| Brief labels of features just completed             | —               | core           |
| Concrete next steps                                 | —               | core           |
| Unresolved blockers, pending decisions              | —               | if real        |
| Failed approaches worth warning about               | —               | if non-obvious |
| Tech stack, architecture, implementation narrative  | —               | —              |
| File paths, directory trees, commit SHAs            | —               | —              |
| "Current progress" narration                        | —               | —              |

"Non-obvious environment facts" means things that would surprise a fresh session — a service running inside a specific container, a port assignment that isn't in `package.json`, an env var whose existence isn't documented anywhere else. Standard commands like `npm run dev` or `cargo build` do not qualify; the next session will find them on its own.

## Workflow

### 1. Understand the request

Decide which files to touch. Most requests touch both; some touch only one. If the current directory is at all ambiguous, confirm it before doing anything — writing these files into the wrong project is a silent corruption that may not surface for a while.

### 2. Gather context

Read whichever of the two files already exist, but treat them as potentially stale. An existing HANDOFF was written by some earlier session (possibly a different tool) and may no longer match reality. Verify against `git status` and `git log --oneline -10` rather than trusting prior narrative.

Then scan the current conversation for the material that actually belongs in each file: the user's explicit instructions and intent for CLAUDE.local.md, the session's concrete outcomes and next steps for HANDOFF.md. If the conversation is fresh and there is nothing to log yet (e.g., the user is initializing CLAUDE.local.md at the start of a project), draft only that file from the user's stated intent, and create HANDOFF.md as an empty scaffold the next session can append to.

Both files live at the project root, alongside each other. If either file does not yet exist, create it there. Do not scatter them into `docs/handoff/` or `.claude/handoff/` subdirectories — keeping the pair colocated at the root is what makes them easy for the next session to find.

If a `CLAUDE.md` is tracked in git from before the user started working with Claude on the repo, leave it alone. That file belongs to the upstream project, not the user. User-specific content goes in `CLAUDE.local.md` beside it.

### 3. Draft, then filter

Draft both files internally, then remove anything that would be rediscoverable from the code. This rediscoverability filter is the whole job — a draft that fails it is worse than no update, because it teaches the next session bad habits and bloats the context budget for every future run. The filtered drafts are what you show the user in step 4; don't present raw unfiltered drafts.

For HANDOFF, append a new dated entry to the top of the file. Treat older entries as history — don't rewrite, merge, or trim them as part of normal updates, because the trail of past decisions is part of what makes the file valuable to the next session.

### 4. Confirm, then write

Show the filtered drafts and wait for approval before writing. The user maintains these files across many projects and expects to review changes. Silent overwrites break that trust and can destroy hand-edited content.

## CLAUDE.local.md template

```markdown
# <Project Name>

> Persistent project memory for Claude Code.
> When starting a new session, also read the latest entry in HANDOFF.md before doing any work.

## Purpose

<What this project is for and who it's for, in 1–3 sentences.>
<Reference services or benchmarks the user has explicitly pointed to, if any.>

## Rules & conventions

- <Explicit rules the user has given across sessions.>
- <Work-style directives and tooling preferences.>

## Cautions

- <Known landmines and things the user has told Claude to stop doing.>

## Environment (non-obvious only)

- <Setup facts that are not visible in package.json, pyproject.toml, or similar.>
```

Keep it short by default. Every line should carry content a future session could not derive on its own; when in doubt, cut.

## HANDOFF.md template

```markdown
# HANDOFF — <Project Name>

<!-- For Claude Code. Append new entries at the top; never edit older ones. -->

## <YYYY-MM-DD HH:MM>

### Just done
- <Feature label. One line. "admin login flow" — not "built admin login using JWT + Supabase Auth with RLS".>
- <Another feature label.>

### Next up
1. <Concrete action, not a vague goal.>
2. ...

### Open issues
- <Only if something is genuinely unresolved.>

### Avoid
- <A failed approach worth a warning. Omit the section if none.>

---

<!-- Older entries follow below, untouched. Omit this divider when writing the very first entry. -->
```

A few things the template alone doesn't capture:

- **Next up** is the highest-value section. Each item should be concrete enough that the next session can act on it without guessing. "Improve the UX" is useless; "add pagination to the posts list" is actionable.
- **Open issues** and **Avoid** are optional. Omit them entirely when empty rather than leaving `(none)` placeholders — noise trains the next session to skim past the whole file.

## Safety

These boundaries exist for specific reasons; follow them, but also understand why, so you can make sensible calls at the edges.

- **Confirm before writing.** These files are the user's memory across sessions. Silent overwrites can destroy hand-edited content that isn't recoverable from git.
- **Append, don't replace, HANDOFF.** Old entries are history. Rewriting them loses the trail of past decisions.
- **Trust code over prose.** When an existing HANDOFF and `git log` disagree, believe `git log` and surface the discrepancy to the user before propagating either version.
- **Leave upstream `CLAUDE.md` alone.** When a repository ships its own `CLAUDE.md`, that file belongs to the project. User-specific additions go in `CLAUDE.local.md` beside it.
- **Verify the target directory** whenever there is any ambiguity. Writing these files into the wrong project is the worst failure mode because the user may not notice until much later.
