# Routing project memory

Classify memory type before deciding whether an item is durable or important. Importance, repetition, and rediscovery cost may affect whether to keep an item; they never change its type.

## Memory hierarchy

| Layer | Holds | Scope |
| --- | --- | --- |
| Global instructions or auto-memory | Cross-project work style, user preferences, machine/tool state | Every project |
| Root `AGENTS.md` | Mandatory agent work behavior for the whole repository | Repository |
| Nested `AGENTS.md` | Mandatory agent work behavior only for a component or subtree | Nearest directory wins |
| `AGENTS.override.md` | Local replacement for the AGENTS file in the same directory | Local directory scope |
| Project documents | Product requirements, domain semantics, architecture, procedures, and troubleshooting | Narrowest relevant topic scope |
| `HANDOFF.md` | One completed outcome, next actions, and real blockers | Next session only |

Do not duplicate a rule across layers. Codex concatenates AGENTS files from root toward the working directory and gives closer scopes precedence. Claude must import the effective AGENTS file from a CLAUDE file in the same scope.

## Type gate

Assign every extracted item exactly one type before evaluating evidence:

| Type | Question | Destination |
| --- | --- | --- |
| `agent_policy` | How must an agent or developer perform work? | AGENTS candidate only |
| `domain_spec` | What must the product, business process, or user-visible behavior do? | Planning or product document |
| `architecture` | What does a field, API, data flow, component, or implementation mean? | Development or design document |
| `runbook` | What exact commands or recovery steps perform an operation? | Operations document |
| `task_state` | What just happened or must happen next? | HANDOFF or task tracker |
| `user_preference` | How does the user prefer to work across projects? | Global instructions or auto-memory |

Only `agent_policy` continues to the admission gate.

### Hard exclusion

Product and domain facts never become agent policy through explicitness, repetition, importance, risk, or rediscovery cost. This includes:

- Product and business rules
- Domain definitions and aggregation semantics
- Schema, field, API, event, and data-contract meaning
- UI behavior and acceptance criteria
- Architecture and implementation mappings
- Notification delivery behavior
- Exact commands and multi-step procedures

Imperative wording does not change the type. `Preserve`, `ensure`, `maintain`, `always`, `must`, or `do not change` wrapped around product semantics is still a project specification, not an AGENTS rule.

Use the actor test:

- If the faithful subject is “the agent/developer working on this repository,” it may be `agent_policy`.
- If the faithful subject is “the application/service/API/field/data/user experience,” it is not `agent_policy`.
- If removing the domain details leaves only “preserve the system behavior,” route the details to a document. Add an AGENTS pointer to read that document only when every agent in the scope must consult it before acting.

Contrasts:

- “When starting local development, use the project-specific port established by the user.” → possible `agent_policy`
- “The deployed service listens on a particular port.” → environment or operations knowledge
- “Preserve the declared runtime compatibility when changing code.” → possible `agent_policy`
- “A record field changes after a particular domain event.” → architecture or data-contract specification
- “Notifications are grouped according to a delivery policy.” → product specification
- “Before changing this component, read its scoped contract document.” → possible narrow AGENTS pointer when always required

## Admission gate

An `agent_policy` candidate enters AGENTS only when every condition passes:

1. It directly controls an agent or developer action, not merely the resulting product behavior.
2. Compliance can be judged from the work trajectory, not only from application output.
3. It remains valid across future sessions in this project.
4. It is project-specific and not already effective from global or ancestor instructions.
5. Evidence exists: an explicit durable user instruction about how to work, the same project-specific correction recurred, or a verified recurring failure has one prevention behavior.
6. Re-deriving the exact safe method would be costly or error-prone, and the behavior is not already enforced completely by config, types, tests, lint, hooks, or scripts.
7. It is placed in the narrowest directory scope where it always applies.

A model's earlier classification or reflection is not independent evidence. One debugging loop repeating the same statement is still one observation.

## Independent critic loop

Read `semantic-review.md` and review every proposed AGENTS addition before editing the file:

1. Build a private packet containing the source statement, proposed rule, evidence, and target scope without the author's promotion conclusion.
2. Give a fresh independent subagent this file, `semantic-review.md`, and the packet. If no independent subagent is available, ask the user before changing AGENTS instead of self-approving it.
3. The critic returns `accept` only when the item is `agent_policy`, passes all admission conditions, contains no laundered project knowledge, and cannot be replaced by a scoped document pointer.
4. Any `reroute` or uncertainty goes to the appropriate document. Do not ask the user to arbitrate safe demotion.
5. Review every non-empty line in the complete AGENTS draft, including headings, not only obvious new rules. Stop after two passes; unresolved items stay out of AGENTS.
6. Produce the temporary hash-bound review artifact required by `semantic-review.md` and pass it to the auditor.

This loop reviews memory placement. It does not modify this skill or treat its own output as new evidence.

## Scoped documents

Use the project's existing documentation system first. Put new knowledge beside the component it governs instead of defaulting everything to a root `docs/` directory.

If no documentation system exists, create one focused topic document. Keep planning, development, and operations in separate topic files. Repository-canonical documents may remain tracked; local AI-only documents must use exact gitignore entries. Never copy the same content into both AGENTS and a project document.
