# Implementation Section Rules

Detailed rules and guidelines for specific implementation plan sub-sections.

## SQL Migration File Rules

Enforced by `scripts/run_migrations.py` during deployment:

- **DDL only** — migrations must contain only schema changes: `CREATE TABLE/INDEX/TYPE`, `ALTER`, `DROP`, `DO $$ ... $$` blocks. DML statements (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`) are automatically stripped and will NOT execute.
- **No semicolons in comments** — avoid `;` inside `--` comments (e.g., `-- this is foo; this is bar`). Semicolons in comments break statement parsing. Put each thought on its own `--` line instead.
- **Idempotent** — use `IF NOT EXISTS`, `IF EXISTS`, `DO $$ BEGIN ... END $$` blocks so migrations can safely re-run.
- **Seed data** goes in `scripts/seed/`, not `scripts/sql/`.
- New migration SQL files go in `scripts/sql/` (numbered sequentially, e.g., `147_feature_name.sql`).

## Implementation Sub-Section Structure

Each sub-section (Key Workflow, Database Schema, CRUD, Services, API Endpoints, Testing, Frontend, Documentation, Chrome Extension Execution) MUST include three sub-sub-sections:

- **To Delete** — what existing code, functions, config, or files to remove
- **To Update** — what existing code, functions, config, or files to modify (describe the change)
- **To Add New** — what new code, functions, config, or files to create (describe the purpose)

If a sub-sub-section has no changes, write "None".

## Pre-commit Loop

Testing must always include a final step to run pre-commit in a loop:

1. Run `source venv/bin/activate && pre-commit run --all-files`.
2. Fix any issues (e.g., lint errors, line count violations).
3. Re-run pre-commit again — Prettier may reformat the fixes and push files back over the line limit (max 300 lines per frontend file). If so, fix again (e.g., extract components to separate files to reduce line count durably).
4. Repeat until pre-commit passes cleanly on a full re-run with no new failures.

## Documentation Section

**This section is MANDATORY — never leave it empty.** Every feature touches at least one documented system.

### Abstract (`docs/abstract/`)

For each affected doc file, list:
- New file(s) to create (with proposed filename)
- Existing file(s) to update
- Which sections change (Problem, Solution, User Flow, Scope, Acceptance Criteria)
- Exactly what is added, updated, or removed

### Technical (`docs/technical/`)

For each affected doc file, list:
- New file(s) to create (with proposed filename)
- Existing file(s) to update
- Which sections change (Architecture, Data Model, Pipeline, API Layer, Service Layer, CRUD Layer, Frontend, etc.)
- Exactly what is added, updated, or removed

If a feature genuinely requires no doc changes (e.g., pure internal refactor with no user-facing or API changes), explicitly write "No changes needed — [reason]."
