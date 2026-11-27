---
description: Open a PR for the current branch using gh CLI. Uses the repo's PR template if available.
agent: general
---

Open a GitHub PR for the current branch.

## Workflow

1. Load the `gh-cli` skill
2. Check if `.github/pull_request_template.md` exists
3. Create the PR using the gh-cli skill, referencing the template if available
4. Ensure PR title and description focus on features and user value

## PR Content Guidelines

- Focus titles and descriptions on **features** and user value, not implementation details
- Highlight what the change enables or fixes from a user/product perspective
- Implementation details belong in the PR body or comments, not the title

## Arguments

$ARGUMENTS - Optional context about the PR (title, description, draft status, target branch).
