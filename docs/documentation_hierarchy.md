# Documentation Hierarchy

All feature documentation lives under `docs/` in two levels. Each level serves a different audience and purpose. When documenting a feature, write one file per feature at each level that applies.

```
docs/
├── abstract/          # Level 1 — What and why
├── technical/         # Level 2 — How it works
└── documentation_hierarchy.md   # This file
```

---

## Level 1: Abstract (`docs/abstract/`)

- **Audience:** Managers, clients, stakeholders, new team members.
- **Purpose:** Explain what the feature does and why it exists. Enable decision-making without technical knowledge.

### Rules

1. **Include a status.** Every feature page must have a `Status` field at the top: `Plan`, `In Progress`, or `Done`.
2. **Link to related docs.** Include a `Related Docs` section linking to the technical file for the same feature.
3. **No code, no file paths, no technical jargon.** If a term is unavoidable (e.g., "API"), explain it in plain language.
4. **Start with Problem and Solution.** Use two sections: `## Problem` explains the user need or business goal, and `## Solution` describes what the feature does to address it.
5. **Describe the user experience.** Walk through what happens from the user's perspective, step by step.
6. **State the scope.** List what is included and what is explicitly out of scope.
7. **Include acceptance criteria.** Bullet points that define "done" in terms a non-technical person can verify (e.g., "User receives an email within 30 seconds").
8. **Use ASCII diagrams for flows.** Plain-text flowcharts or sequence diagrams when the feature involves multiple steps or actors. Keep them inside fenced code blocks so formatting is preserved.
9. **Keep it to one page.** If the document exceeds ~300 lines, split the feature into sub-files.

### Template

```markdown
# Feature Name

[< Prev: ...](./prev.md) | [Parent](./index.md) | [Next: ... >](./next.md)

**Status:** Plan | In Progress | Done

## Related Docs
- Technical: [technical/feature_name.md](../technical/feature_name.md)

## Problem
Why this feature needs to exist.

## Solution
One-paragraph summary of what the feature does to address the problem.

## User Flow
Step-by-step walkthrough from the user's point of view.
Use an ASCII diagram for multi-step flows.

## Scope
- Included: ...
- Not included: ...

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

---

[< Prev: ...](./prev.md) | [Parent](./index.md) | [Next: ... >](./next.md)
```

### Example (Payment Top-Up)

> **Problem:** Users need to purchase credits to use paid products.
>
> **Overview:** Users select a credit package, enter billing details, and complete payment via Stripe. Credits are added to their balance immediately after successful payment.
>
> **User Flow:**
> ```
> User selects package
>       |
>       v
> Fills billing info
>       |
>       v
> Redirected to payment page
>       |
>       v
> Completes payment
>       |
>       v
> Returns to success page --> Credits available
> ```

---

## Level 2: Technical (`docs/technical/`)

- **Audience:** Developers joining the project, code reviewers, future maintainers.
- **Purpose:** Explain how the feature works at an architectural level. A developer should be able to read this and understand the system design without reading source code.

### Rules

1. **Describe the architecture, not the code.** Focus on components, their responsibilities, and how data flows between them.
2. **Name the layers.** Specify which parts are frontend, backend API, service, CRUD, database, and external service.
3. **Document the data model.** Use the SQLAlchemy class name (e.g., `**`UserPrincipleProgress`**`), not the database table name. List columns, types, and constraints.
4. **Document each layer.** Describe the API layer (endpoints, methods, request/response), service layer (business logic, orchestration), LLM requests layer (if applicable — see rule 10), and CRUD layer (database operations).
5. **Explain integrations.** For any external service (Stripe, GCP, Microsoft Graph), describe what the integration does, what credentials it needs, and how errors are handled.
6. **Include a pipeline diagram.** Use a vertical ASCII pipeline diagram (top-to-bottom with `│`, `▼`, `├──`, `└──` connectors) to show the request lifecycle. Do not use horizontal multi-column sequence diagrams. The section heading must be `## Pipeline`.
7. **State constraints and edge cases.** Rate limits, token expiration, retry logic, concurrency concerns.
8. **Include a component checklist at the bottom.** List every component (endpoint, model, service, UI page, etc.) the feature requires as checkboxes. Use `- [x]` for done and `- [ ]` for not done. Place this section at the end of the document, just before the navigation footer.
9. **Link to related docs.** Start with a `Related Docs` section linking to the abstract file for the same feature.
10. **Document LLM calls.** If the feature makes LLM calls, include a `Backend — LLM Requests Layer` section between the Service Layer and CRUD Layer. For each LLM caller, document: (a) the prompt structure as an ASCII diagram showing system prompt file, user prompt components, and any multimodal parts; (b) the output schema as a table listing every field with type and description. Include the model name, temperature, and whether output is structured JSON or free-text.

### System Pipelines Page (`technical/system_pipelines.md`)

The technical level must include a **System Pipelines** page as the first entry in `index.md`. This page is a cross-cutting overview, not a feature page, so it does **not** follow the per-feature template above. Instead it must:

1. **Contain only ASCII data-flow diagrams.** No prose paragraphs, no markdown tables, no duplicated feature-specific details. Each section is a heading followed by a single fenced code block.
2. **Show one pipeline per user entry point.** Each distinct way a user interacts with the system (e.g., send text message, upload image, take a quiz, trigger a proactive reminder) gets its own named pipeline diagram.
3. **Link to feature pages.** Each pipeline heading must include a markdown link to the technical feature page(s) that document the pipeline in full detail (e.g., `## Chat Message Pipeline — [details](./ai_coaching_chat.md)`).
4. **No Component Checklist.** This is a cross-cutting overview, not a feature with its own components.
5. **Keep it current.** When a new feature or pipeline is added, update the overview with a corresponding diagram and link.

### Template

```markdown
# Feature Name — Technical Design

[< Prev: ...](./prev.md) | [Parent](./index.md) | [Next: ... >](./next.md)

## Related Docs
- Abstract: [abstract/feature_name.md](../abstract/feature_name.md)

## Architecture
Which layers are involved and what each one does.
Diagram showing component relationships.

## Data Model
Tables, columns, types, relationships.

## Pipeline
Vertical ASCII pipeline diagram showing the full request lifecycle.

## Algorithms
Key algorithms and logic used in this feature. Use bullet points — do not write wall-of-text paragraphs. Each algorithm gets an `### H3` heading followed by itemized bullets.

## Backend — API Layer
| Method | Path | Auth | Request | Response | Status |
|--------|------|------|---------|----------|--------|
| POST   | ...  | JWT  | ...     | ...      | 201    |

## Backend — Service Layer
Business logic, orchestration, external API calls.

## Backend — LLM Requests Layer
_Include this section only if the feature makes LLM calls._

### LLM Caller Name

Prompt structure (ASCII diagram):
```
+----------------------------------------------------------+
|  SYSTEM PROMPT                                           |
|  (resources/prompts/system_prompt_file.md)               |
|  - What the prompt instructs                             |
+----------------------------------------------------------+
|                                                          |
+----------------------------------------------------------+
|  USER PROMPT  (built by ...)                             |
|                                                          |
|  +----------------------------------------------------+  |
|  | Component 1 — e.g. context, user message           |  |
|  +----------------------------------------------------+  |
|  | Component 2 — e.g. format instructions             |  |
|  +----------------------------------------------------+  |
|                                                          |
+----------------------------------------------------------+
```

Output schema table:

**`OutputSchemaClass`** — model, temperature, output type:

| Field | Type | Description |
|-------|------|-------------|
| `field_name` | type | What this field contains |

## Backend — CRUD Layer
Database operations, queries, transactions.

## Frontend — Pages & Routes
Routes, page components, and their responsibilities.

## Frontend — Components
Reusable UI components involved in this feature.

## Frontend — Services & Hooks
API service functions, custom hooks, context usage.

## External Integrations
Service, purpose, credentials, error handling.

## Constraints & Edge Cases
- ...

## Component Checklist

- [x] Database model — `users` table with auth fields
- [x] POST /login endpoint — validates credentials, returns JWT
- [ ] Google OAuth flow — verifies Google token, creates/links user
- [ ] Frontend login page — sign-in form with email and Google button

---

[< Prev: ...](./prev.md) | [Parent](./index.md) | [Next: ... >](./next.md)
```

---

## Diagram Conventions

All diagrams must be plain ASCII art inside fenced code blocks. Do not use Mermaid, PlantUML, or any rendering-dependent format. ASCII diagrams are universally readable in any editor, terminal, or LLM context.

### Flowchart

```
Start
  |
  v
[Check condition] --Yes--> [Action A] --> End
  |
  No
  |
  v
[Action B] --> End
```

### Pipeline Diagram

```
User selects package
  │
  ▼
POST /api/checkout (package_id)
  │
  ▼
Create Stripe session
  │
  ▼
Redirect to Stripe payment page
  │
  ▼
User completes payment
  │
  ▼
Stripe webhook → POST /api/webhook
  │
  ▼
Finalize order ──> INSERT credits to DB
```

### Component / Layer Diagram

```
+-----------+     +-----------+     +----------+
|  Frontend | --> |  Backend  | --> | Database |
+-----------+     +-----------+     +----------+
                       |
                       v
                  +-----------+
                  |  Stripe   |
                  +-----------+
```

### Rules for Diagrams

1. Always wrap in a fenced code block (triple backticks).
2. Use `-->`, `---`, `|`, `v`, `+--+` for connections and boxes.
3. Label arrows inline (e.g., `--POST-->`, `--webhook-->`).
4. Keep lines under 80 characters wide when possible.
5. Align columns for sequence diagrams so participants read left to right.

---

## Naming Convention

Use the same filename across both levels for the same feature:

```
docs/abstract/payment_topup.md
docs/technical/payment_topup.md
```

For broad features, use a subfolder mirrored across both levels:

```
docs/abstract/auth/login.md
docs/abstract/auth/signup.md
docs/abstract/auth/password_reset.md

docs/technical/auth/login.md
docs/technical/auth/signup.md
docs/technical/auth/password_reset.md
```

---

## File Structure & Navigation

### `index.md` as outline

Every level folder (and every subfolder within it) must contain an `index.md` that serves as the outline for that section. It lists all pages with a one-line description and links to each.

```markdown
# Authentication — Abstract

| # | Page | Description |
|---|------|-------------|
| 1 | [Login](./login.md) | Email/password and Google OAuth login |
| 2 | [Signup](./signup.md) | Multi-step registration with OTP |
| 3 | [Password Reset](./password_reset.md) | Email-based password reset |
```

### Prev / Next navigation

Every page (except `index.md`) must include navigation links at both the **top** and **bottom** of the page, linking to the previous page, next page, and back to the parent `index.md`. Use the order defined in `index.md`. The middle link is labelled **Parent**. Place the top navigation immediately after the title (before any content sections) and the bottom navigation at the very end of the file, preceded by a horizontal rule.

```markdown
# Feature Name

[< Prev: Login](./login.md) | [Parent](./index.md) | [Next: Password Reset >](./password_reset.md)

... page content ...

---

[< Prev: Login](./login.md) | [Parent](./index.md) | [Next: Password Reset >](./password_reset.md)
```

For the first page, omit Prev. For the last page, omit Next:

```markdown
[Parent](./index.md) | [Next: Signup >](./signup.md)
```

```markdown
[< Prev: Signup](./signup.md) | [Parent](./index.md)
```

### Rules

1. **`index.md` is required** in every level folder and subfolder that contains more than one `.md` file.
2. **Keep `index.md` as outline only.** No feature content — just the table of links and one-line descriptions.
3. **Maintain page order.** The Prev/Next links must follow the same sequence as the `index.md` table.
4. **Update navigation when adding or removing pages.** When a new page is inserted, update the Prev/Next links on its neighbours and add it to `index.md`.
5. **Subfolder `index.md` gets Prev / Next navigation.** A subfolder's `index.md` must include navigation at both top and bottom, linking to the previous section, the parent index, and the next section, using the order defined in the parent `index.md`. The same first/last omission rules apply.
6. **Navigation appears at both top and bottom.** Every page (including subfolder `index.md`) must display the same Prev / Parent / Next links at the top (after the title) and at the bottom (after a horizontal rule).

---

## When to Write Each Level

| Situation | Abstract | Technical |
|-----------|----------|-----------|
| New feature request from client | Yes | — |
| Feature approved, design phase | Yes | Yes |
| Ready to build | Yes | Yes |
| Bug fix or small change | — | Optional |
| Documenting existing feature | Yes | Yes |

Write top-down: abstract first, then technical. Each level should be reviewable independently — do not assume the reader has read the other level.
