#!/usr/bin/env python3
"""
Validate commits against conventional commit specification.

Usage:
    python3 validate-commits.py [--range RANGE] [--config CONFIG]

Examples:
    python3 validate-commits.py                    # Check all commits
    python3 validate-commits.py --range origin/main..HEAD    # Check commits since main
"""

import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
import toml
import yaml

CONVENTIONAL_TYPES = {
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "chore",
}


class CommitValidator:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_commitlint_config()
        self.allowed_types = self.config.get("types", list(CONVENTIONAL_TYPES))
        self.require_scope = self.config.get("require_scope", False)
        self.max_header_length = self.config.get("max_header_length", 50)
        self.max_body_length = self.config.get("max_body_length", 72)

    def _load_commitlint_config(self) -> Dict[str, Any]:
        """Load commitlint config from various sources."""
        # Check for commitlint.config.js, .commitlintrc, etc.
        config_files = [
            ".commitlintrc.json",
            ".commitlintrc.yaml",
            ".commitlintrc.yml",
            "commitlint.config.js",
            "pyproject.toml",
        ]

        for config_file in config_files:
            path = Path(config_file)
            if not path.exists():
                continue

            try:
                if config_file.endswith(".json"):
                    with open(path) as f:
                        return json.load(f)
                elif config_file.endswith((".yaml", ".yml")):
                    with open(path) as f:
                        data = yaml.safe_load(f)
                        return data.get("commitlint", {})
                elif config_file == "pyproject.toml":
                    data = toml.load(path)
                    return data.get("tool", {}).get("commitlint", {})
            except Exception:
                continue

        return {}

    def validate_commit(self, commit_hash: str, message: str) -> Dict[str, Any]:
        """Validate a single commit message."""
        lines = message.strip().split("\n")
        if not lines:
            return {
                "commit": commit_hash,
                "valid": False,
                "errors": ["Commit message is empty"],
                "warnings": [],
            }

        header = lines[0]
        errors = []
        warnings = []

        # Parse header
        pattern = r"^([a-z]+)(\(.+?\))?(!)?:\s+(.+)$"
        match = re.match(pattern, header)

        if not match:
            errors.append(f"Invalid header format: {header}")
        else:
            commit_type, scope, breaking, subject = match.groups()

            # Check type
            if commit_type not in self.allowed_types:
                errors.append(
                    f"Invalid type '{commit_type}'. Allowed: {', '.join(sorted(self.allowed_types))}"
                )

            # Check scope requirement
            if self.require_scope and not scope:
                errors.append("Scope is required")

            # Check subject length
            if not subject or len(subject) < 1:
                errors.append("Subject cannot be empty")

            # Check header length
            if len(header) > self.max_header_length:
                warnings.append(
                    f"Header length {len(header)} exceeds recommended {self.max_header_length}"
                )

        # Check header length (always warn)
        if len(header) > self.max_header_length:
            if len(header) > self.max_header_length * 1.5:
                errors.append(
                    f"Header too long ({len(header)} > {self.max_header_length})"
                )
            elif not any("Header length" in w for w in warnings):
                warnings.append(
                    f"Header length {len(header)} exceeds recommended {self.max_header_length}"
                )

        # Check body lines
        if len(lines) > 1:
            # There should be a blank line between header and body
            if lines[1].strip() != "":
                warnings.append("Blank line expected between header and body")

            # Check body line lengths
            for i, line in enumerate(lines[2:], 3):
                if line and len(line) > self.max_body_length:
                    warnings.append(
                        f"Line {i} length {len(line)} exceeds recommended {self.max_body_length}"
                    )

        return {
            "commit": commit_hash,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "message": message,
        }

    def validate_range(self, commit_range: str) -> List[Dict[str, Any]]:
        """Validate all commits in a range."""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--format=%H%n%B%n---END---", commit_range],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return []

            commits = []
            lines = result.stdout.split("\n")
            i = 0
            while i < len(lines):
                if lines[i].startswith("commit "):
                    commit_hash = lines[i].split()[1]
                    i += 1
                    message_lines = []
                    while i < len(lines) and lines[i] != "---END---":
                        message_lines.append(lines[i])
                        i += 1
                    message = "\n".join(message_lines).strip()
                    commits.append(self.validate_commit(commit_hash, message))
                i += 1

            return commits
        except Exception as e:
            return [{"error": str(e)}]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate conventional commits")
    parser.add_argument(
        "--range", default="HEAD~10..HEAD", help="Commit range to check"
    )
    parser.add_argument("--config", help="Path to commitlint config")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--summary", action="store_true", help="Show summary only")

    args = parser.parse_args()

    config = {}
    if args.config and Path(args.config).exists():
        try:
            with open(args.config) as f:
                config = json.load(f)
        except Exception:
            pass

    validator = CommitValidator(config)
    results = validator.validate_range(args.range)

    if not results:
        print("No commits found in range", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    elif args.summary:
        total = len(results)
        valid = sum(1 for r in results if r.get("valid", False))
        print(f"Summary: {valid}/{total} commits valid")
    else:
        for result in results:
            if result.get("valid"):
                print(f"✓ {result['commit'][:8]}")
            else:
                print(f"✗ {result['commit'][:8]}")
                for error in result.get("errors", []):
                    print(f"  Error: {error}")
                for warning in result.get("warnings", []):
                    print(f"  Warning: {warning}")

    # Exit with error if any commits invalid
    if any(not r.get("valid", False) for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
