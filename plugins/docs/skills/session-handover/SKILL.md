---
name: session-handover
description: Maintains a project's CLAUDE.local.md (durable project memory) and HANDOFF.md (rolling next-step log) so a fresh Claude session can resume work without re-explanation. Runs automatically without asking for confirmation, and ensures both files are gitignored. Use whenever the user asks to write, update, sync, or refresh either file — including Korean phrasings like "claude.local.md 최신화", "claude.local.md 적어놔", "claude.local.md 정리", "handoff 업데이트", "handoff 갱신", "핸드오프 작성", "인수인계", "세션 인계", and English phrasings like "update claude local", "refresh claude md", "write handoff", "session handover", "sync memory bank". Handles single-file and combined requests, and the full-set pattern "README / claude.local.md / HANDOFF before PR".
---

# Session Handover

Maintains two files that let a fresh Claude Code session pick up work without the user re-explaining anything:

- **CLAUDE.local.md** — durable project memory. The project's intent and the rules the user has given, valid across every session.
- **HANDOFF.md** — a short rolling log of what was just done and what Claude needs to do next.

Both files are written **for a future Claude session, not as human documentation**. The human already knows what they built and why; these files exist to give the next session the context it cannot recover on its own. Every sentence you write should be something the next Claude needs in order to act. If a human would be the only reader who benefits, cut it.

## What goes where

The single rule that decides what belongs in either file: **if a future session could learn it by reading the code, running `ls`, or running `git log`, it does not belong in either file.** Directory layouts, file paths, tech stack summaries, architecture diagrams, and "we use X for Y" explanations each fail this test. They waste context and grow stale within days.

The difference between the two files is temporal. CLAUDE.local.md holds what is true across every session. HANDOFF.md holds the single handoff point between the last step and the next one.

| Content                                             | CLAUDE.local.md | HANDOFF.md     |
| --------------------------------------------------- | --------------- | -------------- |
| Project purpose, intent, target users               | core            | —              |
| User-given rules, conventions, cautions             | core            | —              |
| Non-obvious environment facts (hidden setup)        | yes             | —              |
| Label of the step just finished                     | —               | core           |
| Concrete next steps                                 | —               | core           |
| Unresolved blocker that gates the next step         | —               | if real        |
| Tech stack, architecture, implementation narrative  | —               | —              |
| File paths, directory trees, commit SHAs            | —               | —              |
| Historical log of every past step                   | —               | —              |
| Narration written for the human to read             | —               | —              |

"Non-obvious environment facts" means things that would surprise a fresh session — a service running inside a specific container, a port assignment that isn't in `package.json`, an env var whose existence isn't documented anywhere else. Standard commands like `npm run dev` or `cargo build` do not qualify; the next session will find them on its own.

## HANDOFF is not a history log

HANDOFF.md is intentionally short. It answers exactly two questions for the next Claude session:

1. **What was just done?** — only the immediately preceding step. Not every step in the session, not a narrative of the whole project, not command outputs or explanations written for a human reader. One or two short lines.
2. **What should happen next?** — concrete, actionable items the next session can start on without guessing.

When updating HANDOFF.md, delete older "just done" entries from prior handoffs. They are fully completed; the code and `git log` are authoritative for anything older than "the step we just finished". Keeping them around trains the next session to wade through stale narrative and bloats the context budget for every future run. The only past entry that survives into the new HANDOFF is the one from the step that was *literally just completed*.

Do not write HANDOFF.md as if you were explaining your work to the user. The user was there. The next Claude was not, and the next Claude is the only reader.

## Workflow

### 1. Understand the request

Decide which files to touch. Most requests touch both; some touch only one. If the current directory is at all ambiguous, confirm it before doing anything — writing these files into the wrong project is a silent corruption that may not surface for a while. (This is the one thing still worth confirming; everything else in this skill runs without asking.)

### 2. Gather context

Read whichever of the two files already exist, but treat them as potentially stale. An existing HANDOFF was written by some earlier session and may no longer match reality. Verify against `git status` and `git log --oneline -10` rather than trusting prior narrative.

Then scan the current conversation for the material that actually belongs in each file: the user's explicit instructions and intent for CLAUDE.local.md, and the step that was literally just finished plus the concrete next actions for HANDOFF.md. If the conversation is fresh and there is nothing to log yet (e.g., the user is initializing CLAUDE.local.md at the start of a project), draft only that file from the user's stated intent, and create a minimal HANDOFF.md with only a "next up" section.

Both files live at the project root, alongside each other. If either file does not yet exist, create it there. Do not scatter them into `docs/handoff/` or `.claude/handoff/` subdirectories — keeping the pair colocated at the root is what makes them easy for the next session to find.

If a `CLAUDE.md` is tracked in git from before the user started working with Claude on the repo, leave it alone. That file belongs to the upstream project, not the user. User-specific content goes in `CLAUDE.local.md` beside it.

### 3. Merge CLAUDE.local.md carefully

CLAUDE.local.md can contain hand-edited content from the user that is not in this conversation. When updating it, preserve every existing rule, caution, and environment fact that is still true; only add, refine, or remove in response to something explicit in the current session. Never blindly overwrite it with a freshly generated version — read it first and merge.

HANDOFF.md is different: it is short-lived and regenerable, so replacing it wholesale with the new "just done + next up" snapshot is the correct behavior.

### 4. Filter, then write

Draft internally, then remove anything that would be rediscoverable from the code. This rediscoverability filter is the whole job — text that fails it is worse than no update, because it teaches the next session bad habits and bloats the context budget.

Once filtered, **write the files directly.** Do not ask the user "작성할까요?" / "이렇게 쓸까요?" / "shall I write this?" — the user invoked the skill because they already want the files written. Report what changed after the write, not before.

### 5. Ensure both files are gitignored

After writing, make sure `HANDOFF.md` and `CLAUDE.local.md` are in the project's `.gitignore`. These files are per-user memory and must not be committed.

- If `.gitignore` does not exist at the project root, create it with both entries.
- If `.gitignore` exists, read it and append only the entries that are not already present (match whole lines; don't duplicate).
- Do not reorder, deduplicate, or reformat the rest of `.gitignore`.

This is part of the skill's contract, not an optional step. The user should never have to remember to gitignore these files themselves.

## CLAUDE.local.md template

```markdown
# <Project Name>

> Persistent project memory for Claude Code.
> When starting a new session, also read HANDOFF.md before doing any work.

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

<!-- For the next Claude session. Not a history log. Only "just done" and "next up". -->

## Just done
- <Label of the single step that was literally just completed. One short line.>

## Next up
1. <Concrete action the next session can start on without guessing.>
2. ...

## Blockers
- <Only if something genuinely gates the next step. Omit the section otherwise.>
```

Notes on the template:

- **Just done** contains only the immediately preceding step. If an older HANDOFF had a stack of past entries, they are deleted during this update — only the step that was literally just finished survives.
- **Next up** is the highest-value section. Each item should be concrete enough that the next session can act on it without guessing. "Improve the UX" is useless; "add pagination to the posts list" is actionable.
- **Blockers** is optional. Omit it entirely when empty rather than leaving `(none)` placeholders — noise trains the next session to skim past the whole file.
- No date headers, no command outputs, no narrative paragraphs. A future Claude reads this file in full every session; every extra line is a tax on every future run.

## Safety

These boundaries exist for specific reasons; follow them, but also understand why, so you can make sensible calls at the edges.

- **Preserve hand-edited CLAUDE.local.md content.** It is the user's memory across sessions. Read it before writing, and only change what this session has a reason to change. Blind overwrites destroy content that isn't recoverable from git (the file is gitignored).
- **Replace HANDOFF.md wholesale, but only with the current snapshot.** It is short-lived by design. The previous HANDOFF's "just done" section is discarded when a new step completes.
- **Trust code over prose.** When an existing HANDOFF and `git log` disagree, believe `git log` and rebuild HANDOFF from the current reality rather than propagating stale narrative.
- **Leave upstream `CLAUDE.md` alone.** When a repository ships its own `CLAUDE.md`, that file belongs to the project. User-specific additions go in `CLAUDE.local.md` beside it.
- **Verify the target directory** whenever there is any ambiguity. Writing these files into the wrong project is the worst failure mode because the user may not notice until much later.
- **Gitignore is mandatory.** Both files are per-user memory. Shipping them to a shared repo leaks user context and pollutes teammates' workspaces.
