# Lesson Quiz Loop Summary

**Feature**: Show a summary card (correct/incorrect counts) after the user completes all quiz questions for a lesson, with a "Next Quiz" button to start the next loop
**Plan Created:** 2026-03-11
**Status:** Plan

---

## Problem Statement

1. When a user takes quizzes scoped to a specific lesson (e.g., arriving from a lesson detail page), the system has a finite set of questions for that lesson (e.g., 10).
2. After the user answers all 10 questions, the system silently starts repeating questions. The user has no indication they've completed a full pass.
3. There is no milestone feedback — the user doesn't know how many they got right or wrong across the loop.
4. Users would benefit from a summary after each complete pass, giving them a sense of progress and encouraging another loop for reinforcement.

---

## Proposed Solution

After every N answers (where N = total questions for the lesson), display a **Loop Summary** interstitial card that replaces the quiz area. The card shows:
- Loop number (1st pass, 2nd pass, etc.)
- Correct count and incorrect count
- Accuracy percentage
- A "Next Quiz" button to begin the next loop

The loop is count-based: every N answers triggers a summary, regardless of whether questions repeated within the loop. This keeps the logic simple and predictable.

**Key design decisions:**
- **Loop tracking lives in the frontend.** The backend only adds one new field (`lesson_question_count`) to the quiz response. All loop state (counter, correct/incorrect tallies) is session-level React state in the `useQuiz` hook. This avoids new database tables or backend complexity.
- **Loop resets on scope change or page navigation.** Since loop state is React state, it naturally resets when the user changes the scope filter or leaves the page.
- **Summary only appears for lesson-scoped quizzes.** When the scope is "all topics" or a specific topic, different lessons may be served each time, so a per-lesson loop summary doesn't apply.

---

## Current Implementation Analysis

### What Exists (keep as-is)

| Component | File | Status |
|-----------|------|--------|
| Quiz selector with dedup/fallback | `backend/src/service/quiz_selector.py` | Keep — loop is frontend concern |
| Answer grading + memory update | `backend/src/service/answer_service.py` | Keep — no change needed |
| QuizCard component | `frontend/src/components/QuizCard.jsx` | Keep — unchanged |
| QuizResult component | `frontend/src/components/QuizResult.jsx` | Keep — unchanged |
| CRUD `get_question_count(db, lesson_id)` | `backend/src/crud/crud_quiz_question.py` | Keep — already provides the count we need |
| TopicLessonFilter component | `frontend/src/components/TopicLessonFilter.jsx` | Keep — unchanged |

### What Changes

| Component | Current | Proposed |
|-----------|---------|----------|
| `QuizNextResponse` schema | No question count field | Add `lesson_question_count: int` |
| `GET /api/quiz/next` handler | Returns quiz without count | Includes `lesson_question_count` from bank |
| `useQuiz` hook | No loop tracking | Tracks `loopProgress` (answered, correct, incorrect, loop number) |
| `QuizPage` | Always shows quiz or empty state | Shows `LoopSummary` when loop is complete |

---

## Implementation Plan

### Key Workflow

**To Delete:** None

**To Update:** None

**To Add New:**

New flow when user is quizzing with lesson scope:

```
User answers quiz (lesson-scoped)
  |
  v
Frontend increments loopProgress.answered
  |
  v
loopProgress.answered === lesson_question_count?
  |           |
  No          Yes
  |           |
  v           v
Show result   Show result, then on "Next Quiz" click:
as usual      show LoopSummary card
              (loop #, correct, incorrect, accuracy)
                |
                v
              User clicks "Next Quiz" on summary
                |
                v
              Reset loopProgress (increment loop number)
                |
                v
              fetchNextQuiz() — begins next loop
```

### Database Schema

**To Delete:** None

**To Update:** None

**To Add New:** None — no database changes required.

### CRUD

**To Delete:** None

**To Update:** None

**To Add New:** None — `get_question_count(db, lesson_id)` already exists in `backend/src/crud/crud_quiz_question.py:34`.

### Services

**To Delete:** None

**To Update:** None

**To Add New:** None — no service logic changes.

### API Endpoints

**To Delete:** None

**To Update:**

`GET /api/quiz/next` — file: `backend/src/api/quiz.py`

Add `lesson_question_count` to the response. Use existing `get_question_count(db, question.lesson_id)`.

Updated response schema (`backend/src/schemas/quiz.py`):

```python
class QuizNextResponse(BaseModel):
    quiz_id: int
    question: str
    options: Dict[str, str]
    quiz_type: str
    topic_id: str
    lesson_id: int
    correct_option_count: int
    lesson_question_count: int  # NEW — total questions in bank for this lesson
```

Response example:
```json
{
  "quiz_id": 42,
  "question": "What is the key principle of...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "quiz_type": "recall",
  "topic_id": "coach",
  "lesson_id": 7,
  "correct_option_count": 1,
  "lesson_question_count": 10
}
```

**To Add New:** None

### Testing

**To Delete:** None

**To Update:**

- `backend/tests/test_api_quiz.py` — Update existing `GET /api/quiz/next` tests to assert `lesson_question_count` is present in response.
- `backend/tests/test_schemas_quiz.py` — Update `QuizNextResponse` schema tests to include the new field.
- `frontend/src/__tests__/components/QuizLaunchButton.test.js` — Update mock data if it constructs `QuizNextResponse` objects.

**To Add New:**

- `frontend/src/__tests__/components/LoopSummary.test.js` — Test rendering with different correct/incorrect/loop values.
- `frontend/src/__tests__/hooks/useQuiz.test.js` — Test loop progress tracking: increments on answer, resets on scope change, triggers summary at boundary.

### Frontend

**To Delete:** None

**To Update:**

1. **`frontend/src/hooks/useQuiz.js`** — Add loop tracking state:

   ```javascript
   const [loopProgress, setLoopProgress] = useState({
     answered: 0,
     correct: 0,
     incorrect: 0,
     loopNumber: 1,
     total: 0,          // set from lesson_question_count
     loopComplete: false,
   });
   ```

   - In `fetchNextQuiz`: set `loopProgress.total` from `data.lesson_question_count` on first fetch (when `loopProgress.total === 0`).
   - In `submitAnswer`: after receiving the result, increment `answered` and `correct`/`incorrect`. If `answered === total` and scope is lesson-scoped (`scope.lessonId != null`), set `loopComplete: true`.
   - Add `startNextLoop()` function: sets `loopComplete: false`, increments `loopNumber`, resets `answered/correct/incorrect` to 0, calls `fetchNextQuiz()`.
   - In `reset()` and `setScope()`: reset `loopProgress` entirely (back to loop 1, all zeros).
   - Export `loopProgress` and `startNextLoop`.

2. **`frontend/src/pages/QuizPage.jsx`** — Add loop summary display:

   - Import `LoopSummary` component.
   - Destructure `loopProgress` and `startNextLoop` from `useQuiz()`.
   - After the result is shown and user clicks "Next Quiz": if `loopProgress.loopComplete`, show `LoopSummary` instead of fetching next quiz.
   - The "Next Quiz" button behavior changes: when `loopComplete` is true, clicking it shows the summary (or the summary auto-appears); the summary's own "Next Quiz" button calls `startNextLoop`.

   Revised "Next Quiz" button logic:
   ```
   if loopComplete and result shown → show LoopSummary
   else → fetchNextQuiz as usual
   ```

**To Add New:**

3. **`frontend/src/components/LoopSummary.jsx`** — New component:

   Props: `loopProgress` (object), `onNextLoop` (function)

   Display:
   - Heading: "Loop {loopNumber} Complete"
   - Stats row: correct count (green), incorrect count (red), accuracy percentage
   - Visual bar showing correct vs incorrect proportion
   - "Next Quiz" button (calls `onNextLoop`)

   Styling: matches existing dark theme (`bg-gray-700`, `border-gray-600`, Tailwind classes consistent with QuizCard/QuizResult).

### Documentation

#### Abstract (`docs/abstract/`)

**Update `docs/abstract/quiz.md`:**

- **User Flow** — Add a step after "User sees result" for the loop summary:
  ```
  If all questions for this lesson have been answered (one loop):
    User sees a summary: correct count, incorrect count, accuracy
    User clicks "Next Quiz" to begin the next loop
  ```
- **Scope → Included** — Add: "Loop summary after completing all questions for a lesson"
- **Acceptance Criteria** — Add:
  - `[ ] After answering all questions for a lesson, user sees a loop summary with correct/incorrect counts`
  - `[ ] User can click "Next Quiz" on the summary to start another loop`
  - `[ ] Loop counter increments on each completed pass`

#### Technical (`docs/technical/`)

**Update `docs/technical/quiz.md`:**

- **Backend — API Layer** — Update `GET /api/quiz/next` response column to note `lesson_question_count` field.
- **Frontend — Components** — Add `LoopSummary` component entry with props and description.
- **Frontend — Services & Hooks** — Update `useQuiz` description to mention `loopProgress` state and `startNextLoop` function.
- **Component Checklist** — Add:
  - `[ ] Frontend LoopSummary component — loop stats display with next loop button`
  - `[ ] Frontend useQuiz loop tracking — loopProgress state, startNextLoop`

---

## Dependencies

- Existing `get_question_count(db, lesson_id)` CRUD function — already implemented.
- Existing `QuizNextResponse` schema — will be extended (non-breaking, additive field).

## Open Questions

None — the scope is well-defined and the approach is minimal.
