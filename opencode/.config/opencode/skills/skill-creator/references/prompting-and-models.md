# Prompting & Model-Steering Reference (2026)

Contents: Retired 2023 Patterns · Shared Cross-Lab Rules · Lab & Model Matrix (Anthropic · OpenAI · Google) · Context & KV-Cache Engineering

Use this reference when writing or auditing skill bodies, agent definitions, system prompts, or project memory files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`).

## Retired 2023–2024 Patterns (Do Not Use)

| Legacy Pattern | Why It Fails in 2026 | Replacement |
|---|---|---|
| `"Think step by step"` / prescriptive CoT | Reasoning/thinking models think natively; forced CoT inflates latency, causes loops, or hurts accuracy. | Control API `effort` / `thinking_level`; use general reasoning cues only when needed. |
| `CRITICAL: YOU MUST...` / ALL-CAPS emphasis | Claude 4.5+ and GPT-6 Astra take emphasis literally, causing tool over-triggering, subagent over-spawning, and premature permission stops. | Use calm, scoped criteria and explain the *why*. |
| `"You are a world-class expert..."` | No factual accuracy gain (and can degrade accuracy; EMNLP 2024, Wharton GAI Lab 2025). | Reserve personas strictly for tone, audience, or formatting. |
| Hand-tuned `temperature` / `top_p` / `top_k` | Deprecated or returns HTTP 400 on GPT-6.2+ and Gemini 3.6+/4. | Enforce determinism via system instructions and strict JSON schemas. |
| Stuffing huge context windows | Causes **Context Rot** (Chroma 2025 across 18 frontier models); distractors degrade accuracy far below max limits. | Curate minimal high-signal context; use JIT retrieval, compaction, and subagents. |
| Rigid guardrails & huge toolsets | Hobbles stronger models (Vercel removed 80% of tools; Manus simplified across 5 rewrites). | Minimal general tools + clean docs + deterministic verification hooks. |

## Shared Cross-Lab Rules

1. **Explain the *why*:** Motivation behind a constraint generalizes better than bare prohibitions (*"Output is read by TTS, so avoid ellipses"* beats *"NEVER use ellipses"*).
2. **Eliminate contradictions:** Reasoning models burn thinking tokens reconciling conflicting rules across system prompts, `AGENTS.md`/`CLAUDE.md`, and tool descriptions.
3. **Define explicit stop conditions & action boundaries:** State what "done" looks like, what reversible work proceeds autonomously, and which irreversible/external actions require confirmation.
4. **Long-context ordering:** Place large documents/codebases **before** the query/instructions, bridged with an anchor phrase (*"Based on the code above..."*).
5. **Preserve prefix stability:** Keep stable instructions at the front and dynamic context at the end. Never mutate earlier turns, system prompts, or tool lists mid-session—doing so breaks KV-cache hits and drops preserved reasoning/thinking state.
6. **API Structured Outputs over prose JSON:** Enforce schemas via `json_schema` (`strict: true`) / `response_format`, and still handle refusals, truncations, and business-logic checks in code.
7. **Prompts guide; hooks enforce:** Use deterministic hooks, linters, typecheckers, tests, and permissions for hard invariants.

## Lab & Model Matrix

| Dimension | Anthropic (Claude 4.5–5.x / Fable 5) | OpenAI (GPT-5–6.2 Astra/Sol / Codex) | Google DeepMind (Gemini 2.5–4) |
|---|---|---|---|
| **Roles & Caching** | `system` + turns (`CLAUDE.md` injected as user message). Select response blocks by `type`, not array index. | `developer` > `user`. Put stable rules in first `developer` message in `input` for caching; use top-level `instructions` only for per-turn guidance (GPT-6.2+). Use Responses API (`v1/responses`), not Chat Completions, for agentic/tool flows. | `system_instruction` + turns. Put single images *before* text. |
| **Reasoning Control** | Adaptive thinking + `output_config.effort` (`low`..`max`). `budget_tokens` is deprecated on 4.6 and **HTTP 400 on 4.7+**. Always-on in Opus 5.5/Fable 5+. | `reasoning.effort` (`none`..`max`). Pin explicitly (`gpt-5.1/5.2` default `none`; `gpt-6.2` defaults `medium` and returns **HTTP 400** on `none`/`minimal`). | `thinking_level` (`minimal`, `low`, `medium`, `high`), replacing numeric `thinking_budget`. |
| **Breaking / Deprecated** | Assistant response prefilling returns **HTTP 400 on 4.6+**. Avoid the word `"think"` when thinking is disabled (Opus 4.5). | `v1/prompts` deprecated (shutdown Nov 2026)—version prompts in code. Omit `temperature`/`top_p`/`logprobs` on GPT-6.2+. Include `Formatting re-enabled` on line 1 of `developer` for o-series Markdown. | `temperature`, `top_p`, `top_k` deprecated/ignored in Gemini 3.6+/4 (future HTTP 400). |
| **Few-Shot** | **3–5** diverse canonical `<examples>` beat long edge-case lists. | Start **zero-shot** on reasoning models; add few-shot only if output contracts require it and match rules 100%. | Useful for format/scope regulation; keep examples strictly uniform. |
| **Eagerness & Output Quirks** | Opus 4.5/4.6 can over-engineer or over-spawn subagents—constrain scope. Opus 5 self-verifies by default (drop legacy verification boilerplate). Quote-first grounding (`<quotes>`) boosts 20k+ token retrieval. | Use `text.verbosity`. **GPT-6.2 Astra** is concise and overly deferential on legacy "always ask" rules—explicitly grant autonomy for safe local work and add persistence cues. Write final answers self-contained (UIs may collapse intermediate commentary). Verify patch tool outcomes with tests. | Concise by default. To break repetitive tool loops, instruct silent thoughts to begin with a 1-sentence progress & completion recap. State current date/cutoff for time-sensitive tasks. |
| **Project Memory** | `CLAUDE.md` (<200 lines) + `.claude/rules/` (`paths:`) + `MEMORY.md` (first 200 lines/25 KB). Native `AGENTS.md` fallback. Audit with `/doctor prompt-audit`. | `AGENTS.md` / `AGENTS.override.md` (root→CWD merge, 32 KiB cap). Contextual pointers > mandatory upfront doc reading. | `GEMINI.md` (global → workspace → subdirectory append; avoid cross-level contradictions). |

## Context & KV-Cache Engineering (Production Rules)

Apply the four pillars (**Write, Select, Compress, Isolate**) plus cache hygiene:
- **KV-cache stability (Manus):** Agents have ~100:1 input:output ratios (10× cost/TTFT impact). Avoid volatile timestamps at the prefix, serialize JSON keys deterministically, and mask tools rather than dynamically adding/removing them.
- **Restorable compression:** Drop bulky raw tool outputs early while keeping file paths/URLs so context can be re-fetched if needed; tune compaction for recall first, then precision.
- **Keep errors in context:** Leaving failed tool calls and stack traces visible prevents repeated mistakes.
- **Externalize state & isolate exploration:** Persist plans/progress in files (`todo.md`, `tests.json`) and isolate noisy search inside subagents that return bounded (1k–2k token) summaries.
- **Harness sanity test:** If upgrading to a stronger model does not improve your workflow, your prompts or scaffolding are over-constraining it.
