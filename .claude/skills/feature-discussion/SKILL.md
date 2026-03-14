---
name: feature-discussion
description: Discuss an existing or new feature with full project context. Use when
  user says "feature discussion", "discuss feature", "feature-discussion", "let's
  discuss", "tell me about feature", or "how does feature work".
---

# Feature Discussion

Discuss a feature with the user, grounded in the project's documentation and codebase: $ARGUMENTS

If the request is empty or unclear, ask the user what feature they'd like to discuss or what question they have.

## Step 0: Prepare the Discussion File

1. Create the `docs/discussion/` directory if it does not exist.
2. Choose a short, descriptive filename based on the topic being discussed. The file path must follow the pattern: `docs/discussion/{YYMMDD}_{topic_slug}.md` — e.g., `docs/discussion/260313_payslip_expense_reimbursement_workflow.md`. Use today's date for `YYMMDD` and a concise snake_case slug for the topic.
3. All output from this skill will be written to this file instead of being displayed inline. After completing the research steps below, write the full discussion result into this file.

## Step 1: Understand Documentation Standards

Read `docs/documentation_hierarchy.md` to understand the two-level documentation structure (abstract and technical) and how features are organized.

## Step 2: Read the Abstract Layer

1. Read `docs/abstract/index.md` to get the full list of documented features.
2. Identify which abstract doc(s) are most relevant to the user's question.
3. Read those abstract doc(s) to understand the feature from a user/stakeholder perspective — Problem, Solution, User Flow, Scope, and Acceptance Criteria.

If no abstract doc exists for the topic, note this — the feature may be undocumented or entirely new.

## Step 3: Read the Technical Layer

1. Read `docs/technical/index.md` to get the full list of technical docs.
2. Identify which technical doc(s) are most relevant to the user's question.
3. Read those technical doc(s) to understand the architecture — Data Model, Pipeline, API Layer, Service Layer, CRUD Layer, Frontend, and Component Checklist.

If no technical doc exists for the topic, note this — the feature may be undocumented or entirely new.

## Step 4: Read Relevant Source Code

Based on file paths found in the technical doc(s) and the nature of the user's question, read the actual source files to ground your answer in the current implementation:

- **Backend**: models, schemas, API routes, CRUD queries, services under `backend/src/`
- **Frontend**: pages, components, services under `frontend_erp/src/`
- **Database**: migration SQL in `scripts/sql/` if relevant
- **Plan files**: check `docs/plan/` for any existing plans related to this feature

Only read files that are directly relevant to the user's question. Do not read the entire codebase.

## Step 5: Write the Discussion to the discussion file

With full context from the abstract doc, technical doc, and source code, write the complete discussion into the file created in Step 0. The content should:

1. **Be grounded in facts.** Reference specific documentation sections and source file paths when making claims. Do not speculate about how something works — either you read it or you say you don't know.
2. **Layer your answer.** Start with the high-level (abstract) context, then go into technical details as needed. Match the depth to what the user is asking.
3. **Identify gaps.** If documentation is missing, outdated, or inconsistent with the code, call it out explicitly.
4. **For new features:** If the user is discussing a feature that doesn't exist yet, explain what currently exists that's related (if anything), what would need to be built, and which existing systems it would interact with. Suggest using `/feature-plan` if the user wants to proceed with planning.
5. **For existing features:** Explain how the feature works end-to-end, referencing the documentation and actual implementation. If the user has a specific question (e.g., "why does X happen?", "can we change Y?"), focus your answer on that.
6. **Keep it conversational.** This is a discussion, not a report. Be direct and concise. Use bullet points and code references where helpful.

### Workflow Presentation Format

When presenting workflows (user flows, pipelines, multi-step processes), structure each workflow as follows:

- Use an `## H2` heading for each workflow/path (e.g., `## Payslip Path (HR-initiated)`).
- Under each workflow, include a `### Current State` subsection with an ASCII flow diagram showing the existing steps. Each step in the diagram must be prefixed with the role performing it in square brackets (e.g., `[HR]`, `[Finance]`, `[CEO]`, `[Employee]`). Include system side effects (status changes, notifications, auto-created records) as indented annotations below each step.
- Include a `### New State` subsection as a placeholder with `_Pending comments._` — this is where the user will add their comments, and the `### New State` diagram will be filled in later based on that feedback.

Example structure:

```markdown
## Feature Path (Role-initiated)

### Current State

\```
[Role A] Does something
  │
  │   system side effect
  │
  ▼
[Role B] Does next thing
  │
  ▼
Done
\```

### New State

_Pending comments._
```

### Suggested Next Steps Section

At the end of the discussion file, include a "Next Steps" section if appropriate:

- `/feature-plan` — if the user wants to plan a new feature or enhancement
- `/feature-update` — if the user wants to modify an existing implemented feature
- Specific files to review — if the user wants to dig deeper into the implementation

**IMPORTANT: The entire discussion result MUST be written to the discussion file created in Step 0 (`docs/discussion/{YYMMDD}_{topic_slug}.md`). After writing, tell the user the file path where the discussion is available.**
