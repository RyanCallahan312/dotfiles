# Pull request workflows

## Contents

- [Inspect and find PRs](#inspect-and-find-prs)
- [Create a PR](#create-a-pr)
- [Review and discuss](#review-and-discuss)
- [Update a PR](#update-a-pr)
- [Check and merge](#check-and-merge)

Use `REPO=owner/repo` and `PR=123` below, replacing them with the target. A PR URL can also select the repository and PR directly. Without an argument, `gh pr view`, `diff`, and `checks` infer the current branch's PR.

## Inspect and find PRs

```bash
gh pr view "$PR" -R "$REPO" \
  --json number,title,body,baseRefName,headRefName,headRefOid,isDraft,url
gh pr diff "$PR" -R "$REPO"
gh pr view "$PR" -R "$REPO" --comments
gh pr list -R "$REPO" --state open --author '@me' --limit 50 \
  --json number,title,headRefName,url
gh pr list -R "$REPO" --state all --search 'review:required'
```

Use `reviewDecision,reviewRequests,reviews` for review state and `statusCheckRollup` for checks. Discover supported fields with `gh pr view --help`; `reviewers` is not a `gh pr view --json` field. List commands are bounded by `--limit`; use the API reference when completeness requires explicit pagination.

## Create a PR

Resolve the base repository/branch and head branch from the task and existing repository conventions. Write a body describing the change and actual verification, then create the requested PR:

```bash
gh pr create -R "$REPO" --base main --head feature-auth \
  --title 'feat: add authentication' --body-file pr-body.md

# Alternative: draft with a body generated from commits
gh pr create -R "$REPO" --base main --head feature-auth --draft --fill

# From a fork into the upstream repository
gh pr create -R upstream/repo --base main --head myuser:feature-auth \
  --title 'fix: handle expired sessions' --body-file pr-body.md
```

`--base` takes a branch name, not `upstream:main`. `--head USER:BRANCH` selects a fork branch; the CLI currently does not support an organization as that head-owner syntax. An explicit `--head` skips automatic pushing/forking, so push the branch to the intended remote when needed before creating the PR.

Use `--body-file -` to read Markdown from stdin. `--fill`, `--fill-first`, and `--fill-verbose` derive text from commits; explicit title/body values override their generated values. Add `--reviewer USER`, `--reviewer ORG/TEAM`, `--label LABEL`, or `--assignee '@me'` when the task calls for them. `Fixes #123` in the body links an issue for closing when merged into the default branch.

`gh pr create --dry-run` prints details but **may still push Git changes**. For a local preview, inspect the prepared body and diff. Capture the created URL; after an ambiguous creation failure, check for an existing PR on the head/base before retrying.

## Review and discuss

```bash
gh pr checkout "$PR" -R "$REPO"
gh pr review "$PR" -R "$REPO" --comment --body-file review.md
gh pr review "$PR" -R "$REPO" --request-changes --body-file review.md
gh pr review "$PR" -R "$REPO" --approve
gh pr comment "$PR" -R "$REPO" --body-file comment.md
```

Choose the review action that matches the requested outcome and findings. `gh pr comment` adds a conversation comment; `gh pr review` submits a review. For inline diff comments, use the REST pull-request review-comment endpoints; for resolving review threads, use GraphQL as shown in [API patterns](api-patterns.md).

## Update a PR

```bash
gh pr edit "$PR" -R "$REPO" --body-file pr-body.md
gh pr edit "$PR" -R "$REPO" --title 'fix: handle expired sessions'
gh pr edit "$PR" -R "$REPO" --add-reviewer username --add-label bug
gh pr edit "$PR" -R "$REPO" --remove-label wip
gh pr ready "$PR" -R "$REPO"
gh pr update-branch "$PR" -R "$REPO"
gh pr close "$PR" -R "$REPO"
gh pr reopen "$PR" -R "$REPO"
```

Use the relevant operation, then inspect the changed fields. Updating the branch changes its head commit and may start new checks; earlier CI results no longer establish the new head's status.

## Check and merge

```bash
gh pr checks "$PR" -R "$REPO" --required
gh pr checks "$PR" -R "$REPO" --required --watch --interval 10
gh pr view "$PR" -R "$REPO" \
  --json headRefOid,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup

# When merging is requested, bind it to the reviewed head SHA
gh pr merge "$PR" -R "$REPO" --squash --match-head-commit "$REVIEWED_SHA"

# Alternative: request automatic merge when requirements are satisfied
gh pr merge "$PR" -R "$REPO" --auto --squash --match-head-commit "$REVIEWED_SHA"
```

Choose `--merge`, `--squash`, or `--rebase` according to the requested strategy and repository policy. Use `--delete-branch` when branch cleanup is part of the task. Required-check success does not establish review or merge eligibility; inspect those separately. Merge queues may enqueue the PR rather than merge it immediately. Read back `state,mergedAt,url` and report whether the PR merged, entered a queue, or has auto-merge enabled.

`gh pr checks` returns `8` for pending checks and nonzero for failures/errors. Use [Actions workflows](actions-workflows.md) to diagnose failed jobs or follow the run for the current commit.
