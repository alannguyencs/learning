# Plan Template

Write the plan to `docs/plan/{yymmdd}_{feature_name}.md` where:
- `{yymmdd}` is today's date (e.g., `260305`)
- `{feature_name}` is a short snake_case name for the feature

Create the `docs/plan/` directory if it doesn't exist.

The plan MUST follow this exact structure:

```markdown
# {Feature Title}

**Feature**: One-line description of the feature
**Plan Created:** {YYYY-MM-DD}
**Status:** Plan
**Reference**:
- [Discussion — {title}](../discussion/{filename}.md)  ← include ONLY if the feature originates from or references a discussion file; omit otherwise
- [Abstract — {title}](../abstract/{filename}.md)  ← list each related abstract doc
- [Technical — {title}](../technical/{filename}.md)  ← list each related technical doc
- [Testing Context](../technical/testing_context.md)

---

## Problem Statement

Describe the current limitation or gap that motivates this feature. Be specific about what exists today and why it falls short. Use numbered points for clarity.

---

## Proposed Solution

Describe the proposed approach at a high level. Explain the core concept, key design decisions, and why this approach was chosen. Include diagrams, formulas, or tables where they aid understanding.

---

## Current Implementation Analysis

### What Exists (keep as-is)

A table of existing components that will NOT change:

| Component | File | Status |
|-----------|------|--------|
| ... | `path/to/file.py` | Keep - reason |

### What Changes

A table summarizing what shifts from current to proposed:

| Component | Current | Proposed |
|-----------|---------|----------|
| ... | current behavior | new behavior |

---

## Implementation Plan

Each of the following sub-sections MUST include three sub-sub-sections:

- **To Delete** — what existing code, functions, config, or files to remove
- **To Update** — what existing code, functions, config, or files to modify (describe the change)
- **To Add New** — what new code, functions, config, or files to create (describe the purpose)

If a sub-sub-section has no changes, write "None".

### Key Workflow

Describe the main flows that change or are introduced. Use ASCII flowcharts for new workflows. Reference function names and file paths.

### Database Schema

See [implementation-sections.md](implementation-sections.md) for SQL migration rules.

Include SQL DDL for new tables, column descriptions, constraints, indexes. New migration SQL files go in `scripts/sql/` (numbered sequentially, e.g., `147_feature_name.sql`). Reference migration file paths and ORM model file paths.

### CRUD

List CRUD functions with signatures and brief descriptions. Reference file paths.

### Services

List service functions/classes with signatures and brief descriptions. Include code snippets for key logic. Reference file paths and config changes.

### API Endpoints

Include method, path, file, and response schema (JSON examples) for new endpoints.

### Testing

Reference test file paths. List specific test cases grouped by: unit tests, integration tests, and validation. Always include a final step to run pre-commit in a loop:

1. Run `source venv/bin/activate && pre-commit run --all-files`.
2. Fix any issues (e.g., lint errors, line count violations).
3. Re-run pre-commit again — Prettier may reformat the fixes and push files back over the line limit (max 300 lines per frontend file). If so, fix again (e.g., extract components to separate files to reduce line count durably).
4. Repeat until pre-commit passes cleanly on a full re-run with no new failures.

### Frontend

Describe UI changes, new components, or extensions to existing components. Include visual specs (color codes, layout) where relevant.

### Documentation

**This section is MANDATORY — never leave it empty.** Every feature touches at least one documented system.

#### Abstract (`docs/abstract/`)

For each affected doc file, list:
- New file(s) to create (with proposed filename)
- Existing file(s) to update
- Which sections change (Problem, Solution, User Flow, Scope, Acceptance Criteria)
- Exactly what is added, updated, or removed

#### Technical (`docs/technical/`)

For each affected doc file, list:
- New file(s) to create (with proposed filename)
- Existing file(s) to update
- Which sections change (Architecture, Data Model, Pipeline, API Layer, Service Layer, CRUD Layer, Frontend, etc.)
- Exactly what is added, updated, or removed

If a feature genuinely requires no doc changes (e.g., pure internal refactor with no user-facing or API changes), explicitly write "No changes needed — [reason]."

### Chrome Claude Extension Execution

After implementation is complete, execute the Chrome Claude Extension E2E tests defined in `docs/chrome_test/{feature_name}.md` (generated in Step 1.6). See [chrome-test-execution.md](chrome-test-execution.md) for execution details.

---

## Dependencies

List any features, tables, or services this feature depends on.

## Open Questions

List any unresolved decisions or questions for the user.
```
