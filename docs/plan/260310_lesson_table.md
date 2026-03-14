# Lesson Table

**Feature**: Add a normalized `Lesson` table to the database and link quiz questions to it via foreign key
**Plan Created:** 2026-03-10
**Status:** Done

---

## Problem Statement

1. Lessons are currently implicit — they exist only as denormalized attributes (`lesson_id`, `lesson_name`, `lesson_filename`) scattered across `QuizQuestion`, `QuizLog`, and `UserLessonMemory`.
2. The source of truth for lesson metadata is `topics.json`, a static file loaded into an in-memory cache (`topic_lookup.py`). There is no database-backed lesson record.
3. There is no place to store lesson content (the markdown text from which quizzes are generated) or the lesson's published date.
4. Adding a new lesson requires editing `topics.json` manually and assigning an `lesson_id` integer by hand.
5. The denormalized design means lesson metadata (name, filename) is duplicated on every `QuizQuestion` row and can drift.

---

## Proposed Solution

Add a `Lesson` model/table with the fields: `id`, `topic` (string), `title`, `published_date`, and `content`. Quiz questions will link to this table via a foreign key (`QuizQuestion.lesson_id → Lesson.id`).

A new REST endpoint `POST /api/lessons` allows creating lessons programmatically (e.g., from the lesson-youtube skill or a local agent). The `lesson_id` will be auto-incremented by the database instead of manually assigned.

`topic_lookup.py` will be updated to sync its in-memory cache from the `lessons` table instead of (or in addition to) `topics.json`. `topics.json` is kept as a seed/fallback but the DB becomes the source of truth.

Existing denormalized fields on `QuizQuestion` (`lesson_name`, `lesson_filename`, `topic_name`) are kept for now to avoid a large migration, but the `Lesson` table becomes the canonical source. A future cleanup can remove the denormalized columns.

---

## Current Implementation Analysis

### What Exists (keep as-is)

| Component | File | Status |
|-----------|------|--------|
| QuizQuestion model | `backend/src/models/quiz_question.py` | Keep — update lesson_id to FK |
| QuizLog model | `backend/src/models/quiz_log.py` | Keep — lesson_id stays denormalized (no FK, fast queries) |
| UserLessonMemory model | `backend/src/models/user_lesson_memory.py` | Keep — lesson_id stays denormalized (no FK, performance) |
| UserTopicMemory model | `backend/src/models/user_topic_memory.py` | Keep — no changes |
| Quiz API routes | `backend/src/api/quiz.py` | Keep — minor update to quiz upload endpoint |
| Quiz selector service | `backend/src/service/quiz_selector.py` | Keep — no changes |
| Answer service | `backend/src/service/answer_service.py` | Keep — no changes |
| Memory service | `backend/src/service/memory_service.py` | Keep — no changes |
| Quiz CRUD | `backend/src/crud/crud_quiz_question.py` | Keep — no changes |
| Quiz schemas | `backend/src/schemas/quiz.py` | Keep — minor update |
| topics.json | `backend/resources/topics.json` | Keep — serves as seed data, but DB becomes source of truth |

### What Changes

| Component | Current | Proposed |
|-----------|---------|----------|
| Lesson storage | Implicit in `topics.json` + denormalized on `QuizQuestion` | Normalized `Lesson` table in DB |
| Lesson ID assignment | Manual integer in `topics.json` | Auto-increment PK in `lessons` table |
| Topic-lesson lookup | `topic_lookup.py` reads `topics.json` + syncs from `quiz_questions` | `topic_lookup.py` syncs from `lessons` table |
| Quiz upload flow | Creates quiz questions directly | Validates `lesson_id` exists in `lessons` table |
| GET `/api/quiz/topics` | Reads from in-memory cache only | Cache synced from `lessons` table |

---

## Implementation Plan

### Key Workflow

#### Lesson creation flow (new)

```
Local agent or lesson-youtube skill
  │
  ▼
POST /api/lessons  { topic, title, published_date, content }
  │
  ▼
Validate: topic is a non-empty string, title is non-empty
  │
  ▼
CRUD: INSERT into lessons table → returns Lesson with auto-incremented id
  │
  ▼
Register in topic_lookup cache
  │
  ▼
Response: { id, topic, title, published_date, created_at }
```

#### Quiz upload flow (updated)

```
POST /api/quiz/questions  [{ lesson_id, topic_id, ... }]
  │
  ▼
Validate: lesson_id exists in lessons table
  │  (if not → 400 "Lesson {id} not found")
  │
  ▼
(rest of existing flow unchanged)
```

#### Topic lookup sync (updated)

```
Server startup
  │
  ▼
topic_lookup.sync_from_db(db)
  ├── SELECT from lessons table (primary source)
  └── Fallback: SELECT DISTINCT from quiz_questions (backward compat)
```

### Database Schema

**To Delete:** None

**To Update:** None (existing tables keep their columns; FK on `QuizQuestion.lesson_id` is added but existing data is compatible since lesson IDs are already integers)

**To Add New:**

New migration file: `scripts/sql/add_lessons_table.sql`

```sql
-- Add lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    topic VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    published_date DATE,
    content TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lessons_topic ON lessons(topic);

-- Seed from existing quiz_questions data
INSERT INTO lessons (id, topic, title, published_date, content)
SELECT DISTINCT ON (qq.lesson_id)
    qq.lesson_id,
    qq.topic_id,
    COALESCE(qq.lesson_name, 'Lesson ' || qq.lesson_id),
    NULL,
    NULL
FROM quiz_questions qq
ORDER BY qq.lesson_id, qq.id
ON CONFLICT (id) DO NOTHING;

-- Reset sequence to max existing ID
SELECT setval('lessons_id_seq', COALESCE((SELECT MAX(id) FROM lessons), 0) + 1, false);

-- Add FK from quiz_questions to lessons
ALTER TABLE quiz_questions
    ADD CONSTRAINT fk_qq_lesson_id FOREIGN KEY (lesson_id) REFERENCES lessons(id);
```

New model file: `backend/src/models/lesson.py`

```python
"""Lesson model — normalized lesson records."""

from datetime import date, datetime

from sqlalchemy import Column, String, Integer, Text, Date, DateTime, Index

from ..database import Base


class Lesson(Base):
    """A lesson record with topic, title, published date, and content."""

    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    title = Column(String, nullable=False)
    published_date = Column(Date, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_lessons_topic", "topic"),
    )
```

### CRUD

**To Delete:** None

**To Update:** None

**To Add New:**

New file: `backend/src/crud/crud_lesson.py`

- `create_lesson(db, topic, title, published_date, content) -> Lesson` — INSERT a new lesson. Returns the created record with auto-incremented `id`.
- `get_lesson_by_id(db, lesson_id) -> Optional[Lesson]` — SELECT by primary key.
- `get_lessons_by_topic(db, topic) -> list[Lesson]` — SELECT all lessons for a topic.
- `get_all_lessons(db) -> list[Lesson]` — SELECT all lessons ordered by topic, id.
- `update_lesson(db, lesson_id, **fields) -> Optional[Lesson]` — UPDATE mutable fields (title, content, published_date). Returns updated record or None.

### Services

**To Delete:** None

**To Update:**

`backend/src/service/topic_lookup.py`:
- Update `sync_from_db(db)` to read from the `lessons` table as the primary source, falling back to `quiz_questions` for any lessons not yet in the `lessons` table.
- The function will: `SELECT id, topic, title FROM lessons` and call `register_topic()` for each row.

**To Add New:** None — lesson creation logic is simple enough to live in CRUD + API layer.

### API Endpoints

**To Delete:** None

**To Update:**

`backend/src/api/quiz.py` — `create_questions()`:
- After `_get_user_or_401`, validate that each `lesson_id` in the payload exists in the `lessons` table. If not, return 400.

**To Add New:**

New file: `backend/src/api/lesson.py`

| Method | Path | Auth | Request | Response | Status |
|--------|------|------|---------|----------|--------|
| POST | `/api/lessons` | Bearer | `{ topic, title, published_date?, content? }` | `{ id, topic, title, published_date, created_at }` | 201 |
| GET | `/api/lessons` | Session | query: `topic` (opt) | `{ lessons: [{ id, topic, title, published_date, created_at }] }` | 200 |
| GET | `/api/lessons/{lesson_id}` | Session | — | `{ id, topic, title, published_date, content, created_at }` | 200 |
| PUT | `/api/lessons/{lesson_id}` | Bearer | `{ title?, published_date?, content? }` | `{ id, topic, title, published_date, created_at }` | 200 |

Notes:
- `POST /api/lessons` uses Bearer auth (same as quiz upload — for local agent use).
- `GET` endpoints use session auth (for the web app).
- The `content` field is excluded from list responses to keep payloads small; it's only returned by the single-lesson GET.
- Register the router in `backend/src/main.py`.

New schema file: `backend/src/schemas/lesson.py`

```python
class LessonCreate(BaseModel):
    topic: str
    title: str
    published_date: Optional[date] = None
    content: Optional[str] = None

class LessonResponse(BaseModel):
    id: int
    topic: str
    title: str
    published_date: Optional[date] = None
    created_at: datetime

class LessonDetailResponse(LessonResponse):
    content: Optional[str] = None

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    published_date: Optional[date] = None
    content: Optional[str] = None
```

### Testing

**To Delete:** None

**To Update:** None

**To Add New:**

New file: `backend/tests/test_lesson_api.py`

Unit tests:
- Create a lesson via POST and verify response fields
- Create a lesson with all optional fields (published_date, content)
- Create a lesson with only required fields (topic, title)
- List all lessons, filter by topic
- Get single lesson includes content
- Update lesson fields

Integration tests:
- Create a lesson, then upload quiz questions referencing its `lesson_id` — verify success
- Upload quiz questions with non-existent `lesson_id` — verify 400 error
- Verify `topic_lookup` cache is updated after lesson creation

Validation:
- POST with missing `topic` → 422
- POST with missing `title` → 422
- PUT with non-existent lesson_id → 404

### Frontend

**To Delete:** None

**To Update:**
- `frontend/src/App.js` — add routes for `/lessons` and `/lessons/:lessonId`
- `frontend/src/services/api.js` — add `getLessons(topic?)` and `getLessonById(lessonId)` functions

**To Add New:**
- `frontend/src/pages/LessonDashboardPage.jsx` — lists all lessons grouped by topic. Each lesson card shows title, topic, and published date. Click navigates to `/lessons/{id}`.
- `frontend/src/pages/LessonDetailPage.jsx` — fetches lesson by ID via `GET /api/lessons/{id}`, renders markdown content using `MarkdownPreview`. Shows title, topic, published date as header.
- `frontend/src/components/MarkdownPreview.jsx` — renders markdown with `react-markdown`, `remark-gfm`, and `react-syntax-highlighter` (vscDarkPlus theme). Custom styled components for all markdown elements. Dark theme with Tailwind prose classes. Adapted from fullstack_erp's exercise/MarkdownPreview.js.

**New dependencies:** `react-markdown`, `remark-gfm`, `react-syntax-highlighter`

### Documentation

#### Abstract (`docs/abstract/`)

**Update `docs/abstract/quiz.md`:**
- **Solution** section: add a sentence explaining that lessons are stored in a dedicated table and created via API before quiz questions can be uploaded.
- **Scope — Included**: add "Lesson records with topic, title, published date, and content"
- **Scope — Not included**: add "Lesson management UI (planned for future)"

#### Technical (`docs/technical/`)

**Update `docs/technical/quiz.md`:**
- **Data Model** section: add the `Lesson` model table (id, topic, title, published_date, content, created_at). Add note that `QuizQuestion.lesson_id` is now an FK to `lessons.id`.
- **Architecture** section: add `Lesson` to the database layer description.
- **Backend — API Layer** table: add the 4 lesson endpoints (POST, GET list, GET single, PUT).
- **Backend — CRUD Layer**: add `crud_lesson` functions.
- **Pipeline** section: add a note in the quiz upload pipeline that `lesson_id` is validated against the `lessons` table.
- **Component Checklist**: add checklist items for Lesson model, lesson API endpoints, lesson CRUD, lesson schemas.

**Update `docs/technical/recall_dashboard.md`:**
- **Data Model** section: add a note that the recall dashboard can now resolve lesson names from the `lessons` table (via topic_lookup cache).

---

## Dependencies

- Existing `quiz_questions` table must have valid `lesson_id` integers for the seed migration to work.
- Bearer token auth (already implemented for quiz upload) is reused for lesson creation.

## Open Questions

1. Should the quiz upload endpoint (`POST /api/quiz/questions`) **hard-fail** (400) if the `lesson_id` doesn't exist in the `lessons` table, or **soft-fail** (auto-create a stub lesson)? Plan assumes hard-fail — the agent must create the lesson first.
2. Should `topics.json` be kept long-term as a seed file, or migrated entirely to DB and removed? Plan keeps it as a backward-compatible seed for now.

---

## Change Request — 2026-03-10

**What changed:** Added frontend lesson dashboard and lesson detail view with markdown rendering.

**Why:** Users need to browse and read their lesson content directly in the web app. The lesson content is stored in markdown format and needs proper rendering with syntax highlighting, tables, and GFM support.

**Frontend additions:**
- `LessonDashboardPage` at `/lessons` — lists all lessons grouped by topic
- `LessonDetailPage` at `/lessons/:lessonId` — renders full lesson markdown content
- `MarkdownPreview` component — adapted from fullstack_erp's exercise/MarkdownPreview.js, using `react-markdown` + `remark-gfm` + `react-syntax-highlighter` with vscDarkPlus theme and dark Tailwind prose styling
- New npm dependencies: `react-markdown`, `remark-gfm`, `react-syntax-highlighter`
- API service additions: `getLessons()`, `getLessonById()`
- Updated App.js routes

**Docs updated:** `docs/abstract/quiz.md`, `docs/technical/quiz.md`

## Change Request — 2026-03-10 (2)

**What changed:** Added "Take Quiz" navigation from lesson detail page to quiz page with lesson scope pre-selected.

**Why:** Users browsing a lesson should be able to jump directly into a quiz scoped to that lesson without manually selecting the scope on the quiz page.

**Frontend updates:**
- `LessonDetailPage` — added "Take Quiz" button next to "Back to Lessons" that navigates to `/quiz?lessonId={id}`
- `QuizPage` — reads `lessonId` query param from URL on mount and initializes scope to that lesson

**Docs updated:** `docs/abstract/quiz.md`, `docs/technical/quiz.md`, `docs/plan/260310_lesson_table.md`

## Change Request — 2026-03-10 (3)

**What changed:** Redesigned lesson dashboard from grouped cards to a table view with topic column, topic filter, and sorting.

**Why:** Users need to see the topic for each lesson at a glance, filter by topic, and sort by topic name or publish date to find lessons quickly.

**Frontend updates:**
- `LessonDashboardPage` — replaced grouped card layout with a table (columns: Title, Topic, Published Date). Added topic filter dropdown. Added sort toggle for topic name and publish date (ascending/descending).

**Docs updated:** `docs/abstract/quiz.md`, `docs/technical/quiz.md`, `docs/plan/260310_lesson_table.md`

## Change Request — 2026-03-10 (4)

**What changed:** Added `topic_name` column to the `lessons` table so lessons carry their own human-readable topic name.

**Why:** The `lessons` table only stored the topic slug (e.g. `"south_china_morning_post"`). The human-readable name (e.g. `"South China Morning Post"`) was only on `quiz_questions` and the in-memory cache. The lesson dashboard and detail pages need to display the readable name.

**Database:**
- Migration `scripts/sql/add_topic_name_to_lessons.sql` — adds `topic_name` column, backfills from `quiz_questions`

**Backend updates:**
- `Lesson` model — added `topic_name` column
- `LessonResponse` / `LessonDetailResponse` schemas — added `topic_name` field
- `crud_lesson.create_lesson()` — accepts `topic_name` parameter
- `lesson.py` API — passes `topic_name` to CRUD and includes it in all responses

**Frontend updates:**
- `LessonDashboardPage` — displays `topic_name` in table and filter (falls back to `topic` slug)
- `LessonDetailPage` — displays `topic_name` instead of slug

**Docs updated:** `docs/technical/quiz.md`, `docs/plan/260310_lesson_table.md`

## Change Request — 2026-03-10 (5)

**What changed:** Added lesson-level recall score column to the lesson dashboard table.

**Why:** Users want to see at a glance how well they remember each lesson, so they can prioritize which lessons to review.

**Backend:** No changes — the existing `GET /api/quiz/recall-map` already returns per-lesson `recall_probability`.

**Frontend updates:**
- `LessonDashboardPage` — fetches recall map on mount, builds a `lessonId → recall_probability` lookup, displays a "Recall" column with percentage and color coding (green >= 70%, yellow >= 40%, red < 40%, gray for no data).

**Docs updated:** `docs/abstract/quiz.md`, `docs/technical/quiz.md`, `docs/plan/260310_lesson_table.md`
