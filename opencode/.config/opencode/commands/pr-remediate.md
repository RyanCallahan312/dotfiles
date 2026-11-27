---
description: Remediate GitHub PR review comments using AI swarm analysis
---

# pr remediation

**Remediate GitHub PR review at `$1` comments using AI swarm analysis**

## Description

Audit and remediate all review comments GitHub Pull Request `$1` review by leveraging a swarm of specialized subagents. Each comment will be analyzed for actionability, severity, and recommended fixes. Approved fixes will be implemented, reviewed, and committed back to the repository.:

1. **Fetch** all review comments from `$1` review using `gh` CLI
2. **Chunk** the review into isolated, actionable comments/suggestions
3. **Analyze** each comment in parallel using @explore subagents to determine:
   - Whether it should be addressed
   - Severity level (HIGH/MEDIUM/LOW)
   - Recommended fix approach
4. Use question tool to clarify any ambiguous comments with the original reviewer if needed
5. **Aggregate** all subagent decisions into a comprehensive remediation plan
6. **Implement** fixes in parallel using @general subagents
7. **Review** implementations using @code-review subagents to catch issues
8. **Fix** any problems found and re-review until clean
9. **Commit** all changes using conventional commits

## Workflow Steps

### Phase 1: Discovery

- Parse `$1` to extract owner, repo, PR number, and (optionally) review ID:
  - Full URL with review anchor: `https://github.com/{owner}/{repo}/pull/{number}#pullrequestreview-{review_id}`
    - Extract `{review_id}` from the `#pullrequestreview-` fragment
  - Full URL without anchor: `https://github.com/{owner}/{repo}/pull/{number}`
  - Short form: just a PR number (use current repo)
- Use `gh` CLI to fetch PR details:
  - `gh pr view <number> --json title,body,headRefName,baseRefName,files -R {owner}/{repo}`
  - `gh pr diff <number> -R {owner}/{repo}`
- Fetch review comments scoped to the specific review:
  - If a review ID was extracted, fetch **only** that review's comments:
    - `gh api repos/{owner}/{repo}/pulls/<number>/reviews/{review_id}`
    - `gh api repos/{owner}/{repo}/pulls/<number>/reviews/{review_id}/comments`
  - If no review ID was provided, fetch all reviews and their comments:
    - `gh api repos/{owner}/{repo}/pulls/<number>/reviews`
    - `gh api repos/{owner}/{repo}/pulls/<number>/comments`
- Only process comments belonging to the targeted review; ignore comments from other reviews

### Phase 2: Analysis

- Parse all review comments and chunk them into isolated issues
- For each chunk, spawn an @explore subagent with context:
  - The specific comment
  - File path and relevant code
  - Repository structure and conventions
- Each subagent returns:
  - Should address: YES/NO
  - Severity: HIGH/MEDIUM/LOW
  - Recommendation: Specific fix approach
  - Rationale: Why this should/shouldn't be addressed

### Phase 3: Planning

- Aggregate all subagent decisions into a priority matrix
- Group related fixes by file/module
- Identify dependencies between fixes
- Use question tool to clarify any ambiguous comments with the original reviewer
- Present comprehensive remediation plan to user

### Phase 4: Implementation

- For each approved fix, spawn a @general subagent:
  - Provide specific file paths and line numbers
  - Include the recommended approach
  - Reference repository coding conventions
- Track all implementations

### Phase 5: Validation

- For each implemented fix, spawn a @code-review subagent:
  - Review for correctness, security, and maintainability
  - Check for unintended side effects
  - Verify test coverage if applicable
- Identify any CI issues by running CI validations
- If issues found, return to Phase 5 with fixes

### Phase 6: Commit

- Use conventional commits skill to create commits:
  - Group related changes logically
  - Write descriptive commit messages
  - Follow repository commit conventions

## Output

The command will output:

1. Summary of all review comments found
2. Analysis results from subagent swarm
3. Remediation plan with priorities
4. Implementation status for each fix
5. Code review results
6. Commit summary

## Error Handling

- If PR review not found: Exit with error message
- If no actionable comments: Report and exit cleanly
- If implementation fails: Stop and report to user for manual intervention
- If git state is dirty: Warn user and abort

## Notes

- Do push commits automatically
- Always run CI validations after remediation (linting, type checking, tests)
