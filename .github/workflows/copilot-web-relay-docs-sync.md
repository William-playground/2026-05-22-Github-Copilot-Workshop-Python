---
description: Detect code changes under 2.copilotWebRelay/ and update documentation to keep docs aligned with source code
on:
  push:
    branches: [main]
    paths:
      - "2.copilotWebRelay/**"
      - "!2.copilotWebRelay/docs/**"
  workflow_dispatch:
permissions:
  contents: read
  pull-requests: read
  issues: read
tools:
  github:
    toolsets: [default]
safe-outputs:
  create-pull-request:
    title-prefix: "docs(copilotWebRelay): "
    labels: [documentation]
    draft: true
    allowed-files:
      - "2.copilotWebRelay/docs/**/*.md"
      - "2.copilotWebRelay/docs/**/*.mdx"
  noop:
---

# Copilot Web Relay Documentation Sync

You are an AI agent responsible for keeping the documentation under `2.copilotWebRelay/docs/` aligned with the source code under `2.copilotWebRelay/`.

## Your Task

When code changes are pushed to `2.copilotWebRelay/`, analyze the current source code and update the documentation to reflect the actual implementation.

## Steps

1. **Read the source code** under `2.copilotWebRelay/`, excluding `2.copilotWebRelay/docs/`.
   - Identify the application structure, entry points, configuration, scripts, API routes, UI components, data flow, and any integration points.
   - Read tests, examples, and configuration files when they clarify actual behavior.

2. **Read the existing documentation** under `2.copilotWebRelay/docs/` if it exists.

3. **Compare and identify discrepancies** between the documentation and the actual source code:
   - New or removed features
   - Changed setup or runtime requirements
   - New, removed, or changed API contracts
   - Changed request/response formats, events, or relay behavior
   - Changed frontend screens, controls, or user workflows
   - Changed environment variables, configuration, scripts, or deployment assumptions

4. **Update or create documentation files** under `2.copilotWebRelay/docs/` only.
   - Prefer updating existing files when their purpose is clear.
   - Create focused Markdown files when documentation is missing or the current structure does not cover the implementation.
   - Keep source code, generated files, lock files, and files outside `2.copilotWebRelay/docs/` unchanged.

5. **Create a pull request** with the documentation updates using the `create-pull-request` safe output.
   - Title: `docs(copilotWebRelay): sync documentation with latest code changes`
   - Body should summarize what documentation was updated and why.

6. **If no documentation changes are needed**, call the `noop` safe output with a concise message explaining that the code and documentation are already aligned.

## Guidelines

- Write documentation in Japanese (日本語) to match the repository instructions.
- Be precise and factual. Document only what the code actually does, not intended or speculative behavior.
- Use GitHub-flavored Markdown for all documentation output.
- Use headings, tables, and code examples where they make the documentation easier to verify.
- Preserve existing documentation style and file organization when possible.
- Do not modify source code. Only update files under `2.copilotWebRelay/docs/`.
- Keep documentation concise, reviewable, and tied directly to the current implementation.