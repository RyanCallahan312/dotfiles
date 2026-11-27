#!/usr/bin/env python3
"""
Generate CHANGELOG.md from conventional commits.

Usage:
    python3 generate-changelog.py [--output CHANGELOG.md] [--version VERSION]

Examples:
    python3 generate-changelog.py                      # Generate from all commits
    python3 generate-changelog.py --version 1.2.0     # Generate with specific version
    python3 generate-changelog.py --output docs/CHANGELOG.md
"""

import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


class ChangelogGenerator:
    def __init__(self, output_path: str = "CHANGELOG.md"):
        self.output_path = Path(output_path)
        self.commits = []

    def fetch_commits(self, range_spec: str = "HEAD") -> List[Dict]:
        """Fetch commits using conventional commit format."""
        try:
            # Get commits with their messages
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--format=%H%n%an%n%ae%n%ai%n%B%n---COMMIT_END---",
                    range_spec,
                ],
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
                if i + 4 < len(lines):
                    commit_hash = lines[i]
                    author = lines[i + 1]
                    email = lines[i + 2]
                    date_str = lines[i + 3]
                    i += 4

                    # Collect message until marker
                    message_lines = []
                    while i < len(lines) and lines[i] != "---COMMIT_END---":
                        message_lines.append(lines[i])
                        i += 1

                    message = "\n".join(message_lines).strip()
                    parsed = self._parse_conventional_commit(message, commit_hash[:8])

                    if parsed:  # Only include conventional commits
                        parsed["author"] = author
                        parsed["email"] = email
                        parsed["date"] = date_str
                        commits.append(parsed)

                    i += 1  # Skip marker
                else:
                    i += 1

            return commits
        except Exception as e:
            print(f"Error fetching commits: {e}", file=sys.stderr)
            return []

    def _parse_conventional_commit(
        self, message: str, short_hash: str
    ) -> Optional[Dict]:
        """Parse a conventional commit message."""
        lines = message.split("\n")
        if not lines:
            return None

        header = lines[0]

        # Parse: type(scope)?: subject OR type(scope)!: subject
        pattern = (
            r"^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+?\))?(!)?:\s+(.+)$"
        )
        match = re.match(pattern, header)

        if not match:
            return None

        commit_type, scope, breaking, subject = match.groups()

        # Extract body and footer
        body = ""
        breaking_description = None

        if len(lines) > 2:
            body_start = 2
            for i, line in enumerate(lines[1:], 1):
                if line.startswith("BREAKING CHANGE:"):
                    breaking_description = line.replace("BREAKING CHANGE:", "").strip()
                elif not line.strip():
                    body_start = i + 1
                    break

            body = "\n".join(lines[body_start:])

        return {
            "type": commit_type,
            "scope": scope.strip("()") if scope else None,
            "subject": subject,
            "body": body.strip(),
            "breaking": breaking == "!" or breaking_description is not None,
            "breaking_description": breaking_description,
            "hash": short_hash,
        }

    def group_commits(self, commits: List[Dict]) -> Dict:
        """Group commits by type and scope."""
        grouped = defaultdict(lambda: defaultdict(list))

        for commit in commits:
            commit_type = commit["type"]
            scope = commit["scope"] or "general"
            grouped[commit_type][scope].append(commit)

        return grouped

    def generate_changelog_content(
        self,
        commits: List[Dict],
        version: Optional[str] = None,
        include_breaking: bool = True,
    ) -> str:
        """Generate changelog markdown content."""

        if not commits:
            return "# Changelog\n\nNo commits found.\n"

        # Get version and date
        version = version or "Unreleased"
        date_str = datetime.now().strftime("%Y-%m-%d")
        if version == "Unreleased":
            date_str = ""
        else:
            date_str = f" - {date_str}"

        lines = ["# Changelog\n"]
        lines.append(f"## [{version}]{date_str}\n")

        # Group commits
        grouped = self.group_commits(commits)

        # Type order for display
        type_order = [
            "feat",
            "fix",
            "perf",
            "refactor",
            "docs",
            "style",
            "test",
            "chore",
        ]
        type_labels = {
            "feat": "Features",
            "fix": "Bug Fixes",
            "perf": "Performance",
            "refactor": "Refactoring",
            "docs": "Documentation",
            "style": "Styling",
            "test": "Tests",
            "chore": "Chores",
        }

        # Breaking changes section
        breaking_commits = [c for c in commits if c["breaking"]]
        if breaking_commits and include_breaking:
            lines.append("### ⚠️ Breaking Changes\n")
            for commit in breaking_commits:
                lines.append(
                    f"- **{commit['scope'] or 'general'}**: {commit['subject']}"
                )
                if commit["breaking_description"]:
                    lines.append(f"  \n  {commit['breaking_description']}")
            lines.append("")

        # Grouped commits
        for commit_type in type_order:
            if commit_type not in grouped:
                continue

            lines.append(f"### {type_labels.get(commit_type, commit_type.title())}\n")

            scopes = grouped[commit_type]
            for scope in sorted(scopes.keys()):
                commits_in_scope = scopes[scope]
                for commit in commits_in_scope:
                    scope_str = f"**{scope}**" if scope != "general" else ""
                    prefix = f"{scope_str}: " if scope_str else ""
                    lines.append(
                        f"- {prefix}{commit['subject']} ([{commit['hash']}](../commit/{commit['hash']}))"
                    )

            lines.append("")

        return "\n".join(lines)

    def generate(self, version: Optional[str] = None, range_spec: str = "HEAD"):
        """Generate and write changelog."""
        commits = self.fetch_commits(range_spec)
        content = self.generate_changelog_content(commits, version)

        # Merge with existing changelog if it exists
        if self.output_path.exists():
            with open(self.output_path) as f:
                existing = f.read()
            # Simple merge: insert new version after header
            if "# Changelog" in existing:
                existing = existing.replace(
                    "# Changelog\n", f"# Changelog\n\n{content}"
                )
                content = existing

        with open(self.output_path, "w") as f:
            f.write(content)

        return self.output_path


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate changelog from conventional commits"
    )
    parser.add_argument("--output", default="CHANGELOG.md", help="Output file path")
    parser.add_argument("--version", help="Version for this changelog entry")
    parser.add_argument("--range", default="HEAD", help="Git range to include")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    generator = ChangelogGenerator(args.output)
    commits = generator.fetch_commits(args.range)

    if args.json:
        print(json.dumps(commits, indent=2))
    else:
        output_path = generator.generate(args.version, args.range)
        print(f"✓ Changelog generated: {output_path}")


if __name__ == "__main__":
    main()
