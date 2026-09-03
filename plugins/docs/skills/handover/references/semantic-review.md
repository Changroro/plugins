# Independent AGENTS semantic review

Use this whenever handover modifies an AGENTS file and for every restart.

## Review process

1. Draft memory destinations and AGENTS content without writing the final files.
2. Give a fresh independent subagent the draft, source evidence, target scope, and `routing.md`. Do not include the author's classification or rationale.
3. The reviewer classifies every non-empty line independently. Headings may contain structure only. Reject any other line when it describes project knowledge, product behavior, domain meaning, architecture, implementation mechanics, an exact procedure, task state, or a cross-project preference.
4. A retained line must be either:
   - `behavior`: durable direction for how an agent or developer performs work
   - `document_pointer`: direction to consult a scoped document, without copying its details
5. Remove or reroute rejected lines, then ask the independent reviewer to inspect the revised complete AGENTS draft. Stop after two review passes. If any line remains uncertain, keep it out of AGENTS.

An independent subagent is mandatory. If the environment cannot provide one, ask the user before changing AGENTS instead of self-approving the draft.

## Review artifact

After the final review, write a temporary JSON artifact outside the repository:

```json
{
  "schema": 1,
  "reviewer": "independent_subagent",
  "files": [
    {
      "path": "AGENTS.md",
      "sha256": "<sha256 of the final file bytes>",
      "items": [
        {
          "line": 5,
          "text": "- <exact trimmed line from the final file>",
          "memory_type": "agent_policy",
          "kind": "behavior",
          "decision": "accept"
        }
      ]
    }
  ]
}
```

Include every non-empty line exactly once. A heading uses `memory_type: structure` and `kind: heading`; use `document_pointer` for pointer-only lines. The main agent may add line numbers and the file hash to the reviewer's decisions, but may not change its type, kind, or decision.

Pass this artifact to `audit.py --review-file`. The audit fails when the reviewer is not independent, a file hash is stale, a content line is missing or changed, or a retained line lacks an `agent_policy` acceptance. Delete the temporary artifact after the audit.
