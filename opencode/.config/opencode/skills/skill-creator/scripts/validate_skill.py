#!/usr/bin/env python3
"""
Deterministic Agent Skill validator & linter (pure Python 3 stdlib).

Checks agentskills.io specification compliance, progressive-disclosure budgets,
broken relative links, legacy prompt smells, and supply-chain security hazards.

Usage:
    python3 -B validate_skill.py <skill-directory> [--allow-harness-keys] [--strict]
    python3 -B validate_skill.py --self-test
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
HARNESS_KEYS = {
    "disable-model-invocation",
    "user-invocable",
    "when_to_use",
    "argument-hint",
    "arguments",
    "disallowed-tools",
    "model",
    "effort",
    "context",
    "agent",
    "background",
    "hooks",
    "paths",
    "shell",
    "icon",
    "color",
}
RESERVED_NAMES = {"anthropic", "claude", "synced", "anthropic-skills"}
CLUTTER_FILES = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"}

SECRET_PATTERNS = [
    ("OpenAI/Stripe-style key", re.compile(r"\bsk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

LEGACY_SMELLS = [
    ("prescriptive CoT ('think step by step')", re.compile(r"\bthink step[- ]by[- ]step\b", re.I)),
    ("aggressive emphasis ('CRITICAL: YOU MUST')", re.compile(r"\bCRITICAL:\s*YOU MUST\b")),
]

# Unicode Tag block (U+E0000..U+E007F) and Bidi override controls used in hidden prompt injection
BIDI_CODEPOINTS = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A)) | {0x200E, 0x200F, 0x061C}


def parse_frontmatter(text: str) -> tuple[dict[str, object] | None, str, str | None]:
    """Minimal stdlib YAML frontmatter parser supporting scalars, folded/literal blocks, and 1-level maps."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, text, "Missing YAML frontmatter starting with '---' on line 1."
    lines = text.splitlines()
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return None, text, "Unterminated YAML frontmatter (missing closing '---')."

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    data: dict[str, object] = {}
    i = 0
    while i < len(fm_lines):
        raw = fm_lines[i]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if raw[0].isspace():
            return None, body, f"Unexpected indentation on frontmatter line {i + 2}: {raw!r}"
        if ":" not in raw:
            return None, body, f"Invalid YAML line {i + 2} (missing ':'): {raw!r}"
        key, rest = raw.split(":", 1)
        key = key.strip()
        val = rest.strip()
        if not key:
            return None, body, f"Empty YAML key on line {i + 2}."

        # Block scalar (| or >)
        if val in ("|", ">", "|-", ">-", "|+", ">+"):
            block: list[str] = []
            i += 1
            while i < len(fm_lines) and (fm_lines[i].startswith((" ", "\t")) or fm_lines[i].strip() == ""):
                block.append(fm_lines[i])
                i += 1
            non_empty = [b for b in block if b.strip()]
            indent = min((len(b) - len(b.lstrip(" ")) for b in non_empty), default=0)
            cleaned = [b[indent:] if len(b) >= indent else "" for b in block]
            joined = " ".join(c.strip() for c in cleaned if c.strip()) if val.startswith(">") else "\n".join(cleaned)
            data[key] = joined.strip()
            continue

        # Nested map or list
        if val == "":
            nested: dict[str, str] = {}
            items: list[str] = []
            i += 1
            while i < len(fm_lines) and (fm_lines[i].startswith((" ", "\t")) or fm_lines[i].strip() == ""):
                sub = fm_lines[i].strip()
                i += 1
                if not sub or sub.startswith("#"):
                    continue
                if sub.startswith("- "):
                    items.append(sub[2:].strip().strip("\"'"))
                elif ":" in sub:
                    sk, sv = sub.split(":", 1)
                    nested[sk.strip()] = sv.strip().strip("\"'")
            data[key] = items if items and not nested else (nested if nested else "")
            continue

        # Inline scalar (strip matching quotes)
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        data[key] = val
        i += 1

    return data, body, None


def find_hidden_unicode(text: str) -> list[str]:
    hits: list[str] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for ch in line:
            cp = ord(ch)
            if 0xE0000 <= cp <= 0xE007F:
                hits.append(f"line {line_no}: Unicode Tag character U+{cp:05X}")
                break
            if cp in BIDI_CODEPOINTS:
                hits.append(f"line {line_no}: Bidi control character U+{cp:04X}")
                break
    return hits


def is_text_file(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\x00" not in sample


def validate_skill(skill_dir: Path, allow_harness_keys: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not skill_dir.exists() or not skill_dir.is_dir():
        return [f"Skill directory not found: {skill_dir}"], []

    # Case-sensitive SKILL.md check (macOS filesystems are often case-insensitive)
    top_entries = {p.name for p in skill_dir.iterdir()}
    if "SKILL.md" not in top_entries:
        errors.append("Missing required 'SKILL.md' (exact uppercase filename required).")
        return errors, warnings

    skill_md = skill_dir / "SKILL.md"
    raw = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body, parse_err = parse_frontmatter(raw)
    if parse_err or fm is None:
        errors.append(parse_err or "Failed to parse frontmatter.")
        return errors, warnings

    allowed = SPEC_KEYS | (HARNESS_KEYS if allow_harness_keys else set())
    unexpected = sorted(set(fm.keys()) - allowed)
    if unexpected:
        errors.append(
            f"Unexpected frontmatter key(s): {', '.join(unexpected)}. "
            f"Allowed spec keys: {', '.join(sorted(SPEC_KEYS))} "
            "(pass --allow-harness-keys for harness-specific top-level keys)."
        )

    # Validate name
    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("Missing or empty required frontmatter field: 'name'.")
    else:
        name = name.strip()
        if len(name) > 64:
            errors.append(f"'name' exceeds 64 chars ({len(name)}).")
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"'name' ({name!r}) must use lowercase letters, digits, and hyphens only.")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append(f"'name' ({name!r}) cannot start/end with '-' or contain '--'.")
        if name in RESERVED_NAMES:
            errors.append(f"'name' ({name!r}) is a reserved identifier.")
        if name != skill_dir.name:
            errors.append(f"'name' ({name!r}) must match parent directory name ({skill_dir.name!r}).")

    # Validate description
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append("Missing or empty required frontmatter field: 'description'.")
    else:
        desc = desc.strip()
        if len(desc) > 1024:
            errors.append(f"'description' exceeds 1,024 chars ({len(desc)}).")
        if "<" in desc or ">" in desc:
            errors.append("'description' must not contain angle brackets (< or >).")
        if re.search(r"\b(I can|I will|You can|You should)\b", desc):
            warnings.append("'description' uses first/second person; write routing logic in third-person or imperative.")
        if not re.search(r"\b(do not|don't|never|not for|outside|except)\b", desc, re.I):
            warnings.append("'description' has no explicit negative trigger ('Do not use when...').")

    # Validate compatibility if present
    compat = fm.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str) or not (1 <= len(compat.strip()) <= 500):
            errors.append("'compatibility' must be a non-empty string up to 500 chars.")

    # Progressive disclosure & budget checks
    total_lines = len(raw.splitlines())
    if total_lines > 500:
        warnings.append(f"SKILL.md is {total_lines} lines (recommended <500; move detail into references/).")

    # Check relative file paths & Windows backslashes in SKILL.md (outside fenced blocks)
    non_code_lines = []
    in_fence = False
    for ln in body.splitlines():
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            non_code_lines.append(ln)
    non_code_body = "\n".join(non_code_lines)

    if re.search(r"(?:scripts|references|assets)\\[A-Za-z0-9._-]+", non_code_body):
        errors.append("SKILL.md contains Windows backslash paths; use forward slashes.")

    rel_refs = sorted(
        set(re.findall(r"(?<![A-Za-z0-9_/-])((?:scripts|references|assets)/[A-Za-z0-9._/-]+\.[A-Za-z0-9]+)", non_code_body))
    )
    for ref in rel_refs:
        ref_clean = ref.rstrip(".,;:)`\"'")
        if "*" in ref_clean or "<" in ref_clean:
            continue
        if not (skill_dir / ref_clean).exists():
            errors.append(f"SKILL.md references missing local path: {ref_clean}")

    # Legacy 2023 prompt smells
    for label, pat in LEGACY_SMELLS:
        for ln in non_code_lines:
            if pat.search(ln) and not re.search(r"\b(skip|avoid|drop|do not|don't|legacy|retired)\b", ln, re.I):
                warnings.append(f"SKILL.md contains legacy prompt pattern: {label}.")
                break

    # Clutter & .mcp.json checks
    for clutter in sorted(CLUTTER_FILES & top_entries):
        warnings.append(f"Extraneous doc file in skill directory: {clutter} (keep only agent-needed files).")
    if ".mcp.json" in top_entries:
        warnings.append("Bundled '.mcp.json' detected; prefer Code Mode scripts over preloading MCP tool suites.")

    # Check references/ files (>100 lines need TOC; avoid nested references)
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        for ref_file in sorted(refs_dir.rglob("*.md")):
            rtext = ref_file.read_text(encoding="utf-8", errors="replace")
            rlines = rtext.splitlines()
            rel = ref_file.relative_to(skill_dir).as_posix()
            if len(rlines) > 100:
                head = "\n".join(rlines[:15])
                if not re.search(r"(?:^Contents:|^##?\s*Table of Contents|^\s*-\s*\[.+\]\(#)", head, re.I | re.M):
                    warnings.append(f"{rel} is {len(rlines)} lines (>100) without a top Table of Contents / 'Contents:' line.")
            nested = re.findall(r"(?<![A-Za-z0-9_/-])(references/[A-Za-z0-9._/-]+\.md)", rtext)
            if nested:
                warnings.append(f"{rel} links to nested reference(s): {', '.join(sorted(set(nested)))} (keep references 1 level deep).")

    # Security scan across all text files in skill directory
    for fpath in sorted(skill_dir.rglob("*")):
        if not fpath.is_file() or "__pycache__" in fpath.parts:
            continue
        if not is_text_file(fpath):
            continue
        rel = fpath.relative_to(skill_dir).as_posix()
        ftext = fpath.read_text(encoding="utf-8", errors="replace")
        for hit in find_hidden_unicode(ftext):
            errors.append(f"Security: hidden/bidi Unicode in {rel} ({hit}).")
        # Skip secret-regex self-matches on this validator itself
        if fpath.resolve() == Path(__file__).resolve():
            continue
        for label, pat in SECRET_PATTERNS:
            if pat.search(ftext):
                errors.append(f"Security: possible hardcoded {label} in {rel}.")

    return errors, warnings


def run_self_test() -> int:
    """Assert-based self-check covering valid skills, spec errors, security hazards, and warnings."""
    with tempfile.TemporaryDirectory(prefix="skill-val-test-") as tmp:
        root = Path(tmp)

        # 1. Valid skill passes cleanly
        ok = root / "good-skill"
        (ok / "references").mkdir(parents=True)
        (ok / "SKILL.md").write_text(
            "---\n"
            "name: good-skill\n"
            "description: Validates widgets. Use when checking widget specs. Do not use for unrelated tasks.\n"
            "---\n\n"
            "# Good Skill\n\nSee references/guide.md.\n",
            encoding="utf-8",
        )
        (ok / "references" / "guide.md").write_text("# Guide\n\nShort.\n", encoding="utf-8")
        errs, warns = validate_skill(ok)
        assert not errs and not warns, f"Expected clean pass, got errs={errs}, warns={warns}"

        # 2. Bad frontmatter, broken link, hidden Unicode tag, and .mcp.json fail properly
        bad = root / "bad-skill"
        bad.mkdir()
        (bad / ".mcp.json").write_text("{}", encoding="utf-8")
        (bad / "SKILL.md").write_text(
            "---\n"
            "name: wrong-name\n"
            "description: I can help with stuff\n"
            "extra-key: nope\n"
            "---\n\n"
            "See references/missing.md\n"
            f"Hidden: {chr(0xE0041)}\n",
            encoding="utf-8",
        )
        errs, warns = validate_skill(bad)
        assert any("Unexpected frontmatter key" in e for e in errs), errs
        assert any("must match parent directory" in e for e in errs), errs
        assert any("missing local path" in e for e in errs), errs
        assert any("Unicode Tag" in e for e in errs), errs
        assert any(".mcp.json" in w for w in warns), warns
        assert any("negative trigger" in w for w in warns), warns

    print("PASS: validate_skill.py self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Agent Skill directory against 2026 standards.")
    parser.add_argument("skill_dir", nargs="?", help="Path to skill directory containing SKILL.md")
    parser.add_argument("--allow-harness-keys", action="store_true", help="Allow harness-specific top-level frontmatter keys")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--self-test", action="store_true", help="Run built-in validator self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.skill_dir:
        parser.error("Provide <skill_dir> or --self-test.")

    target = Path(args.skill_dir).expanduser().resolve()
    errors, warnings = validate_skill(target, allow_harness_keys=args.allow_harness_keys)

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")

    failed = bool(errors) or (args.strict and bool(warnings))
    if not failed:
        print(f"OK: {target.name} passed validation ({len(warnings)} warning(s)).")
        return 0
    print(f"FAIL: {target.name} failed validation ({len(errors)} error(s), {len(warnings)} warning(s)).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
