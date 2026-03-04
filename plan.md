# Plan: Update Documentation to Match Current Codebase

## Summary

After comparing all existing docs against the actual codebase, here are the gaps found and the changes needed.

---

## Findings

### 1. All statuses are `Plan` but features are implemented
Every abstract doc says `Status: Plan`. The code is built and functional — all models, endpoints, services, frontend pages, and components exist.

### 2. Authentication — Bearer token support undocumented
`authenticate_user_from_request()` now checks `Authorization: Bearer <token>` header as a fallback when no cookie is present. Both the abstract and technical docs only mention cookie-based auth.

### 3. Authentication — `role` column listed but doesn't exist
The technical doc's `Users` data model table includes a `role` column (nullable). The actual `Users` model only has `id`, `username`, and `hashed_password`.

### 4. Quiz — New `POST /api/quiz/questions` endpoint undocumented
The bulk-create endpoint for uploading quiz questions via the API is not in any doc. This is a new pathway: questions can now be uploaded via API with Bearer auth (in addition to the offline DB insert).

### 5. Quiz — New CRUD functions undocumented
- `create_quiz_questions(db, questions)` — bulk insert
- `get_question_count_for_topic(db, topic_id)` — count by topic
- `get_total_question_count(db)` — count all

### 6. Quiz — Stale reference to prompt file
The technical doc references `markdown_notes/.claude/commands/test-knowledge.md` as the prompt reference. The actual path is `backend/resources/prompts/quiz_system_prompt.md` and the command is `.claude/commands/quiz_generate.md`.

### 7. Quiz — Architecture diagram missing API upload path
The architecture section only shows the offline agent → DB path. Now there's also an agent → API → DB path.

### 8. System pipelines — Missing quiz upload pipeline
No pipeline for the `POST /api/quiz/questions` upload flow.

---

## Changes

### File 1: `docs/abstract/authentication.md`
- Change `Status: Plan` → `Status: Done`
- In Solution, mention that the system also supports token-based access for tools and scripts (Bearer token)

### File 2: `docs/abstract/quiz.md`
- Change `Status: Plan` → `Status: Done`
- In Solution paragraph, add that questions can also be uploaded via an API endpoint (not only direct DB insert)
- Update Scope "Not included" to remove "On-the-fly question generation" wording ambiguity — clarify that API upload is supported but runtime generation is not

### File 3: `docs/abstract/recall_dashboard.md`
- Change `Status: Plan` → `Status: Done`

### File 4: `docs/technical/authentication.md`
- Remove `role` column from the `Users` data model table
- Update the architecture description to mention Bearer token support: `authenticate_user_from_request()` checks cookie first, then falls back to `Authorization: Bearer` header
- Update the Service Layer bullet for `authenticate_user_from_request` to mention Bearer fallback

### File 5: `docs/technical/quiz.md`
- Update architecture diagram to show both paths: offline agent → DB, and agent → API → DB
- Update the architecture description to mention the API upload path
- Add `POST /api/quiz/questions` to the API Layer table
- Add `create_quiz_questions`, `get_question_count_for_topic`, `get_total_question_count` to the CRUD Layer section
- Fix stale prompt reference from `markdown_notes/.claude/commands/test-knowledge.md` to `.claude/commands/quiz_generate.md`
- Add `QuizQuestionCreate` and `QuizBulkCreateResponse` mention (no need for full tables — they mirror the `QuizQuestion` columns)
- Add component checklist items for the new endpoint and CRUD functions

### File 6: `docs/technical/system_pipelines.md`
- Add a "Quiz Upload Pipeline" section with link to `quiz.md`, showing: Agent generates questions → `POST /api/quiz/questions` with Bearer token → CRUD bulk insert → response with count

### File 7: `docs/technical/index.md`
No changes needed — the page list is still correct (no new feature pages added).

### File 8: `docs/abstract/index.md`
No changes needed — the page list is still correct.

---

## Files Modified

| File | Changes |
|------|---------|
| `docs/abstract/authentication.md` | Status → Done, mention Bearer token |
| `docs/abstract/quiz.md` | Status → Done, mention API upload |
| `docs/abstract/recall_dashboard.md` | Status → Done |
| `docs/technical/authentication.md` | Remove `role` column, document Bearer fallback |
| `docs/technical/quiz.md` | Add POST endpoint, update architecture, fix prompt ref, add CRUD functions |
| `docs/technical/system_pipelines.md` | Add Quiz Upload Pipeline |
