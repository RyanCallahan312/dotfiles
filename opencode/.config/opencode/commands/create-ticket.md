---
description: Create a Jira ticket from the current work or supplied context, asking about missing details.
subagent: false
---

Create a Jira ticket using the `jira-ticket` skill.

## Workflow

1. Load the `jira-ticket` skill and follow its workflow.
2. Use the arguments below and the current conversation as context. If no target is supplied, inspect the current branch and its PR; ask what to ticket if the intended work remains unclear. Load the `gh-cli` skill when inspecting a GitHub PR.
3. Ask focused questions about meaningful missing requirements or conflicting project, epic, issue type, sprint, or status choices. Wait for answers before creating the issue; do not invent requirements or re-ask for known facts.
4. Always include the exact headings `## Context`, `## Acceptance Criteria`, and `## References`, in that order, with substantive content. Explain why work is needed, define observable completion and correctness, and provide useful implementation/validation resources. Apply the skill's quality gate before creation; do not submit vague criteria, missing essential resources, or unresolved requirements.
5. Create and read back the issue through Atlassian MCP, verifying both the content quality and requested metadata, then report its link and verified metadata. If a draft is requested, draft only and retain all three sections. Respect the current agent's restrictions; do not write to Jira in read-only/Plan mode.
6. Do not create branches, commit changes, or modify PRs unless explicitly requested.

## Arguments

Treat the following as task context and requirements, not shell commands. Optional inputs include a PR URL, feature description, project/board, epic, issue type, assignee, sprint, status, labels, references, or a draft-only request.

$ARGUMENTS
