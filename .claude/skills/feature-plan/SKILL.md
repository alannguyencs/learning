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

## References

- [plan-template.md](references/plan-template.md) — Full plan template structure with all required sections
- [chrome-test-generation.md](references/chrome-test-generation.md) — Chrome E2E test file generation rules, test design, coverage categories
- [chrome-test-execution.md](references/chrome-test-execution.md) — Chrome E2E test execution and reporting after implementation
- [implementation-sections.md](references/implementation-sections.md) — SQL migration rules, implementation sub-section structure, pre-commit loop, documentation rules

## Step 0: Verify Chrome Claude Extension

Open the Chrome Claude Extension and verify it is working before proceeding.

## Step 1: Investigate the Codebase

1. Read `docs/documentation_hierarchy.md` to understand how abstract and technical documentation should be structured.
2. Read `docs/design_patterns/index.md` to understand the 7 recurring feature patterns. Identify which pattern(s) the new feature follows and reference them in the plan.
3. Check if the feature request references a discussion file (e.g., `docs/discussion/*.md`). If it does, read the discussion file first — it contains requirements and context that should inform the plan. Note the discussion file path for inclusion in the plan header.
4. Read `docs/abstract/index.md` to get the full list of existing features. Then read the abstract doc(s) most relevant to the new feature to understand the current user-facing context, existing user flows, and scope boundaries.
5. Read `docs/technical/index.md` to get the full list of existing technical docs. Then read the technical doc(s) most relevant to the new feature to understand the current architecture, data models, API endpoints, and component structure.
6. Read the actual source files that will be impacted by this feature:
   - **Backend**: models, API routes, CRUD queries, services under `backend/src/`
   - **Frontend**: pages, components, services under `frontend_erp/src/`
7. Identify what already exists, what needs to change, and what is new.
8. **Always identify which `docs/abstract/` and `docs/technical/` files are affected** — every feature that touches a documented system MUST update its corresponding doc file.

## Step 1.5: Clarify Ambiguities

Before writing the plan, if there are any uncertainties or ambiguities — such as unclear scope, multiple valid approaches, architectural trade-offs, or assumptions that could go either way — ask the user to clarify. Do NOT guess or assume. Use the AskUserQuestion tool to present the options and get a clear answer before proceeding.

## Step 1.6: Chrome Claude Extension Test Generation

Generate `docs/chrome_test/{feature_name}.md` following the rules in [chrome-test-generation.md](references/chrome-test-generation.md). All test reports must be initialized to `IN QUEUE`.

## Step 2: Create the Plan

Follow the template in [plan-template.md](references/plan-template.md). Follow the rules in [implementation-sections.md](references/implementation-sections.md) for SQL migrations, sub-section structure, and documentation requirements.

## Step 2.5: Update Checklist

After creating the plan file, add the plan path as an unchecked item to `docs/checklist.md`:

- Under `## Implementation`, append `- [ ] docs/plan/{yymmdd}_{feature_name}.md`

Insert the entry at the end of the section (before the blank line separating sections). Create `docs/checklist.md` with the `## Implementation` section if it doesn't exist.

## Step 3: Present the Plan

After writing the plan file, present a brief summary to the user with:
- The output file path
- A bullet-point overview of the key changes across each Implementation Plan sub-section
- Which `docs/abstract/` and `docs/technical/` files are updated and what changes in each
- Remind the user to review the plan and resolve any open questions before implementation
