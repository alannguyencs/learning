Review documentation quality for `docs/abstract/` and `docs/technical/` against the rules in `docs/documentation_hierarchy.md`.

If $ARGUMENTS is provided, review only the specified file(s). Otherwise review all files in both directories.

For each file, check and report violations:

## Abstract (`docs/abstract/`) checks

1. **Status field** — has `**Status:** Plan | In Progress | Done` near the top
2. **Related Docs link** — has a `## Related Docs` section linking to the corresponding technical file
3. **No code or file paths** — no backtick code spans with file paths, class names, or function names
4. **Problem and Solution sections** — has `## Problem` and `## Solution`
5. **User Flow section** — has `## User Flow` with step-by-step walkthrough
6. **Scope section** — has `## Scope`
7. **Acceptance Criteria** — has `## Acceptance Criteria` with checkbox items
8. **ASCII diagrams** — flows use fenced code blocks, not Mermaid/PlantUML
9. **Page length** — under 300 lines
10. **Navigation** — Prev/Next links at both top and bottom matching `index.md` order

## Technical (`docs/technical/`) checks

1. **Related Docs link** — has `## Related Docs` linking to the abstract file
2. **Architecture section** — has `## Architecture`
3. **Data Model** — uses SQLAlchemy class name (e.g., `**`UserPrincipleProgress`**`), not database table name (e.g., ~~`Table: coach_user_principle_progress_260202`~~)
4. **Pipeline diagram** — has `## Pipeline` section with vertical ASCII diagram (uses `│`, `▼`, `├──`, `└──`), not horizontal multi-column sequence diagrams
5. **Algorithms** — if present, uses bullet points under `### H3` headings, not wall-of-text paragraphs
6. **API Layer** — has `## Backend — API Layer` with endpoint table
7. **Service Layer** — has `## Backend — Service Layer`
8. **LLM Requests Layer** — if feature makes LLM calls, has `## Backend — LLM Requests Layer` with prompt structure diagrams and output schema tables
9. **Component Checklist** — has `## Component Checklist` with checkbox items at the bottom before footer
10. **Navigation** — Prev/Next links at both top and bottom matching `index.md` order

## System Pipelines page (`technical/system_pipelines.md`) checks

1. **Only ASCII diagrams** — no prose paragraphs, no markdown tables
2. **One pipeline per entry point** — each section is a heading + fenced code block
3. **Links to feature pages** — each heading links to the detail page
4. **No Component Checklist** — must not have one

## Cross-file checks

1. **Navigation chain** — Prev/Next links form an unbroken chain matching `index.md` row order in both abstract and technical
2. **Filename parity** — every abstract file has a matching technical file and vice versa (except `system_pipelines.md` which has no abstract counterpart)
3. **index.md completeness** — every `.md` file in the directory (except `index.md`) is listed in `index.md`

## Output format

For each violation found, report:
- **File**: path
- **Rule**: rule number and name
- **Issue**: what is wrong
- **Fix**: what to change

At the end, print a summary: `X files checked, Y violations found`.
