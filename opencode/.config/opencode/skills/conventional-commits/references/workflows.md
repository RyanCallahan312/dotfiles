# Conventional Commits Workflows

This document describes common workflows for working with conventional commits.

## Workflow 1: Generate a Conventional Commit Message

**When to use**: You have staged changes and need to write a descriptive conventional commit message.

**Steps**:

1. Stage your changes: `git add .`
2. Run the message generator
3. Review the generated message
4. Adjust if needed (add body, breaking change notice, etc.)
5. Commit with the message

**Example**:

```bash
# Generate message for a bug fix in the auth module
python3 generate-commit-message.py \
  --type fix \
  --scope auth \
  --summary "prevent race condition in token refresh"

# Or let it infer the type from your changes
python3 generate-commit-message.py \
  --infer \
  --summary "update dependencies"
```

**Output**:

```
fix(auth): prevent race condition in token refresh
```

## Workflow 2: Validate Existing Commits

**When to use**: You want to check if recent commits follow conventional format, or audit a branch before merging.

**Steps**:

1. Run the validator on a commit range
2. Review any errors or warnings
3. Fix non-compliant commits (use `git rebase -i` if needed)
4. Re-validate

**Example**:

```bash
# Check last 10 commits
python3 validate-commits.py --range HEAD~10..HEAD

# Check commits on feature branch vs main
python3 validate-commits.py --range origin/main..HEAD

# Get JSON output for programmatic processing
python3 validate-commits.py --range HEAD~5..HEAD --json
```

**Output**:

```
✓ a1b2c3d
✓ d4e5f6g
✗ h7i8j9k
  Error: Invalid type 'bugfix'. Allowed: feat, fix, docs, style, refactor, perf, test, chore
  Warning: Header length 72 exceeds recommended 50
```

## Workflow 3: Generate Changelog from Commits

**When to use**: You're preparing a release or want to document changes for users.

**Steps**:

1. Ensure all commits in your release are conventional
2. Run changelog generator with version number
3. Review the generated changelog
4. Commit the changelog

**Example**:

```bash
# Generate changelog for new version
python3 generate-changelog.py --version 2.1.0 --range v2.0.0..HEAD

# Generate and append to existing CHANGELOG.md
python3 generate-changelog.py --output CHANGELOG.md --version 1.5.0

# Get changelog as JSON
python3 generate-changelog.py --json --range HEAD~20..HEAD
```

**Output**:

```markdown
## [2.1.0] - 2024-01-22

### ⚠️ Breaking Changes

- **api**: Remove deprecated `/v1/auth` endpoints ([abc1234](../commit/abc1234))

### Features

- **auth**: Add two-factor authentication support ([def5678](../commit/def5678))
- **dashboard**: Add export to CSV functionality ([ghi9012](../commit/ghi9012))

### Bug Fixes

- **api**: Fix race condition in token refresh ([jkl3456](../commit/jkl3456))

### Performance

- **database**: Optimize user query by 40% ([mno7890](../commit/mno7890))
```

## Workflow 4: Create a Complete Commit with Body and Footer

**When to use**: Making significant changes that need detailed explanation or breaking change notice.

**Steps**:

1. Stage changes
2. Generate message with type and scope
3. Add body explaining the "why" 
4. Add breaking change notice or footer if needed
5. Review and commit

**Example**:

```bash
python3 generate-commit-message.py \
  --type feat \
  --scope api \
  --summary "redesign user authentication flow" \
  --body "Refactor authentication to use OAuth2 with PKCE.
This improves security and supports mobile applications.
Implements RFC-6234 for token management." \
  --breaking \
  --breaking-description "The /auth/legacy endpoint is removed. Use /auth/oauth2 instead."
```

**Result**:

```
feat(api): redesign user authentication flow

Refactor authentication to use OAuth2 with PKCE.
This improves security and supports mobile applications.
Implements RFC-6234 for token management.

BREAKING CHANGE: The /auth/legacy endpoint is removed. Use /auth/oauth2 instead.
```

## Workflow 5: Enforce Conventional Commits in CI/CD

**When to use**: You want to automatically validate commits in your pipeline.

**Steps**:

1. Place scripts in a shared location (e.g., `scripts/commit-tools/`)
2. Configure pre-commit hook or CI check
3. Run validator on incoming commits
4. Block merge if validation fails

**Example GitHub Actions Workflow**:

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
        run: |
          python3 validate-commits.py \
            --range origin/main..HEAD \
            --summary
```

## Workflow 6: Fix Non-Compliant Commits

**When to use**: You have commits that don't follow conventional format and need to fix them.

**Steps**:

1. Identify non-compliant commits with validator
2. Use `git rebase -i` to edit commits
3. Use `git commit --amend` to fix the message
4. Re-validate
5. Force push (use with caution)

**Example**:

```bash
# Identify problematic commits
python3 validate-commits.py --range HEAD~5..HEAD

# Start interactive rebase for last 5 commits
git rebase -i HEAD~5

# In editor, change 'pick' to 'reword' for commits to fix
# When prompted, update message to conventional format

# Validate the fixed commits
python3 validate-commits.py --range HEAD~5..HEAD

# If on a feature branch, force push
git push origin feature-branch --force-with-lease
```

## Workflow 7: Configure Project for Conventional Commits

**When to use**: Setting up a new project to enforce conventional commits.

**Suggested structure**:

1. Create `.commitlintrc.json` in project root:

```json
{
  "types": ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"],
  "require_scope": false,
  "max_header_length": 50,
  "max_body_length": 72
}
```

2. Create pre-commit hook (`.git/hooks/commit-msg`):

```bash
#!/bin/bash
MESSAGE=$(cat "$1")
python3 scripts/commit-tools/generate-commit-message.py --validate "$MESSAGE" || exit 1
```

3. Add CI check to validate incoming PRs

4. Document guidelines in CONTRIBUTING.md
