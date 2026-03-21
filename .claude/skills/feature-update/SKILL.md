---
name: feature-update
description: Apply a change request to an already-implemented feature, updating
  docs and code together. Use when user says "feature update", "update feature",
  "feature-update", "change the feature", or "modify the feature".
---

# Feature Update

Apply a change request to an already-implemented feature, updating abstract docs, technical docs, and codebase together.

The user's change request is: $ARGUMENTS

If the request is empty or unclear, ask the user to describe what change they want.

## Step 1: Understand Documentation Standards

Read `docs/documentation_hierarchy.md` to understand the rules for writing abstract and technical documentation. All doc updates in later steps must follow these rules.

## Step 2: Identify Affected Files from Conversation Context

Review the recent conversation history to determine which feature was just implemented and which files are involved. Build a file map with three categories:

1. **Abstract doc(s)**: which `docs/abstract/*.md` file(s) describe this feature
2. **Technical doc(s)**: which `docs/technical/*.md` file(s) describe this feature
3. **Chrome test doc**: which `docs/chrome_test/*.md` file describes E2E tests for this feature
4. **Implementation files**: which backend and frontend source files were created or modified

If the conversation does not contain enough context (e.g., the user started a fresh session), ask the user which feature this change applies to, then:
- Read `docs/abstract/index.md` and `docs/technical/index.md` to locate the relevant doc files
- Read those doc files to find the implementation file paths listed in them

## Step 3: Read All Affected Files

Read every file identified in Step 2 to understand the current state:
- The abstract doc — current Problem, Solution, User Flow, Scope, Acceptance Criteria
- The technical doc — current Architecture, Data Model, Pipeline, API Layer, CRUD Layer, Frontend sections, Component Checklist
- The chrome test doc — current test cases, seed data, and cleanup SQL
- The implementation files — current code that will be touched by the change
- Read `docs/design_patterns/index.md` to understand which pattern the feature follows, so changes stay consistent with the pattern.

## Step 4: Clarify Ambiguities

If the change request has any uncertainties — unclear scope, multiple valid approaches, architectural trade-offs, or assumptions that could go either way — ask the user to clarify using the AskUserQuestion tool. Do NOT guess or assume.

## Step 5: Apply Changes

Make all changes across the three layers. Work top-down: docs first, then code.

### 5a. Update Abstract Doc (`docs/abstract/`)

Update the affected abstract doc file(s) to reflect the change:
- Update **User Flow** if the user-facing behavior changes
- Update **Scope** if included/excluded items change
- Update **Acceptance Criteria** if new criteria are needed or existing ones change
- Update **Problem** or **Solution** only if the change fundamentally alters the feature's purpose
- Follow all rules from `docs/documentation_hierarchy.md` (no code, no file paths, no jargon)

### 5b. Update Technical Doc (`docs/technical/`)

Update the affected technical doc file(s) to reflect the change:
- Update **Data Model** if tables or columns change
- Update **Pipeline** diagram if the request lifecycle changes
- Update **API Layer** table if endpoints are added, modified, or removed
- Update **Service Layer** if business logic changes
- Update **CRUD Layer** if database operations change
- Update **Frontend** sections if pages, components, or routes change
- Update **Component Checklist** to reflect new or changed components
- Follow all rules from `docs/documentation_hierarchy.md` (architecture focus, ASCII diagrams, vertical pipelines)

### 5c. Update Chrome Test Doc (`docs/chrome_test/`)

Find the chrome test file in `docs/chrome_test/` that corresponds to this feature. Update it to reflect the change request:
- Update **Remarks** if the feature behavior changes (e.g., notes are now shareable)
- Update **Database Pre-Interaction** if new seed data or tables are needed for the new tests
- Update **Cleanup** SQL to cover any new tables or data
- Update **existing tests** if the change alters expected UI state (e.g., new columns in a list page)
- Add **new test cases** for any new user-facing functionality introduced by the change (e.g., sharing, notifications, revoking access). Follow the existing test format with User(s) involved, Steps (checkboxes), Expected UI state, Error handling, and Report fields.

### 5d. Update Plan Doc (`docs/plan/`)

Find the plan file in `docs/plan/` that corresponds to this feature (created by `/feature-plan`). Update it to reflect the change request:
- Add a new section at the bottom: `## Change Request — {YYYY-MM-DD}` with a description of what changed and why
- Update the **What Changes** table if the change alters the current-vs-proposed comparison
- Update the relevant **Implementation Plan** sub-sections (Database Schema, CRUD, Services, API Endpoints, Frontend, Documentation) to reflect the new state
- If the change adds new components, add them to the relevant sub-section with the To Add New / To Update / To Delete structure

### 5e. Update Codebase

Apply the actual code changes:
- **Database**: new migration SQL in `scripts/sql/` if schema changes are needed. Follow the SQL migration file rules:
  - **DDL only** — only schema changes (`CREATE`, `ALTER`, `DROP`, `DO $$ ... $$`). DML (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`) is stripped by the migration runner and will NOT execute. Seed data goes in `scripts/seed/`.
  - **No semicolons in comments** — never use `;` inside `--` comments. It breaks statement parsing. Use separate comment lines instead.
  - **Idempotent** — use `IF NOT EXISTS`, `IF EXISTS`, `DO $$ BEGIN ... END $$` blocks.
- **Backend models**: update or add SQLAlchemy models in `backend/src/models/`
- **Backend schemas**: update or add Pydantic schemas in `backend/src/schemas/`
- **Backend CRUD**: update or add queries/write_ops in `backend/src/crud/`
- **Backend services**: update or add service logic in `backend/src/services/`
- **Backend API**: update or add route handlers in `backend/src/api/`
- **Frontend pages**: update or add pages in `frontend_erp/src/components/pages/`
- **Frontend components**: update or add components in `frontend_erp/src/components/`
- **Frontend services**: update or add API services in `frontend_erp/src/services/`
- **Frontend routes**: update route config if new pages are added

## Step 6: Run Pre-commit

Run pre-commit to catch linting and formatting errors:

```bash
source venv/bin/activate && pre-commit run --all-files
```

Fix any issues reported.

## Step 7: Present Summary

After all changes are applied, present a summary to the user:
- **Change request**: one-line restatement of what was requested
- **Abstract doc**: which file was updated and what changed
- **Technical doc**: which file was updated and what changed
- **Chrome test**: which file was updated and what tests were added/modified
- **Plan doc**: which file was updated and what changed
- **Codebase**: list of files created/modified with a brief description of each change
- **Pre-commit result**: passed / issues fixed
