# Issue workflows

Use `REPO=owner/repo` and `ISSUE=123` below, replacing them with the target. Prefer a URL or explicit repository when issue numbers could refer to more than one repository.

## Find and inspect

```bash
gh issue list -R "$REPO" --state open --label bug --limit 100 \
  --json number,title,state,labels,url
gh issue list -R "$REPO" --state all --search 'auth in:title'
gh issue list -R "$REPO" --assignee '@me'
gh issue view "$ISSUE" -R "$REPO" --json title,body,state,labels,assignees,url
gh issue view "$ISSUE" -R "$REPO" --comments
```

Use `--state all` when closed issues matter. List results are limited (default 30); a bounded list is not a complete inventory. Use `gh search issues --repo OWNER/REPO` for search-specific filters and [API patterns](api-patterns.md) for pagination. The REST issues endpoint includes PRs, while `gh issue list` targets issues.

## Create and comment

```bash
gh issue create -R "$REPO" --title 'Bug: login fails after session expiry' \
  --body-file issue-body.md --label bug
gh issue comment "$ISSUE" -R "$REPO" --body-file response.md
gh issue comment "$ISSUE" -R "$REPO" --edit-last --body-file updated-response.md
```

Supply both title and body to avoid interactive prompts. Use `--body-file -` for stdin. Capture the returned URL; if creation times out ambiguously, search for the intended issue before retrying. `--edit-last` edits the current user's most recent comment; use the specific REST comment ID when targeting a different comment.

For bug reports, include the observed behavior, expected behavior, reproduction, and relevant evidence available from the task. Use existing repository templates and labels when applicable, without inventing missing reproduction details.

## Update and close

```bash
gh issue edit "$ISSUE" -R "$REPO" --body-file updated-issue.md
gh issue edit "$ISSUE" -R "$REPO" --add-label 'bug,urgent' --remove-label needs-triage
gh issue edit "$ISSUE" -R "$REPO" --add-assignee username
gh issue edit "$ISSUE" -R "$REPO" --milestone 'v2.0'
gh issue close "$ISSUE" -R "$REPO" --reason completed --comment 'Fixed in #456'
gh issue close "$ISSUE" -R "$REPO" --reason 'not planned'
gh issue reopen "$ISSUE" -R "$REPO" --comment 'Reopening with a new reproduction'
```

Choose the state change and close reason that fit the task. Replacing a body overwrites it; incorporate existing content that should remain. For requested bulk updates, select the intended set with explicit repository, state, and search filters, then act on those IDs. Increase `--limit` or paginate when the scope exceeds one page.

## Link development work

```bash
gh issue develop "$ISSUE" -R "$REPO" --name fix-auth --base main
gh issue develop "$ISSUE" -R "$REPO" --list
```

Reference `Fixes #123`, `Closes #123`, or `Resolves #123` in the PR body to link completion. Use `Fixes OWNER/REPO#123` across repositories. Automatic closing occurs when the PR is merged into the default branch; a mention alone is not evidence the issue closed.

## Less common operations

Use `gh issue <command> --help` for operation-specific flags:

| Outcome | Command |
| --- | --- |
| Pin or unpin | `gh issue pin` / `gh issue unpin` |
| Lock or unlock discussion | `gh issue lock` / `gh issue unlock` |
| Move to another repository | `gh issue transfer` |
| Delete an issue | `gh issue delete` |
| Inspect issues relevant to the authenticated user | `gh issue status` |

After a write, use the returned URL or inspect the relevant fields to confirm the requested result.
