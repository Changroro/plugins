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

# 4. Create commit with emoji
git commit -m "✨ feat(scope): add new feature"
```

## Commit Structure

Format: `emoji type(scope): subject`

| Component | Description | Example |
|-----------|-------------|---------|
| **emoji** | Visual indicator | ✨, 🐛, ♻️ |
| **type** | Change category | `feat`, `fix`, `refactor` |
| **scope** | Affected area (kebab-case) | `auth`, `api-client` |
| **subject** | What changed (imperative mood) | `add login validation` |

**Rules:**
- First line ≤ 72 characters
- Use imperative mood ("add", not "added" or "adding")
- No period at end

## Commit Types with Emoji

### Core Types

| Emoji | Type | Purpose |
|-------|------|---------|
| ✨ | `feat` | New feature |
| 🐛 | `fix` | Bug fix |
| 📝 | `docs` | Documentation |
| 💄 | `style` | Formatting/style (no logic change) |
| ♻️ | `refactor` | Code refactoring |
| ⚡️ | `perf` | Performance improvement |
| ✅ | `test` | Add/update tests |
| 🔧 | `chore` | Tooling, config |
| 🚀 | `ci` | CI/CD improvements |
| ⏪️ | `revert` | Revert changes |

### Detailed Types

**Features (feat):**
| Emoji | Usage |
|-------|-------|
| 🧵 | Multithreading/concurrency |
| 🔍️ | SEO improvements |
| 🏷️ | Add/update types |
| 💬 | Text and literals |
| 🌐 | Internationalization/localization |
| 👔 | Business logic |
| 📱 | Responsive design |
| 🚸 | UX/usability improvements |
| 📈 | Analytics/tracking |
| 🚩 | Feature flags |
| 💫 | Animations/transitions |
| ♿️ | Accessibility |
| 🦺 | Validation |
| 🔊 | Add/update logs |
| 🥚 | Easter eggs |
| 💥 | Breaking changes |
| ✈️ | Offline support |

**Fixes (fix):**
| Emoji | Usage |
|-------|-------|
| 🚨 | Compiler/linter warnings |
| 🔒️ | Security issues |
| 🩹 | Simple fix for non-critical issue |
| 🥅 | Catch errors |
| 👽️ | External API changes |
| 🔥 | Remove code/files |
| 🚑️ | Critical hotfix |
| ✏️ | Typos |
| 💚 | CI build |
| 🔇 | Remove logs |

**Refactor:**
| Emoji | Usage |
|-------|-------|
| 🚚 | Move/rename resources |
| 🏗️ | Architectural changes |
| 🎨 | Improve structure/format |
| ⚰️ | Remove dead code |

**Chore:**
| Emoji | Usage |
|-------|-------|
| 👥 | Add/update contributors |
| 🔀 | Merge branches |
| 📦️ | Compiled files/packages |
| ➕ | Add dependency |
| ➖ | Remove dependency |
| 🌱 | Seed files |
| 🧑‍💻 | Developer experience |
| 🙈 | .gitignore |
| 📌 | Pin dependencies |
| 👷 | CI build system |
| 📄 | License |
| 🎉 | Begin project |
| 🔖 | Release/version tags |
| 🚧 | Work in progress |

**Database/Assets:**
| Emoji | Usage |
|-------|-------|
| 🗃️ | Database changes |
| 🍱 | Assets |

**Test:**
| Emoji | Usage |
|-------|-------|
| 🧪 | Add failing test |
| 🤡 | Mock things |
| 📸 | Snapshots |
| ⚗️ | Experiments |

## Commit Scope (Logical Atomicity)

**MUST FOLLOW:** Do not commit per file. Commit per **feature unit**.

- **Principle:** If you modified `main.py`, `utils.py`, `config.yaml` to develop Feature A, these 3 files **MUST be in a single commit**.
- **Reason:** When reverting to a specific commit, that feature should work completely.

**❌ Bad Example**
```bash
git add search.py
git commit -m "feat: create search module"
git add api.py
git commit -m "fix: fix api connection"
```

**✅ Good Example**
```bash
git add search.py api.py
git commit -m "✨ feat(search): implement keyword search with API endpoint"
```

## Result-Oriented Messages

**MUST FOLLOW:** Do not write conversation history (process). Write only the **final code changes (result)**.

Even if there were 10 modifications during development (error fixes, typo fixes, etc.), the commit message should only state the finally implemented feature.

| ❌ Bad (Process) | ✅ Good (Result) |
|------------------|------------------|
| "Fixed typo, fixed A function error, added library to implement login" | `✨ feat(auth): implement JWT-based login` |
| "fix api connection and variable name errors and import errors" | `✨ feat(search): implement keyword search` |

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

## Commit Split Guidelines

When analyzing diffs, consider splitting commits based on:

| Criteria | Description |
|----------|-------------|
| **Different concerns** | Changes to unrelated parts of codebase |
| **Change types** | Feature vs bug fix vs refactoring |
| **File patterns** | Source code vs documentation vs config |
| **Logical grouping** | Changes easier to review separately |
| **Size** | Very large changes that benefit from granularity |

**Split Example:**
```
1st: ✨ feat: add new solc version type definitions
2nd: 📝 docs: update documentation for new solc version
3rd: 🔧 chore: update package.json dependencies
4th: 🏷️ feat: add type definitions for new API endpoints
5th: 🧵 feat: improve worker thread concurrency handling
6th: 🚨 fix: resolve linting issues in new code
7th: ✅ test: add unit tests for new solc version features
8th: 🔒️ fix: update dependencies for security vulnerabilities
```

## Pre-Commit Checklist

Before creating a commit, ask yourself:

1. **Are all related files included?** (Are all dependency files modified for the feature `git add`ed?)
2. **Is the message clean?** (Does it contain only the core implementation without repetitive "fix", "modify"?)
3. **Is it the diff from previous commit?** (Did you summarize `git diff` content, not conversation log?)

## Good Commit Examples

```
✨ feat: add user authentication system
🐛 fix: resolve memory leak in rendering process
📝 docs: update API documentation with new endpoints
♻️ refactor: simplify error handling logic in parser
🚨 fix: resolve linter warnings in component files
🧑‍💻 chore: improve developer tools setup process
👔 feat: implement business logic for transaction validation
🩹 fix: resolve minor style inconsistency in header
🚑️ fix: patch critical security vulnerability in auth flow
🎨 style: restructure component for better readability
🔥 fix: remove deprecated legacy code
🦺 feat: add input validation for user registration form
💚 fix: resolve CI pipeline test failures
📈 feat: implement tracking for user engagement analytics
🔒️ fix: strengthen authentication password requirements
♿️ feat: improve form accessibility for screen readers
```

## Important Rules

- **ALWAYS** check project conventions (CLAUDE.md) before committing
- **ALWAYS** review staged changes before committing
- **ALWAYS** commit per feature unit, not per file
- **ALWAYS** write result-oriented messages (final changes only)
- **ALWAYS** use imperative mood in subject ("add", not "added")
- **ALWAYS** include appropriate emoji at the start
- **ALWAYS** keep first line ≤ 72 characters
- **ALWAYS** use HEREDOC for multi-line messages
- **NEVER** stage secrets, credentials, or large binaries
- **NEVER** use vague subjects ("fix bug", "update code")
- **NEVER** list process steps in commit message
- **NEVER** end subject with period
