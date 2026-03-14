# Quiz Question Counter

**Feature**: Display "{current question number} / {total questions}" during lesson-scoped quizzes
**Plan Created:** 2026-03-12
**Status:** Plan

---

## Problem Statement

When a user takes a quiz scoped to a specific lesson, there is no visual indicator of how far through the question set they are. The user cannot tell whether they are on question 2 of 5 or question 2 of 50. This makes it harder to gauge progress within a loop.

---

## Proposed Solution

Display a question counter (e.g. "3 / 12") in the QuizCard header when the quiz is scoped to a specific lesson. The counter uses data already available in the frontend — `loopProgress.answered` from the `useQuiz` hook and `lesson_question_count` from the API response. No backend changes needed.

The current question number is derived as:
- Before answering: `answered + 1` (the question being viewed)
- After answering: `answered` (the question just answered, still on screen)

The counter is only shown when `scope.lessonId` is set and `loopProgress.total > 0`.

---

## Current Implementation Analysis

### What Exists (keep as-is)

| Component | File | Status |
|-----------|------|--------|
| `QuizNextResponse.lesson_question_count` | `backend/src/schemas/quiz.py` | Keep — already returns total count |
| `useQuiz` hook loop tracking | `frontend/src/hooks/useQuiz.js` | Keep — already tracks `answered` and `total` |
| `QuizPage` passing `loopProgress` | `frontend/src/pages/QuizPage.jsx` | Keep — already has access to loop state |

### What Changes

| Component | Current | Proposed |
|-----------|---------|----------|
| `QuizCard` | Shows quiz_type label and View Lesson button in header | Also shows question counter when `questionNumber` and `totalQuestions` props are provided |
| `QuizPage` | Passes `quiz`, `onSubmit`, `disabled`, `result`, `userAnswer` to QuizCard | Also passes `questionNumber` and `totalQuestions` props |

---

## Implementation Plan

### Key Workflow

```
QuizPage renders QuizCard
  │
  ├── scope.lessonId is set AND loopProgress.total > 0?
  │     │
  │     Yes ──> compute currentNumber:
  │     │         result ? loopProgress.answered : loopProgress.answered + 1
  │     │
  │     └──> pass questionNumber={currentNumber} totalQuestions={loopProgress.total}
  │
  └── No ──> don't pass counter props (counter hidden)

QuizCard header
  │
  ├── quiz_type label (left)
  ├── question counter "3 / 12" (center, only if props provided)
  └── View Lesson button (right)
```

### Database Schema

**To Delete**: None
**To Update**: None
**To Add New**: None

### CRUD

**To Delete**: None
**To Update**: None
**To Add New**: None

### Services

**To Delete**: None
**To Update**: None
**To Add New**: None

### API Endpoints

**To Delete**: None
**To Update**: None
**To Add New**: None

### Testing

**To Delete**: None

**To Update**:
- `frontend/src/__tests__/components/QuizCard.test.js` — add test: counter is rendered when `questionNumber` and `totalQuestions` props are passed; counter is hidden when props are absent.

**To Add New**: None

### Frontend

**To Delete**: None

**To Update**:

1. `frontend/src/components/QuizCard.jsx`
   - Accept two new optional props: `questionNumber` (number) and `totalQuestions` (number)
   - In the header `div` (between quiz_type label and View Lesson button), render `"{questionNumber} / {totalQuestions}"` when both props are provided and `totalQuestions > 0`
   - Style: `text-sm text-gray-400` to match the quiz_type label style

2. `frontend/src/pages/QuizPage.jsx`
   - Compute `questionNumber` from `loopProgress` and `result`:
     ```js
     const questionNumber = result ? loopProgress.answered : loopProgress.answered + 1;
     ```
   - Pass `questionNumber` and `totalQuestions={loopProgress.total}` to `QuizCard` only when `scope.lessonId` is set and `loopProgress.total > 0`

### Documentation

#### Abstract (`docs/abstract/`)

- Update `docs/abstract/quiz.md`
  - **User Flow** section: add note that during lesson-scoped quizzes, the current question number out of total is shown
  - **What the User Sees** section: mention the question counter display

#### Technical (`docs/technical/`)

- Update `docs/technical/quiz.md`
  - **Frontend — Components** section: update QuizCard description to mention `questionNumber` and `totalQuestions` props
  - **Frontend — Pages & Routes** section: note that QuizPage computes and passes question counter to QuizCard for lesson-scoped quizzes

---

## Dependencies

- Existing `loopProgress` tracking in `useQuiz` hook
- Existing `lesson_question_count` in `GET /api/quiz/next` response

## Open Questions

None.
