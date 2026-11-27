# Structured checker result v1

`../scripts/check-result.mjs` owns validation, exact-byte freshness checks, and
conversion to native XGraph. This is a renderer-independent handoff, not a
statechart execution format. Producers must use `parseCheckResult` before
writing JSON; consumers must validate after reading. Unknown versions fail.

| Field             | Contract                                                                                                                                                                                                                                                                                     |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| schemaVersion     | `stately.check-result.v1`                                                                                                                                                                                                                                                                    |
| kind              | `explored-configurations` or `summary-only` (empty state/edge/path arrays); never an authored executable model                                                                                                                                                                               |
| binding.artifacts | `{ role, path, content, sha256 }[]`; original UTF-8 bytes, lowercase SHA-256. Roles: spec, config, model, view, scope, trace, dot. Paths unique. Retain all semantic dependency modules as additional spec artifacts; owned runs bind the SANY loaded local closure.                         |
| checker           | `{ name, version, command: string[], complete, bounds: object, assumptions: string[] }`; include constants, constraints, action constraints, symmetry/VIEW, worker/rerun limits, and errors when applicable. Commands are provenance, never executed on import.                              |
| rules             | `{ id, kind, name, outcome }[]`; kind invariant/property/deadlock; outcome holds/broken/not-checked. Never infer holds from absent marks.                                                                                                                                                    |
| states            | `{ id, variables, initial, violations: ruleId[] }[]`; stable producer raw IDs and original JSON/tagged values. Fingerprints are strings, not JS numbers. Boundary states may carry `{ past, excluded }`.                                                                                     |
| transitions       | `{ id, from, to, action, label? }[]`; stable raw endpoints and action identity, distinct from a human label.                                                                                                                                                                                 |
| counterexamples   | `{ id, ruleId, states: rawId[], transitions: stepId[], loopStart?, stutters? }[]`; first state initial; consecutive edges must match. Loop index is zero based. Explicit closing steps may repeat a state; stuttering may instead identify the last state as loopStart with stutters true.   |
| projection        | Optional `{ regions, notes, ... }`; each region has `{ id, name, states }`. Each projected state has `{ id, path: string[], members: rawId[], marks }`; marks are `{ ruleId, kind: breaks/mayBreak }`. Resolved arrow conditions and hidden-step notes can be retained as additional fields. |
| uncitedConditions | Optional, native runs: `{ edgeId, guard?, eventType, source }[]`, guarded transitions whose guard has no source citation in the rules file.                                                                                                                                                  |

Additional producer metadata is retained, not interpreted as executable code.
Changing field meaning requires a new schema version. Paths/loop indices always
refer to raw configurations, even when a projection merges or hides them.
Retain the original source/report as well; serializing a finite explored graph
cannot reconstruct arbitrary TLA+ or prove application equivalence.

## Optional pstack producer

Use `../scripts/pstack-result.mjs` as a small upstream integration candidate.
Its `exportPstackResult` takes the **already computed** `result`, `walked`,
`chart`, and `found` values from `scripts/pipeline.ts`, plus exact `artifacts`
and `checker` provenance. `result` is pstack's CheckResult, `walked` its Walk,
`chart` its resolved Chart (or undefined), and `found` its sorted Bug array.
It preserves tagged TLA+ values, raw IDs, rule outcomes, bounds, raw-to-projected
membership, marks, conditions, counterexamples and loops.

A producer can add this after projection, independently of Mermaid rendering:

```js
const handoff = exportPstackResult({
  result,
  walked,
  chart,
  found,
  artifacts, // artifact(role, relativePath, exactContent) for spec/config/view/dependencies
  checker: {
    name: "TLC",
    version: actualTlcVersion,
    command: actualCommand,
    bounds: actualConstantsAndConstraints,
    assumptions: reviewedAssumptions,
  },
});
files.set("check-result.json", [JSON.stringify(handoff, null, 2)]);
```

This is an optional upstream seam, not a patched or forked `/statechart`.
Do not rerun view callbacks: stateful/expensive callbacks could change the
projection. Do not reconstruct membership or verdicts from Mermaid/prose.
Keep TLC flags, checking, exit codes, report, and Mermaid output unchanged.
The included live evaluation checks the installed pstack seam with TLC and
asserts no extra view callbacks or changed Mermaid text. Upstream distribution
and adoption are separate steps.

## Native reports and freshness

The owned runner produces this full standalone result plus a bounded XGraph
carrying `@statelyai.checkReport` (`stately.check-report.v1`): run/status/checker,
per-rule outcomes, raw-variable trace frames and entity mappings, artifact
hashes, view digest, authoritative recheck inputs with an explicit original
source-file map, and separate application checks. The reviewed scope file
supplies domain bounds, assumptions, and rule descriptions. An included trace
need not map every raw state into the projection; empty mappings are explicit,
and invalid entity references are rejected.

```sh
sh SKILL_DIR/scripts/stately-check graph check-result.json checked.graph.json
```

The full result retains original source/trace bytes locally. The legacy
raw-configuration converter budgets 180000 characters; the projection/report
view budgets 195000. Complete artifacts are always retained; explicit
`view --trace` slicing discloses omitted paths and preserves original verdicts,
run ID/time and full-result reference. A successful large check may have only a
summary view. Unsupported oversize witnesses fall back to complete local
Markdown/JSON; no invented configuration is used to make an empty chart appear
executable.

`graphCheckFreshness(graph, currentArtifacts)` and `resultFreshness` compare
exact bytes, including the full result reference where present. Keep the
original model separate from a synthetic explored/projection view.
