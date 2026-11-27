---
name: conventional-commits
description: Write, validate, and manage conventional commits with git. Generate properly formatted commit messages following the conventional commits specification (feat, fix, docs, style, refactor, perf, test, chore). Use when creating commits, validating commit history, generating changelogs, or setting up conventional commit workflows in projects.
---

# Conventional Commits Skill

## Overview

This skill provides comprehensive support for writing, validating, and managing conventional commits. Conventional commits is a specification for adding human and machine readable meaning to commit messages. This skill includes tools to generate compliant commit messages, validate existing commits, generate changelogs, and manage full commit workflows.

## When to Use This Skill

Use this skill when:
- **Creating commits**: Generate properly formatted conventional commit messages
- **Validating commits**: Check if commits follow the conventional format
- **Generating changelogs**: Create CHANGELOG.md from commit history
- **Enforcing standards**: Set up CI/CD checks or pre-commit hooks
- **Auditing commits**: Review commit history for compliance
- **Learning conventions**: Understanding conventional commit format and best practices

## Quick Start

### Generate a Conventional Commit Message

```bash
# Simple feature commit
python3 generate-commit-message.py \
  --type feat \
  --scope auth \
  --summary "add JWT token refresh"

# Let the tool infer the type from your changes
python3 generate-commit-message.py \
  --infer \
  --summary "update dependencies"

# Create with body and breaking change
python3 generate-commit-message.py \
  --type feat \
  --scope api \
  --summary "redesign authentication" \
  --body "Switch to OAuth2 with PKCE for improved security." \
  --breaking \
  --breaking-description "The /auth/legacy endpoint is removed."
```

### Validate Commits

```bash
# Check last 10 commits
python3 validate-commits.py --range HEAD~10..HEAD

# Check feature branch against main
python3 validate-commits.py --range origin/main..HEAD

# Get summary only
python3 validate-commits.py --range HEAD~5..HEAD --summary
```

### Generate Changelog

```bash
# Generate changelog for release
python3 generate-changelog.py --version 2.1.0 --range v2.0.0..HEAD

# Append to existing CHANGELOG.md
python3 generate-changelog.py --output CHANGELOG.md --version 1.5.0
```

## Bundled Scripts

This skill includes three Python scripts for common conventional commit workflows:

### generate-commit-message.py

Generate properly formatted conventional commit messages. Supports inferring commit type from staged changes, adding detailed bodies, and marking breaking changes.

**Key features:**
- Auto-detect commit type from git diff
- Support for scopes and breaking changes
- Message validation with line length checking
- JSON output for programmatic use

**Example usage:**
```bash
python3 generate-commit-message.py \
  --type fix \
  --scope database \
  --summary "prevent race condition in migrations" \
  --validate "your message here"
```

### validate-commits.py

Validate commits against conventional commit format and optional commitlint configuration.

**Key features:**
- Check commits against conventional format
- Load commitlint config from `.commitlintrc.json`, `.commitlintrc.yaml`, or `pyproject.toml`
- Validate specific commit ranges
- Report errors and warnings separately
- JSON output for CI/CD integration

**Example usage:**
```bash
python3 validate-commits.py \
  --range origin/main..HEAD \
  --config .commitlintrc.json
```

### generate-changelog.py

Generate CHANGELOG.md from conventional commits, organizing by type and scope.

**Key features:**
- Group commits by type (feat, fix, perf, etc.)
- Organize by scope within each type
- Highlight breaking changes
- Merge with existing changelogs
- JSON output of parsed commits

**Example usage:**
```bash
python3 generate-changelog.py \
  --version 2.1.0 \
  --range v2.0.0..HEAD \
  --output CHANGELOG.md
```

## Conventional Commits Format

### Basic Structure

```
<type>[optional scope]: <subject>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix  
- **docs**: Documentation only changes
- **style**: Changes that do not affect code meaning (formatting, semicolons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to build process, dependencies, or tooling

### Examples

```
# Simple fix
fix(auth): prevent race condition in token refresh

# Feature with scope
feat(api): add user export to CSV

# Breaking change
feat(core)!: remove legacy API endpoints

BREAKING CHANGE: The /api/v1 endpoints are removed. Use /api/v2 instead.

# With detailed body
feat(search): implement full-text search

Add full-text search using Elasticsearch. Supports filtering by date range
and document type. Improves search performance by 60% for large datasets.

Implements RFC-234 for search indexing.
```

## Complete Workflows

For detailed workflows covering different scenarios, see `references/workflows.md`:

- **Workflow 1**: Generate a conventional commit message
- **Workflow 2**: Validate existing commits
- **Workflow 3**: Generate changelog from commits
- **Workflow 4**: Create complete commit with body and footer
- **Workflow 5**: Enforce conventional commits in CI/CD
- **Workflow 6**: Fix non-compliant commits
- **Workflow 7**: Configure project for conventional commits

## Reference Documentation

**Conventional Commits Specification** (`references/conventional-commits-spec.md`):
Complete specification with detailed examples, best practices, and relationship to semantic versioning.

**Workflows** (`references/workflows.md`):
Step-by-step guides for common tasks: generating messages, validating commits, creating changelogs, enforcing standards, and more.

## Common Tasks

### Creating a New Feature Commit

1. Stage your changes: `git add .`
2. Generate message:
   ```bash
   python3 generate-commit-message.py --type feat --scope ui --summary "add dark mode toggle"
   ```
3. Commit with the generated message

### Validating a Branch Before Merge

```bash
python3 validate-commits.py --range origin/main..HEAD

# If errors found, fix them with git rebase -i and --amend
```

### Preparing a Release

1. Generate changelog:
   ```bash
   python3 generate-changelog.py --version 2.0.0 --range v1.5.0..HEAD
   ```
2. Review the generated CHANGELOG.md
3. Commit the changelog
4. Tag the release: `git tag v2.0.0`

### Setting Up CI/CD Validation

1. Place scripts in `scripts/commit-tools/`
2. Create GitHub Actions workflow or pre-commit hook
3. Run validator on incoming commits
4. Block merge if validation fails

See workflow 5 in `references/workflows.md` for detailed setup.

## Tips & Best Practices

1. **Use scopes consistently**: Scopes should match your project structure (e.g., auth, api, ui, database)
2. **Write clear subjects**: Be specific about what changed, not how
3. **Use body for "why"**: Explain the motivation and context, not just what changed
4. **Mark breaking changes**: Always use `!` or `BREAKING CHANGE:` footer
5. **Keep commits atomic**: Each commit should represent one logical change
6. **Use tools early**: Validate commits before pushing to prevent issues
7. **Configure your project**: Create `.commitlintrc.json` to enforce custom rules

## Integration Examples

### Pre-commit Hook

Create `.git/hooks/commit-msg`:

```bash
#!/bin/bash
MESSAGE=$(cat "$1")
python3 scripts/commit-tools/validate-commits.py --validate "$MESSAGE" || exit 1
```

### GitHub Actions

```yaml
name: Validate Commits
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: Validate commits
        run: python3 validate-commits.py --range origin/main..HEAD
```

### Project Configuration

Create `.commitlintrc.json`:

```json
{
  "types": ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"],
  "require_scope": false,
  "max_header_length": 50,
  "max_body_length": 72
}
```
