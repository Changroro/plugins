# Templates

Use these only when creating a file or repairing its shape. Omit empty sections.

## Root or nested AGENTS.md

```markdown
# Project rules

## Required behavior

- <Evidenced behavior every agent in this directory scope must follow.>

## Constraints

- <Compatibility, safety, or environment constraint that cannot be enforced automatically.>
```

Do not add purpose, architecture, feature, command, setup, status, or history sections. A nested file contains only the delta for its subtree and does not repeat ancestor rules.

## Local override

Use `AGENTS.override.md`, which Codex recognizes, when a proven external/upstream repository must remain untouched or local behavior intentionally replaces the repository AGENTS file.

```markdown
# Local project rules

## Required behavior

- <Mandatory local behavior.>
```

An override replaces the AGENTS file in the same directory. Include any same-directory rule that must remain effective.

## Claude import

When no Claude file exists, create only the import:

```markdown
@AGENTS.md
```

For an override, use `@AGENTS.override.md`, normally in `CLAUDE.local.md`.

When a CLAUDE file already contains repository instructions, preserve them and add the effective import as a standalone line. Do not rewrite the file into a one-line shim.

## HANDOFF.md

```markdown
# HANDOFF — <Project Name>

## Just done

- <One outcome and its durable result.>

## Next up

- <Concrete action the next session can begin without guessing.>

## Blockers

- <Only a blocker that actually prevents the next action.>
```

Keep exactly one list item under Just done. Keep as many next actions as the immediate continuation genuinely needs; there is no line budget. Omit Blockers when empty. Exclude dates, SHAs, digests, counts, live server/process state, command output, and older completed steps.

## Scoped topic document

Match the project's existing document shape when one exists. Otherwise use:

```markdown
# <Topic>

## Current decisions

- <Durable decision or requirement.>

## Procedure

1. <Exact working step, only when this is a runbook.>

## Open questions

- <Unresolved question that affects future work.>
```

Choose a topic-specific filename at the narrowest relevant scope. Planning, development knowledge, and operations procedures should not share a catch-all document.
