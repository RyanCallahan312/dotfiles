# Ticket Quality Examples and Sources

Use these examples to sharpen a draft, not to introduce unrequested requirements. Example behaviors below are illustrative; confirm the actual contract for the task before using them.

## Replace activities with observable outcomes

| Weak criterion | Stronger criterion, if this is the agreed behavior |
| --- | --- |
| Add retries. | When the provider returns a retryable error, retry according to the agreed policy without creating duplicate records; verify transient failure, exhausted retries, and duplicate delivery with provider-stub integration tests. Ask for the retry policy if unspecified. |
| Users can upload files. | The picker offers only formats supported by the selected model; the upload endpoint rejects unsupported formats even when the picker is bypassed. Verify accepted and rejected payloads, including a model switch before submission. |
| The query is faster. | Under the agreed dataset, warehouse, and comparison procedure, the query meets the agreed runtime and cost thresholds while returning equivalent results. Ask for the missing benchmark conditions, equivalence rule, or thresholds rather than inventing them. |
| Add tests and pass CI. | The reported reproduction returns the expected result after the fix; a regression test fails against the prior behavior and passes with the change. Applicable CI gates also pass. Name the reproduction and expected result in the actual ticket. |
| Investigate caching. | Compare the agreed caching options against the workload, document measured hit rate and staleness behavior, and produce a recommendation with tradeoffs and remaining risks. Implementation is excluded unless separately agreed. |

Keep distinct assertions in separate numbered criteria in the actual description. The examples combine them for comparison only.

## Make Context explain causality

**Weak:** “Remove the legacy routing library. See PR.”

**Stronger:** “All environments now use a single primary database. The legacy replica-routing layer no longer routes traffic to a replica, but still adds connection proxies and lifecycle hooks that complicate worker connection management. Remove the obsolete layer while preserving callers' existing behavior. Provisioning databases and changing the deployment topology are out of scope.”

Use this pattern: current situation → consequence → intended improvement → boundary. Do not claim a root cause is proven merely because removing a component seems helpful.

## Make References support action

**Weak:** an unlabeled PR link, a repository homepage, or “see Slack.”

**Stronger:** a direct decision permalink explaining the agreed scope, a repository-qualified code entry point describing the relevant contract, and a regression fixture or safe manual procedure explaining how to verify it. Include actual URLs/paths only after inspecting them. Summarize essential decisions in Context so links provide depth, not missing requirements.

If a required document is inaccessible, report that limitation and obtain its relevant content before finalizing. If no external material exists, keep References and supply concrete, supported inline setup/validation steps rather than fake links or an empty “N/A.”

## Quick handoff test

Read only the proposed ticket, without relying on conversation memory:

- Can an unfamiliar implementer explain the reason for the work and its boundaries?
- Can an independent reviewer distinguish complete/correct from partial/incorrect using the stated conditions and evidence?
- Can both locate the resources or follow the inline procedures needed to do that?

If any answer is no, improve the draft or ask a focused question. Do not use ticket length as a proxy for quality.

## Supporting guidance

Consulted 2026-10-27. These sources support the writing principles; the exact three-heading structure is the user's requirement, not a Jira platform requirement.

- [Atlassian: Acceptance criteria](https://www.atlassian.com/work-management/project-management/acceptance-criteria) — clear, concise, testable, outcome-focused criteria; objective measurement; collaborative clarification; acceptance criteria versus the broader Definition of Done.
- [Atlassian: User stories](https://www.atlassian.com/agile/project-management/user-stories) — explain who benefits, what they need, and why; clarify through conversation and confirm with acceptance criteria. Apply these principles to technical tasks too, without forcing every ticket into an “As a…” sentence.
