# Quiz Selection Rules — Three Scope Cases

## Context

The quiz system has a two-level MEMORIZE spaced-repetition algorithm that selects questions differently depending on user scope. The user can:

1. Select a specific **topic + lesson**
2. Select a specific **topic only**
3. Select **nothing** (all topics)

Each case follows a different path through the `select_quiz()` function in `backend/src/service/quiz_selector.py`.

---

## Case 1: User Selects Topic + Lesson (lesson_id provided)

### Current State

```
[User] Selects a lesson from TopicLessonFilter (or arrives via /quiz?lessonId=8)
  │
  │   scope = { topicId: null, lessonId: 8 }
  │
  ▼
[System] select_quiz(db, username, lesson_id=8)
  │
  │   Topic selector: SKIPPED
  │   Lesson selector: SKIPPED
  │   resolved_topic = get_topic_for_lesson(8)  (lookup only, not selection)
  │   resolved_lesson = 8
  │
  ▼
[System] Ensure lesson memory exists
  │   get_or_create_lesson_memory(db, username, topic, 8)
  │
  ▼
[System] Sliding window dedup (lesson-scoped path)
  │   total = get_question_count(db, 8)        → e.g. 10 questions
  │   window = max(total - 1, 0)               → 9
  │   exclude_ids = get_recent_question_ids_for_lesson(db, username, 8, 9)
  │     → SELECT quiz_question_id FROM quiz_log
  │       WHERE username AND lesson_id=8
  │       ORDER BY created_at DESC LIMIT 9
  │
  ▼
[System] get_question_for_lesson(db, 8, exclude_ids)
  │   SELECT * FROM quiz_questions
  │   WHERE lesson_id=8 AND id NOT IN (exclude_ids)
  │   ORDER BY RANDOM() LIMIT 1
  │
  ▼
[Result] One random question from the 1 remaining (not in window)
```

**Key behaviors:**
- **No topic/lesson selection** — both MEMORIZE selectors are bypassed.
- **No quiz type rotation** — questions come from ALL quiz types, randomly.
- **Sliding window dedup** — excludes the last K-1 questions served (regardless of quiz type). This guarantees all K questions appear before any repeat.
- **Random order** — within the eligible pool (the 1 question not excluded), the question is picked randomly via `ORDER BY RANDOM()`.
- **Loop 1 priority**: All 10 questions appear in random order. No question repeats until all 10 have been served.
- **Loop 2 priority**: The window slides — after question 10 is served, questions 2-10 are excluded, so question 1 is the only eligible one. After that, questions 3-10 + 1 are excluded, so question 2 is eligible. Effectively, Loop 2 serves questions in the same relative order as Loop 1 (shifted by one position). The randomness is only within the eligible pool (which is always size 1 after the first loop completes).

### New State

_Pending comments._

---

## Case 2: User Selects Topic Only (topic_id provided, no lesson_id)

### Current State

```
[User] Selects a topic from TopicLessonFilter (lesson dropdown left at "All")
  │
  │   scope = { topicId: "coach", lessonId: null }
  │
  ▼
[System] select_quiz(db, username, topic_id="coach")
  │
  │   Topic selector: SKIPPED (topic already provided)
  │   resolved_topic = "coach"
  │
  ▼
[System] select_lesson_for_quiz(db, username, "coach")
  │   MEMORIZE lesson selection within topic:
  │
  │   1. Get all lesson IDs for topic "coach" (from topic_lookup cache)
  │   2. Load all UserLessonMemory for user + topic
  │   3. Get user's total quiz count (across ALL topics)
  │   4. For each lesson:
  │      ├── Skip if get_question_count(db, lesson_id) == 0  (no questions in bank)
  │      ├── If memory exists AND review_count > 0:
  │      │     recall = exp(-n * (total_quizzes - last_review_quiz_count) / 10)
  │      └── Else (never reviewed OR review_count == 0):
  │            recall = 0.0  ← PRIORITIZED for first exposure
  │   5. Pick lesson with LOWEST recall
  │
  │   resolved_lesson = lesson with lowest m(t)
  │
  ▼
[System] Ensure lesson memory exists
  │   get_or_create_lesson_memory(db, username, "coach", resolved_lesson)
  │
  ▼
[System] Quiz type rotation (topic/global path)
  │   select_quiz_type(db, username)
  │   1. Get last 3 quiz types from quiz_log (most recent first)
  │   2. Iterate: recall → understanding → application → analysis
  │   3. Return first type NOT in the last 3
  │   4. If all 4 seen recently → default to "recall"
  │
  │   selected_type = e.g. "analysis"
  │
  ▼
[System] Per-type dedup
  │   seen_ids = get_seen_question_ids(db, username, resolved_lesson, "analysis")
  │     → ALL question IDs user has ever been served for this lesson + type
  │   question = get_question(db, resolved_lesson, "analysis", exclude_ids=seen_ids)
  │     → SELECT * FROM quiz_questions
  │       WHERE lesson_id AND quiz_type="analysis" AND id NOT IN (seen)
  │       ORDER BY id LIMIT 1
  │
  ▼
[System] Fallback if no unseen questions for selected type
  │   Try each alternative type (recall, understanding, application)
  │   with its own per-type dedup
  │
  ▼
[System] Last resort: any question (all seen, new cycle)
  │   get_question(db, resolved_lesson, quiz_type, exclude_ids=None)
  │
  ▼
[Result] Question from weakest lesson, rotated quiz type, deduped per-type
```

**Key behaviors:**
- **Lesson selection uses MEMORIZE** — picks the lesson with lowest recall within the topic.
- **Never-reviewed lessons get m(t) = 0.0** — they are prioritized over all reviewed lessons.
- **Lessons without questions are skipped** — `get_question_count(db, lid) == 0` check.
- **Quiz type rotates** — avoids repeating the same cognitive level in consecutive quizzes.
- **Per-type dedup** — within a lesson + type, already-served questions are excluded. Once all seen, fall through to other types, then allow repeats.
- **Question order is deterministic** — `ORDER BY id` (not random), so within a type, questions are served in insertion order.

### New State

```
[User] Selects a topic from TopicLessonFilter (lesson dropdown left at "All")
  │
  │   scope = { topicId: "coach", lessonId: null }
  │
  ▼
[System] Compute loop size
  │   total_topic_questions = count all quiz_questions WHERE topic_id = "coach"
  │   loop_size = min(10, total_topic_questions)
  │
  ▼
[Frontend] Initialize loop tracking
  │   loopProgress = { total: loop_size, answered: 0, results: [] }
  │   Display loop_size gray progress squares in QuizCard header
  │
  ▼
[System] select_quiz(db, username, topic_id="coach")
  │
  │   Topic selector: SKIPPED (topic already provided)
  │   Quiz type: IGNORED (no rotation — all types eligible)
  │
  ▼
[System] Per-question recall selection (MEMORIZE at question level)
  │
  │   1. Gather ALL questions for topic "coach" (across all lessons, all types)
  │   2. For each question, compute question-level recall:
  │      ├── If user has answered this question before:
  │      │     Use the latest answer's timestamp to compute quizzes_elapsed
  │      │     recall = exp(-n * quizzes_elapsed / 10)
  │      │     where n = question's forgetting rate (adapts on correct/incorrect)
  │      └── If never answered:
  │            recall = 0.0  ← PRIORITIZED for first exposure
  │   3. Exclude questions already served in this loop (sliding window)
  │   4. Pick question with LOWEST recall from remaining pool
  │
  ▼
[System] Serve question
  │   CRUD: INSERT QuizLog (assessment_result = null)
  │   Response: { quiz_id, question, options[], ... }
  │
  ▼
[User] Answers (or skips via "Next Quiz")
  │
  │   correct → green square   │   incorrect → red square
  │   skipped → yellow square  │   upcoming → gray square
  │
  ▼
[System] Update question-level recall on answer
  │   Correct:  n *= 0.7 (forgetting slows)
  │   Incorrect: n *= 1.2 (forgetting accelerates, capped at 1.5)
  │   Also update lesson-level and topic-level memory (as before)
  │
  ▼
[System] Repeat until loop_size questions served (answered + skipped)
  │
  ▼
[Frontend] Loop complete → show LoopSummary
  │   Display: correct count, incorrect count, skipped count, accuracy
  │   "Next Loop" button → reset loop, begin next pass
  │
  ▼
[User] Clicks "Next Loop"
  │   Loop counter increments
  │   Progress squares reset to gray
  │   Selection continues with updated question-level recall scores
  │   (questions answered correctly have higher recall → deprioritized)
```

**Key changes from current state:**
- **Loop of min(10, total questions in topic)** — bounded loop with summary at end, same UX as Case 1.
- **Progress squares** — green/red/yellow/gray squares in QuizCard header showing per-question status within the loop.
- **Question-level recall (MEMORIZE)** — recall is computed per individual question, not per lesson. Lower recall questions are prioritized. Never-answered questions get m(t) = 0.0.
- **No quiz type rotation** — quiz type is ignored during selection. Questions from all types (recall, understanding, application, analysis) compete equally based on their individual recall score.
- **Cross-lesson within topic** — a single loop can include questions from multiple lessons within the topic, selected purely by question-level recall.

**New data model consideration:**
- Need a `UserQuestionMemory` (or equivalent) to track per-question forgetting rate, last_review_quiz_count, and review_count. Currently recall is only tracked at topic and lesson level.
- Alternative: derive question-level recall from `quiz_log` entries (latest answer timestamp + number of times answered correctly/incorrectly) without a dedicated table.

---

## Case 3: User Selects Nothing (no topic_id, no lesson_id)

### Current State

```
[User] Leaves TopicLessonFilter at defaults ("All Topics", no lesson)
  │
  │   scope = { topicId: null, lessonId: null }
  │
  ▼
[System] select_quiz(db, username)
  │
  ▼
[System] select_topic_for_quiz(db, username)
  │   MEMORIZE topic selection:
  │
  │   1. Get user's total quiz count
  │   2. Load all UserTopicMemory for user
  │   3. For each topic (from topic_lookup cache):
  │      ├── If memory exists AND review_count > 0:
  │      │     recall = exp(-n * (total_quizzes - last_review_quiz_count) / 10)
  │      └── Else (never reviewed OR review_count == 0):
  │            recall = 0.0  ← PRIORITIZED for first exposure
  │   4. Pick topic with LOWEST recall
  │
  │   resolved_topic = topic with lowest m(t)
  │
  ▼
[System] select_lesson_for_quiz(db, username, resolved_topic)
  │   (Same MEMORIZE lesson selection as Case 2)
  │   Pick lesson with lowest m(t) within the selected topic
  │
  │   resolved_lesson = lesson with lowest m(t)
  │
  ▼
[System] Ensure lesson memory exists
  │
  ▼
[System] Quiz type rotation + per-type dedup
  │   (Same as Case 2 — type rotation, per-type seen IDs, fallback chain)
  │
  ▼
[Result] Question from weakest topic → weakest lesson → rotated type → deduped
```

**Key behaviors:**
- **Both MEMORIZE selectors active** — topic first, then lesson within topic.
- **Never-reviewed topics/lessons get m(t) = 0.0** — prioritized over reviewed ones.
- **Same quiz type rotation and dedup as Case 2** — once topic + lesson are resolved, the question selection is identical.
- **Cross-topic rotation** — the system naturally rotates across topics as recall decays at different rates.

### New State

```
[User] Leaves TopicLessonFilter at defaults ("All Topics", no lesson)
  │
  │   scope = { topicId: null, lessonId: null }
  │
  ▼
[System] Compute loop size
  │   total_all_questions = count all quiz_questions (across all topics)
  │   loop_size = min(10, total_all_questions)
  │
  ▼
[Frontend] Initialize loop tracking
  │   loopProgress = { total: loop_size, answered: 0, results: [] }
  │   Display loop_size gray progress squares in QuizCard header
  │
  ▼
[System] select_quiz(db, username)
  │
  │   Topic selector: SKIPPED (question-level recall handles cross-topic)
  │   Lesson selector: SKIPPED (question-level recall handles cross-lesson)
  │   Quiz type: IGNORED (no rotation — all types eligible)
  │
  ▼
[System] Per-question recall selection (MEMORIZE at question level)
  │
  │   1. Gather ALL questions across ALL topics and lessons
  │   2. For each question, compute question-level recall:
  │      ├── If user has answered this question before:
  │      │     recall = exp(-n * quizzes_elapsed / 10)
  │      └── If never answered:
  │            recall = 0.0  ← PRIORITIZED for first exposure
  │   3. Exclude questions already served in this loop (sliding window)
  │   4. Pick question with LOWEST recall from remaining pool
  │
  ▼
[System] Serve question
  │   CRUD: INSERT QuizLog (assessment_result = null)
  │   Response includes lesson_title for context (questions may come from any lesson)
  │
  ▼
[User] Answers (or skips via "Next Quiz")
  │
  │   correct → green square   │   incorrect → red square
  │   skipped → yellow square  │   upcoming → gray square
  │
  ▼
[System] Update question-level recall on answer
  │   Also update lesson-level and topic-level memory (as before)
  │
  ▼
[System] Repeat until loop_size questions served
  │
  ▼
[Frontend] Loop complete → show LoopSummary
  │   Display: correct count, incorrect count, skipped count, accuracy
  │   "Next Loop" button → reset loop, begin next pass
  │
  ▼
[User] Clicks "Next Loop"
  │   Selection continues with updated question-level recall scores
  │   Questions span across ALL topics — the loop naturally mixes topics
  │   based on which individual questions have the lowest recall
```

**Key changes from current state:**
- **Loop of min(10, total questions across all topics)** — bounded loop with summary, same UX as Cases 1 and 2.
- **Progress squares** — green/red/yellow/gray squares showing status within the loop.
- **Question-level recall (MEMORIZE)** — replaces the two-level topic → lesson selection. Each question has its own recall score. The system picks from ALL questions globally, prioritizing the lowest recall.
- **No quiz type rotation** — quiz type is ignored. Questions compete purely on recall score.
- **No topic/lesson selector** — both are bypassed. A single loop can include questions from any topic and any lesson, mixed together based on recall.
- **Cross-topic naturally** — instead of picking "weakest topic then weakest lesson", the system directly picks the weakest *questions*. This may pull questions from multiple topics in a single loop.

---

## Summary Comparison

| Aspect | Case 1: Topic + Lesson | Case 2: Topic Only | Case 3: Nothing |
|--------|----------------------|-------------------|-----------------|
| **Loop size** | K (all questions in lesson) | min(10, total in topic) | min(10, total across all) |
| **Topic selector** | Skipped | Skipped | Skipped |
| **Lesson selector** | Skipped | Skipped | Skipped |
| **Selection level** | Question (sliding window) | Question (recall-based) | Question (recall-based) |
| **Quiz type** | All types (no rotation) | All types (no rotation) | All types (no rotation) |
| **Question order** | Random | Lowest recall first | Lowest recall first |
| **Dedup strategy** | Sliding window (K-1) | Within-loop exclusion | Within-loop exclusion |
| **Never-answered priority** | Implicit (window) | m(t) = 0.0 (highest priority) | m(t) = 0.0 (highest priority) |
| **Progress squares** | Yes | Yes | Yes |
| **Loop summary** | Yes | Yes | Yes |
| **Question pool** | Single lesson | All lessons in topic | All lessons across all topics |

## Source Files

- Quiz selector logic: `backend/src/service/quiz_selector.py`
- Topic memory model: `backend/src/models/user_topic_memory.py`
- Lesson memory model: `backend/src/models/user_lesson_memory.py`
- Question CRUD: `backend/src/crud/crud_quiz_question.py`
- Quiz log CRUD: `backend/src/crud/crud_quiz_log.py`
- Topic lookup (cache): `backend/src/service/topic_lookup.py`
- Abstract doc: `docs/abstract/quiz.md`
- Technical doc: `docs/technical/quiz.md`

## Next Steps

- `/feature-update` — if you want to change the selection rules for any case
- `/feature-plan` — if you want to add a new selection strategy
- Review `backend/src/service/quiz_selector.py` to see the full implementation
