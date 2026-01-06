---
name: git-commit
description: Creates commits following Conventional Commits format with type/scope/subject. Use when user wants to commit changes, create commit, or save work. Analyzes staged changes, generates proper commit message, validates format.
---

# Git Commit Guide

Creates commits using the Conventional Commits format with type, scope, and subject components.

## Quick Start

```bash
# 1. Check project conventions
cat CLAUDE.md 2>/dev/null | head -30

# 2. Review staged changes
git diff --staged --stat
git diff --staged

# 3. Stage files if needed
git add <files>

# 4. Create commit
git commit -m "type(scope): subject"
```

## Commit Structure

Format: `type(scope): subject`

| Component | Description | Example |
|-----------|-------------|---------|
| **type** | Change category | `feat`, `fix`, `refactor` |
| **scope** | Affected area (kebab-case) | `auth`, `api-client` |
| **subject** | What changed (< 50 chars) | `add login validation` |

## Commit Types

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature | `feat(auth): add JWT refresh` |
| `fix` | Bug fix | `fix(api): handle null response` |
| `refactor` | Code restructure | `refactor(db): extract query builder` |
| `docs` | Documentation | `docs(readme): add setup guide` |
| `test` | Test changes | `test(auth): add login tests` |
| `chore` | Maintenance | `chore(deps): update lodash` |
| `ci` | CI/CD changes | `ci(github): add lint workflow` |
| `perf` | Performance | `perf(query): add index for lookup` |
| `style` | Formatting | `style(lint): fix indentation` |

## Core Workflow

### 1. Check Project Conventions

```bash
cat CLAUDE.md 2>/dev/null | head -30
```

Always check for project-specific commit rules.

### 2. Review Staged Changes

```bash
git diff --staged --stat
git diff --staged
```

Understand what's being committed.

### 3. Analyze Changes

Identify:
- Primary type (feat > fix > refactor)
- Scope (module/component affected)
- Summary (what changed, in imperative mood)

### 4. Create Commit

```bash
git commit -m "type(scope): subject"
```

### 5. Add Body (if needed)

For complex changes:

```bash
git commit -m "$(cat <<'EOF'
type(scope): subject

Body explaining WHY and HOW.
Wrap at 72 characters.

Refs: #123
EOF
)"
```

## Breaking Changes

Use `!` after type/scope:

```bash
git commit -m "feat(api)!: change response format"
```

Or use footer:

```bash
git commit -m "$(cat <<'EOF'
feat(api): change response format

BREAKING CHANGE: Response now returns array instead of object.
EOF
)"
```

## Subject Line Rules

- **DO**: Use imperative mood ("add", "fix", "change")
- **DO**: Keep under 50 characters
- **DO**: Start lowercase after colon
- **DON'T**: End with period
- **DON'T**: Use vague words ("update", "improve", "change stuff")

## Review Fix Commits

When addressing PR review comments:

```bash
git commit -m "$(cat <<'EOF'
fix(scope): address review comment #ID

Brief explanation of what was wrong and how it's fixed.
Addresses review comment #123456789.
EOF
)"
```

## Important Rules

- **ALWAYS** check project conventions (CLAUDE.md) before committing
- **ALWAYS** review staged changes before committing
- **NEVER** stage secrets, credentials, or large binaries
- **NEVER** use vague subjects ("fix bug", "update code")
- **ALWAYS** use imperative mood in subject
- **ALWAYS** use HEREDOC for multi-line messages
- Use separate commits for unrelated changes
- Group related changes into single commit
