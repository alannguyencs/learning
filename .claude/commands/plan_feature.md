Create a feature plan for: $ARGUMENTS

## Instructions

### Step 1: Investigate the codebase

Read the tech documentation index and all relevant doc files to understand the current architecture:

1. Read `docs/abstract/` to get an overview
2. Read the specific documentation files most relevant to the requested feature (e.g., quiz system, principle learning, chat & response, dashboard, etc.)
3. Read the actual source files (api/, crud/, service/, models/) that will be impacted by this feature
4. Identify what already exists, what needs to change, and what is new

### Step 1.5: Clarify ambiguities

Before writing the plan, if there are any uncertainties or ambiguities — such as unclear scope, multiple valid approaches, architectural trade-offs, or assumptions that could go either way — ask the user to clarify. Do NOT guess or assume. Use the AskUserQuestion tool to present the options and get a clear answer before proceeding.

### Step 2: Create the plan

Write the plan to `docs/plan/{yymmdd}_{feature_name}.md` where:
- `{yymmdd}` is today's date (e.g., `260221`)
- `{feature_name}` is a short snake_case name for the feature (e.g., `quiz_learning`, `recall_heatmap`)

The plan MUST follow this exact structure:

---

# {Feature Title}

**Feature**: One-line description of the feature
**Project**: Weight Management AI Coach

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

Include SQL DDL for new tables, column descriptions, constraints, indexes, and model methods. Include migration scripts if needed. Reference ORM model file paths.

### CRUD

List CRUD functions with signatures and brief descriptions. Reference file paths.

### Services

List service functions/classes with signatures and brief descriptions. Include code snippets for key logic. Reference file paths and config changes.

### API Endpoints

Include method, path, file, and response schema (JSON examples) for new endpoints.

### LLM Requests

_Include this section only if the feature makes LLM calls (runtime or offline)._

For each LLM caller, document:

1. **Prompt structure** — ASCII diagram showing system prompt file, user prompt components, and any multimodal parts:

```
+----------------------------------------------------------+
|  SYSTEM PROMPT                                           |
|  (resources/prompts/prompt_file.md)                      |
|  - What the prompt instructs                             |
+----------------------------------------------------------+
|                                                          |
+----------------------------------------------------------+
|  USER PROMPT  (built by ...)                             |
|                                                          |
|  +----------------------------------------------------+  |
|  | Component 1 — e.g. context, user input             |  |
|  +----------------------------------------------------+  |
|  | Component 2 — e.g. format instructions             |  |
|  +----------------------------------------------------+  |
|                                                          |
+----------------------------------------------------------+
```

2. **Output schema** — table listing every field with type and description. Include the model name, temperature, and whether output is structured JSON or free-text.

| Field | Type | Description |
|-------|------|-------------|
| `field_name` | type | What this field contains |

### Testing

Reference test file paths. List specific test cases grouped by: unit tests, integration tests, and validation.

### Frontend

Describe UI changes, new components, or extensions to existing components. Include visual specs (color codes, layout) where relevant.

### Documentation (`docs/tech_documentation/`)

**This section is MANDATORY — never leave it empty.** Every feature touches at least one documented system.

For each affected doc file, list:
- Which sections change (Description, Examples, Key Workflow, Database Schema, API Endpoints, etc.)
- Exactly what is added, updated, or removed

If a feature genuinely requires no doc changes (e.g., pure internal refactor with no user-facing or API changes), explicitly write "No changes needed — [reason]."

---

### Step 3: Run pre-commit

Run pre-commit on all staged files to catch linting, formatting, and type errors:

```
cd backend && source venv/bin/activate && pre-commit run --all-files
```

Fix any issues reported before proceeding.

### Step 4: Present the plan

After writing the plan file, present a brief summary to the user with:
- The output file path
- A bullet-point overview of the key changes across each Implementation Plan sub-section
- Which `docs/tech_documentation/` files are updated and what changes in each
- Pre-commit result (passed / issues fixed)

---

Reference example: `docs/plan/260220_quiz_learning.md`
