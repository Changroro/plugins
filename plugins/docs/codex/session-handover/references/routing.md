# Routing — where each kind of content belongs

Read this when a piece of content's destination is not obvious, or when auditing existing files for misplacement.

## The asymmetry that decides everything

AGENTS.md is loaded into every session of every tool. Every line there costs context forever, and a bloated memory file makes agents ignore the rules that matter. HANDOFF.md is read once at session start; `docs/` files are read only when the work touches them.

**When in doubt, route away from AGENTS.md.**

## Memory layers — do not duplicate across them

| Layer | Owner | Holds |
| --- | --- | --- |
| Global instructions (`~/.codex/AGENTS.md` + its imports; in Claude Code, global `CLAUDE.md` and auto-memory) | The user / the agent, across all projects | Who the user is, their work-style preferences, machine state, tool setup |
| **AGENTS.md** (project root) | this skill | Project rules that **another tool** (Claude Code, Cursor, Gemini CLI) also needs — that is its whole reason to exist |
| `docs/`, HANDOFF.md | this skill | Topical knowledge; the next concrete step |

A rule already in the global layer does not get restated in the project's AGENTS.md.

Codex does not expand `@import` inside a project AGENTS.md — it concatenates AGENTS.md files along the directory path. Keep project AGENTS.md self-contained; point at `docs/` files by name so a session can open them explicitly.

## Routing table

| Content | Destination |
| --- | --- |
| Project purpose, intent, target users — 1–2 sentences | AGENTS.md |
| User-given rules, conventions, cautions | AGENTS.md |
| Non-obvious environment facts | AGENTS.md |
| Planning, feature design, specs, roadmap, reference-service detail, troubleshooting lore, other durable topical knowledge | a `docs/<topic>.md` that fits — create or extend one, named by topic |
| Label of the step just finished | HANDOFF.md |
| Concrete next steps (≤5) | HANDOFF.md |
| Unresolved blocker gating the next step | HANDOFF.md, if real |
| Task backlog larger than next-up | the project's existing task file (e.g. root `TODO.md`) if it has one, else a `docs/` topic doc |
| Incident story ("X broke when we did Y, rolled back") | compress to a one-line rule in AGENTS.md: "Do not Y (breaks X)." |
| Tech stack, architecture, file paths, directory trees, commit SHAs | nowhere — rediscoverable |
| History of past steps, command outputs, narration for humans | nowhere |

"Non-obvious environment fact" = a service inside a specific container, a port not in `package.json`, an env var documented nowhere. `npm run dev` does not qualify; the same command with flags or env vars a session could not guess does.

## The two filters

Every line destined for AGENTS.md or HANDOFF.md — including lines already in the file — must survive both:

1. **Rediscoverable?** Learnable from the code, `ls`, or `git log` → out.
2. **Load-bearing?** Would removing it cause the next session to make a mistake? No → cut, even if not rediscoverable.

## docs/ topic files

- Decide the set per project, by topic. No fixed list, one topic per file, short names that say what's inside.
- AGENTS.md carries only a one-line pointer to `docs/` — never an enumeration or summary of them.
- A topic doc holds intent, design, and knowledge. Not rules (→ AGENTS.md), not next steps (→ HANDOFF.md), not history.
- Open each with a one-line HTML comment stating its job: `<!-- Planning memory for AI sessions. Read on demand. -->`
- When a plan is fully implemented, compress the doc to its surviving decisions.
- Never write session content into a git-tracked doc — skill-created docs are separate, untracked, gitignored.
