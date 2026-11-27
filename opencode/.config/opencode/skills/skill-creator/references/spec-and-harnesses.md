# Agent Skills Specification & Cross-Harness Matrix

Contents: Directory Layout · Frontmatter Schema · Progressive Disclosure · Cross-Harness Compatibility · Portability Rules

Use this reference when designing skill structure, frontmatter, invocation policy, or multi-harness distribution.

## Directory Layout (`agentskills.io`)

```text
skill-name/
├── SKILL.md           # Required (case-sensitive on Anthropic/spec)
├── scripts/           # Optional: deterministic executable CLI tools
├── references/        # Optional: focused on-demand docs (one level deep)
├── assets/            # Optional: static templates, schemas, lookup tables
└── agents/
    └── openai.yaml    # Optional (Codex-only): UI metadata, invocation policy, MCP deps
```

- Always use forward slashes (`scripts/<tool>.py`, `references/<topic>.md`), never backslashes.
- Keep references **one level deep** from `SKILL.md` (avoid `SKILL.md` → `a.md` → `b.md`, which causes partial reads).
- Add a **Table of Contents** (`Contents:` or heading list) to any reference file over **100 lines**.
- Exclude process/repo clutter (`README.md`, `CHANGELOG.md`, `INSTALLATION_GUIDE.md`) from the skill directory.

## Portable Frontmatter Schema (`agentskills.io`)

Cross-platform uploads (claude.ai, Anthropic Skills API, strict validators) accept **only these 6 top-level keys**—extra top-level keys cause a hard error:

| Field | Required | Constraints |
|---|---|---|
| `name` | **Yes** | 1–64 chars, lowercase `a-z0-9-`, no leading/trailing/`--`, no XML tags, no reserved words (`anthropic`, `claude`, `synced`, `anthropic-skills`). **Must match parent directory name.** |
| `description` | **Yes** | 1–1,024 chars, non-empty, no `<` or `>`. States *what* it does, *when* to use it (front-loaded), and *when NOT* to use it. |
| `license` | No | SPDX identifier (e.g., `Apache-2.0`) or reference to bundled license file. |
| `compatibility` | No | 1–500 chars. Runtime, system packages, or network requirements. Omit unless needed. |
| `metadata` | No | `Record<string, string>` free-form map (`author`, `version`, tool-scoped keys like `opencode/autoinvoke`). |
| `allowed-tools` | No | *(Experimental)* Space-separated pre-approved tool patterns. Syntax and enforcement vary by harness. |

## Progressive Disclosure Tiers

1. **Tier 1 — Metadata (~100 tokens/skill, always loaded):** Only `name` and `description` load at startup. Codex caps the total startup skill list at **≤2% of the context window** (or 8,000 chars) and truncates descriptions first.
2. **Tier 2 — `SKILL.md` body (<500 lines / <5,000 tokens, loaded on trigger):** Workflow router, decision boundaries, checklists, and Error Recovery table.
3. **Tier 3 — `scripts/`, `references/`, `assets/` (zero cost until used):** Executed scripts consume tokens only for stdout/stderr, not source code.

## Cross-Harness Compatibility Matrix

`.agents/skills/` (project) and `~/.agents/skills/` (user) have converged as the primary interoperable paths.

| Harness | Discovery Paths | Explicit Invoke | Key Extensions & Divergences |
|---|---|---|---|
| **Claude Code** | `.claude/skills/`, `~/.claude/skills/` | `/skill-name` | Top-level extensions: `when_to_use` (1,536-char combined cap), `disable-model-invocation`, `user-invocable`, `context: fork`, `agent`, `paths`, `model`, `effort`, `hooks`, `argument-hint`, `${CLAUDE_SKILL_DIR}`, `` !`cmd` `` load-time shell injection. API/claude.ai uploads reject non-spec keys. |
| **OpenAI Codex** | `.agents/skills/`, `~/.agents/skills/`, `/etc/codex/skills` | `$skill-name` / `/skills` | Keeps extensions out of `SKILL.md` in `agents/openai.yaml` (`interface`, `policy.allow_implicit_invocation`, `dependencies.tools`). Hosted API zip limits: 50 MB / 500 files / 25 MB uncompressed. |
| **VS Code / Copilot** | `.github/skills/`, `.claude/skills/`, `.agents/skills/`, `~/.copilot/skills/` | `/skill-name` | Supports `disable-model-invocation`, `user-invocable`, `argument-hint`, experimental `context: fork`, extension `chatSkills`, MCP-served skills. Invalid `name` chars silently fail to load. |
| **Cursor** | `.agents/skills/`, `.cursor/skills/`, `.claude/skills/`, `.codex/skills/` | `/skill-name` | Supports `paths` (replaces `globs`), `disable-model-invocation`, `icon`, `color`. Nested `.cursor/skills/` auto-scope to their subtree. |
| **OpenCode** | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`, `~/.config/opencode/skills/` | `@skill-id` or `skill` tool | Skill ID is **path-derived** (case-sensitive); frontmatter `name` is display-only. Reads `metadata.opencode/autoinvoke: false` (overrides `disable-model-invocation`). Granular permissions in `opencode.jsonc`. |
| **Gemini CLI** | `.agents/skills/` (precedence), `.gemini/skills/` | `activate_skill` | Prompts for **interactive user consent** before injecting `SKILL.md` and granting directory read access. |

## Portability Rules

- **Targeting multiple harnesses:** Stick strictly to the 6 `agentskills.io` keys in `SKILL.md`, put Codex extras in `agents/openai.yaml`, put OpenCode auto-invoke opt-out in `metadata.opencode/autoinvoke: false`, and store skills under `.agents/skills/`.
- **Targeting a single harness:** Harness-specific features (`context: fork`, `paths`, `` !`cmd` ``) are fine—document that requirement in `compatibility` and run `validate_skill.py --allow-harness-keys`.
- **Hosted / offline sandboxes:** Claude API code execution and OpenAI hosted shell disable open internet by default; write `scripts/` using stdlib only and declare any external tools in `compatibility`.
