---
name: gh-cli
description: Use GitHub CLI (gh) to manage PRs, issues, releases, Actions runs and workflows, or make GitHub REST/GraphQL API requests.
---

# GitHub CLI

Use `gh` to complete the requested GitHub operation. Prefer a dedicated subcommand when it exposes the needed operation; use `gh api` for missing fields, endpoints, or precise pagination.

## Choose the relevant reference

Read the reference that fits the task; use individual sections as needed.

| Task | Reference |
| --- | --- |
| Create, review, update, or merge a PR | [Pull request workflows](references/pr-workflows.md) |
| Find, create, or update issues | [Issue workflows](references/issue-workflows.md) |
| Diagnose CI, inspect jobs/logs/artifacts, rerun, dispatch, or use `gh` inside Actions | [Actions workflows](references/actions-workflows.md) |
| Construct REST/GraphQL requests, paginate, handle authentication or API errors | [API patterns](references/api-patterns.md) |

## Working conventions

- Resolve the repository and host from the request, URL, or checkout. Use `-R [HOST/]OWNER/REPO` on repository subcommands when needed. `gh api` has no `-R`; use an explicit endpoint or `GH_REPO` for placeholders, and `--hostname` for Enterprise.
- Supply IDs and input flags to avoid interactive prompts. Use `--body-file` for substantial Markdown and `--json` with selected fields for structured output. `gh api` already returns JSON; filter it with `--jq`.
- Scope queries to the relevant PR, workflow, commit, or time range. Fetch more pages when the answer needs completeness; a default list is only a sample.
- Treat these patterns as defaults. Follow the user's requested scope and carry authorized work through to its result without adding approval steps. Ask only when unresolved information would materially change the target or outcome.
- Match verification to the operation: inspect the returned URL/state after a write, and distinguish accepting a workflow dispatch from finishing its run. For CI diagnosis, report the run/attempt, failing job, evidence, and next action. If asked to fix CI, continue through the fix and relevant verification available within the task's scope.
- Use `gh <command> <subcommand> --help` for current flags and JSON fields. Use `gh auth status --hostname HOST` to investigate authentication failures.

## Other common operations

```bash
# Search within a repository
gh search issues 'auth bug' --repo owner/repo --state open
gh search prs 'review:required' --repo owner/repo --state open
gh search code 'function authenticate' --repo owner/repo

# Inspect releases or publish an existing tag when requested
gh release list -R owner/repo
gh release view v1.0.0 -R owner/repo
gh release create v1.0.0 -R owner/repo --verify-tag --generate-notes
gh release upload v1.0.0 ./dist/app.zip -R owner/repo
```

For an unfamiliar operation, consult the [CLI manual](https://cli.github.com/manual/) or the endpoint's [REST](https://docs.github.com/en/rest) / [GraphQL](https://docs.github.com/en/graphql) documentation rather than extrapolating flags or fields from another command.
