# GitHub API patterns

## Contents

- [Target and authenticate](#target-and-authenticate)
- [Choose methods and encode fields](#choose-methods-and-encode-fields)
- [Shape output and paginate](#shape-output-and-paginate)
- [Use GraphQL](#use-graphql)
- [Select the correct endpoint](#select-the-correct-endpoint)
- [Read and update repository files](#read-and-update-repository-files)
- [Diagnose errors and rate limits](#diagnose-errors-and-rate-limits)

## Target and authenticate

`gh api` makes authenticated REST requests; use `gh api graphql` for GraphQL. It has no `--repo`/`-R` flag. Use a literal `repos/OWNER/REPO/...` endpoint or set the repository context for placeholders:

```bash
GH_REPO=owner/repo gh api 'repos/{owner}/{repo}' --jq '{full_name, default_branch}'
gh api --hostname github.example.com 'repos/owner/repo'
```

The remaining examples use the current checkout's repository. Set `GH_REPO=owner/repo` in the environment when targeting another repository. Only `{owner}`, `{repo}`, and `{branch}` are substituted automatically; replace other IDs yourself. Quote endpoints and bracketed fields to prevent shell interpretation. Use GET fields for query values that need URL encoding; percent-encode dynamic path components such as branch names containing `/` when the endpoint requires a single segment.

| Environment variable | Purpose |
| --- | --- |
| `GH_REPO` | Repository context for placeholders, `[HOST/]OWNER/REPO` |
| `GH_HOST` | Target GitHub hostname; `--hostname` selects it explicitly |
| `GH_TOKEN`, then `GITHUB_TOKEN` | GitHub.com token; takes precedence over stored credentials |
| `GH_ENTERPRISE_TOKEN`, then `GITHUB_ENTERPRISE_TOKEN` | Enterprise token |

Use `gh auth status --hostname HOST` for auth diagnosis. An environment token can override a valid stored login. Check the target repository grant, token permissions, and organization SSO authorization when relevant.

For reproducible REST behavior, pin an API version supported by the host:

```bash
gh api 'repos/{owner}/{repo}' \
  -H 'Accept: application/vnd.github+json' \
  -H 'X-GitHub-Api-Version: 2026-03-10'
```

Consult the host's endpoint documentation for its supported version; Enterprise may lag GitHub.com. Use preview headers only when a specific endpoint still requires them.

## Choose methods and encode fields

The default method is GET, but adding `-f`, `-F`, or `--input` switches it to POST unless a method is specified. Set `--method GET` when adding query parameters and set PATCH/PUT/DELETE explicitly for those operations.

| Input | Behavior |
| --- | --- |
| `-f key=value` | String value, including literal `true`, digits, or `@text` |
| `-F key=value` | Converts booleans, integers, and `null`; expands repository placeholders |
| `-F body=@body.md` / `-F body=@-` | Reads a field's value from a file / stdin |
| `-f 'inputs[environment]=staging'` | Nested object field |
| `-f 'labels[]=bug' -f 'labels[]=urgent'` | Array entries |
| `-F 'labels[]'` | Empty array |
| `--input request.json` / `--input -` | Entire request body from a file / stdin |

Quote shell variables (`-f "body=$BODY"`). Use `-f` for text that must remain a string, especially values beginning with `@` or numeric-looking identifiers. Prefer JSON input for complex nested structures.

```bash
# Read with query parameters; without GET this would become POST
gh api --method GET 'repos/{owner}/{repo}/pulls' \
  -f state=open -F per_page=100
gh api --method GET search/issues \
  -f q='repo:owner/repo is:issue is:open label:bug' -F per_page=100

# Post a comment using file contents as one string field
gh api --method POST 'repos/{owner}/{repo}/issues/123/comments' \
  -F body=@comment.md

# Replace labels; use -F 'labels[]' to clear them
gh api --method PATCH 'repos/{owner}/{repo}/issues/123' \
  -f 'labels[]=bug' -f 'labels[]=urgent'

# Typed boolean
gh api --method POST 'repos/{owner}/{repo}/actions/runs/123456/rerun' \
  -F enable_debug_logging=true

# An issue-comment ID has its own endpoint, without the issue number
gh api --method DELETE 'repos/{owner}/{repo}/issues/comments/456' --silent

# Complete JSON body, including a typed nested input
gh api --method POST 'repos/{owner}/{repo}/actions/workflows/ci.yml/dispatches' \
  --input - <<'JSON'
{"ref":"main","inputs":{"run_tests":true}}
JSON
```

The dispatch example assumes that `ci.yml` declares a boolean `run_tests` input. With `--input`, extra `-f`/`-F` fields become **query parameters**, not additions to the JSON body. Put all intended body fields in the input document. Empty `204` responses are normal for many successful mutations.

## Shape output and paginate

`gh api` already outputs JSON and does not take a `--json` field list. Its `--jq` works without installing standalone `jq`. Use external `jq` when combining page streams or validating a saved response.

```bash
# Request one page when a bounded sample is enough
gh api --method GET 'repos/{owner}/{repo}/pulls' -F per_page=10 \
  --jq '.[] | {number, title, html_url}'

# Stream selected records from every page of a top-level array
gh api --method GET 'repos/{owner}/{repo}/pulls' \
  -f state=all -F per_page=100 --paginate \
  --jq '.[] | {number, title, state}'

# Collect all pages into one array of records (requires standalone jq)
gh api --method GET 'repos/{owner}/{repo}/pulls' \
  -f state=all -F per_page=100 --paginate --slurp \
  | jq '[.[][] | {number, title, state}]'

# Actions endpoints wrap records in an object on each page
gh api --method GET 'repos/{owner}/{repo}/actions/runs' \
  -f event=workflow_dispatch -F per_page=100 --paginate --slurp \
  | jq '[.[].workflow_runs[] | {id, head_sha, status, conclusion}]'
```

`--paginate` follows REST pagination links; each response is a separate JSON value. `--slurp` wraps those pages in an outer array, so an array endpoint becomes an array of arrays. `--jq` filters each page separately: `length` is a per-page count, not a total. Use a shell's `pipefail` setting when piping to external tools so their success does not hide a failed request.

Know the response shape: search uses `.items[]`, runs `.workflow_runs[]`, jobs `.jobs[]`, artifacts `.artifacts[]`, and checks `.check_runs[]`. The issues endpoint also includes PRs; use `select(.pull_request == null)` when you need only issues.

Pagination does not bypass endpoint caps. Search returns at most 1,000 results and can report `incomplete_results`; filtered Actions run searches also cap results. Narrow or partition by time/repository to obtain a complete result. Apply server-side filters before collecting large histories.

Use `--cache 5m` for repeated reads of stable metadata. Fetch fresh run status and post-mutation state without caching. `--include` adds status/headers to stdout and `--verbose` adds request/response details; keep that diagnostic output separate from JSON or binary files.

## Use GraphQL

Use GraphQL for related data in one request or functionality absent from REST, such as review-thread resolution. Supply variables rather than interpolating values into query text. Except for `query` and `operationName`, supplied fields become GraphQL variables.

```bash
# Page all review threads for a PR
gh api graphql --paginate \
  -F owner='{owner}' -F name='{repo}' -F number=123 \
  -f query='
    query($owner: String!, $name: String!, $number: Int!, $endCursor: String) {
      repository(owner: $owner, name: $name) {
        pullRequest(number: $number) {
          reviewThreads(first: 100, after: $endCursor) {
            nodes { id isResolved isOutdated path line }
            pageInfo { hasNextPage endCursor }
          }
        }
      }
    }' --jq '.data.repository.pullRequest.reviewThreads.nodes[]'
```

GraphQL auto-pagination requires a nullable `$endCursor: String` variable, `after: $endCursor`, and `pageInfo { hasNextPage endCursor }`. It does not independently paginate every nested connection. If adding thread comments or reviews, inspect each connection's `pageInfo` and fetch remaining pages separately rather than treating `first: 100` as exhaustive.

```bash
# Use the thread's GraphQL node ID discovered above
gh api graphql -f threadId="$THREAD_ID" -f query='
  mutation($threadId: ID!) {
    resolveReviewThread(input: {threadId: $threadId}) {
      thread { id isResolved }
    }
  }'
```

Keep GraphQL node IDs distinct from REST numeric IDs. GraphQL can return HTTP `200` with an `errors` array and partial `data`; inspect the error and command exit status before claiming complete results. If filtering `.data` hid context, inspect the full response. Use POST for both queries and mutations; the GraphQL operation determines whether state changes.

## Select the correct endpoint

Replace `NUMBER`, `ID`, and `SHA` below with discovered values; they are not automatic placeholders.

| Need | REST path under `repos/{owner}/{repo}/` | Notes |
| --- | --- | --- |
| PR conversation comments | `issues/NUMBER/comments` | PRs share the issue conversation API |
| Inline PR review comments | `pulls/NUMBER/comments` | Different from conversation comments |
| Submitted reviews | `pulls/NUMBER/reviews` | Review decisions and bodies |
| Files in a PR | `pulls/NUMBER/files` | Paginate; endpoint caps still apply |
| Diff | `pulls/NUMBER` | Set `Accept: application/vnd.github.diff` |
| Commit checks | `commits/SHA/check-runs` | Results in `.check_runs[]` |
| Legacy commit status | `commits/SHA/status` | Distinct from check runs |
| Check annotations | `check-runs/ID/annotations` | Paginated top-level array |
| Workflow runs / jobs / artifacts | `actions/runs`, `actions/runs/ID/jobs`, `actions/runs/ID/artifacts` | See Actions reference |
| Branches / releases | `branches`, `releases` | Paginated top-level arrays |

For archive downloads, redirect raw bytes to a file and check the command's exit status before opening it. `gh api` follows download redirects; an API error can otherwise leave JSON in a file named `.zip`.

```bash
gh api 'repos/{owner}/{repo}/actions/artifacts/123/zip' > artifact.zip
```

## Read and update repository files

```bash
# Read raw content at a specific ref; --method GET keeps ref in the query
gh api --method GET 'repos/{owner}/{repo}/contents/README.md' \
  -f ref=main -H 'Accept: application/vnd.github.raw+json'
```

Use Git for ordinary multi-file changes. When a direct Contents API update is requested, supply base64 content and the existing blob SHA from the **same branch**:

```bash
set -euo pipefail
BRANCH=docs-update
FILE_SHA=$(gh api --method GET 'repos/{owner}/{repo}/contents/README.md' \
  -f "ref=$BRANCH" --jq '.sha // empty')
test -n "$FILE_SHA"
CONTENT=$(base64 < README.md | tr -d '\n')
gh api --method PUT 'repos/{owner}/{repo}/contents/README.md' \
  -f message='docs: update README' -f "branch=$BRANCH" \
  -f "sha=$FILE_SHA" -f "content=$CONTENT"
```

The snippet stops if the SHA lookup fails or returns no SHA. Omit `sha` only when creating a new file. Double quotes allow shell expansion; `-f content='$(base64 README.md)'` would send literal text. On a conflict, reread the branch/file and reconcile before retrying the update.

## Diagnose errors and rate limits

Use the response body and endpoint documentation first. For a read request, `--include` exposes status and rate-limit headers; use `--verbose` only when request details are necessary, and avoid including sensitive bodies or signed download URLs in reports. Do not reissue a mutation solely to obtain diagnostics.

```bash
gh api 'repos/{owner}/{repo}' --include
gh api rate_limit --jq '.resources | {core, graphql, search}'
```

| Symptom | Check |
| --- | --- |
| `401` | Token validity, host, and environment-token precedence |
| `403` | Endpoint permissions, repository/organization policy, SSO, or rate-limit details |
| `404` | Host/path/ID and repository access; private resources may be hidden from an unauthorized token |
| `405` / unexpected `422` | Whether adding fields changed GET to POST; required fields, field types, supported ref/state |
| `409` | Concurrent updates or an operation invalid in the current resource state |
| `403` / `429` with throttling details | `Retry-After`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`; reduce request frequency/concurrency |
| `5xx` or transport failure | Retry bounded reads with backoff; check server state before retrying writes |

Honor the server's retry delay; primary reset times are Unix timestamps. Secondary rate limits can apply even with primary quota remaining. Avoid tightly polling or parallelizing large mutation batches. After an ambiguous timeout on create/comment/dispatch, query for the intended result before sending another request to avoid duplicates.

## Sources

- [gh api manual](https://cli.github.com/manual/gh_api)
- [REST API best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)
- [GraphQL pagination](https://docs.github.com/en/graphql/guides/using-pagination-in-the-graphql-api)
