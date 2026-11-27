# Building the HTML walkthrough

Choose the teaching format in [design.md](design.md) first. Building uses standard-library Python, plain HTML, and the bundled kit. The optional browser tooling must already be installed to run its checks.

Contents: [Workflow](#workflow) · [Flow spec](#flow-spec) · [Chart spec](#chart-spec) · [Hand-written components](#hand-written-components) · [Verify](#verify) · [Deliver](#deliver)

`$SKILL` below is this skill's directory.

## Workflow

1. **Sketch the answer:** the reader's question, the concrete case, the relationship it illustrates, and a useful qualification. If there is a calculation, verify the inputs, rules, units, and result. For multi-step arithmetic, compute the values once in a scratch script and reuse them in copy and figures.
2. **Choose components.** For a definition or comparison, start with a [hand-written example](#hand-written-components). For a sequence or dependency, use a flow. For a pattern across observations, use a chart. Don't invent stages or data to fit the kit.
3. **Render any figures needed** from their JSON specs; skip this step for plain HTML components:
   ```bash
   python3 "$SKILL/scripts/figures.py" flow overview.json > overview.html
   python3 "$SKILL/scripts/figures.py" chart rainfall.json > rainfall.html
   ```
   Treat every `warning:` as a defect: shorten the label, change `side`, raise `gap`, or fix the step count.
4. **Write `page.src.html`** from `$SKILL/assets/page.html`. Fill the overview section or replace it with a figure with `id="overview"`. Write the sections; match the navigation links to their IDs. Keep `<link rel="stylesheet" href="kit.css">` and `<script src="kit.js"></script>` for inlining. Use the empty `<style>` for requested theme overrides.
5. **Inline** into the single deliverable:
   ```bash
   python3 "$SKILL/scripts/figures.py" inline page.src.html walkthrough.html
   ```
6. **Verify, look and fix** (see [Verify](#verify)), then **deliver**.

## Flow spec

Illustrative library pickup: a hold reserves access to a copy; the loan begins at checkout. The node `value` can name a state rather than a number.

```json
{
  "id": "overview",
  "start": "last",
  "label": "A reader requests a book, the library sets a copy aside, and checkout starts the loan.",
  "lanes": [{"title": "Arrange pickup"}, {"title": "Borrow"}],
  "nodes": [
    {"id": "request", "lane": 0, "col": 0, "unit": 1, "label": "Hold", "value": "Requested", "step": 1},
    {"id": "pickup", "lane": 0, "col": 1, "unit": 1, "label": "Hold", "value": "Ready", "step": 2},
    {"id": "loan", "lane": 1, "col": 1, "unit": 2, "label": "Loan", "value": "On loan", "step": 3, "out": true}
  ],
  "edges": [
    {"from": "request", "to": "pickup", "label": "set aside copy"},
    {"from": "pickup", "to": "loan", "label": "check out", "side": "l"}
  ],
  "steps": [
    {"name": "Request", "unit": 1, "text": "The reader places a hold for the next available copy."},
    {"name": "Pickup", "unit": 1, "text": "A copy is waiting, but the reader has not borrowed it yet."},
    {"name": "Checkout", "unit": 2, "text": "The reader checks out the copy and the loan begins."}
  ]
}
```

- `lane` is the row (phase) and `col` is the column. Place inputs top-left and results bottom-right. Edges may go right in the same lane or down to a later lane, never up or left within a lane. Columns size themselves to their widest node.
- `unit` is a palette slot (1–6, mapping to `--u1…--u6`). Use slots consistently for categories or units. For a category key, set e.g. `"legend_title": "Record type", "legend": [{"unit": 1, "text": "Hold"}, {"unit": 2, "text": "Loan"}]`.
- `from` as a list draws a **merge**. Inputs meet at a junction dot, and one labelled shared line enters the target; inputs must be in the target's lane or above. When every input sits to the left, the line enters from the left. Otherwise the inputs drop to a bus over the target and enter from the top; same-lane inputs on either side step up to that bus. This covers "three inputs above combine into one result" and "a rate above plus a factor beside it".
- Two edges from one node to two targets draw **branches**. Use them whenever outputs share an input.
- `step` (1-based) on nodes; edges default to their target's step. You need exactly as many `steps` captions as the highest step. Omit `steps` for a static figure; it then reveals on scroll.
- `start`: `"last"` opens the stepper on the complete path, so the first screen shows every value; Restart walks it from step 1. Use it for the overview. Chart steppers usually start at 1 (omit `start`).
- A legend that doesn't fit in a free top-right corner becomes a key under the drawing instead of shrinking it.
- Optional: `gap` (column gap, default 130), `side` per edge (`"l"`/`"r"` label preference), `x` per vertical edge, `w` per node, `legend_title`, `caption` (static only).
- Step caption `text` may contain inline HTML (`<b>`, `<code>`).

## Chart spec

Illustrative daily rainfall: a bar shows how much fell that day, not a running total.

```json
{
  "id": "rainfall",
  "label": "Wednesday had the most rain, 8 mm.",
  "x": {"labels": ["Mon", "Tue", "Wed", "Thu", "Fri"], "ticks": [0, 1, 2, 3, 4], "title": "Day"},
  "y": {"min": 0, "max": 10, "ticks": [0, 5, 10], "title": "Rainfall (mm)"},
  "series": [{"name": "Daily rainfall (mm)", "unit": 1, "values": [2, 0, 8, 4, 1], "style": "bars"}],
  "at": 2
}
```

- Points are evenly spaced. For irregular timestamps, give `x.positions` (numbers, e.g. minutes elapsed) and optionally `x.min`/`x.max`. `x.tick_labels` overrides tick text, and `x.readout_labels` overrides the tooltip label per point.
- `style` is one of `line` (default; draws in), `area`, `dash` (baseline or comparison), `dot`, `thin` or `bars`. Use `null` for gaps. Set `readout: false` to keep a series out of the tooltip, and `text` to give per-point display strings.
- Use `marks: [{"at": 2, "label": "Storm"}]` for an event, `windows: [{"from": 2, "to": 3, "label": "Storm period"}]` for a span, or `refs: [{"y": 5, "label": "Reference: 5 mm"}]` for a horizontal line. Point indices are zero-based. With two series, `between` can shade their positive difference (`upper`, `lower` series indices plus `from`, `to` point indices). Use `step` on parts and `steps` captions as in the flow spec to reveal them in order.
- `at` is the resting point of the crosshair, the point the page is about. `table` (default: on for 60 points or fewer) adds a data table behind a disclosure. `key` overrides the series key.
- `width`/`height` default to 1000×330 in viewBox units; the chart scales to its frame.

## Hand-written components

For a qualitative comparison, replace the template's overview section with ordinary HTML:

```html
<section id="overview">
  <h2>Who owns the painting, and who has it?</h2>
  <p>Imagine an artist lends a painting to a museum.</p>
  <dl>
    <dt>Ownership</dt><dd>The painting still belongs to the artist.</dd>
    <dt>Custody</dt><dd>The museum has the painting in its care during the loan.</dd>
  </dl>
</section>
```

For arithmetic, use an equation chain that can also be read as a sentence:

```html
<figure class="chains"><div class="u1"><h3>Average speed for this trip</h3><div class="chain">
  <span class="lk"><small>Distance</small><b>12 km</b></span><span class="op">÷</span>
  <span class="lk"><small>Elapsed time</small><b>1 h</b></span><span class="op">=</span>
  <span class="lk out"><small>Average speed</small><b>12 km/h</b></span>
</div></div></figure>
```

Other pieces: `<p class="stage">Step 2</p>` before an h2; `<ul class="key"><li class="u2">Series</li><li class="u6 hollow">Baseline (dashed)</li></ul>` under a hand-drawn chart; `<code>literal</code>` for terms the reader must see verbatim; `<details id="…"><summary>Reader's question?</summary>…</details>` for tangents (link it from the TOC with `class="d2"`). A hand-drawn SVG chart can still get the crosshair: put `tabindex="0"` and a `data-hover` JSON on the `<svg>` in the same shape `figures.py chart` emits.

## Verify

1. **Meaning.** Check the case against the definitions. Read each relationship in the overview as a sentence and check it against the text. If the example uses a calculation script, rerun it and compare its output with the displayed values. When a claim changes, check its captions, labels, and accessible names too.
2. **Browser, on the final file:**
   ```bash
   node "$SKILL/scripts/check.mjs" walkthrough.html --out shots/
   ```
   This tests every stepper (Next, Back, rail by keyboard, all parts visible at the end) and every chart readout (keyboard, pointer, resting point, announced, tooltip inside the chart). It also checks TOC links, SVG text collisions and clipping, 1440px and 320px overflow, reduced motion, console errors, network requests and no-JS reading. It records the file's sha256 and saves screenshots. Fix every `FAIL`. Exit code 2 means no browser was available; say which behaviours went unexercised.
3. **Look at the screenshots.** Open `check-first-screen.png`, `check-desktop.png` and `check-320.png` and judge them against the [rubric](design.md#rubric). Automated checks can't tell whether a caption adds meaning or a diagram reads well.
4. If you edit after checking, re-inline and recheck. Only the bytes you checked are verified.

## Deliver

If `command -v plannotator` succeeds, deliver with Plannotator's visual-explainer flow: run `plannotator annotate "$PWD/walkthrough.html"` on the final file, as raw HTML, with no `--markdown`, `--gate`, `--tailscale` or sharing. Don't use `open`. Wait for the review to close. Address each returned annotation, sweeping its siblings by meaning, then re-inline and recheck. Closing without feedback isn't approval; don't reopen automatically.

Without Plannotator, give the validated path and say review wasn't launched. Never auto-install or upload. In the final message, give the path and sha256, the checks that passed, anything not exercised, and the open questions. Keep verification separate from review or disclosure approval.
