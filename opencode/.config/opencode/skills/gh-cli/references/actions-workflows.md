# GitHub Actions workflows

## Contents

- [Identify the workflow and run](#identify-the-workflow-and-run)
- [Diagnose jobs and logs](#diagnose-jobs-and-logs)
- [Watch and interpret results](#watch-and-interpret-results)
- [Rerun and manage runs](#rerun-and-manage-runs)
- [Dispatch a workflow](#dispatch-a-workflow)
- [Retrieve artifacts](#retrieve-artifacts)
- [Use Actions REST endpoints](#use-actions-rest-endpoints)
- [Run gh inside Actions](#run-gh-inside-actions)
- [Secrets and variables](#secrets-and-variables)

Use explicit repository and run IDs in automation. In these examples, set `REPO=owner/repo`, `PR=123`, and replace `RUN_ID`, `JOB_ID`, `ATTEMPT`, and `SHA` with values discovered for the task. Use `-R HOST/OWNER/REPO` for Enterprise subcommands; for API examples, use `REPO=OWNER/REPO` plus `--hostname HOST`.

## Identify the workflow and run

Start a PR investigation with its checks, which can include both Actions and external CI:

```bash
gh pr view "$PR" -R "$REPO" \
  --json headRefOid,headRefName,baseRefName,url
gh pr checks "$PR" -R "$REPO" \
  --json name,state,bucket,workflow,event,link

gh workflow list -R "$REPO" --all --json id,name,path,state
gh workflow view ci.yml -R "$REPO" --yaml --ref main
gh run list -R "$REPO" --workflow ci.yml --commit "$SHA" --limit 20 \
  --json databaseId,attempt,headSha,headBranch,event,status,conclusion,createdAt,url
```

Use check links to locate the associated Actions run. A branch can have several runs for different workflows and events; selecting the repository's latest run can diagnose the wrong commit. Use `--event`, `--branch`, `--created`, or `--status` to narrow discovery when necessary. A PR workflow may execute a synthetic merge commit, and merge queues use `merge_group`; if a head-SHA filter misses a check, follow its link and inspect the run metadata. External checks may have no Actions run.

Keep the identifiers distinct:

| Identifier | Source and use |
| --- | --- |
| Workflow ID or filename | `gh workflow list`; select a workflow for viewing/dispatch |
| Run ID | `databaseId` from `gh run list`; REST uses `id`. Pass to `gh run view/watch/rerun` |
| Run number | `number` / REST `run_number`; display counter, not the run ID |
| Attempt | `attempt` / REST `run_attempt`; increases on reruns of the same run ID |
| Job ID | `jobs[].databaseId` from `gh run view`; REST jobs use `id` |
| Check run ID | Checks API; use for annotations, not as a workflow run ID |

`gh workflow list` hides disabled workflows unless `--all` is supplied. There is no `--state` flag; filter the returned `state` field. `gh run list --all --workflow ci.yml` includes runs for a disabled workflow. Organization ruleset runs may have no workflow name.

## Diagnose jobs and logs

```bash
gh run view "$RUN_ID" -R "$REPO" \
  --json databaseId,attempt,headSha,event,status,conclusion,jobs,url

# Discover job IDs and steps before fetching large logs
gh run view "$RUN_ID" -R "$REPO" --json jobs \
  --jq '.jobs[] | {id: .databaseId, name, status, conclusion, steps}'
gh run view "$RUN_ID" -R "$REPO" --log-failed
gh run view "$RUN_ID" -R "$REPO" --job "$JOB_ID" --log

# Inspect the attempt that actually failed, even after a rerun
gh run view "$RUN_ID" -R "$REPO" --attempt "$ATTEMPT" --log-failed
```

Read the failing step and enough surrounding output to identify the first actionable error. Distinguish a test/build failure from setup failures, unavailable runners, concurrency cancellation, skipped dependencies, or environment protection waits. Inspect the workflow YAML at the run's ref when conditions, permissions, or matrix configuration explain the failure.

Logs may be unavailable until a job finishes or after retention/deletion. An empty `--log-failed` result does not establish success. Inspect job conclusions and annotations; use full logs only when the focused output is insufficient. If run-wide log retrieval fails on a large matrix, request individual job logs. `UNKNOWN STEP` can reflect GitHub's log-to-step mapping limitations.

When a run is waiting on an environment, inspect the pending deployment rather than rerunning it:

```bash
gh api "repos/$REPO/actions/runs/$RUN_ID/pending_deployments" \
  --jq '.[] | {environment: .environment.name, wait_timer, current_user_can_approve, reviewers}'
```

Report the run URL/attempt and job name with a concise error excerpt. Identify what the evidence establishes and what remains unresolved.

## Watch and interpret results

```bash
gh run watch "$RUN_ID" -R "$REPO" --exit-status --interval 10
gh run view "$RUN_ID" -R "$REPO" --json status,conclusion,attempt,headSha,url

# For merge readiness, watch the PR's required checks
gh pr checks "$PR" -R "$REPO" --required --watch --interval 10
```

- `gh run view --exit-status` is a snapshot and can exit zero while the run is pending. It does not wait.
- `gh run watch --exit-status` waits and returns nonzero for failure. Inspect `status` and `conclusion` to distinguish success, cancellation, timeout, or skipped work; CLI exit code `2` is not a universal mapping for a cancelled workflow.
- `gh pr checks` uses exit code `8` for pending checks and nonzero for failures/errors. Treat pending as incomplete, not as a command syntax failure.
- For strict success, require `status == "completed"` and `conclusion == "success"`. Check the SHA again if the branch advanced while watching. Required checks passing does not establish that every workflow passed.

Some CLI versions, including 2.96, do not support `gh run watch` with fine-grained PATs. If watching is unavailable, use bounded polling of `gh run view --json status,conclusion` or the REST run endpoint with Actions read access. Space requests apart and report the last state if the task's waiting budget expires.

## Rerun and manage runs

Choose the smallest rerun that addresses the diagnosed failure:

```bash
gh run rerun "$RUN_ID" -R "$REPO" --failed
gh run rerun "$RUN_ID" -R "$REPO" --job "$JOB_ID"
gh run rerun "$RUN_ID" -R "$REPO" --failed --debug

# Other operations when requested
gh run rerun "$RUN_ID" -R "$REPO"
gh run cancel "$RUN_ID" -R "$REPO"
gh run delete "$RUN_ID" -R "$REPO"
gh workflow disable ci.yml -R "$REPO"
gh workflow enable ci.yml -R "$REPO"
```

Obtain rerun job IDs from `jobs[].databaseId`, not by assuming a browser job URL contains the accepted ID. Job and failed-job reruns also include dependent jobs. A rerun uses the original run's SHA/ref; to test a new commit, find or trigger its new run. Record the old attempt and verify that the new attempt appears before interpreting a watch result, since the old completed state can briefly remain visible. Rerunning alone does not fix a deterministic failure.

## Dispatch a workflow

Inspect the workflow's `workflow_dispatch` inputs and the intended branch/tag. The workflow must exist on the default branch for manual dispatch; `--ref` selects the version to execute.

```bash
gh workflow view deploy.yml -R "$REPO" --yaml --ref main
gh workflow run deploy.yml -R "$REPO" --ref main \
  -f environment=staging -f version=1.0.0

# Alternative: supply only the inputs object on stdin
gh workflow run deploy.yml -R "$REPO" --ref main --json <<'JSON'
{"environment":"staging","version":"1.0.0"}
JSON
```

`gh workflow run -f` and `-F` supply string inputs; `-F` additionally reads `@file` values. Its `--json` input also expects a string-valued object in CLI 2.96 (for example, `{"run_tests":"true"}`). For a body containing native booleans or numbers, use `gh api --input` and match the workflow's declared types. `gh api -F` performs typed conversion; `gh workflow run -F` does not.

Capture the created run URL when the CLI returns one. Dispatch support varies by CLI/API version; if no run identity is returned, record the dispatch time and discover candidates:

```bash
gh run list -R "$REPO" --workflow deploy.yml --event workflow_dispatch \
  --branch main --limit 20 \
  --json databaseId,headSha,createdAt,displayTitle,url,status,conclusion
```

Match workflow, event, ref/SHA, actor, and creation time to the request. Allow for brief propagation delay. If concurrent dispatches remain ambiguous, use a correlation input reflected in `run-name` when the workflow supports it. Avoid choosing `--limit 1` as proof of identity or retrying a dispatch merely because the run has not appeared.

For a machine-readable dispatch response on GitHub.com with API version `2026-03-10`:

```bash
gh api --method POST "repos/$REPO/actions/workflows/deploy.yml/dispatches" \
  -H 'X-GitHub-Api-Version: 2026-03-10' \
  -f ref=main -f 'inputs[environment]=staging' -f 'inputs[version]=1.0.0'
```

This version returns `workflow_run_id`, `run_url`, and `html_url`. Older APIs/Enterprise versions may return an empty `204` response; use their documented behavior and the discovery fallback. A dispatch is complete when accepted if triggering was the requested outcome; if asked to wait or validate a deployment, follow the identified run to its outcome.

## Retrieve artifacts

```bash
gh api --method GET "repos/$REPO/actions/runs/$RUN_ID/artifacts" \
  -F per_page=100 --paginate \
  --jq '.artifacts[] | {id, name, size_in_bytes, expired, expires_at}'
gh run download "$RUN_ID" -R "$REPO" --name build-output \
  --dir "./artifacts/$RUN_ID"
```

Select the run by workflow and commit before downloading. Without a run ID, artifact discovery may select a different run; without a name/pattern, downloads can be unnecessarily large. Use `--pattern '*-linux-*'` for a relevant subset. Expired artifacts cannot be recovered by retrying the download. Prefer `gh run download` for extracted files; use the artifact REST endpoint when the ZIP itself is needed.

## Use Actions REST endpoints

Use these when the dedicated commands omit metadata or historical jobs:

```bash
# Jobs from an exact attempt, with pagination for large matrices
gh api --method GET "repos/$REPO/actions/runs/$RUN_ID/attempts/$ATTEMPT/jobs" \
  -F per_page=100 --paginate \
  --jq '.jobs[] | {id, name, status, conclusion, runner_name, labels, check_run_url}'

# All attempts rather than the endpoint's default latest jobs
gh api --method GET "repos/$REPO/actions/runs/$RUN_ID/jobs" \
  -f filter=all -F per_page=100 --paginate --jq '.jobs[]'

# Retrieve annotations using the check_run_url returned for a job
gh api --paginate "$CHECK_RUN_URL/annotations" \
  --jq '.[] | {path, start_line, end_line, annotation_level, message}'

# Raw logs as an archive; binary output goes to a file
gh api "repos/$REPO/actions/runs/$RUN_ID/attempts/$ATTEMPT/logs" \
  > "run-$RUN_ID-attempt-$ATTEMPT.zip"
```

REST uses snake_case (`head_sha`, `run_attempt`); CLI `--json` uses camelCase (`headSha`, `attempt`). Paginate wrapper arrays such as `.jobs[]`, `.workflow_runs[]`, and `.artifacts[]` rather than assuming a top-level array. See [API patterns](api-patterns.md) for field types, output shaping, and error handling.

## Run gh inside Actions

Set `GH_TOKEN` from the job token and make the target explicit. No interactive `gh auth login` or checkout is needed just to query GitHub:

```yaml
permissions:
  actions: read
jobs:
  inspect:
    runs-on: ubuntu-latest
    steps:
      - name: Inspect this run
        env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
          RUN_ID: ${{ github.run_id }}
        run: |
          gh api "repos/{owner}/{repo}/actions/runs/$RUN_ID" \
            --jq '{id, status, conclusion, head_sha}'
```

For Enterprise, also set `GH_HOST` to the actual hostname and configure the appropriate host credential. Match job `permissions` to the operation: Actions reads need `actions: read`, dispatch/rerun/cancel need `actions: write`, and PR or issue writes need their corresponding permission. A repository's `GITHUB_TOKEN` normally cannot access another private repository; use an appropriately scoped installation token or configured credential for that target.

Fork PRs commonly receive read-only tokens and no repository secrets. Diagnose that constraint rather than switching an untrusted workflow to `pull_request_target`. Pass event-derived text through environment variables or input files instead of embedding it in shell code. Events created with `GITHUB_TOKEN` generally do not start further workflows, with exceptions including `workflow_dispatch` and `repository_dispatch`; account for this when automation creates commits or PRs.

## Secrets and variables

```bash
gh secret list -R "$REPO"
gh secret list -R "$REPO" --env staging
gh secret set DEPLOY_TOKEN -R "$REPO" --env staging < token.txt
gh variable list -R "$REPO" --env staging
gh variable set DEPLOY_REGION -R "$REPO" --env staging --body us-east-1
```

Use `--env` for environment scope and `--org` for organization scope. GitHub does not return secret values; list metadata to verify a write. Supply secret values through stdin or a secure file rather than literal command arguments.

## Sources

- [CLI run commands](https://cli.github.com/manual/gh_run) and [workflow commands](https://cli.github.com/manual/gh_workflow)
- [Actions REST API](https://docs.github.com/en/rest/actions)
- [Using GitHub CLI in workflows](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/using-github-cli-in-workflows)
