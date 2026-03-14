# Question-Level Recall Selection for Topic & Global Scope

**Feature**: Replace lesson-level MEMORIZE selection with question-level recall for topic-scoped and global-scoped quizzes, add bounded loops with progress squares and loop summary
**Plan Created:** 2026-03-14
**Status:** Plan
**Reference**: [Discussion — Quiz Selection Rules](../discussion/260314_quiz_selection_rules.md)

---

## Problem Statement

1. **Cases 2 & 3 lack loop UX.** When a user selects a topic (Case 2) or nothing (Case 3), there is no loop with progress squares or summary screen — unlike Case 1 (lesson scope), which shows colored squares, tracks correct/incorrect/skipped, and displays a LoopSummary after all questions.

2. **Selection is at lesson level, not question level.** The current MEMORIZE algorithm picks the weakest *lesson* and then picks a question from that lesson. This means questions the user already knows well may be served simply because they belong to a weak lesson. Question-level recall would prioritize the individual questions the user is most likely to have forgotten.

3. **Quiz type rotation adds unnecessary constraint.** The current type rotation (recall → understanding → application → analysis) limits the pool of eligible questions. Removing it lets all question types compete equally based on recall.

---

## Proposed Solution

**For Cases 2 & 3:**
- Add a bounded loop of `min(10, total_questions_in_scope)` questions.
- Add progress squares (green/red/yellow/gray) and LoopSummary — same UX as Case 1.
- Replace lesson-level MEMORIZE with **question-level recall**: each question has its own forgetting rate `n` that adapts on correct/incorrect answers. The question with the lowest recall `m(t) = exp(-n * quizzes_elapsed / 10)` is served first. Never-answered questions get `m(t) = 0.0`.
- Remove quiz type rotation — all types compete equally.
- Use a sliding window of `loop_size - 1` within scope to prevent repeats within a loop.

**Case 1 unchanged.** Lesson-scoped quizzes keep random order with sliding window dedup.

**New data model:** `UserQuestionMemory` table — same structure as `UserLessonMemory` but keyed by `quiz_question_id`. Updated on every answer alongside topic and lesson memory.

---

## Current Implementation Analysis

### What Exists (keep as-is)

| Component | File | Status |
|-----------|------|--------|
| `UserTopicMemory` model | `backend/src/models/user_topic_memory.py` | Keep — still updated on answers |
| `UserLessonMemory` model | `backend/src/models/user_lesson_memory.py` | Keep — still updated on answers |
| `select_topic_for_quiz()` | `backend/src/service/quiz_selector.py` | Keep — unused by Cases 2/3 but still used conceptually |
| `select_lesson_for_quiz()` | `backend/src/service/quiz_selector.py` | Keep — unused by Cases 2/3 now |
| Case 1 lesson-scoped path | `backend/src/service/quiz_selector.py:144-148` | Keep — unchanged |
| `get_question_for_lesson()` | `backend/src/crud/crud_quiz_question.py` | Keep — used by Case 1 |
| `get_question_count_for_topic()` | `backend/src/crud/crud_quiz_question.py` | Keep — used for loop size |
| `get_total_question_count()` | `backend/src/crud/crud_quiz_question.py` | Keep — used for loop size |
| `QuizCard` progress squares | `frontend/src/components/QuizCard.jsx` | Keep — already supports props |
| `LoopSummary` component | `frontend/src/components/LoopSummary.jsx` | Keep — reused for all scopes |
| `TopicLessonFilter` | `frontend/src/components/TopicLessonFilter.jsx` | Keep — no changes |

### What Changes

| Component | Current | Proposed |
|-----------|---------|----------|
| Cases 2/3 question selection | Lesson-level MEMORIZE → quiz type rotation → per-type dedup | Question-level recall → lowest m(t) → sliding window dedup |
| Quiz type rotation (Cases 2/3) | Rotates through 4 types, skips last 3 | Removed — all types eligible |
| `select_quiz()` Cases 2/3 path | Lines 150-168: type rotation + per-type dedup | New recall-based path calling `select_question_by_recall()` |
| `memory_service.update_memory()` | Updates topic + lesson memory | Updates topic + lesson + question memory |
| `QuizNextResponse` schema | `lesson_question_count: int` | Add `loop_question_count: int` |
| API `/api/quiz/next` | Returns `lesson_question_count` only | Also returns `loop_question_count` (scope-aware) |
| `useQuiz` loop tracking | Only tracks loop when `scope.lessonId` | Tracks loop for ALL scopes |
| `QuizPage` progress squares | Only shown when `scope.lessonId` | Shown for all scopes |

---

## Implementation Plan

### Key Workflow

**To Delete**: None.

**To Update**: The `select_quiz()` function's Cases 2/3 path.

**To Add New**: `select_question_by_recall()` function.

#### New Cases 2/3 Flow

```
GET /api/quiz/next?topic_id=coach  (or no params)
  │
  ▼
Compute scope questions:
  ├── topic_id provided → all questions WHERE topic_id = "coach"
  └── neither → all questions
  │
  ▼
Compute loop_size = min(10, scope_question_count)
  │
  ▼
Sliding window dedup:
  window = max(loop_size - 1, 0)
  exclude_ids = last `window` question IDs from quiz_log within scope
  │
  ▼
Question-level recall selection:
  For each question in scope (not in exclude_ids):
    ├── Has UserQuestionMemory with review_count > 0:
    │     recall = exp(-n * quizzes_elapsed / 10)
    └── No memory or review_count == 0:
          recall = 0.0  (prioritized)
  Pick question with LOWEST recall
  │
  ▼
INSERT QuizLog, return response with loop_question_count
```

### Database Schema

**To Delete**: None.

**To Update**: None.

**To Add New**:

Migration file: `scripts/sql/add_question_memory.sql`

```sql
CREATE TABLE IF NOT EXISTS user_question_memory (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL REFERENCES users(username),
    quiz_question_id INTEGER NOT NULL REFERENCES quiz_questions(id),
    forgetting_rate FLOAT NOT NULL DEFAULT 0.3,
    last_review_at TIMESTAMP,
    last_review_quiz_count INTEGER NOT NULL DEFAULT 0,
    review_count INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_question_forgetting_rate_positive CHECK (forgetting_rate > 0),
    CONSTRAINT uq_user_question_memory UNIQUE (username, quiz_question_id)
);

CREATE INDEX IF NOT EXISTS idx_question_memory_user
    ON user_question_memory (username);
```

ORM model file: `backend/src/models/user_question_memory.py`

```python
class UserQuestionMemory(Base):
    __tablename__ = "user_question_memory"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    quiz_question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    forgetting_rate = Column(Float, nullable=False, default=0.3)
    last_review_at = Column(DateTime, nullable=True)
    last_review_quiz_count = Column(Integer, nullable=False, default=0)
    review_count = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)

    # Same recall_probability(), update_on_correct(), update_on_incorrect()
    # as UserLessonMemory / UserTopicMemory
```

Register in `backend/src/models/__init__.py`.

### CRUD

**To Delete**: None.

**To Update**:

`backend/src/crud/crud_quiz_log.py`:
- Add `get_recent_question_ids_for_topic(db, username, topic_id, limit) -> List[int]` — like `get_recent_question_ids_for_lesson` but filtered by `topic_id` instead of `lesson_id`.
- Add `get_recent_question_ids_global(db, username, limit) -> List[int]` — same but no topic/lesson filter.

**To Add New**:

`backend/src/crud/crud_question_memory.py`:
- `get_or_create_memory(db, username, quiz_question_id) -> UserQuestionMemory`
- `get_question_memories_for_ids(db, username, question_ids: List[int]) -> List[UserQuestionMemory]` — batch load for recall computation.
- `update_memory_on_quiz_result(db, username, quiz_question_id, is_correct, current_quiz_count)` — same alpha/beta logic as topic/lesson memory.

### Services

**To Delete**: None.

**To Update**:

`backend/src/service/quiz_selector.py`:
- Update `select_quiz()`: replace lines 150-168 (Cases 2/3 path) with call to `select_question_by_recall()`.

```python
# Cases 2/3: question-level recall selection
if topic_id is not None:
    total = get_question_count_for_topic(db, topic_id)
else:
    total = get_total_question_count(db)
loop_size = min(10, total)
window = max(loop_size - 1, 0)

if topic_id is not None:
    exclude_ids = get_recent_question_ids_for_topic(db, username, topic_id, window)
else:
    exclude_ids = get_recent_question_ids_global(db, username, window)

return select_question_by_recall(db, username, topic_id=topic_id, exclude_ids=exclude_ids)
```

- Add `select_question_by_recall(db, username, topic_id=None, exclude_ids=None) -> Optional[QuizQuestion]`:

```python
def select_question_by_recall(db, username, topic_id=None, exclude_ids=None):
    query = db.query(QuizQuestion)
    if topic_id:
        query = query.filter(QuizQuestion.topic_id == topic_id)
    questions = query.all()

    qids = [q.id for q in questions]
    existing = {
        r.quiz_question_id: r
        for r in get_question_memories_for_ids(db, username, qids)
    }
    current_quiz_count = get_user_total_quiz_count(db, username)

    best = None
    lowest = float("inf")
    for q in questions:
        if exclude_ids and q.id in exclude_ids:
            continue
        mem = existing.get(q.id)
        if mem and mem.review_count > 0:
            recall = mem.recall_probability(current_quiz_count)
        else:
            recall = RECALL_NEVER_REVIEWED  # 0.0
        if recall < lowest:
            lowest = recall
            best = q
    return best
```

`backend/src/service/memory_service.py`:
- Add `quiz_question_id` parameter.
- Add call to `update_question_memory(db, username, quiz_question_id, is_correct, current_quiz_count)`.

`backend/src/service/answer_service.py`:
- Pass `quiz_log.quiz_question_id` to `update_memory()`.

### API Endpoints

**To Delete**: None.

**To Update**:

`backend/src/api/quiz.py` — `GET /api/quiz/next`:

```python
# Compute loop_question_count based on scope
if lesson_id is not None:
    loop_count = get_question_count(db, question.lesson_id)
elif topic_id is not None:
    loop_count = min(10, get_question_count_for_topic(db, question.topic_id))
else:
    loop_count = min(10, get_total_question_count(db))

return QuizNextResponse(
    ...,
    lesson_question_count=get_question_count(db, question.lesson_id),
    loop_question_count=loop_count,
)
```

**To Add New**: None (existing endpoint updated).

`backend/src/schemas/quiz.py` — `QuizNextResponse`:

```python
class QuizNextResponse(BaseModel):
    quiz_id: int
    question: str
    options: Dict[str, str]
    quiz_type: str
    topic_id: str
    lesson_id: int
    lesson_title: str
    correct_option_count: int
    lesson_question_count: int
    loop_question_count: int  # NEW — loop size for any scope
```

### Testing

**To Delete**: None.

**To Update**:

`backend/tests/test_quiz_selector.py`:
- Update `TestScopeResolution.test_scope_topic_id` and `test_scope_default` — these now use question-level recall, not type rotation.
- Remove or update any assertions about quiz type rotation in Cases 2/3.

`backend/tests/test_api_quiz.py`:
- Assert `loop_question_count` in `/api/quiz/next` response.

`backend/tests/test_memory_service.py`:
- Assert question-level memory is updated alongside topic and lesson.

**To Add New**:

`backend/tests/test_question_memory.py`:
- `test_recall_probability_never_reviewed` — returns 1.0 (model), treated as 0.0 (selector).
- `test_recall_probability_decays` — m(t) decreases with quizzes elapsed.
- `test_update_on_correct` — forgetting rate decreases by 30%.
- `test_update_on_incorrect` — forgetting rate increases by 20%, capped at 1.5.
- `test_get_or_create_memory` — creates if not exists, returns existing if present.

`backend/tests/test_question_recall_selection.py`:
- `test_never_answered_prioritized` — never-answered question selected over recently-correct one.
- `test_lowest_recall_selected` — question with lowest m(t) selected.
- `test_sliding_window_excludes_recent` — last loop_size-1 questions excluded.
- `test_cross_lesson_within_topic` — questions from multiple lessons in one loop.
- `test_loop_size_capped_at_10` — min(10, total) behavior.
- `test_all_types_eligible` — questions from all quiz types can be selected (no rotation).

`frontend/src/__tests__/hooks/useQuiz.test.js`:
- `test_loop_tracking_topic_scope` — loopProgress tracks for topic-scoped quizzes.
- `test_loop_tracking_global_scope` — loopProgress tracks for no-scope quizzes.
- `test_loop_summary_shown_topic_scope` — LoopSummary appears after loop completes.

### Frontend

**To Delete**: None.

**To Update**:

`frontend/src/hooks/useQuiz.js`:

1. `fetchNextQuiz()` — set loop total for ALL scopes (remove `scope.lessonId` guard):

```javascript
// Before:
if (scope.lessonId && data.lesson_question_count) {
    setLoopProgress((prev) => ({ ...prev, total: data.lesson_question_count }));
}

// After:
if (data.loop_question_count) {
    setLoopProgress((prev) => ({ ...prev, total: data.loop_question_count }));
}
```

2. `submitAnswer()` — track loop progress for ALL scopes (remove `scope.lessonId` guard):

```javascript
// Before:
if (scope.lessonId) { setLoopProgress(...) }

// After:
setLoopProgress(...)  // always track
```

3. `skipQuestion()` — same: remove `scope.lessonId` guard.

`frontend/src/pages/QuizPage.jsx`:

1. Pass `totalQuestions` and `loopResults` to QuizCard for ALL scopes (remove `scope.lessonId` condition):

```javascript
// Before:
totalQuestions={scope.lessonId ? loopProgress.total : null}
loopResults={scope.lessonId ? loopProgress.results : []}

// After:
totalQuestions={loopProgress.total > 0 ? loopProgress.total : null}
loopResults={loopProgress.results}
```

2. Update skip tracking in `handleNextQuiz` — remove `scope.lessonId` guard:

```javascript
// Before:
if (quiz && !result && scope.lessonId) { skipQuestion(); ... }

// After:
if (quiz && !result && loopProgress.total > 0) { skipQuestion(); ... }
```

3. Show LoopSummary for all scopes — the existing `showingSummary` logic already works since it's driven by `loopProgress.loopComplete`.

**To Add New**: None — existing components reused.

### Documentation

#### Abstract (`docs/abstract/quiz.md`)

**Update** the following sections:

- **User Flow**: Update the ASCII diagram to show that topic-scoped and global quizzes also have bounded loops, progress squares, and loop summaries.
- **How Smart Selection Works (MEMORIZE)**: Add a new sub-section "Step 3 — Pick the weakest question" explaining question-level recall for Cases 2/3. Clarify that quiz type rotation is removed for these cases.
- **User-Selected Scope**: Update the description for "A specific topic" and "All topics" to mention the loop of min(10, total) and question-level recall.
- **What the User Sees**: Update to clarify that colored progress squares appear for ALL scope selections, not just lesson scope.
- **Scope — Included**: Add "Bounded quiz loops with progress tracking for all scope selections".
- **Acceptance Criteria**: Add:
  - `- [ ] Topic-scoped quizzes show colored progress squares and loop summary`
  - `- [ ] Global-scoped quizzes show colored progress squares and loop summary`
  - `- [ ] Questions are prioritized by individual recall score (lowest first) in topic and global scope`
  - `- [ ] Loop size is min(10, total questions in scope)`

#### Technical (`docs/technical/quiz.md`)

**Update** the following sections:

- **Data Model**: Add `UserQuestionMemory` table documentation (same format as `UserLessonMemory`).
- **Pipeline**: Update the Cases 2/3 path in the ASCII diagram — replace type rotation + per-type dedup with question-level recall + sliding window.
- **Algorithms**: Add `### MEMORIZE — Question Selection (Within Scope)` section describing the question-level recall formula, never-answered = 0.0 priority, and sliding window of loop_size - 1.
- **Algorithms — Quiz Type Rotation**: Add note that rotation is only used in edge cases / legacy; Cases 2/3 no longer use it.
- **Algorithms — Question Deduplication**: Update the "Topic/global scope" description — replace per-type dedup with sliding window of loop_size - 1.
- **Backend — Service Layer**: Add `select_question_by_recall()` description.
- **Backend — CRUD Layer**: Add `crud_question_memory` entries. Add `get_recent_question_ids_for_topic()` and `get_recent_question_ids_global()`.
- **Backend — API Layer**: Add `loop_question_count` to `GET /api/quiz/next` response.
- **Frontend — Services & Hooks**: Update `useQuiz` description — loop tracking for all scopes.
- **Frontend — Pages & Routes**: Update QuizPage — progress squares and loop summary for all scopes.

---

## Dependencies

- `QuizQuestion` table must be populated (existing requirement).
- `UserTopicMemory` and `UserLessonMemory` continue to be updated alongside the new `UserQuestionMemory`.
- Frontend `QuizCard` and `LoopSummary` components already support the required props.

## Open Questions

1. **Performance at global scope**: `select_question_by_recall()` loads ALL questions when no topic is specified. With thousands of questions, this could be slow. Consider adding a SQL-level optimization (e.g., pre-filter questions with no memory record first, then compute recall only for those with records). Acceptable for now given current scale (~100-200 questions).

2. **Case 1 alignment**: Should lesson-scoped quizzes (Case 1) also use question-level recall instead of random order? The discussion leaves Case 1 unchanged, but the question memory is still built up from Case 1 answers. This can be a follow-up.

## Change Request — 2026-03-14

**Auto-fetch quiz on page load.** The quiz page now loads the first quiz immediately when the user navigates to `/quiz`, instead of showing an empty state with a "Select a scope and click Next Quiz to begin" message. Changing scope also auto-fetches a new quiz.

**What changed:**
- `QuizPage.jsx`: `autoFetchRef` is set to `true` on mount for all scopes (not just when `lessonId` param is present). `handleScopeChange` sets `autoFetchRef = true` for all scope changes (not just lesson scope). The second `useEffect` triggers fetch when `autoFetchRef` is true regardless of scope type.
- Empty state message changed from instructional to generic "No quiz loaded."
- Abstract doc User Flow updated to reflect immediate loading.
- Technical doc QuizPage description updated.
