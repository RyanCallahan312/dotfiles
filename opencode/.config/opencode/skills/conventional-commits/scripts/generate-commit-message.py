#!/usr/bin/env python3
"""
Generate a conventional commit message from git diff or user input.

Usage:
    python3 generate-commit-message.py [--type TYPE] [--scope SCOPE] [--breaking] [--summary SUMMARY]

Example:
    python3 generate-commit-message.py --type feat --scope auth --summary "add JWT token refresh"
    python3 generate-commit-message.py --type fix --scope api --breaking --summary "change API response format"
"""

import sys
import json
import subprocess
import re
from typing import Optional
from pathlib import Path

CONVENTIONAL_TYPES = {
    "feat": "A new feature",
    "fix": "A bug fix",
    "docs": "Documentation only changes",
    "style": "Changes that do not affect code meaning (formatting, semicolons, etc.)",
    "refactor": "Code change that neither fixes a bug nor adds a feature",
    "perf": "Code change that improves performance",
    "test": "Adding missing tests or correcting existing tests",
    "chore": "Changes to build process, dependencies, or tooling",
}


def get_git_diff() -> str:
    """Get the current git diff to analyze changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True, check=False
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def infer_commit_type(diff: str) -> str:
    """Infer commit type from diff content (heuristic)."""
    if not diff:
        return "chore"

    # Simple heuristics
    if re.search(r"\b(test|spec)\b.*\.js", diff):
        return "test"
    if re.search(r"(\.md|README)", diff):
        return "docs"
    if any(marker in diff for marker in ["^@@", "- ", "+ "]):
        # Check if it's mostly additions (new feature) or modifications (fix/refactor)
        lines = diff.split("\n")
        added = len([l for l in lines if l.startswith("+")])
        removed = len([l for l in lines if l.startswith("-")])
        return "feat" if added > removed * 1.5 else "fix"
    return "chore"


def format_commit_message(
    commit_type: str,
    scope: Optional[str],
    summary: str,
    body: Optional[str] = None,
    breaking: bool = False,
    breaking_description: Optional[str] = None,
) -> str:
    """Format a complete conventional commit message."""

    # Build the header
    header = commit_type
    if scope:
        header += f"({scope})"
    if breaking:
        header += "!"
    header += f": {summary}"

    # Build the full message
    message = header
    if body:
        message += f"\n\n{body}"
    if breaking and breaking_description:
        message += f"\n\nBREAKING CHANGE: {breaking_description}"

    return message


def validate_commit_message(message: str) -> tuple[bool, str]:
    """Validate commit message format."""
    lines = message.split("\n")
    if not lines:
        return False, "Commit message is empty"

    header = lines[0]

    # Check header format: type(scope)?: subject OR type(scope)!: subject
    pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?!?: .+$"
    if not re.match(pattern, header):
        return False, f"Invalid header format: {header}"

    # Check header length (convention: <= 50 chars)
    if len(header) > 50:
        return False, f"Header too long ({len(header)} chars, max 50)"

    # Check body lines (convention: <= 72 chars)
    for i, line in enumerate(lines[1:], 1):
        if line and len(line) > 72:
            return False, f"Line {i + 1} too long ({len(line)} chars, max 72)"

    return True, "Valid"


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate conventional commit messages"
    )
    parser.add_argument(
        "--type", help="Commit type", choices=list(CONVENTIONAL_TYPES.keys())
    )
    parser.add_argument("--scope", help="Commit scope (optional)")
    parser.add_argument("--summary", required=True, help="Commit summary (required)")
    parser.add_argument("--body", help="Commit body (optional)")
    parser.add_argument(
        "--breaking", action="store_true", help="Mark as breaking change"
    )
    parser.add_argument("--breaking-description", help="Description of breaking change")
    parser.add_argument("--infer", action="store_true", help="Infer type from git diff")
    parser.add_argument("--validate", help="Validate a commit message")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Handle validation mode
    if args.validate:
        is_valid, message = validate_commit_message(args.validate)
        output = {
            "valid": is_valid,
            "message": message,
            "details": {"message": args.validate},
        }
        print(json.dumps(output, indent=2))
        sys.exit(0 if is_valid else 1)

    # Determine commit type
    commit_type = args.type
    if not commit_type:
        if args.infer:
            diff = get_git_diff()
            commit_type = infer_commit_type(diff)
        else:
            commit_type = "chore"

    # Format the message
    message = format_commit_message(
        commit_type=commit_type,
        scope=args.scope,
        summary=args.summary,
        body=args.body,
        breaking=args.breaking,
        breaking_description=args.breaking_description,
    )

    # Validate
    is_valid, validation_msg = validate_commit_message(message)

    if args.json:
        output = {
            "commit_message": message,
            "valid": is_valid,
            "validation": validation_msg,
            "type": commit_type,
            "scope": args.scope or None,
            "summary": args.summary,
            "breaking": args.breaking,
        }
        print(json.dumps(output, indent=2))
    else:
        if not is_valid:
            print(f"⚠️  Warning: {validation_msg}", file=sys.stderr)
        print(message)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
