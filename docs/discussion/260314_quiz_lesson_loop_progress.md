# Quiz Lesson Loop: Question Priority, Progress Squares, and Bug Analysis

**Context**: User navigates to `http://localhost:3999/quiz?lessonId=8` to take a quiz loop for lesson 8 (which has 10 questions).

---

## 1. Full Flow: URL → First Quiz

```
[Browser] Navigate to /quiz?lessonId=8
  │
  ▼
[QuizPage] useEffect reads searchParams
  │  setScope({ topicId: null, lessonId: 8 })
  │  autoFetchRef.current = true
  │
  ▼
[QuizPage] useEffect detects scope change + autoFetchRef
  │  Calls fetchNextQuiz()
  │
  ▼
[useQuiz] fetchNextQuiz()
  │  setResult(null), setQuiz(null)
  │  Calls apiService.getNextQuiz(null, 8)
  │    → GET /api/quiz/next?lesson_id=8
  │
  ▼
[Backend] quiz.py:get_next_quiz()
  │  select_quiz(db, username, lesson_id=8)
  │    → quiz_selector.py: lesson_id is not None
  │    → get_topic_for_lesson(8) → resolved_topic
  │    → get_question_count(db, 8) → total (e.g. 10)
  │    → window = max(10 - 1, 0) = 9
  │    → get_recent_question_ids_for_lesson(db, username, 8, 9)
  │      → First call: no quiz_logs yet → exclude_ids = []
  │    → get_question_for_lesson(db, 8, exclude_ids=None)
  │      → Random question from all 10
  │
  │  create_quiz_log(db, username, question.id, ...)
  │    → quiz_log created (pending, no answer yet)
  │
  │  Returns QuizNextResponse with lesson_question_count=10
  │
  ▼
[useQuiz] setQuiz(data)
  │  scope.lessonId=8 && data.lesson_question_count=10
  │  setLoopProgress(prev => ({ ...prev, total: 10 }))
  │
  ▼
[QuizPage] Renders QuizCard with:
  │  totalQuestions = 10
  │  loopResults = []  (all 10 squares gray)
```

---

## 2. Question Priority

### First Loop (Questions 1–10)

**Algorithm**: Sliding window dedup with **random** ordering (`quiz_selector.py:142-146`).

```python
# lesson_id is not None → lesson-scoped loop
total = get_question_count(db, resolved_lesson)     # e.g. 10
window = max(total - 1, 0)                          # 9
exclude_ids = get_recent_question_ids_for_lesson(db, username, resolved_lesson, window)
return get_question_for_lesson(db, resolved_lesson, exclude_ids=exclude_ids or None)
```

- **No quiz type rotation** — lesson-scoped mode ignores `select_quiz_type()`. All 4 types (recall, understanding, application, analysis) are mixed randomly.
- **No topic/lesson selection** — lesson_id is provided, both selectors are skipped.
- **Dedup mechanism**: The last `total - 1 = 9` question IDs from `quiz_log` are excluded. Since there are only 10 questions, at most 1 question is eligible at any time. This guarantees **all 10 questions appear exactly once before any repeat**.
- **Order**: `func.random()` — questions appear in **random order** within each loop. There is no fixed priority.

| Question # | Exclude Window (last 9 logs) | Eligible Questions |
|------------|-----------------------------|--------------------|
| 1st | 0 logs → exclude nothing | All 10 → random pick |
| 2nd | 1 log → exclude 1 | 9 remaining → random |
| 3rd | 2 logs → exclude 2 | 8 remaining → random |
| ... | ... | ... |
| 9th | 8 logs → exclude 8 | 2 remaining → random |
| 10th | 9 logs → exclude 9 | 1 remaining → forced pick |

### Second Loop (Questions 11–20)

The sliding window continues across loop boundaries:

| Question # | Exclude Window (last 9 logs) | Effect |
|------------|------------------------------|--------|
| 11th (loop 2, Q1) | Logs 2–10 excluded → only Q1 from loop 1 is eligible | Forces the one question NOT in the last 9 |
| 12th (loop 2, Q2) | Logs 3–11 excluded | Q1 and Q2 from loop 1 eligible → random pick |
| ... | Window slides forward | Gradually more questions become eligible |

**Key insight**: The second loop does NOT reset the dedup window. The `startNextLoop()` in `useQuiz.js` resets the frontend `loopProgress` state, but the backend still has all quiz_log entries. The sliding window ensures no question repeats within any 9-question span across loops.

---

## 3. Progress Square Colors

### Rendering Logic (`QuizCard.jsx:63-78`)

```jsx
{totalQuestions > 0 && (
    <div className="flex gap-1">
        {Array.from({ length: totalQuestions }, (_, i) => {
            const status = loopResults[i];
            const color =
                status === "correct"   ? "bg-green-500"
                : status === "incorrect" ? "bg-red-500"
                : status === "skipped"   ? "bg-yellow-500"
                : "bg-gray-500";          // default: not yet answered
            return <div key={i} className={`w-3 h-3 rounded-sm ${color}`} />;
        })}
    </div>
)}
```

### Color Outcomes

| User Action | `loopResults[i]` value | Square Color |
|-------------|----------------------|--------------|
| Correct answer | `"correct"` | **Green** (`bg-green-500`) |
| Wrong answer | `"incorrect"` | **Red** (`bg-red-500`) |
| Not yet answered this loop | `undefined` | **Gray** (`bg-gray-500`) |
| Skipped (not implemented) | `"skipped"` | **Yellow** (`bg-yellow-500`) |

### How Results Are Recorded (`useQuiz.js:60-72`)

```javascript
if (scope.lessonId) {
    setLoopProgress((prev) => {
        const newAnswered = prev.answered + 1;
        return {
            ...prev,
            answered: newAnswered,
            correct: prev.correct + (data.is_correct ? 1 : 0),
            incorrect: prev.incorrect + (data.is_correct ? 0 : 1),
            loopComplete: prev.total > 0 && newAnswered >= prev.total,
            results: [...prev.results, data.is_correct ? "correct" : "incorrect"],
        };
    });
}
```

---

## 4. Identified Issues

### Issue 1: TopicLessonFilter Not Synced with URL Params (ROOT CAUSE of progress bug)

**Severity**: High — this is the most likely cause of the reported "squares not updating" bug.

**Problem**: When navigating via `?lessonId=8`, the scope is set correctly in `useQuiz` state, BUT the `TopicLessonFilter` component has **its own internal state** (`selectedTopic=""`, `selectedLesson=""`) that is NOT synced to the URL param.

**File**: `frontend/src/components/TopicLessonFilter.jsx`

The filter is an **uncontrolled component** with respect to the parent's scope:
```jsx
const [selectedTopic, setSelectedTopic] = useState("");   // Always starts empty
const [selectedLesson, setSelectedLesson] = useState("");  // Always starts empty
```

The parent passes `scope` as a prop, but the filter **never reads it** to initialize its own state. So:
- User navigates to `?lessonId=8` → `scope = { topicId: null, lessonId: 8 }` ✓
- Filter shows "All Topics" with no lesson dropdown
- If user **touches the topic dropdown at all** (even selecting and deselecting), `handleTopicChange` fires → `onScopeChange({ topicId: "...", lessonId: null })` → `handleScopeChange` → `setScope({ topicId: "...", lessonId: null })` + `reset()`
- **`scope.lessonId` becomes `null`** → `submitAnswer` skips `loopProgress` update → squares stay gray forever

Even just clicking "All Topics" (the default) fires `handleTopicChange` with `topicId = ""` → `lessonId: null`.

**Impact**: Any accidental interaction with the filter permanently breaks the progress tracking for the rest of the session. The quiz still loads (because `fetchNextQuiz` uses whatever scope is current), but the loop progress tracking is silently disabled when `scope.lessonId` becomes null.

### Issue 2: Quiz Log Created Before Answer (Design Observation)

**File**: `backend/src/api/quiz.py:76-83`

```python
quiz_log = create_quiz_log(db, username=user.username, ...)  # Created on GET /next
```

The quiz_log entry is created when the question is **fetched**, not when it's **answered**. This means:
- If the user fetches a question but never answers it (clicks "Next Quiz" without answering), the quiz_log still exists
- The sliding window dedup counts this unanswered question as "seen"
- The question won't reappear until it exits the sliding window

This is a design choice, not a bug per se — but it means skipping a question "wastes" a slot in the dedup window.

### Issue 3: No Skip Tracking in Frontend

**File**: `frontend/src/hooks/useQuiz.js`

When the user clicks "Next Quiz" without answering:
- `fetchNextQuiz()` runs, setting `setResult(null)` and `setQuiz(null)`
- The previous question's result is cleared
- `loopProgress.results` is NOT updated (no "skipped" entry is added)
- The total questions answered (`loopProgress.answered`) doesn't increment
- The progress squares show a "gap" — the skipped question's square stays gray

Combined with Issue 2 (backend creates quiz_log on fetch), this creates a mismatch: the backend considers 10 questions served, but the frontend only tracks 9 answers (one was skipped). The loop never reaches `loopComplete` unless all questions are answered.

### Issue 4: Loop Completion Check Uses `total` from First Fetch Only

**File**: `frontend/src/hooks/useQuiz.js:32-37`

```javascript
if (scope.lessonId && data.lesson_question_count) {
    setLoopProgress((prev) => ({ ...prev, total: data.lesson_question_count }));
}
```

The `total` is set from `lesson_question_count` on every fetch. If a new quiz question is added to the lesson mid-loop, `total` would change. This is minor but worth noting.

---

## 5. Expected vs Actual Behavior Summary

| Aspect | Expected | Actual (with Issue 1) |
|--------|----------|----------------------|
| Squares shown | 10 gray squares on first load | ✓ Works |
| After answering Q1 correctly | First square turns green | Only if user hasn't touched the filter |
| After answering Q2 incorrectly | First green, second red | Same condition |
| After clicking "Next Quiz" | Squares persist, new quiz loads | Squares persist IF scope.lessonId is still set |
| After touching filter dropdown | Should maintain lesson scope | **BUG**: scope.lessonId resets to null, all future answers don't track |

---

## Next Steps

1. **Fix Issue 1** — Sync TopicLessonFilter with URL params, or make it a controlled component that reflects the parent's `scope`. This is the likely root cause of the reported bug.
2. **Consider Issue 3** — Add skip tracking: when `fetchNextQuiz` is called while `result` is null and `quiz` is not null, append `"skipped"` to `loopProgress.results`.
3. **Update documentation** — `docs/technical/quiz.md` still references the old dedup approach and `questionNumber/totalQuestions` pattern. Should be updated to reflect sliding window dedup and colored progress squares.

- `/feature-plan` — to plan the TopicLessonFilter sync fix
- `/feature-update` — to implement the fix directly
