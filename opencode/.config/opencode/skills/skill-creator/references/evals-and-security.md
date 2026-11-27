# Skill Evaluation, Cost Optimization & Security Reference

Contents: Trigger & Task Evals · Production Eval Mix & Ablation · Cost & Token Efficiency · Security & Supply-Chain Threat Model

Use this reference when designing skill test suites, optimizing token/cost overhead, or auditing skills for security.

## Trigger & Task Evals (Before Shipping)

Build a **10–20 prompt** dataset across four buckets (OpenAI / `agentskills.io`):

| Bucket | Count | Purpose |
|---|---|---|
| **Explicit invocation** (`/skill`, `$skill`, `@skill`) | 2–3 | Confirm workflow executes end-to-end when directly invoked. |
| **Implicit invocation** (target scenario, skill unnamed) | 4–6 | Confirm `description` triggers on natural user intent. |
| **Contextual / noisy prompts** | 2–3 | Confirm resilience with realistic extra domain context. |
| **Near-miss negative controls** (`should_trigger=false`) | 4–8 | Catch false positives on adjacent topics. |

Rules:
- Run each trigger query **~3×**; use a **60/40 train/validation split** when iterating on `description` to prevent keyword overfitting.
- Adding explicit `"Don't use when..."` negative examples recovered a ~20% trigger drop and raised accuracy from **73% → 85%** while cutting TTFT by **18.1%** (OpenAI / Glean production data).
- Use a **fresh session ("Two-Claude loop")** to test: author in Session A, run in clean Session B, inspect which references were ignored, over-read, or caused thrashing, and feed observations back.

## Production Eval Mix, Clean-Room & Ablation (Uber / OpenAI)

1. **Two-tier grading:**
   - **Deterministic trace graders:** Parse JSONL execution traces (`command_execution`, tool calls, exit codes, artifacts written, command-count thrashing, token budget, clean `git status`).
   - **Qualitative rubric graders:** Separate read-only LLM judge outputting strict JSON against a human-calibrated rubric.
2. **Production eval composition (Uber, 1M+ monthly invocations):**
   - **5% golden cases** (fixed input + expected output with mocked tools)
   - **80% real prompts graded on trajectory** (right skills, tools, and error-recovery steps in order)
   - **15% author-judged** (calibrates LLM-as-judge)
   - Treat **70–90% pass rates** as healthy signal on non-deterministic suites; 100% often indicates an eval too weak to catch real regressions.
3. **Clean-room remote testing:** Run evals in isolated sandboxes/containers—not only the author's laptop—to expose hidden local paths, cached docs, and OS tool dependencies.
4. **Word & whole-skill ablation:** Replay real prompts *with vs. without* the skill (and with sections trimmed) under a blind judge. Keep skills that deliver non-guessable domain/internal capability; trim verbose recipes and retire skills as newer models outgrow them.
5. **Closed-loop self-healing ("Papercuts"):** Capture agent-reported friction (broken flags, silent 0-exit errors, thrashing retries) and rejected/commented human PRs as new regression cases in the eval suite.

## Cost & Token Efficiency Levers

Every skill's instructions and tool results sit in context and are re-paid on every subsequent turn. Four proven levers (Uber Engineering):

1. **Code Mode over preloaded MCPs:** Preloading 100+ MCP tool definitions costs 50k–70k tokens before the user types. Replace repeated tool calls with small utility scripts in `scripts/` calling a gateway/CLI and writing large results to files; **avoid `.mcp.json` inside skills/plugins**.
2. **Cheap-model worker subagents:** Dispatch noisy lookup or tracing skills to a smaller model so bulky outputs stay out of the main context (46% cost reduction observed on tracing; always measure before/after).
3. **Load-time script execution:** When a small, deterministic snippet is always needed, inject its output at load time (e.g., Claude Code `` !`cmd` ``) to eliminate a model turn (32% lower mean cost observed on search).
4. **Move polling out of the main session:** Polling/notification turns can drive ~1/3 of spend in long sessions; offload monitoring (e.g., CI watch) to a cheap background agent.

## Security & Supply-Chain Threat Model

Public skill ecosystems carry high real-world risk (Snyk ToxicSkills Feb 2026: **36.8%** of 3,984 audited skills had flaws, **13.4%** critical, 76 malicious; ClawHavoc delivered macOS stealers via `SKILL.md` "Prerequisites" social engineering; Skill-Inject showed natural-language and invisible Unicode prompt injections evade static scanners).

**Mandatory Defenses:**
1. **Break the Lethal Trifecta / Rule of Two (real abuse paths only):** Never combine **(1) private data/secret access + (2) untrusted external content + (3) privileged external writes, credentialed messaging (email/Slack/webhooks/uploads), or shell-driven exfiltration** without per-action human approval. Distinguish untrusted third-party skills and headless/external-facing agents from **first-party local developer workflows**: read-only web doc lookup (`webfetch`/`websearch`) on a no-shell, secret-redacted local agent is not a Lethal Trifecta violation by itself.
2. **Restrict network with shell:** Skills + Shell + Open Network = exfiltration. Disable network in sandboxes or enforce two-layer allowlists (org allowlist + narrow per-request policy) whenever a skill runs shell/scripts over untrusted inputs.
3. **Zero raw secrets in skills or context:** Never hardcode tokens/keys in `SKILL.md`, `references/`, or `scripts/`. Inject credentials outside model context (e.g., `domain_secrets` / env placeholders).
4. **Gate side effects:** Set `disable-model-invocation: true` (or `metadata.opencode/autoinvoke: false` / `allow_implicit_invocation: false`) on any skill that deploys, commits, sends messages, or mutates external state.
5. **Audit the entire directory & verify intended tool scope:** Inspect `SKILL.md`, every script, hidden files, hidden Unicode (tags/bidi overrides), `.mcp.json`, and `allowed-tools` scope (Claude Code honors repo `allowed-tools` even in `-p` runs). Before flagging a wildcard or extra tool permission on an agent as an over-grant, check whether the agent is primary-capable (`mode: all`) and intentionally supports user-invoked commands using those tools. Pin third-party skill versions and run untrusted scripts only in external sandboxes.
