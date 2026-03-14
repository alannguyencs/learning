# Loop Completion Navigation

**Feature**: After completing a quiz loop, show contextual navigation options based on the current scope (lesson, topic, or global)
**Plan Created:** 2026-03-14
**Status:** Done

---

## Problem Statement

1. When a user finishes a quiz loop, the only option is a single "Next Loop" button that repeats the same scope.
2. A user who just finished a lesson-scoped loop might want to broaden to the topic or go global — but currently must manually change the dropdown filter and lose the loop summary view.
3. The navigation options should reflect the scope hierarchy: lesson < topic < all topics — offering the user a natural way to zoom out after completing a loop.

---

## Proposed Solution

Replace the single "Next Loop" button in `LoopSummary` with **contextual navigation buttons** based on which scope the completed loop used:

| Completed Scope | Buttons Shown |
|----------------|---------------|
| **Global** (no topic, no lesson) | "Next Loop" (same global scope) |
| **Topic** (topic selected, no lesson) | "Next Loop - {topic_name}" + "Next Loop - All Topics" |
| **Lesson** (topic + lesson selected) | "Next Loop - {lesson_title}" + "Next Loop - {topic_name}" + "Next Loop - All Topics" |

Each button starts a new loop with the corresponding scope. The button labels use actual topic/lesson names so the user knows exactly what they're choosing.

**Design decisions:**
- No backend changes needed — the frontend already supports changing scope via `setScope` + `startNextLoop`
- Topic and lesson names are already available: `quiz.topic_id` from the last served question, topic/lesson names from `TopicLessonFilter`'s loaded topics data
- The current scope's button is styled as primary (blue), broader scopes as secondary (outlined)

---

## Current Implementation Analysis

### What Exists (keep as-is)

| Component | File | Status |
|-----------|------|--------|
| `useQuiz` hook | `frontend/src/hooks/useQuiz.js` | Keep — scope state, startNextLoop logic unchanged |
| `QuizPage` orchestration | `frontend/src/pages/QuizPage.jsx` | Keep — showingSummary state machine unchanged |
| `TopicLessonFilter` | `frontend/src/components/TopicLessonFilter.jsx` | Keep — dropdown behavior unchanged |
| Quiz API endpoint | `backend/src/api/quiz.py` | Keep — no backend changes |
| Quiz selector | `backend/src/service/quiz_selector.py` | Keep — no backend changes |

### What Changes

| Component | Current | Proposed |
|-----------|---------|----------|
| `LoopSummary` | Single "Next Loop" button, single `onNextLoop` callback | Multiple scope-aware buttons, `onNextLoop(scope)` callback with scope parameter |
| `QuizPage.handleNextLoop` | Calls `startNextLoop()` with current scope | Receives scope from LoopSummary, calls `setScope` if different, then `startNextLoop()` |
| `LoopSummary` heading | Shows "Loop {loopNumber} Complete" | Shows "Loop Complete" (no loop number) |
| `LoopSummary` props | `{ loopProgress, onNextLoop }` | `{ loopProgress, onNextLoop, scope, topicName, lessonTitle }` |

---

## Implementation Plan

### Key Workflow

```
Loop completes → LoopSummary renders
                    │
                    ├─ scope = global (no topic, no lesson)
                    │   └─ [Next Loop]  → startNextLoop(null, null)
                    │
                    ├─ scope = topic (topicId set, no lessonId)
                    │   ├─ [Next Loop - {topic_name}]  → startNextLoop(topicId, null)
                    │   └─ [Next Loop - All Topics]     → startNextLoop(null, null)
                    │
                    └─ scope = lesson (topicId + lessonId set)
                        ├─ [Next Loop - {lesson_title}] → startNextLoop(topicId, lessonId)
                        ├─ [Next Loop - {topic_name}]   → startNextLoop(topicId, null)
                        └─ [Next Loop - All Topics]      → startNextLoop(null, null)
```

**To Delete**: None
**To Update**: `LoopSummary.jsx`, `QuizPage.jsx`
**To Add New**: None

### Database Schema

None — no database changes.

### CRUD

None — no CRUD changes.

### Services

None — no backend service changes.

### API Endpoints

None — no API changes. The existing `GET /api/quiz/next?topic_id=&lesson_id=` already supports all three scopes.

### Testing

None — this is a frontend-only change with no new backend logic.

### Frontend

#### `frontend/src/components/LoopSummary.jsx`

**To Delete**: None
**To Update**:
- Change heading from `"Loop {loopNumber} Complete"` to `"Loop Complete"` (remove loop number)
- Change props from `{ loopProgress, onNextLoop }` to `{ loopProgress, onNextLoop, scope, topicName, lessonTitle }`
- Replace single "Next Loop" button with conditional button group

**To Add New**:
- Scope detection logic: determine which case (global / topic / lesson) based on `scope.topicId` and `scope.lessonId`
- Button rendering for each case:

**Case 1 — Global** (no topicId, no lessonId):
```jsx
<button onClick={() => onNextLoop({ topicId: null, lessonId: null })}>
  Next Loop
</button>
```

**Case 2 — Topic** (topicId set, no lessonId):
```jsx
<button onClick={() => onNextLoop({ topicId: scope.topicId, lessonId: null })}>
  Next Loop - {topicName}
</button>
<button onClick={() => onNextLoop({ topicId: null, lessonId: null })}>
  Next Loop - All Topics
</button>
```

**Case 3 — Lesson** (topicId + lessonId set):
```jsx
<button onClick={() => onNextLoop({ topicId: scope.topicId, lessonId: scope.lessonId })}>
  Next Loop - {lessonTitle}
</button>
<button onClick={() => onNextLoop({ topicId: scope.topicId, lessonId: null })}>
  Next Loop - {topicName}
</button>
<button onClick={() => onNextLoop({ topicId: null, lessonId: null })}>
  Next Loop - All Topics
</button>
```

**Button styling:**
- Current scope button: `bg-blue-600 hover:bg-blue-700 text-white` (primary, full-width)
- Broader scope buttons: `border border-gray-500 text-gray-300 hover:bg-gray-600` (secondary, full-width)
- All buttons stacked vertically with `gap-3`

#### `frontend/src/pages/QuizPage.jsx`

**To Delete**: None
**To Update**:
- `handleNextLoop` — accept `newScope` parameter from LoopSummary
- If `newScope` differs from current `scope`, call `setScope(newScope)` then reset and fetch
- If same scope, call `startNextLoop()` as before
- Pass `scope`, `topicName`, `lessonTitle` props to `LoopSummary`

**To Add New**:
- Derive `topicName` and `lessonTitle` from the last served quiz question (`quiz.topic_id` and `quiz.lesson_title` are already in the quiz response)
- Store these values so they survive after quiz state is cleared for the summary view

Specifically:
- Add `loopMeta` state: `{ topicName, lessonTitle }` — set when a quiz is fetched, persisted across the summary view
- In `fetchNextQuiz` success path (inside useQuiz or QuizPage), capture `quiz.lesson_title` and derive topic name from the topics list or from `quiz.topic_id`

For topic name resolution, the simplest approach: the `QuizNextResponse` already returns `topic_id` and `lesson_title`. The `TopicLessonFilter` fetches topics with names. QuizPage can either:
1. Store `topicName` alongside scope when scope is set from filter (preferred — already available)
2. Or add `topic_name` to `QuizNextResponse` (requires backend change — avoid)

**Preferred approach**: When `handleScopeChange` is called from TopicLessonFilter, also capture the display names. Extend `scope` state to include `topicName` and `lessonTitle`:
```js
// In handleScopeChange or via a small extension
setScope({ topicId, lessonId, topicName, lessonTitle });
```

For lesson-scoped loops initiated via URL param (`?lessonId=8`), the topic/lesson names can be captured from the first quiz response (`quiz.lesson_title`) and from the topics list after it loads.

### Documentation

#### Abstract (`docs/abstract/`)

- **Update** `docs/abstract/quiz.md`:
  - **User Flow** section: Update step after "loop completion" to describe the three navigation cases instead of a single "Next Loop"
  - **Acceptance Criteria**: Add criteria for contextual navigation buttons

#### Technical (`docs/technical/`)

- **Update** `docs/technical/quiz.md`:
  - **Frontend** section: Update `LoopSummary` component description to document new props and button cases

---

## Dependencies

- Existing `LoopSummary` component
- Existing `useQuiz` hook with `scope`, `setScope`, `startNextLoop`
- Topic/lesson name data from `TopicLessonFilter` topics API or quiz response

## Open Questions

None — all resolved.
