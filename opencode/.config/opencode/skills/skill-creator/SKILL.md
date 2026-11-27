---
name: skill-creator
description: Author, audit, refactor, and evaluate Agent Skills (SKILL.md), bundled scripts/references, and agent prompts using 2026 cross-lab standards. Use when creating a new skill, updating or auditing an existing skill, optimizing skill descriptions or triggers, writing skill evals, or deciding between AGENTS.md/CLAUDE.md, rules, hooks, and skills. Do not use for general software coding unrelated to skills, prompts, or agent configuration.
---

# Skill Creator

Build minimal, eval-backed, portable Agent Skills (`SKILL.md`) and clean agent prompts aligned with `agentskills.io`, Anthropic, OpenAI, Google, and production harness practices.

## Reference Playbooks (Read Only What You Need)

Read at `<base-directory>/<path>`:

| Need | File |
|---|---|
| 2026 prompting hygiene, model quirks (Claude 4.6–5.x, GPT-5–6.2, Gemini 2.5–4), KV-cache & context rules | `references/prompting-and-models.md` |
| `agentskills.io` 6-key schema, progressive disclosure, cross-harness matrix (Claude Code, Codex, Copilot, Cursor, OpenCode, Gemini CLI) | `references/spec-and-harnesses.md` |
| Trigger/trajectory/ablation evals, cost optimization (Code Mode, worker subagents), Lethal Trifecta & supply-chain security | `references/evals-and-security.md` |

## Workflow

Follow these steps in order; verify each step before moving to the next.

### 1. Decide Whether It Should Be a Skill

Skills are **not** a drop-in replacement for always-on project rules. Vercel's evals showed a compact `AGENTS.md` index beat Skills (100% vs. 79%) because agents skipped invoking the skill 56% of the time; SkillsBench showed 16/84 tasks suffered negative transfer from over-prescriptive or poorly scoped skills.

| Mechanism | Use When | Budget / Scope |
|---|---|---|
| `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` | Facts, build/test commands, repo maps, or compact doc indexes needed in nearly every session | Always loaded; keep **<200 lines** |
| Path-scoped rules (`.claude/rules/`, `.instructions.md`, `paths:`) | Conventions tied to a directory, language, or file glob (`src/**/*.tsx`) | Loaded only on matching paths |
| **Agent Skill (`SKILL.md`)** | Multi-step specialized workflows, domain runbooks, templates, or deterministic helper scripts | Tier 1 metadata always loaded (~100 tokens); body on trigger |
| **Manual-only Skill** (`disable-model-invocation: true` / `allow_implicit_invocation: false`) | Side-effecting or explicit workflows (`/deploy`, `/commit`, `/release`) | Zero startup cost; user-triggered only |
| Hooks / CI / Permissions | Hard invariants (linting, formatting, secret blocking, approval gates) | Deterministic; never rely on prose alone |
| Subagents (`context: fork`) | Noisy exploration, adversarial review, or long-running polling | Isolated context; returns bounded summary |

**Done when:** You have confirmed a Skill (and whether auto-invoked or manual-only) is the right primitive. If `AGENTS.md`, a path rule, or a hook fits better, recommend that instead and stop.

### 2. Establish a Baseline and Spec First

Self-generated skills written without real domain artifacts yield ~0 net gain (SkillsBench). Never start by asking an LLM to invent generic best practices.

1. Gather 3+ concrete examples of real tasks, runbooks, PR feedback, or failure traces.
2. Run (or inspect) those tasks **without the skill** to find where the model actually fails. Write only what fixes observed failures.
3. Capture a concise spec before authoring `SKILL.md`:
   - **Goal & checkable definition of done**
   - **Required & forbidden tool actions** (including side-effect gates)
   - **Target harnesses & model tiers** (e.g., OpenCode + Claude Code + Codex; small vs. flagship models)
   - **Explicit out-of-scope triggers** (near-miss tasks that must NOT load this skill)

**Done when:** You have observed failure modes and a concrete spec with negative triggers.

### 3. Design Progressive Disclosure & Cost Levers

Keep the context window lean—every line loaded into a session is re-paid on every subsequent turn.

```text
skill-name/
├── SKILL.md           # Required (case-sensitive): YAML frontmatter + concise router (<500 lines)
├── scripts/           # Optional: deterministic CLI utilities (stdout only enters context)
├── references/        # Optional: focused on-demand docs (one level deep; TOC if >100 lines)
├── assets/            # Optional: static templates, schemas, lookup tables
└── agents/openai.yaml # Optional (Codex-only): UI metadata, invocation policy, MCP deps
```

Rules:
- **Assume the model is smart.** Cut explanations of fundamentals the model already knows; keep non-obvious repo/domain rules, **Gotchas**, and decision boundaries.
- **Keep `SKILL.md` under 500 lines.** Split variant/domain details into `references/*.md` linked **one level deep** from `SKILL.md` (never `SKILL.md` → `a.md` → `b.md`). Add a 1-line `Contents:` TOC to any reference file over 100 lines.
- **Give one default, not a menu.** Pick one recommended tool/library and add a brief escape hatch for edge cases.
- **Match degrees of freedom to task fragility:**
  - *High freedom* (heuristics/criteria) for flexible tasks (reviews, synthesis).
  - *Medium freedom* (templates/pseudocode) for preferred patterns.
  - *Low freedom* (exact scripts/commands) for fragile ops (migrations, billing, releases).
- **Prefer Code Mode scripts over preloaded MCPs.** Preloading large MCP tool suites burns 50k–70k tokens upfront; prefer small utility scripts in `scripts/` that call gateways/APIs and emit bounded stdout or write to files. Avoid bundling `.mcp.json` inside skills.
- **Avoid extraneous clutter:** Do not add `README.md`, `CHANGELOG.md`, or `INSTALLATION_GUIDE.md` inside a skill directory.

**Done when:** You have mapped which content belongs in `SKILL.md` vs. `references/`, `assets/`, and `scripts/`.

### 4. Author `SKILL.md`, References, and Scripts

Read `references/spec-and-harnesses.md` if targeting multiple harnesses, and `references/prompting-and-models.md` before writing complex instructions.

1. **Frontmatter (strictly portable by default):**
   - Use only the 6 `agentskills.io` keys (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`) unless the user specifically requests harness-native top-level flags (e.g., Claude Code `context: fork`, `paths`). For OpenCode manual-only skills, prefer `metadata: { opencode/autoinvoke: false }` to preserve strict 6-key portability.
   - `name`: 1–64 chars, lowercase `a-z0-9-`, must match parent directory name, no reserved words (`anthropic`, `claude`).
   - `description`: 1–1,024 chars, no `<` or `>`, written as **routing logic** (never first/second person). Front-load the primary use case (harnesses truncate long descriptions), list concrete user intents/triggers, and state **"Do not use for..."** negative triggers.
2. **Body instructions:**
   - Use numbered steps, each with one clear objective and a checkable verification/done condition.
   - Explain the *why* behind non-obvious constraints; prefer positive framing; eliminate contradictory rules across sections.
   - Skip legacy 2023 prompt tricks ("think step by step", `CRITICAL: YOU MUST`, accuracy-boosting personas).
   - Include concrete **Gotchas**, reusable templates/checklists, and a concrete **Error Recovery** table (specific failure → exact fix; never *"try again"*).
   - Distinguish execution vs. reading explicitly: *"Run `scripts/validate_skill.py`"* vs. *"Read `references/spec-and-harnesses.md`"*. Use forward slashes everywhere.
3. **Bundled scripts (`scripts/`):**
   - Default to instruction-only; add scripts only for deterministic checks, parsing, or repeated boilerplate.
   - Build scripts as self-contained CLIs (prefer stdlib so they run in offline/clean-room sandboxes without `pip`/`npm` install), fail loudly with actionable error messages, comment non-obvious constants, and test every script by running it directly.

**Done when:** `SKILL.md`, needed references/assets, and tested scripts are written on disk.

### 5. Validate & Audit Security

Run the bundled validator CLI against the target skill directory (do not read the script source unless editing it):

```bash
python3 -B <base-directory>/scripts/validate_skill.py <path/to/skill-dir>
```

Pass `--allow-harness-keys` if the skill intentionally uses harness-specific top-level frontmatter keys (e.g., Claude Code `disable-model-invocation`, `context`, `paths`), or `--strict` to fail on warnings too.

Then complete a manual security pass (see `references/evals-and-security.md`):
- Verify untrusted external content cannot steer **privileged external side effects or shell-based exfiltration** (the **Lethal Trifecta**). Do not flag standard read-only documentation lookups (`webfetch`/`websearch`) on no-shell, secret-redacted local developer agents, or wildcard tool permissions intentionally shared with user-invoked commands on primary-capable (`mode: all`) agents without verifying how users invoke them.
- Confirm side-effecting workflows are gated manual-only and contain zero hardcoded secrets.
- Audit all bundled scripts and third-party snippets for prompt injection, broad `allowed-tools`, or unsafe shell interpolation.

**Done when:** `validate_skill.py` exits `0` with all errors resolved and security checks pass.

### 6. Evaluate, Ablate, and Iterate

Read `references/evals-and-security.md` for full eval templates. At minimum:

1. **Trigger & negative-control test:** Prepare 10–20 realistic prompts covering explicit invocation, implicit invocation, noisy context, and **near-miss negatives** (`should_trigger=false`). When tuning descriptions, use a **60/40 train/validation split** across ~3 runs per prompt to avoid keyword overfitting.
2. **Clean-room & fresh-session check:** Test the skill in a clean session (and ideally an isolated sandbox/repo) to catch hidden local path/tool assumptions and verify the agent actually reads the right references without thrashing.
3. **Cross-tier & ablation check:** Verify across small and flagship models. Replay tasks *with vs. without* the skill (and with verbose sections trimmed) to confirm net gain; prune bloat or retire skills as models outgrow them.

**Done when:** Trigger accuracy, clean-room execution, and baseline-vs-skill improvement are verified.

## Error Recovery

| Failure | Fix |
|---|---|
| `validate_skill.py` reports unexpected frontmatter keys | Move harness-only flags under `metadata:` (e.g., `metadata.opencode/autoinvoke: false`) for strict `agentskills.io` portability, or re-run with `--allow-harness-keys` if targeting a single harness. |
| Skill fails to auto-trigger on target prompts | Front-load user intent and concrete keywords in sentence 1 of `description`, shorten total length to avoid truncation, and verify `metadata.opencode/autoinvoke` / `disable-model-invocation` isn't disabling it. If always needed, move a compact index into `AGENTS.md`/`CLAUDE.md` instead. |
| Skill false-triggers on unrelated prompts | Add explicit `"Do not use for..."` negative triggers to `description` and re-test against near-miss negative queries. |
| Agent ignores a linked `references/*.md` file | Ensure the link is one level deep directly from `SKILL.md`, state explicitly *when* to read it, and add a `Contents:` TOC if the file exceeds 100 lines. |
| Script fails in hosted or clean-room sandbox | Replace third-party dependencies with stdlib, remove runtime network/install assumptions, and emit actionable stderr with non-zero exit codes. |
| Skill hurts quality or adds latency vs. baseline | Run word/module ablation: cut over-prescriptive step-by-step recipes (especially for GPT-6.2 Astra / Claude 5+), keep only non-obvious constraints, Gotchas, and deterministic validators. |
