# Chrome Test Generation

Generate the test file at `docs/chrome_test/{feature_name}.md` **before** writing the implementation plan. This ensures the E2E acceptance tests are defined upfront and all test reports are initialized to `IN QUEUE`.

Reference `docs/technical/testing_context.md` for available test users, application ports, and the sign-in/sign-out procedure. Reference `docs/chrome_test/comment_thread.md` as an example of a completed test file.

The file must start with a **Remarks** block documenting key context (port numbers, sign-in flow, cleanup instructions).

## Database Pre-Interaction

Before designing the tests, specify any database records that must exist for the tests to run. For each record, provide:
- **Table** — the target table name
- **SQL** — an `INSERT` statement (or short script) that creates the necessary seed data. UUIDs must use valid hex format (digits 0-9 and letters a-f only). Include all required columns per the actual table schema (check with `\d table_name` if unsure).
- **Purpose** — why this record is needed (e.g., "employee needs an existing leave balance to submit a request")

Include a **Cleanup** section with `DELETE` statements to remove test data from prior runs, so each test session starts clean.

These records set up the preconditions so the Chrome tests can focus on UI interactions rather than data bootstrapping. Include records for all roles involved in the tests (e.g., existing job posts for recruitment tests, existing expense categories for reimbursement tests).

## Pre-requisite

Include a pre-requisite section that instructs the tester to sign in as the correct starting user before the tests begin. Reference the sign-in/sign-out procedure from `docs/technical/testing_context.md`.

## Tests

Design ~5 integration tests that validate the feature end-to-end through real browser interactions.

For each test, specify:
- **Test name** — a short descriptive name
- **User(s) involved** — pick the appropriate test user email(s) based on the company role needed (e.g., CEO, Head of Finance, Head of HR, Head of IT, external candidate). Multi-user tests must include explicit sign-out / sign-in steps between users.
- **Steps** — use **checklist items** (`- [ ]`) for each interaction step (navigate, click, fill, verify). Each step must specify which username/email is performing the action (e.g., "As `thanhnguyenhuu.cs@gmail.com` (Head of Finance): click Approve").
- **Expected UI state** — what the screen should look like after key steps (visible elements, data, labels, empty states)
- **Error handling** — if any step produces an unexpected error or UI state, the test must flag it and fix the issue immediately before continuing
- **Report** — initialize to `IN QUEUE`. Include placeholder for itemized findings and an **Improvement Proposals** sub-list with entries formatted as:
  `+ {priority} - {proposal name} - brief description`
  where priority is `must have` or `good to have`.

## Test Coverage

Tests should cover:
1. **Happy-path CRUD** — a single user creates/views/edits/deletes the feature's primary entity.
2. **Role-based visibility** (1–3 scenarios depending on feature complexity) — verify that different roles see the correct data and controls (e.g., a regular employee sees only their own records while a manager sees the team's).
3. **Multi-user workflow** (1–3 scenarios depending on feature complexity) — a cross-role interaction where one user's action triggers or changes what another user sees (e.g., employee submits a reimbursement → finance reviews it → CEO approves it, signing in and out between each role).
4. **Validation & edge cases** — attempt invalid input, empty states, boundary values, and confirm the UI shows appropriate errors or empty-state messages.
5. **Permission guard** — confirm that a user without whitelist access to the feature's endpoints cannot access the page or sees an appropriate denial.

## Example Multi-User Test Flow (reimbursement)

1. Sign in as `alanshareteam@gmail.com` (employee) → submit a reimbursement request → verify it appears in the list.
2. Sign out → sign in as `thanhnguyenhuu.cs@gmail.com` (Head of Finance) → verify the request appears for review → approve it.
3. Sign out → sign in as `alannguyen.cs@gmail.com` (CEO) → verify the approved request is visible in the CEO dashboard.
