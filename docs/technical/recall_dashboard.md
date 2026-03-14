# Recall Dashboard — Technical Design

[< Prev: Quiz](./quiz.md) | [Parent](./index.md)

## Related Docs
- Abstract: [abstract/recall_dashboard.md](../abstract/recall_dashboard.md)

## Architecture

```
+-----------+       +---------------------+       +------------+
|  Frontend | ----> |  Backend (FastAPI)   | ----> | PostgreSQL |
|  (React)  | <---- |                     | <---- |            |
+-----------+       +---------------------+       +------------+
```

**Layers involved:**

- **Frontend** — Recall dashboard page. Fetches recall data at topic and lesson level, renders heatmap, stats, and topic matrix.
- **Backend — API** — REST endpoints that return computed recall data at both levels.
- **Backend — Service** — Calculates recall probabilities from stored memory state at topic and lesson level. Assembles matrix from quiz logs.
- **Backend — CRUD** — Reads `UserTopicMemory`, `UserLessonMemory`, and `QuizLog`.
- **Database** — Source of truth for two-level memory state and quiz history.

No LLM calls. This feature is pure data retrieval and computation.

## Data Model

This feature reads from models defined in the Quiz technical doc:

- **`UserTopicMemory`** — Per-topic forgetting rate, review counts, and last-review checkpoint. Used to calculate topic-level recall probability.
- **`UserLessonMemory`** — Per-lesson forgetting rate, review counts, and last-review checkpoint. Used to calculate lesson-level recall probability. Includes `topic_id` for grouping.
- **`QuizLog`** — Individual quiz records with `topic_id`, `lesson_id`, and results. Used to build the topic matrix grid.
- **`Lesson`** — Normalized lesson records. Lesson names displayed in the recall dashboard are resolved from the `lessons` table via the `topic_lookup` in-memory cache (which syncs from the `lessons` table on startup).

No additional tables are created by this feature, but it reads from the `Lesson` table indirectly via the topic lookup cache.

## Pipeline

### Recall Map

```
User opens Recall Dashboard
  │
  ▼
GET /api/quiz/recall-map
  │
  ▼
RecallService.get_recall_map()
  ├── CRUD: SELECT all UserTopicMemory for user
  ├── CRUD: SELECT all UserLessonMemory for user
  ├── CRUD: COUNT total quizzes for user (current_quiz_count)
  │
  ▼
For each topic:
  ├── Calculate topic m(t):
  │   ├── If UserTopicMemory exists:
  │   │   └── m(t) = exp(-n * (current_quiz_count - last_review_quiz_count) / 10)
  │   └── If no record (never reviewed):
  │       └── m(t) = 1.0 (no data yet, shown as neutral)
  │
  └── For each lesson in this topic:
      ├── If UserLessonMemory exists:
      │   └── m(t) = exp(-n * (current_quiz_count - last_review_quiz_count) / 10)
      └── If no record (never reviewed):
          └── m(t) = 1.0
  │
  ▼
Compute summary:
  ├── global_recall = mean of all 13 topic m(t) values
  ├── topics_at_risk = count of topics where m(t) < 0.5
  └── lessons_at_risk = count of lessons where m(t) < 0.5
  │
  ▼
Response: { topics[], global_recall, topics_at_risk, lessons_at_risk }
```

### Topic Matrix

```
User views topic matrix tab
  │
  ▼
GET /api/quiz/topic-matrix
  │
  ▼
RecallService.get_topic_matrix()
  ├── CRUD: SELECT all QuizLog for user, ordered by created_at
  ├── Assign column_index (1, 2, 3, ...) chronologically across all topics
  ├── Group quiz records by topic_id
  │
  ▼
For each topic:
  └── Build row with quiz attempts:
      { quiz_id, result ("correct"/"incorrect"/null), column_index, lesson_id }
  │
  ▼
Response: { topics[], max_quiz_count }
```

## Algorithms

### Recall Probability Calculation

- Uses the same MEMORIZE formula as quiz selection: `m(t) = exp(-n * quizzes_elapsed / 10)`.
- `quizzes_elapsed = current_quiz_count - last_review_quiz_count`.
- Applied identically at both topic and lesson level using their respective memory records.
- Topics and lessons are user-defined (general domain). The dashboard shows all topics that have questions in the question bank.
- For topics/lessons with no memory record (never reviewed), the dashboard shows `m(t) = 1.0`. This differs from the quiz selector which uses `0.0` for never-reviewed items — the distinction is intentional: the selector wants to prioritize unreviewed items, while the dashboard should not alarm the user about items they haven't started yet.

### Color Thresholds

Applied at both topic and lesson level:

- Green: `m(t) > 0.7` — well-remembered.
- Yellow: `0.5 < m(t) <= 0.7` — weakening.
- Red: `m(t) <= 0.5` — at risk.

### Matrix Column Assignment

- All quiz attempts across all topics are sorted by `created_at` globally.
- Each attempt gets a sequential `column_index` (1-based).
- This means quiz attempts for different topics interleave in the matrix columns, showing the real chronological order.

## Backend — API Layer

| Method | Path | Auth | Request | Response | Status |
|--------|------|------|---------|----------|--------|
| GET | `/api/quiz/recall-map` | Session | — | `RecallMapResponse` (see below) | 200 |
| GET | `/api/quiz/topic-matrix` | Session | — | `TopicMatrixResponse` (see below) | 200 |

**`RecallMapResponse`:**

| Field | Type | Description |
|-------|------|-------------|
| `topics` | list[TopicRecallItem] | Per-topic recall data with nested lessons |
| `global_recall` | float | Mean m(t) across all topics |
| `global_accuracy` | float | Overall correct / total across all topics |
| `topics_at_risk` | int | Count of topics with m(t) < 0.5 |
| `lessons_at_risk` | int | Count of lessons with m(t) < 0.5 |

**`TopicRecallItem`:**

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | string | Topic identifier |
| `topic_name` | string | Human-readable topic name |
| `lesson_count` | int | Number of lessons in this topic |
| `recall_probability` | float | Topic-level m(t) value, 0.0–1.0 |
| `forgetting_rate` | float | Topic-level n value |
| `last_review_at` | datetime, nullable | When this topic was last quizzed |
| `review_count` | int | Total quizzes in this topic |
| `correct_count` | int | Correct answers in this topic |
| `lessons` | list[LessonRecallItem] | Per-lesson recall data within this topic |

**`LessonRecallItem`:**

| Field | Type | Description |
|-------|------|-------------|
| `lesson_id` | int | Lesson identifier |
| `lesson_name` | string | Human-readable lesson name |
| `recall_probability` | float | Lesson-level m(t) value, 0.0–1.0 |
| `forgetting_rate` | float | Lesson-level n value |
| `last_review_at` | datetime, nullable | When this lesson was last quizzed |
| `review_count` | int | Total quizzes for this lesson |
| `correct_count` | int | Correct answers for this lesson |

**`TopicMatrixResponse`:**

| Field | Type | Description |
|-------|------|-------------|
| `topics` | list[TopicMatrixRow] | One row per topic |
| `max_quiz_count` | int | Total columns in the matrix |

**`TopicMatrixRow`:**

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | string | Topic identifier |
| `topic_name` | string | Human-readable topic name |
| `lesson_count` | int | Number of lessons in this topic |
| `last_quiz_at` | datetime, nullable | Most recent quiz in this topic |
| `quizzes` | list[TopicQuizAttempt] | Quiz attempts for this topic |

**`TopicQuizAttempt`:**

| Field | Type | Description |
|-------|------|-------------|
| `quiz_id` | int | QuizLog id |
| `result` | string, nullable | `"correct"`, `"incorrect"`, or null (pending) |
| `asked_at` | datetime | When the quiz was generated |
| `column_index` | int | Global chronological position (1-based) |
| `lesson_name` | string | Name of the quizzed lesson |

## Backend — Service Layer

**RecallService** — Computes the recall map and topic matrix. Stateless — reads from CRUD, applies the m(t) formula at both levels, and returns response schemas.

- `get_recall_map(db, username)` — Loads all `UserTopicMemory` and `UserLessonMemory` records and the current quiz count. Iterates over all topics, calculates topic-level `m(t)`, then for each topic calculates lesson-level `m(t)` for each of its lessons. Assembles `RecallMapResponse` with nested `LessonRecallItem` lists.
- `get_topic_matrix(db, username)` — Loads all `QuizLog` records for the user, assigns chronological column indices, groups by topic, and assembles `TopicMatrixResponse`.

## Backend — CRUD Layer

This feature reuses CRUD operations defined in the Quiz feature:

- `get_all_memory_states(db, username)` — SELECT all `UserTopicMemory` records for the user.
- `get_all_lesson_memories(db, username)` — SELECT all `UserLessonMemory` records for the user.
- `get_user_total_quiz_count(db, username)` — COUNT all `QuizLog` records for the user.
- `get_all_quiz_logs(db, username)` — SELECT all `QuizLog` records ordered by `created_at`. Used by the topic matrix.

## Frontend — Pages & Routes

| Route | Page | Description |
|-------|------|-------------|
| `/dashboard` | RecallDashboardPage | Displays recall heatmap (topic + lesson level), summary stats, and topic matrix. |

## Frontend — Components

- **RecallHeatmap** — Grid of topic cards. Each card shows the topic name and is colored green/yellow/red based on topic-level `recall_probability`. Shows `review_count` and accuracy percentage within each card. Cards are expandable to show a nested list of lessons with their own color-coded recall scores.
- **LessonRecallList** — Nested within an expanded topic card. Lists each lesson with its recall score, color indicator, quiz count, and accuracy. Includes a button to start a quiz for that specific lesson.
- **RecallSummary** — Displays `global_recall` as a percentage, `global_accuracy` as a percentage (correct/total across all topics), `topics_at_risk` count, and `lessons_at_risk` count.
- **TopicMatrix** — Grid table. Rows are topics (sorted by most recent quiz). Columns are chronological quiz attempts. Each cell is colored by result: green (correct), red (incorrect), grey (pending). Cell tooltip shows the lesson name.
- **QuizLaunchButton** — Navigates the user to the quiz page. Appears on topic cards (pre-fills topic scope) and lesson rows (pre-fills lesson scope).

## Frontend — Services & Hooks

- **api.js** — `getRecallMap()` calls GET `/api/quiz/recall-map`. `getTopicMatrix()` calls GET `/api/quiz/topic-matrix`.
- **useDashboardData** — Custom hook that fetches both recall map and topic matrix on mount. Manages `loading`, `recallMap`, `topicMatrix`, and `expandedTopics` state. Re-fetches when the user navigates back to the dashboard.

## Constraints & Edge Cases

- A brand-new user with no quizzes will see all topics at `m(t) = 1.0` (neutral grey or green) and `global_recall = 1.0`. The dashboard should display a prompt encouraging the user to take their first quiz.
- Expanding a topic with no lesson memory records shows all lessons at `m(t) = 1.0`.
- The topic matrix may have sparse columns — most topics will have empty cells for any given column, since each quiz belongs to exactly one topic.
- Recall probabilities are computed on read, not stored. They always reflect the current state based on `forgetting_rate` and `quizzes_elapsed` at both levels.
- The `topic-matrix` endpoint returns all quiz history. For users with a very large history, the frontend may need to paginate or truncate older columns. Initial implementation does not paginate.

## Component Checklist

- [ ] GET `/api/quiz/recall-map` — returns per-topic recall with nested per-lesson recall + summary stats
- [ ] GET `/api/quiz/topic-matrix` — returns quiz history grid
- [ ] RecallService — `get_recall_map()` with two-level recall and `get_topic_matrix()`
- [ ] CRUD `get_all_lesson_memories` — select all lesson memories for recall map
- [ ] CRUD `get_all_quiz_logs` — select all quiz logs for matrix
- [ ] Frontend RecallDashboardPage — page layout and data fetching
- [ ] Frontend RecallHeatmap component — color-coded topic cards, expandable
- [ ] Frontend LessonRecallList component — nested lesson recall within expanded topic
- [ ] Frontend RecallSummary component — global recall + topics at risk + lessons at risk
- [ ] Frontend TopicMatrix component — chronological quiz result grid
- [ ] Frontend QuizLaunchButton component — navigate to quiz page with scope (topic or lesson)
- [ ] Frontend useDashboardData hook — fetch recall map + topic matrix, manage expanded state

---

[< Prev: Quiz](./quiz.md) | [Parent](./index.md)
