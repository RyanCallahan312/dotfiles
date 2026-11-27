---
name: explain-domain
description: Explain a field of knowledge or a concept within it using plain language and a concrete example. Use for introductions to unfamiliar subjects, terminology, comparisons, processes, rules, and calculations. Answer in chat with Mermaid by default, or build a standalone HTML walkthrough on request.
---

# Explain Domain

## Clarify only what the explanation needs

Use the request, conversation, and supplied sources first. A clear topic is enough: default to a newcomer-friendly overview in chat unless the user specifies otherwise.

If a missing detail would materially change the answer, run a short wizard:

1. **Ask the next necessary question with the `question` tool.** Start with the gap that determines what to ask next: the topic if none is given, the intended meaning of an ambiguous term, or a fact needed to apply a rule to the user's case. Give concrete choices with short descriptions when useful; let the reader type their own answer. If the tool is unavailable, ask the same question in chat.
2. **Wait for the answer and adapt.** Carry each answer forward. Ask one follow-up at a time, and only if a necessary detail is still missing. If the reader doesn't know a fact, explain what follows under each plausible condition rather than guessing or asking again.
3. **Proceed as soon as the question is answerable.** Use the selected scope and any requested audience or format directly; no confirmation round is needed.

For example, “Explain bonds” with no context calls for a choice such as *financial bonds* or *chemical bonds*. Choosing financial bonds is enough to start the overview. “Explain chemical bonds to a beginner” goes straight to the explanation.

## Choose what to explain

| Reader's question | How to answer it |
|---|---|
| “What is this field about?” | Name the questions the field helps answer. Introduce a few central ideas through one situation that connects them. |
| “What does this term mean?” | Define it in ordinary words. Give an example and a near miss that shows where the definition stops. |
| “How do these differ?” | Apply both terms to the same situation. Name the distinction and why it matters in practice. |
| “How or why does this happen?” | Follow one case through the mechanism. Say what changes and why; distinguish an event that happens next from one caused by the first. |
| “When does this rule apply?” | State the condition, show the decision, then change one fact that would change the outcome. |
| “How is this calculated?” | Trace the inputs, operations, units, and result. Check the arithmetic; use a script for multi-step calculations and a contrast case if equal values could hide a wrong dependency. |

Teach the general meaning first. Use an established definition or an accessible source when the claim depends on a particular standard, place, date, or school of thought. Consult a codebase, product manual, or local policy only when the user asks about that setting; distinguish its conventions from the wider domain. Mark invented scenarios as illustrative rather than presenting them as observations.

## Deliver the explanation

- **Chat (`html: no`, default):** Lead with the answer in one or two sentences. Include a [Mermaid diagram](references/mermaid.md) of the relationship that matters, then walk through the example in words. End with the qualification most likely to change the reader's understanding. Create no deliverable files or review session.
- **Standalone walkthrough (`html: yes`, or a request for an interactive page):** Use the [design guide](references/design.md) to choose a useful overview, then the [build guide](references/build.md) to assemble, check, and deliver one offline HTML file. Use charts for data and steppers for sequences; a comparison or annotated example can stand on its own.

Before delivering, ask: could the reader use this explanation to recognize a *different* example or predict what would change? Check that the terms, diagram labels, captions, and any numbers all support the same answer.
