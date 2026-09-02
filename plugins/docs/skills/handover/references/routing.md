# Routing project memory

Read this for borderline handover candidates and every restart.

## Memory hierarchy

| Layer | Holds | Scope |
| --- | --- | --- |
| Global instructions or auto-memory | Cross-project work style, user preferences, machine/tool state | Every project |
| Root `AGENTS.md` | Mandatory behavior for the whole repository | Repository |
| Nested `AGENTS.md` | Mandatory behavior only for a component or subtree | Nearest directory wins |
| `AGENTS.override.md` | Local replacement for the AGENTS file in the same directory | Local directory scope |
| Project documents | Requirements, decisions, architecture, exact procedures, troubleshooting | Read on demand at the narrowest relevant scope |
| `HANDOFF.md` | One completed outcome, next actions, real blockers | Next session only |

Do not duplicate a rule across layers. Codex concatenates AGENTS files from root toward the working directory and gives closer scopes precedence. Claude must import the effective AGENTS file from a CLAUDE file in the same scope.

## Decide by consequence

Do not ask only whether a fact can be found somewhere in the repository. Ask:

1. Must every agent working in this scope follow it?
2. How expensive is it to recover the exact safe method?
3. How likely is a plausible but wrong method to cause a mistake?
4. Does the agent still need the intent before acting, even if the repository checks the result automatically?

High rediscovery cost and error risk support AGENTS promotion only when the candidate is mandatory behavior. A project preference or compatibility target may remain useful even when config or tests also reflect it; a purely mechanical formatting or generated-output constraint does not need duplication. Durable knowledge that informs work but is not always an instruction belongs in a document.

## Evidence

Accept one of these as promotion evidence:

- The user explicitly states a durable project convention, preference, prohibition, or compatibility constraint.
- The same project-specific correction or request appears repeatedly in the available conversation history.
- A verified recurring failure has one current prevention rule.

Do not treat a one-time request, completed implementation detail, command output, or repetition caused by the current debugging loop as evidence. Record the evidence category in the final report for every promoted rule.

## Routing table

| Content | Destination |
| --- | --- |
| Project-wide mandatory convention with evidence | Root `AGENTS.md` |
| Component-only mandatory convention with evidence | Nearest component `AGENTS.md` |
| Local replacement for repository instructions | `AGENTS.override.md` and a Claude local import |
| General user work style or cross-project preference | Global instructions or auto-memory |
| Feature request, acceptance criteria, roadmap, product decision | Existing planning/product document at the relevant scope |
| Architecture, implementation mapping, durable development decision | Existing development/design document at the relevant scope |
| Exact command, deployment procedure, recovery steps | Scoped operations/runbook document |
| Non-obvious environment knowledge that informs but does not command every task | Scoped environment/operations document |
| One verified incident with a permanent mandatory prevention behavior | Compress to one AGENTS rule; keep diagnostics in troubleshooting docs |
| Just-completed outcome and concrete continuation | `HANDOFF.md` |
| Larger backlog | Existing task tracker or planning document |
| SHA, digest, metrics, dated state, command output, old session narration | Nowhere unless a canonical history artifact explicitly requires it |

Examples:

- "For this project, always start local web development on port 3002" is evidenced mandatory behavior and belongs in the applicable AGENTS scope.
- "Run these seven deployment commands" belongs in an operations document; AGENTS may say to follow that runbook only if doing so is itself mandatory and evidenced.
- "Cards use `published_at` in one sort mode" is implementation knowledge, not an always-followed agent rule.
- "Please add CSV export" is a feature requirement even if requested repeatedly.

## Scoped documents

Use the project's existing documentation system first. Follow its naming, ownership, and location rules. Put new knowledge beside the component it governs, such as `services/api/docs/operations.md`, instead of defaulting everything to root `docs/`.

If no documentation system exists, create one focused topic document. Separate independent topics such as planning, development, and operations. Do not create a generic session dump or enumerate every document from AGENTS.

Repository-canonical documents may remain tracked. Local AI-only documents must use exact gitignore entries. Never copy the same content into both.
