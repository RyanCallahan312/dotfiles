---
name: architecture-explainer
description: Explain codebase architecture, package boundaries, feature directories, domain ownership, dependency direction, side effects, and end-to-end flows in an evidence-first visual format. Use when a user asks how modules relate, what directories are for, who owns a concept, how a request moves through the system, where new behavior belongs, or for a codebase map with Mermaid diagrams, responsibility tables, concise mental models, and file:line citations.
---

# Architecture Explainer

Produce a teaching-oriented map of the code as it exists. Explain concepts and consequences before cataloging files.

Read `references/presentation-template.md` before drafting the final response. Select only the sections that help answer the question.

## Investigation Workflow

1. Define the scope.
   - Identify the packages, directories, concepts, or execution path named by the user.
   - Read the nearest `AGENTS.md` files before drawing conclusions.
2. Establish documented intent.
   - Inspect root and package READMEs, design docs, ADRs, language glossaries, package manifests, export maps, and public entrypoints.
   - Record whether design documents are current, proposed, historical, or contradicted by implementation.
3. Prove the executable structure.
   - Trace imports and package dependencies to establish direction.
   - Find public services, functions, contracts, callers, and downstream collaborators.
   - Use tests to confirm sequencing, invariants, failure behavior, and replay or idempotency semantics.
   - Follow at least one representative end-to-end path when behavior is part of the question.
4. Classify each responsibility.
   - State what each area owns.
   - State what it explicitly does not own.
   - Classify effects as durable writes, durable reads, remote effects, ephemeral delivery, telemetry, or pure transformation.
   - Distinguish authority from coordination, policy from mechanism, canonical contracts from local views, and durable truth from live delivery.
5. Reconcile naming with behavior.
   - Flag misleading directory names, duplicated vocabulary, compatibility aliases, test-only helpers, planned seams, and stale documentation.
   - Label these conclusions as inference unless directly documented.
6. Build the explanation around the user's mental model.
   - Lead with a one-sentence thesis.
   - Use diagrams for relationships and temporal flow.
   - Use tables for ownership and contrasts.
   - End with placement rules and a recommended reading order.

## Evidence Standard

- Treat imports, calls, service definitions, package manifests, tests, and explicit ownership documentation as direct evidence.
- Treat naming, directory placement, missing callers, and architectural consistency as inference.
- Cite repo-relative `path:line` references for substantive claims when line numbers are available.
- Prefer the closest executable evidence over broad documentation when they disagree.
- Mention contradictions instead of silently choosing one source.
- Never infer ownership from a directory name alone.
- Do not claim a feature is unused until repository-wide callers and exports have been checked.
- Scope confidence honestly. State which boundaries were searched and what remains unverified.

## Conceptual Lenses

Choose the smallest set needed:

- **Ownership:** Who defines canonical meaning and validates state?
- **Coordination:** Who decides when and in what order capabilities run?
- **Policy:** Who supplies product- or environment-specific decisions?
- **Mechanism:** Who performs persistence, network calls, generation, or delivery?
- **Data flow:** Where does data enter, transform, persist, and leave?
- **Side effects:** Which effects are durable, ephemeral, remote, or observational?
- **Boundaries:** What must not leak across package or layer seams?
- **Change placement:** Which decision rule tells a maintainer where new code belongs?

When possible, reduce the result to a memorable contrast such as:

> Core owns durable truth; Runtime coordinates it over time.

The contrast must be supported by evidence and fit the repository rather than being forced.

## Diagram Selection

- Use `graph TD` for layers, ownership, or vertical dependency direction.
- Use `graph LR` for peer modules and capability collaboration.
- Use `sequenceDiagram` for temporal request or event flows.
- Use `stateDiagram-v2` only when state transitions are central.
- Label important edges with verbs such as `accept`, `claims`, `publishes`, or `loads`.
- Use `-->` for directly proven relationships and `-.->` only for inferred or observational relationships.
- Keep nodes conceptual. Add file citations in prose or tables rather than crowding diagrams.
- Do not use ASCII diagrams.

## Presentation Rules

- Start with `# [Scope] Map` or another concrete title.
- Follow with a bold `Thesis:` sentence.
- Put the primary diagram before detailed prose.
- Use a responsibility table with `Area`, `Purpose`, and a memorable shorthand when explaining several directories or packages.
- For each major area, explain purpose, lifecycle position, ownership, exclusions, and the practical mental model.
- Use short blockquotes beginning with `Think:` for memorable summaries.
- Include one representative end-to-end lifecycle when the scope contains behavior.
- Add focused contrast tables for easily confused areas.
- Include a `Shortest Useful Summary` for broad maps.
- Include a recommended reading order that follows behavior rather than alphabetical paths.
- Finish with `Architectural Consequences` and `Confidence and Gaps` when the map is broad or contains inference.
- Adapt section count to the question. Do not mechanically emit empty sections.

## Writing Rules

- Explain why a boundary exists, not merely what files it contains.
- Prefer domain language from repository documentation.
- Define overloaded terms before using them.
- Keep inventories subordinate to the mental model.
- Make dependency direction explicit.
- Separate durable authority from best-effort publication or transport.
- Say `appears test-only` or `no production caller found` rather than declaring dead code without proof.
- Avoid prescribing refactors unless the user asks; identify navigational ambiguity without turning the explainer into a review.
- Keep prose compact even when the investigation is thorough.

## Completion Check

Before delivering, verify:

- The thesis explains the architecture in one sentence.
- Every important arrow is supported by imports, calls, configuration, or docs.
- Ownership and non-ownership are both clear.
- At least one concrete flow validates the static map when behavior matters.
- Durable, ephemeral, remote, and observational effects are not conflated.
- Citations use repo-relative paths and useful line numbers.
- Inferences and stale or proposed docs are labeled.
- The final summary gives a maintainer a rule for navigating or placing code.

If evidence supports only part of the requested map, call it a partial map and identify the unverified boundary.
