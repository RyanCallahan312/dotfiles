# Conventional Commits Specification

## Overview

The Conventional Commits specification is a lightweight convention on top of commit messages. It provides an easy set of rules for creating an explicit commit history; which makes it easier to write automated tools on top of. This convention dovetails with SemVer by describing the features, fixes, and breaking changes made in commit messages.

## Format

A conventional commit message has the following structure:

```
<type>[optional scope][optional !]: <subject>

[optional body]

[optional footer(s)]
```

### Components

#### Type (required)

The type must be one of the following:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect code meaning (formatting, semicolons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to build process, dependencies, or tooling

#### Scope (optional)

A scope may be provided after the type. The scope is a noun describing a section of the codebase surrounded by parentheses:

```
feat(parser): add ability to parse arrays
```

#### Subject (required)

The subject contains a succinct description of the change:

- Use the imperative, present tense ("add" not "added" or "adds")
- Do not capitalize the first letter
- Do not end with a period (.)
- Limit to 50 characters

#### Body (optional)

The body provides more context about the changes. It can include motivation and contrasts with previous behavior:

- Use the imperative, present tense
- Include motivation for the change
- Contrast with previous behavior
- Wrap at 72 characters
- Use blank line to separate from subject

#### Footers (optional)

Footers are structured as `Token: value` pairs and use the following conventions:

- **BREAKING CHANGE**: Indicates a breaking change in the commit. Can be followed by a description.
- **Refs**: Reference to issues or pull requests

Example:

```
feat(auth): implement JWT token refresh

Add automatic token refresh mechanism that reduces authentication
overhead by 30%. Implements RFC-123 for token lifecycle management.

BREAKING CHANGE: The /auth/refresh endpoint now requires Bearer token
instead of session cookie. Clients must update their auth headers.

Refs: #456, #789
```

## Examples

### Example 1: Simple Feature

```
feat: allow provided config object to extend other configs
```

### Example 2: Feature with Scope

```
feat(lang): add Polish language support
```

### Example 3: Bug Fix

```
fix(core): prevent race condition in concurrent requests
```

### Example 4: Breaking Change

```
feat(api)!: send an email to the customer when a product is shipped

BREAKING CHANGE: The API response format has changed from XML to JSON
```

### Example 5: With Body

```
fix(email): improve error handling for SMTP timeouts

Increase SMTP timeout from 5s to 10s to handle slow mail servers.
Add retry logic with exponential backoff for transient failures.

Refs: #1234
```

## Best Practices

1. **Be descriptive**: The commit message should describe WHAT changed and WHY
2. **Use lowercase**: Keep types and scopes lowercase
3. **Be consistent**: Maintain consistency with your project's conventions
4. **Use scopes**: Scopes help organize commits by feature or module
5. **Mention breaking changes**: Always clearly mark breaking changes
6. **Reference issues**: Link to issue trackers when relevant
7. **Limit message size**: Keep headers to 50 chars, body lines to 72 chars

## Relationship to SemVer

Conventional commits map to semantic versioning:

- `fix:` patches → PATCH version
- `feat:` features → MINOR version  
- `BREAKING CHANGE:` → MAJOR version

For example:
- Version 1.0.0 → fix bumps to 1.0.1, feat bumps to 1.1.0, breaking bumps to 2.0.0
