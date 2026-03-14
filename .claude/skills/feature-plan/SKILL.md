---
name: feature-plan
description: Create a development plan for a new feature. Use when user says
  "feature plan", "plan feature", "feature-plan", "plan a new feature", or
  "write a feature plan".
---

# Feature Plan

Create a development plan for a new feature: $ARGUMENTS

If the request is empty or unclear, ask the user to describe the feature they want to plan.

**IMPORTANT: This skill only creates the plan file in `docs/plan/`. Do NOT modify any abstract docs, technical docs, or codebase files. No implementation changes until the user explicitly confirms the plan and requests implementation.**

## Step 1: Investigate the Codebase

1. Read `docs/documentation_hierarchy.md` to understand how abstract and technical documentation should be structured.
2. Check if the feature request references a discussion file (e.g., `docs/discussion/*.md`). If it does, read the discussion file first — it contains requirements and context that should inform the plan. Note the discussion file path for inclusion in the plan header.
3. Read `docs/abstract/index.md` to get the full list of existing features. Then read the abstract doc(s) most relevant to the new feature to understand the current user-facing context, existing user flows, and scope boundaries.
4. Read `docs/technical/index.md` to get the full list of existing technical docs. Then read the technical doc(s) most relevant to the new feature to understand the current architecture, data models, API endpoints, and component structure.
5. Read the actual source files that will be impacted by this feature:
   - **Backend**: models, API routes, CRUD queries, services under `backend/src/`
   - **Frontend**: pages, components, services under `frontend_erp/src/`
6. Identify what already exists, what needs to change, and what is new.
7. **Always identify which `docs/abstract/` and `docs/technical/` files are affected** — every feature that touches a documented system MUST update its corresponding doc file.

## Step 1.5: Clarify Ambiguities

Before writing the plan, if there are any uncertainties or ambiguities — such as unclear scope, multiple valid approaches, architectural trade-offs, or assumptions that could go either way — ask the user to clarify. Do NOT guess or assume. Use the AskUserQuestion tool to present the options and get a clear answer before proceeding.

## Step 2: Create the Plan

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
**Reference**: [Discussion — {title}](../discussion/{filename}.md)  ← include this line ONLY if the feature originates from or references a discussion file; omit it otherwise

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

Include SQL DDL for new tables, column descriptions, constraints, indexes. New migration SQL files go in `scripts/sql/` (numbered sequentially, e.g., `147_feature_name.sql`). Reference migration file paths and ORM model file paths.

### CRUD

List CRUD functions with signatures and brief descriptions. Reference file paths.

### Services

List service functions/classes with signatures and brief descriptions. Include code snippets for key logic. Reference file paths and config changes.

### API Endpoints

Include method, path, file, and response schema (JSON examples) for new endpoints.

### Testing

Reference test file paths. List specific test cases grouped by: unit tests, integration tests, and validation.

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

---

## Dependencies

List any features, tables, or services this feature depends on.

## Open Questions

List any unresolved decisions or questions for the user.
```

## Step 2.5: Update Checklist

After creating the plan file, add the plan path as an unchecked item to `docs/checklist.md` under **both** sections:

- Under `## Implementation`, append `- [ ] docs/plan/{yymmdd}_{feature_name}.md`
- Under `## DB Cloud Migration`, append `- [ ] docs/plan/{yymmdd}_{feature_name}.md`

Insert each entry at the end of its respective section (before the blank line separating sections). Create `docs/checklist.md` with both sections if it doesn't exist.

## Step 3: Run Pre-commit

Run pre-commit on all staged files to catch linting and formatting errors:

```bash
source venv/bin/activate && pre-commit run --all-files
```

Fix any issues reported before proceeding.

## Step 4: Present the Plan

After writing the plan file, present a brief summary to the user with:
- The output file path
- A bullet-point overview of the key changes across each Implementation Plan sub-section
- Which `docs/abstract/` and `docs/technical/` files are updated and what changes in each
- Pre-commit result (passed / issues fixed)
- Remind the user to review the plan and resolve any open questions before implementation
