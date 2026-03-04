# Recall Dashboard

**Feature**: Recall heatmap with two-level memory visualization and quiz history matrix
**Project**: Learning App

---

## Problem Statement

1. Users take quizzes over time but have no way to see which topics and lessons they are strong in and which are slipping.
2. Without visibility into their overall learning state, users cannot make informed decisions about what to study next.
3. The system tracks recall at two levels (topic and lesson), so the dashboard must expose both levels.

---

## Proposed Solution

Adapt the recall dashboard from `coach_weight` with these key changes:

- **Two-level recall**: Topic cards are expandable to show per-lesson recall scores (coach_weight only showed topic level).
- **Nested lessons**: Each `TopicRecallItem` includes a `lessons[]` list of `LessonRecallItem` with individual m(t) values.
- **Lesson-level stats**: `lessons_at_risk` count added to summary stats.
- **Quiz launch from dashboard**: Buttons on topic cards and lesson rows navigate to quiz page with scope pre-filled.

---

## Current Implementation Analysis

### What Exists (keep as-is)

| Component | File (coach_weight) | Status |
|-----------|---------------------|--------|
| Recall formula | `models/user_topic_memory.py` → `recall_probability()` | Keep — same m(t) formula |
| Topic memory CRUD | `crud/crud_topic_memory.py` → `get_all_memory_states()` | Keep — used by recall map |
| Quiz log count | `crud/crud_quiz_log.py` → `get_user_total_quiz_count()` | Keep — used by recall map |
| Topic matrix aggregation | `crud/crud_quiz_log_topic.py` → `get_topic_quiz_matrix()` | Keep — matrix logic |
| Topic card styling | `frontend/.../LearningProgressCards.jsx` | Keep — color mapping and layout |
| Quiz matrix grid | `frontend/.../QuizPrincipleMatrix.jsx` | Keep — cell rendering logic |
| API client calls | `frontend/src/services/api.js` → `getRecallMap()` | Keep — fetch pattern |

### What Changes

| Component | Current (coach_weight) | Proposed (learning) |
|-----------|----------------------|---------------------|
| Recall map response | `TopicRecallItem` with topic-only data | `TopicRecallItem` with nested `lessons: LessonRecallItem[]` |
| Summary stats | `global_recall`, `topics_at_risk` | Add `lessons_at_risk` |
| Topic cards | Static cards, no expansion | Expandable cards with nested lesson list |
| Quiz launch | No navigation from dashboard | Buttons on topics/lessons → quiz page with scope |
| Domain | 13 hardcoded health topics | User-defined topics (general domain) |
| Data source for lessons | N/A (topic-only) | `UserLessonMemory` table |

---

## Implementation Plan

### Key Workflow

**To Delete:** None
**To Update:** None
**To Add New:**

Two data flows (see `docs/technical/system_pipelines.md`):

```
Recall Map:
  GET /api/quiz/recall-map
    → Load all UserTopicMemory + UserLessonMemory + quiz count
    → For each topic: calculate topic m(t)
    → For each lesson in topic: calculate lesson m(t)
    → Compute global_recall, topics_at_risk, lessons_at_risk
    → Return { topics[] (with nested lessons[]), summary }

Topic Matrix:
  GET /api/quiz/topic-matrix
    → Load all QuizLog for user, ordered chronologically
    → Assign global column_index (1-based)
    → Group by topic_id
    → Return { topics[] (with quizzes[]), max_quiz_count }
```

### Database Schema

**To Delete:** None
**To Update:** None
**To Add New:**

No new tables. This feature reads from tables defined in the Quiz feature:
- `user_topic_memory`
- `user_lesson_memory`
- `quiz_logs`

### CRUD

**To Delete:** None
**To Update:** None
**To Add New:**

File: `backend/src/crud/crud_quiz_log.py` — add function:

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_all_quiz_logs` | `(db, username) -> List[QuizLog]` | All quiz logs ordered by created_at (for matrix) |

**Copy from:** `coach_weight/backend/src/crud/crud_quiz_log.py` — `get_user_quiz_logs()` with no limit.

All other CRUD functions are already defined in the Quiz feature plan:
- `crud_topic_memory.get_all_memory_states()`
- `crud_lesson_memory.get_all_lesson_memories()`
- `crud_quiz_log.get_user_total_quiz_count()`

### Services

**To Delete:** None
**To Update:** None
**To Add New:**

File: `backend/src/service/recall_service.py`

```python
class RecallService:
    def get_recall_map(db, username) -> RecallMapResponse:
        """Compute two-level recall map.
        1. Load all UserTopicMemory, UserLessonMemory, quiz count
        2. For each topic: compute topic m(t), then for each lesson compute lesson m(t)
        3. Never-reviewed: m(t) = 1.0 (neutral, not alarming)
        4. Compute global_recall = mean of topic m(t)s
        5. Count topics_at_risk (m(t) < 0.5), lessons_at_risk (m(t) < 0.5)
        """

    def get_topic_matrix(db, username) -> TopicMatrixResponse:
        """Build quiz history grid.
        1. Load all QuizLog ordered by created_at
        2. Assign global column_index (1-based, chronological)
        3. Group by topic_id into rows
        4. Each cell: quiz_id, result, asked_at, column_index, lesson_name
        """
```

**Copy from:** `coach_weight/backend/src/api/quiz_dashboard_memory.py` (recall-map and topic-matrix endpoint logic)
**Modify:**
- Extract inline endpoint logic into `RecallService` class.
- Add lesson-level recall: iterate `UserLessonMemory` records grouped by topic, compute per-lesson m(t), nest inside `TopicRecallItem`.
- Add `lessons_at_risk` to summary computation.
- Replace `principle_title` with `lesson_name` in matrix tooltips.
- Use `topic_lookup.get_lesson_name()` instead of `get_principle_title()`.

Pydantic schemas — file: `backend/src/schemas/recall_dashboard.py`

```python
class LessonRecallItem(BaseModel):
    lesson_id: int
    lesson_name: str
    recall_probability: float
    forgetting_rate: float
    last_review_at: Optional[datetime]
    review_count: int
    correct_count: int

class TopicRecallItem(BaseModel):
    topic_id: str
    topic_name: str
    lesson_count: int
    recall_probability: float
    forgetting_rate: float
    last_review_at: Optional[datetime]
    review_count: int
    correct_count: int
    lessons: List[LessonRecallItem]       # NEW — nested lessons

class RecallMapResponse(BaseModel):
    topics: List[TopicRecallItem]
    global_recall: float
    topics_at_risk: int
    lessons_at_risk: int                   # NEW

class TopicQuizAttempt(BaseModel):
    quiz_id: int
    result: Optional[str]
    asked_at: Optional[datetime]
    column_index: int
    lesson_name: str                       # Changed from principle_title

class TopicMatrixRow(BaseModel):
    topic_id: str
    topic_name: str
    lesson_count: int
    last_quiz_at: Optional[datetime]
    quizzes: List[TopicQuizAttempt]

class TopicMatrixResponse(BaseModel):
    topics: List[TopicMatrixRow]
    max_quiz_count: int
```

**Copy from:** `coach_weight/backend/src/schemas/quiz_dashboard.py`
**Modify:** Add `LessonRecallItem` schema. Add `lessons` field to `TopicRecallItem`. Add `lessons_at_risk` to `RecallMapResponse`. Replace `principle_title` with `lesson_name`.

### API Endpoints

**To Delete:** None
**To Update:** None
**To Add New:**

File: `backend/src/api/recall_dashboard.py`

| Method | Path | Request | Response JSON |
|--------|------|---------|---------------|
| GET | `/api/quiz/recall-map` | — | `{"topics": [{"topic_id": "...", "recall_probability": 0.85, "lessons": [{"lesson_id": 1, "recall_probability": 0.72, ...}], ...}], "global_recall": 0.78, "topics_at_risk": 2, "lessons_at_risk": 5}` |
| GET | `/api/quiz/topic-matrix` | — | `{"topics": [{"topic_id": "...", "quizzes": [{"quiz_id": 1, "result": "correct", "column_index": 3, "lesson_name": "..."}]}], "max_quiz_count": 47}` |

**Copy from:** `coach_weight/backend/src/api/quiz_dashboard_memory.py` (recall-map and topic-matrix endpoints)
**Modify:** Delegate to `RecallService` instead of inline logic. Return nested `LessonRecallItem` in recall map. Replace `principle_title` with `lesson_name`.

Register in `backend/src/api/api_router.py`:
```python
api_router.include_router(recall_dashboard.router, tags=["dashboard"])
```

### Testing

**To Delete:** None
**To Update:** None
**To Add New:**

Test infrastructure (`conftest.py`, `setupTests.js`, `.pre-commit-config.yaml`) is set up in the Authentication feature plan.

#### Backend Test Files

File: `backend/tests/test_recall_service.py`

- **Class: `TestRecallMap`**
  - `test_recall_map_no_quizzes` — all topics at m(t)=1.0, global_recall=1.0
  - `test_recall_map_with_topic_data` — correct topic m(t) computation
  - `test_recall_map_with_lesson_data` — correct lesson m(t) nested in topics
  - `test_topics_at_risk_count` — counts topics with m(t) < 0.5
  - `test_lessons_at_risk_count` — counts lessons with m(t) < 0.5
  - `test_global_recall_mean` — mean of topic m(t) values
  - `test_never_reviewed_shows_1_0` — never-reviewed topics/lessons = 1.0 (not 0.0)

- **Class: `TestTopicMatrix`**
  - `test_matrix_chronological_order` — column_index matches created_at order
  - `test_matrix_groups_by_topic` — quizzes grouped into correct topic rows
  - `test_matrix_lesson_name_tooltip` — each cell includes lesson_name
  - `test_matrix_empty_user` — returns empty topics with max_quiz_count=0

File: `backend/tests/test_schemas_dashboard.py`

- `test_lesson_recall_item` — all fields present and typed
- `test_topic_recall_item_with_lessons` — nested lessons list
- `test_recall_map_response` — includes lessons_at_risk
- `test_topic_matrix_response` — topics with quiz attempts

File: `backend/tests/test_api_dashboard.py`

- **Class: `TestDashboardEndpoints`**
  - `test_recall_map_endpoint` — returns 200 with correct schema
  - `test_recall_map_nested_lessons` — response includes lesson-level data
  - `test_topic_matrix_endpoint` — returns 200 with correct schema
  - `test_recall_map_requires_auth` — returns 401 without session
  - `test_topic_matrix_requires_auth` — returns 401 without session

#### Frontend Test Files

File: `frontend/src/__tests__/hooks/useDashboardData.test.js`

- `describe("useDashboardData hook")`:
  - `it("fetches recall map and topic matrix on mount")` — mocks both API calls
  - `it("manages expandedTopics state")` — toggleTopic adds/removes
  - `it("handles loading state")` — loading true during fetch
  - `it("handles API error")` — shows error state

File: `frontend/src/__tests__/components/RecallHeatmap.test.js`

- `describe("RecallHeatmap")`:
  - `it("renders topic cards")` — one card per topic
  - `it("applies green for recall > 0.7")`
  - `it("applies yellow for recall 0.5-0.7")`
  - `it("applies red for recall < 0.5")`
  - `it("expands topic to show lessons")` — click toggles LessonRecallList

File: `frontend/src/__tests__/components/RecallSummary.test.js`

- `describe("RecallSummary")`:
  - `it("renders global recall percentage")`
  - `it("renders topics at risk count")`
  - `it("renders lessons at risk count")`

File: `frontend/src/__tests__/components/TopicMatrix.test.js`

- `describe("TopicMatrix")`:
  - `it("renders topic rows")` — correct number of rows
  - `it("renders quiz cells with colors")` — green/red/grey
  - `it("shows lesson name in tooltip")` — hover tooltip

File: `frontend/src/__tests__/components/QuizLaunchButton.test.js`

- `describe("QuizLaunchButton")`:
  - `it("navigates to /quiz with topic_id")` — for topic-level button
  - `it("navigates to /quiz with lesson_id")` — for lesson-level button

### Frontend

**To Delete:** None
**To Update:** None
**To Add New:**

File: `frontend/src/pages/RecallDashboardPage.jsx`

- Main dashboard page layout
- Fetches recall map and topic matrix on mount
- Renders RecallSummary, RecallHeatmap, TopicMatrix

**Copy from:** `coach_weight/frontend/src/components/dashboard/tabs/LearningProgressTab.jsx`
**Modify:** Extract into standalone page (not a tab). Add lesson-level expansion. Add quiz launch buttons.

File: `frontend/src/components/RecallHeatmap.jsx`

- Grid of topic cards, each colored green/yellow/red by topic recall
- Shows review_count and accuracy per card
- **Expandable**: click card to toggle lesson list

**Copy from:** `coach_weight/frontend/src/components/dashboard/quiz/LearningProgressCards.jsx` (TopicCard)
**Modify:** Add expand/collapse toggle. Render `LessonRecallList` inside expanded card.

File: `frontend/src/components/LessonRecallList.jsx`

- Nested list within expanded topic card
- Each lesson row: name, recall score (colored), quiz count, accuracy
- QuizLaunchButton per lesson row

**New** — coach_weight had no lesson-level UI.

File: `frontend/src/components/RecallSummary.jsx`

- Cards: global_recall %, topics_at_risk count, lessons_at_risk count

**Copy from:** `coach_weight/frontend/src/components/dashboard/quiz/LearningProgressCards.jsx` (SummaryCard)
**Modify:** Add `lessons_at_risk` card.

File: `frontend/src/components/TopicMatrix.jsx`

- Grid: rows = topics, columns = chronological quiz attempts
- Cells colored green/red/grey by result
- Tooltip shows lesson_name + date

**Copy from:** `coach_weight/frontend/src/components/dashboard/quiz/QuizPrincipleMatrix.jsx`
**Modify:** Replace `principle_title` with `lesson_name` in tooltips. Keep sticky column, color mapping, and scrolling behavior.

File: `frontend/src/components/QuizLaunchButton.jsx`

- Button that navigates to `/quiz?topic_id=X` or `/quiz?lesson_id=Y`
- Appears on topic cards and lesson rows

**New** — coach_weight had no quiz launch from dashboard.

File: `frontend/src/hooks/useDashboardData.js`

```javascript
const { loading, recallMap, topicMatrix, expandedTopics, toggleTopic } = useDashboardData();
```

- Fetches recall map and topic matrix on mount
- Manages `expandedTopics` Set for accordion state
- Re-fetches when navigating back to dashboard

**New** — coach_weight fetched inline in component.

File: `frontend/src/services/api.js` — add dashboard methods:

```javascript
getRecallMap: () => GET /api/quiz/recall-map
getTopicMatrix: () => GET /api/quiz/topic-matrix
```

**Copy from:** `coach_weight/frontend/src/services/api.js` — same pattern.

### Documentation (`docs/tech_documentation/`)

**To Delete:** None
**To Update:** None
**To Add New:**

- `docs/technical/recall_dashboard.md` — already written, no changes needed
- `docs/technical/system_pipelines.md` — Recall Dashboard and Topic Matrix pipelines already documented

---
