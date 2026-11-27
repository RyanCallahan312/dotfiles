# Designing a domain walkthrough

Put the reader's question and its short answer on the first screen. Choose one concrete example that makes the answer easier to see. If the topic is *custody versus ownership*, for instance, a borrowed painting lets the reader identify who holds it and who owns it. No measurements or timeline are needed.

## Choose the overview

| What the reader needs to see | Useful overview |
|---|---|
| The parts of a subject and their relationships | A labelled sketch or concept map. Write the relationship on each link: “is part of” means something different from “causes”. |
| The boundary between two ideas | A side-by-side comparison using the same case and the same question for each side. |
| Who does what, or how something changes | An ordered sequence of actions or states. Mark the handoff, decision, or event that causes the change. |
| How a rule selects an outcome | A decision tree or table. Change one condition in the example so the reader can see when the other outcome applies. |
| How inputs produce a result | A dependency map. Put values and units on the nodes and name operations on the edges. Show shared inputs and merges explicitly. |

Use a phase-lane map when order or dependencies are the point. Name lanes for meaningful stages, keep labels short, and use a stepper only if seeing the stages separately helps. Open an overview stepper on the complete path. Use text labels as well as colour for categories or units, and explain the key. For other overviews, ordinary semantic HTML is enough; see [build.md](build.md) for examples.

## Build the page around the example

- Give the topic a plain title. Identify an illustrative case as such; include a date, location, or unit only if it changes the interpretation.
- Give each section a question the reader might ask or a heading that answers it. Reuse the example to explain one idea at a time. Number steps only if the order matters.
- Put a limitation beside the claim it qualifies. Use `<details>` for a reader to explore a near miss or an exception without interrupting the main explanation. Keep the core answer visible.
- Use reader-facing terms consistently across prose, captions, navigation, and accessible names. When relying on a particular definition, cite a source the reader can consult. Respect any disclosure limits on supplied material.

## When numbers matter

Use an equation chain for a calculation the reader should be able to repeat. Show the units, state any rounding, and check each dependency independently of the example values. Use a chart for a pattern across observations: a line for a continuous quantity, bars for discrete periods. Label axes and distinguish observations from illustrative values. Mark a threshold, event, comparison series, or time window only if it helps explain the pattern.

Give each chart an accessible name that states the takeaway, a keyboard-readable crosshair resting at the point of interest, and a data table for exact values. Use `table: true` in the chart spec when the default would omit it.

## Presentation and access

Use the kit's neutral palette and system fonts by default. Apply supplied styling only when requested, using token overrides rather than remote assets. Keep text contrast at least 4.5:1, meaningful marks at least 3:1, and focus indicators visible. Keep wide figures within scrollable frames at 320px and express their takeaway in adjacent text. Motion should explain a change; the page must still make sense with reduced motion and with JavaScript disabled.

## Rubric

Before delivery, check the rendered page:

- Can a newcomer find the answer on the first screen and explain it in their own words?
- Does the example show the key relationship or distinction? Would it still hold if one fact changed?
- Do the labels, cases, and any calculations agree with the definitions? Is it clear what is general and what is particular to this case?
- Does each visual teach something, and is the same information available without colour, a pointer, or animation?
