---
name: feature-implementation-review
description: Review an implementation plan against the actual codebase to find and
  fix missing parts. Use when user says "feature implementation review", "review implementation",
  "implementation review", "check implementation", or "verify implementation".
---

# Feature Implementation Review

Review an implementation plan against the actual codebase, identify missing or incomplete parts, and implement them. Loops until every detail of the plan is complete.

The user's arguments: $ARGUMENTS

If no plan file is specified, check the recent conversation history for which plan was just implemented. If still unclear, list files in `docs/plan/` and ask the user which plan to review.

## Step 1: Load the Plan

1. Read the plan file from `docs/plan/`.
2. Parse all sub-sections of **Implementation Plan**: Database Schema, CRUD, Services, API Endpoints, Frontend, Documentation, and any other sub-sections present.
3. Build a checklist of every concrete deliverable mentioned in the plan:
   - Files to create (To Add New)
   - Files to modify (To Update)
   - Files to delete (To Delete)
   - Database tables/columns to create
   - API endpoints to add
   - Frontend components/pages to add or modify
   - Documentation files to create or update
   - Any other specific items (e.g., route registrations, navigation config entries, service functions)

## Step 2: Investigate the Codebase

For each item in the checklist from Step 1, verify whether it has been implemented:

1. Read `docs/design_patterns/index.md` to understand the expected pattern, which helps verify architectural consistency.
2. **Files exist**: Check that every file listed as "To Add New" exists using Glob.
3. **Files modified**: Read every file listed as "To Update" and verify the described changes are present.
4. **Files deleted**: Verify that files listed as "To Delete" no longer exist.
5. **Database schema**: Read the migration SQL file(s) referenced in the plan. Verify all tables, columns, constraints, and indexes are present as specified. Also verify the SQL follows migration file rules:
   - **DDL only** — no DML (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`). DML is stripped by the migration runner and will NOT execute. Seed data belongs in `scripts/seed/`.
   - **No semicolons in comments** — no `;` inside `--` comments. It breaks statement parsing.
   - **Idempotent** — uses `IF NOT EXISTS`, `IF EXISTS`, `DO $$ BEGIN ... END $$` blocks.
6. **Backend models**: Read the model file(s) and verify all fields match the schema.
7. **Backend CRUD**: Read CRUD files and verify all functions described in the plan exist with the correct signatures and logic.
8. **Backend services**: Read service files and verify all functions/classes described in the plan exist.
9. **Backend API**: Read API route files and verify all endpoints described in the plan are registered with correct methods, paths, and handler logic.
10. **API router registration**: Verify the new router is included in `backend/src/api/api_router.py` or `backend/src/api/__init__.py`.
11. **Frontend pages**: Read page component files and verify they implement the UI described in the plan.
12. **Frontend services**: Read service files and verify all API call methods exist.
13. **Frontend routes**: Read `frontend_erp/src/routes.js` and verify new pages are registered.
14. **Frontend navigation**: Read `frontend_erp/src/components/layout/navigationConfig.js` and verify new nav entries exist if mentioned in the plan.
15. **Abstract docs**: Read `docs/abstract/` files listed in the plan's Documentation section and verify they are updated.
16. **Technical docs**: Read `docs/technical/` files listed in the plan's Documentation section and verify they are updated.
17. **Email gating / notifications**: If the plan mentions email functions or notification integration, verify those are implemented.
18. **Key Workflow**: Verify the workflow described in the plan matches the actual code flow.

## Step 3: Report Findings

Present a summary table of every checklist item and its status:

```
| # | Category | Item | Status | Detail |
|---|----------|------|--------|--------|
| 1 | Database | Create table X | Done | scripts/sql/150_....sql |
| 2 | CRUD | Add function get_settings() | Missing | File exists but function not found |
| 3 | API | POST /api/v1/foo | Partial | Endpoint exists but missing validation |
...
```

Status values:
- **Done** — fully implemented as described in the plan
- **Partial** — exists but incomplete or deviates from the plan
- **Missing** — not implemented at all
- **Extra** — implemented but not in the plan (informational only, no action needed)

If everything is **Done**, skip to Step 5.

## Step 4: Implement Missing Parts (Loop)

For each **Missing** or **Partial** item, implement it according to the plan specification:

1. Work through items in dependency order (database first, then models, CRUD, services, API, frontend, docs).
2. After implementing each batch of fixes, re-verify the items by reading the updated files.
3. If a fix reveals additional missing items (e.g., a missing import, a missing route registration), add them to the checklist and implement them.
4. **Loop**: After each implementation pass, go back to Step 2 and re-investigate. Continue until all items are **Done**.
5. Maximum 3 loop iterations. If items remain after 3 passes, report them to the user with details on what's still missing and why.

## Step 5: Run Pre-commit (Loop)

Run pre-commit in a loop until it passes cleanly:

1. Run `source venv/bin/activate && pre-commit run --all-files`.
2. Fix any issues (e.g., lint errors, unused imports, line count violations).
3. Re-run pre-commit again — Prettier may reformat the fixes and push files back over the line limit (max 300 lines per frontend file). If so, fix again (e.g., extract components to separate files to reduce line count durably).
4. Repeat until pre-commit passes cleanly on a full re-run with no new failures.

If fixes change files that were just verified, do a quick re-check to ensure the fixes didn't break the implementation.

## Step 6: Final Summary

Present the final summary to the user:

- **Plan reviewed**: path to the plan file
- **Total items checked**: count
- **Items already done**: count
- **Items fixed**: count (list each with a brief description of what was implemented)
- **Items remaining**: count (if any, with explanation)
- **Pre-commit result**: passed / issues fixed
- **Confidence**: High / Medium / Low — based on how closely the implementation matches the plan

## Step 7: Update Checklist

After a successful review (all items **Done** or no remaining items), mark the plan as completed in `docs/checklist.md` under the `## Implementation` section:

- Change `- [ ] docs/plan/{plan_file}.md` to `- [x] docs/plan/{plan_file}.md`

If there are still remaining items (implementation incomplete), do NOT check it off.
