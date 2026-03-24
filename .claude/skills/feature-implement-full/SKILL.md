---
name: feature-implement-full
description: Execute an implementation plan end-to-end — implement code, review for
  completeness, and commit. Use when user says "feature implement full", "implement
  full", "full implement", "implement and commit", or "execute plan".
---

# Feature Implement Full

Execute an implementation plan from `docs/plan/` end-to-end: implement all changes, review for completeness, and commit.

The user's arguments: $ARGUMENTS

If no plan file is specified, list files in `docs/plan/` and ask the user which plan to implement.

## Step 0: Clear Conversation

Type `/clear` to clear the conversation before starting implementation.

## Step 1: Implement the Plan

1. Read the plan file from `docs/plan/`.
2. Extract the feature name from the plan title (the `# {Feature Title}` heading).
3. Implement every item described in the **Implementation Plan** section, working in dependency order:
   - **Database Schema**: Create migration SQL files in `scripts/sql/`, following the SQL migration file rules:
     - **DDL only** — only schema changes (`CREATE`, `ALTER`, `DROP`, `DO $$ ... $$`). DML (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`) is stripped by the migration runner and will NOT execute. Seed data goes in `scripts/seed/`.
     - **No semicolons in comments** — never use `;` inside `--` comments. It breaks statement parsing. Use separate comment lines instead.
     - **Idempotent** — use `IF NOT EXISTS`, `IF EXISTS`, `DO $$ BEGIN ... END $$` blocks.
   - **Backend models**: Create or update model files.
   - **CRUD**: Create or update CRUD files (`queries.py`, `write_ops.py`).
   - **Services**: Create or update service files.
   - **API Endpoints**: Create or update API route files. Register new routers in `backend/src/api/api_router.py` if needed.
   - **Frontend**: Create or update pages, components, services, routes, and navigation config.
   - **Documentation**: Update `docs/abstract/` and `docs/technical/` files as specified in the plan.
   - **Testing**: Create test files and run pre-commit in a loop until it passes cleanly:
     1. Run `source venv/bin/activate && pre-commit run --all-files`.
     2. Fix any issues (e.g., lint errors, unused imports, line count violations).
     3. Re-run pre-commit — Prettier may reformat fixes and push files back over the line limit (max 300 lines per frontend file). If so, fix durably (e.g., extract components to separate files).
     4. Repeat until pre-commit passes with no new failures.
4. Follow the plan's **To Delete**, **To Update**, and **To Add New** sub-sections precisely.
5. For any ambiguity in the plan, check the existing codebase patterns (e.g., similar features) and follow the same conventions.

## Step 2: Review Implementation

Run the `feature-implementation-review` skill against the same plan file to verify completeness:

```
/feature-implementation-review {plan_file_path}
```

This will:
- Compare every deliverable in the plan against the actual codebase
- Identify any missing or partial implementations
- Fix any gaps found
- Run pre-commit and fix issues
- Update `docs/checklist.md` to mark the plan as complete

## Step 3: Commit

After the review passes (all items **Done**), create a git commit:

1. Run `git status` to see all changed files.
2. Run `git diff --stat` to see the scope of changes.
3. Stage all relevant files (do NOT stage `.env`, credentials, or unrelated files).
4. Commit with the message format:

```
feat: claude - {feature name}
```

Where `{feature name}` is the lowercase feature title extracted from the plan heading (e.g., `# Onboarding 7-Stage Pipeline Refactor` becomes `onboarding 7-stage pipeline refactor`).

5. Do NOT push to remote — only commit locally.
