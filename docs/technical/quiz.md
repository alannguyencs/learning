# Quiz — Technical Design

[< Prev: Authentication](./authentication.md) | [Parent](./index.md) | [Next: Recall Dashboard >](./recall_dashboard.md)

## Related Docs
- Abstract: [abstract/quiz.md](../abstract/quiz.md)

## Architecture

```
+-----------+       +---------------------+       +------------+
|  Frontend | ----> |  Backend (FastAPI)   | ----> | PostgreSQL |
|  (React)  | <---- |                     | <---- |            |
+-----------+       +---------------------+       +------------+
                                                   QuizQuestion
                                                   (pre-generated
                                                    question bank)

Offline (quiz upload via API):
+-------------+       +---------------------+       +------------+
| Local Agent | ----> |  Backend (FastAPI)   | ----> | PostgreSQL |
| (LLM call)  |  POST |  POST /api/quiz/    |       | INSERT     |
+-------------+  Bearer  questions           |       +------------+
                  token +---------------------+
```

**Layers involved:**

- **Frontend** — Quiz page. User selects scope (all topics / specific topic / specific lesson), requests a quiz, answers it, sees the result.
- **Backend — API** — REST endpoints for serving quizzes and submitting answers. Accepts optional scope filters.
- **Backend — Service** — Quiz selector (two-level MEMORIZE algorithm), answer grader, memory updater (topic + lesson).
- **Backend — CRUD** — Reads `QuizQuestion` (question bank), reads/writes `QuizLog`, `UserTopicMemory`, and `UserLessonMemory`.
- **Database** — Stores the pre-generated question bank, quiz logs, and two-level memory state.

Quiz questions are **not generated at runtime**. A local AI agent generates questions offline and uploads them via `POST /api/quiz/questions` using a Bearer token for authentication. The web app only selects and serves them.

Topics and lessons are user-defined. The user provides lesson content (markdown files) organized by topic. The local agent reads each lesson and generates quiz questions for it.

Topics are derived at runtime from the `quiz_questions` table. When new questions are uploaded with a previously unseen `topic_id`, the server registers the topic automatically. `topics.json` serves as the initial seed and as the local metadata source for the upload command.

## Data Model

### **`QuizQuestion`**

Pre-generated question bank. Populated offline by a local agent. Always exactly 4 options (A–D). Single-answer quizzes have `correct_options` with one entry; multi-answer quizzes have multiple.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer, PK | Auto-increment |
| `topic_id` | String | Topic this question belongs to |
| `lesson_id` | Integer | Lesson identifier |
| `lesson_filename` | String | Filename of the lesson source (e.g. `"sleep_hygiene.md"`) |
| `topic_name` | String, nullable | Human-readable topic name (e.g. "Coach") |
| `lesson_name` | String, nullable | Human-readable lesson name (e.g. "Bloom: LLM-Augmented Behavior Change") |
| `quiz_type` | String | `recall`, `understanding`, `application`, or `analysis` |
| `question` | Text | The question text |
| `quiz_learnt` | Text | What the user is learning from this quiz — shown after the user answers |
| `option_A` | Text | Text for option A |
| `option_B` | Text | Text for option B |
| `option_C` | Text | Text for option C |
| `option_D` | Text | Text for option D |
| `correct_options` | JSON (list[string]) | Correct letter(s), e.g. `["B"]` or `["A", "C"]` |
| `response_to_user_option_A` | Text | Explanation shown if user picks A |
| `response_to_user_option_B` | Text | Explanation shown if user picks B |
| `response_to_user_option_C` | Text | Explanation shown if user picks C |
| `response_to_user_option_D` | Text | Explanation shown if user picks D |
| `quiz_take_away` | Text | Key takeaway — shown after the user answers |
| `created_at` | DateTime | When the question was generated |

Indexes: `(topic_id, lesson_id, quiz_type)`, `(lesson_id, quiz_type)`

### **`QuizLog`**

Records each quiz served to a user and their response.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer, PK | Auto-increment |
| `username` | String, FK → users | Who took the quiz |
| `quiz_question_id` | Integer, FK → QuizQuestion | Which pre-generated question was served |
| `topic_id` | String | Topic (denormalized for fast queries) |
| `lesson_id` | Integer | Lesson (denormalized for fast queries) |
| `quiz_type` | String | `recall`, `understanding`, `application`, or `analysis` |
| `user_answer` | JSON (list[string]), nullable | What the user selected, e.g. `["B"]` or `["A", "C"]`; null while pending |
| `assessment_result` | String, nullable | `correct` or `incorrect`; null while pending |
| `created_at` | DateTime | When the quiz was served to the user |

Indexes: `(username, topic_id)`, `(username, lesson_id)`, `(username, created_at)`

### **`UserTopicMemory`**

Tracks the MEMORIZE spaced-repetition state per user per **topic**.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer, PK | Auto-increment |
| `username` | String, FK → users | Who this memory belongs to |
| `topic_id` | String | Topic identifier |
| `forgetting_rate` | Float, CHECK > 0 | The `n` parameter; adapts on each answer |
| `last_review_at` | DateTime | Timestamp of the last quiz in this topic |
| `last_review_quiz_count` | Integer | User's global quiz count at time of last review |
| `review_count` | Integer | Total quizzes taken in this topic |
| `correct_count` | Integer | Correct answers in this topic |

Constraint: UNIQUE(`username`, `topic_id`)

### **`UserLessonMemory`**

Tracks the MEMORIZE spaced-repetition state per user per **lesson**.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer, PK | Auto-increment |
| `username` | String, FK → users | Who this memory belongs to |
| `topic_id` | String | Parent topic (for grouping queries) |
| `lesson_id` | Integer | Lesson identifier |
| `forgetting_rate` | Float, CHECK > 0 | The `n` parameter; adapts on each answer |
| `last_review_at` | DateTime | Timestamp of the last quiz for this lesson |
| `last_review_quiz_count` | Integer | User's global quiz count at time of last review |
| `review_count` | Integer | Total quizzes taken for this lesson |
| `correct_count` | Integer | Correct answers for this lesson |

Constraint: UNIQUE(`username`, `lesson_id`)

Index: `(username, topic_id)` — for fetching all lesson memories within a topic.

## Pipeline

```
User selects scope (all topics / specific topic / specific lesson)
  │
  ▼
GET /api/quiz/next?topic_id=X&lesson_id=Y  (params optional)
  │
  ▼
QuizSelector: resolve scope
  ├── If lesson_id provided → use that lesson directly
  ├── If topic_id provided → select weakest lesson in that topic
  └── If neither → select weakest topic, then weakest lesson
  │
  ▼
QuizSelector: select topic (skipped if topic_id or lesson_id provided)
  ├── Load all UserTopicMemory for user
  ├── Calculate m(t) for each topic
  │   m(t) = exp(-n * quizzes_elapsed / 10)
  │   Never-reviewed topics: m(t) = 0.0
  └── Pick topic with lowest m(t)
  │
  ▼
QuizSelector: select lesson (skipped if lesson_id provided)
  ├── Load all UserLessonMemory for lessons in selected topic
  ├── Calculate m(t) for each lesson
  │   Never-reviewed lessons: m(t) = 0.0
  └── Pick lesson with lowest m(t)
  │
  ▼
QuizSelector: select quiz type
  └── Rotate: recall → understanding → application → analysis
      Skip the 3 most recently used types
  │
  ▼
CRUD: SELECT QuizQuestion
  └── WHERE lesson_id = selected AND quiz_type = selected
      AND id NOT IN (user's recently seen question ids)
  │
  ▼
CRUD: INSERT QuizLog
  └── assessment_result = null (pending)
  │
  ▼
Response: { quiz_id, question, options[], quiz_type, topic_id, lesson_id }
  │
  ▼
User selects answer
  │
  ▼
POST /api/quiz/{quiz_id}/answer  { answer: ["B"] }
  │
  ▼
AnswerService: grade answer
  ├── Load QuizLog + linked QuizQuestion
  ├── Compare answer list to correct_options (exact match, order-independent)
  ├── Store user_answer on QuizLog
  └── Set assessment_result = "correct" or "incorrect"
  │
  ▼
MemoryService: update memory (BOTH levels)
  ├── Update UserTopicMemory for this topic
  │   ├── Correct:  n *= 0.7
  │   └── Incorrect: n *= 1.2, capped at 1.5
  ├── Update UserLessonMemory for this lesson
  │   ├── Correct:  n *= 0.7
  │   └── Incorrect: n *= 1.2, capped at 1.5
  └── Increment review_count + correct_count, set last_review_quiz_count
  │
  ▼
CRUD: UPDATE QuizLog + UserTopicMemory + UserLessonMemory
  │
  ▼
Response: { is_correct, correct_options, quiz_learnt, explanations{A,B,C,D}, quiz_take_away }
```

## Algorithms

### MEMORIZE — Two-Level Selection

The algorithm operates at two levels. Both use the same recall formula and update rules, but are tracked independently.

**Hierarchy:** Topic > Lesson

### MEMORIZE — Topic Selection

- Each user has a `UserTopicMemory` record per topic, tracking the forgetting rate `n`.
- Recall probability: `m(t) = exp(-n * quizzes_elapsed / QUIZ_DECAY_SCALE)` where `QUIZ_DECAY_SCALE = 10`.
- `quizzes_elapsed` = user's current total quiz count minus the quiz count at last review of this topic.
- Never-reviewed topics use `m(t) = 0.0` so they are prioritized for first exposure.
- The topic with the **lowest** `m(t)` is selected.
- Skipped if the user provides a `topic_id` or `lesson_id` in the request.

### MEMORIZE — Lesson Selection (Within Topic)

- Each user has a `UserLessonMemory` record per lesson, tracking its own forgetting rate `n`.
- Uses the same recall formula: `m(t) = exp(-n * quizzes_elapsed / 10)`.
- `quizzes_elapsed` = user's total quiz count minus the quiz count at last review of this lesson.
- Never-reviewed lessons use `m(t) = 0.0`.
- The lesson with the **lowest** `m(t)` within the selected topic is chosen.
- Skipped if the user provides a `lesson_id` in the request.

### MEMORIZE — Forgetting Rate Update

Applied at **both** topic and lesson level after each answer:

- On correct answer: `n *= (1 - alpha)` where `alpha = 0.3`. Forgetting slows.
- On incorrect answer: `n *= (1 + beta)` where `beta = 0.2`. Forgetting accelerates.
- `n` is capped at `N_MAX = 1.5` to prevent runaway decay.

### Initial Forgetting Rates

**Per topic** (used when creating `UserTopicMemory`):

- Default: `0.3` for all topics.
- Topics and lessons are user-defined (general domain). The default rate can be overridden per-topic in a config/lookup table if specific topics are known to be harder.

**Per lesson** (used when creating `UserLessonMemory`):

- Defaults to the parent topic's initial forgetting rate.
- Can be overridden per-lesson in a config/lookup table if specific lessons are known to be harder.

### Quiz Type Rotation

- Four types cycle in order: recall → understanding → application → analysis.
- The 3 most recently used types for this user are excluded from selection.
- This ensures variety across consecutive quizzes.

### Question Deduplication

- When selecting from `QuizQuestion`, exclude question IDs the user has already seen (present in their `QuizLog`).
- If all questions for the selected lesson + type have been used, allow repeats starting from the oldest-seen question.

## Backend — API Layer

| Method | Path | Auth | Request | Response | Status |
|--------|------|------|---------|----------|--------|
| GET | `/api/quiz/next` | Session | query: `topic_id` (opt), `lesson_id` (opt) | `{ quiz_id, question, options[], quiz_type, topic_id, lesson_id }` | 200 |
| POST | `/api/quiz/{quiz_id}/answer` | Session | `{ answer: ["B"] }` | `{ is_correct, correct_options, quiz_learnt, explanations{A,B,C,D}, quiz_take_away }` | 200 |
| GET | `/api/quiz/history` | Session | query: `limit`, `offset` | `{ quizzes[] }` | 200 |
| GET | `/api/quiz/stats` | Session | — | `{ total, correct, accuracy }` | 200 |
| GET | `/api/quiz/eligibility` | Session | — | `{ eligible, reason }` | 200 |
| GET | `/api/quiz/topics` | Session | — | `{ topics[] }` with lesson lists | 200 |
| POST | `/api/quiz/questions` | Bearer | `List[QuizQuestionCreate]` | `{ inserted, lesson_id, topic_id }` | 200 |

## Backend — Service Layer

**QuizSelector** — Implements the two-level MEMORIZE algorithm. Resolves scope (all / topic / lesson), selects the optimal topic and lesson using recall scores, selects quiz type, and picks a `QuizQuestion` from the question bank. Pure logic, no side effects.

**AnswerService** — Grades the user's answer by comparing the submitted `answer` list against `correct_options` from the linked `QuizQuestion` (exact match, order-independent). Stores `user_answer` on the `QuizLog`, determines `assessment_result`, and returns all 4 option explanations. Delegates memory update to `MemoryService`.

**MemoryService** — Updates **both** `UserTopicMemory` and `UserLessonMemory` after each answer. Applies the MEMORIZE forgetting-rate adjustment (alpha/beta) at both levels, increments counters, and sets the last review checkpoint.

**TopicLookup** — Maintains the in-memory topic/lesson cache. Seeds from `topics.json` on module import. `sync_from_db()` is called on server startup to register any topics in the DB not present in `topics.json`. `register_topic()` is called after each quiz upload to immediately register new topics without restart.

## Offline Quiz Generation — LLM Prompt & Output Schema

Quiz questions are generated offline by a local AI agent and uploaded to the `QuizQuestion` table via `POST /api/quiz/questions`. The agent uses a Bearer token (stored in `.env` as `WEBAPP_ACCESS_TOKEN`) for authentication. This section documents the prompt and output schema used by the agent.

Reference command: `.claude/commands/quiz_upload.md`

### Question Formats

Each question uses one of two formats (randomly assigned during generation):

- **Multiple Choice** — exactly 4 options (A–D), exactly 1 correct answer. `correct_options` has one entry.
- **Multiple Selection** — exactly 4 options (A–D), 2 or more correct answers. The question text includes "select all that apply". `correct_options` has multiple entries. All correct options must be selected to count as fully correct.

### Prompt Structure

```
+----------------------------------------------------------+
|  SYSTEM PROMPT                                           |
|  (resources/prompts/quiz_system_prompt.md)               |
|                                                          |
|  Role: quiz question author for learning lessons         |
|                                                          |
|  Question rules:                                         |
|  - Exactly 4 options (A-D)                               |
|  - Randomly alternate between Multiple Choice (1 correct)|
|    and Multiple Selection (2+ correct, "select all that  |
|    apply")                                               |
|  - Questions should test deep understanding, not         |
|    surface-level memorization                            |
|                                                          |
|  Field rules:                                            |
|  - quiz_learnt: brief summary of the lesson being tested |
|    — shown after the user answers                        |
|  - response_to_user_option_*: explain why the option is  |
|    correct or wrong with concrete reasoning — not just   |
|    "correct" / "incorrect". For wrong options, explain    |
|    what would need to be different for them to be right.  |
|    Clarify, expand, or correct as needed.                |
|  - quiz_take_away: a concise, memorable insight the user |
|    should internalize — a rule, distinction, or pattern  |
|                                                          |
|  Output format: structured JSON                          |
+----------------------------------------------------------+
|                                                          |
+----------------------------------------------------------+
|  USER PROMPT                                             |
|                                                          |
|  +----------------------------------------------------+  |
|  | Lesson content                                     |  |
|  | - Title, what, why, how                            |  |
|  +----------------------------------------------------+  |
|  | Quiz type instruction                              |  |
|  | - Cognitive level: recall, understanding,           |  |
|  |   application, or analysis                         |  |
|  | - e.g. "Write an application-level question"       |  |
|  +----------------------------------------------------+  |
|  | Output format reminder                             |  |
|  | - JSON with quiz_learnt, question, option_A..D,    |  |
|  |   correct_options, response_to_user_option_A..D,   |  |
|  |   quiz_take_away                                   |  |
|  +----------------------------------------------------+  |
|                                                          |
+----------------------------------------------------------+
```

### Cognitive Levels (quiz_type)

Each question targets one of four cognitive levels, varied across generation:

| Level | What it tests | Example stem |
|-------|--------------|--------------|
| `recall` | Basic facts from the lesson | "Which of the following is..." |
| `understanding` | Explain concepts, rephrase, compare | "What best describes why..." |
| `application` | Apply knowledge to a situation | "Given this scenario, what would..." |
| `analysis` | Compare, contrast, identify relationships | "What is the key difference between..." |

### Field Guidance

**`quiz_learnt`** — Briefly summarizes what the user is learning from this quiz. Shown after the user answers, before the per-option explanations. Example: "How the MEMORIZE forgetting rate changes with correct and incorrect answers."

**`response_to_user_option_*`** — Each explanation should cover *why* the option is correct or wrong with concrete reasoning. For wrong options, explain what would need to be different for them to be right. Avoid generic "This is incorrect" — instead give the user something to learn from each option.

**`quiz_take_away`** — A concise insight the user should remember. Can be a rule, a distinction between easily confused concepts, or a pattern to internalize. Shown after the user answers. Example: "ambivalent = internal tug-of-war ('I want to... but I also don't want to') vs. barrier_discussion = external blocker ('I want to... but something is stopping me')."

### Output Schema

**`QuizQuestionOutput`** — structured JSON:

| Field | Type | Description |
|-------|------|-------------|
| `quiz_learnt` | string | What the user is learning from this quiz — shown after the user answers |
| `question` | string | The quiz question text. For Multiple Selection, includes "select all that apply". |
| `option_A` | string | First answer choice (always exactly 4 options) |
| `option_B` | string | Second answer choice |
| `option_C` | string | Third answer choice |
| `option_D` | string | Fourth answer choice |
| `correct_options` | list[string] | Correct letter(s). `["B"]` for Multiple Choice, `["A", "C"]` for Multiple Selection. |
| `response_to_user_option_A` | string | Explanation if user selects A — why correct/wrong with reasoning |
| `response_to_user_option_B` | string | Explanation if user selects B — why correct/wrong with reasoning |
| `response_to_user_option_C` | string | Explanation if user selects C — why correct/wrong with reasoning |
| `response_to_user_option_D` | string | Explanation if user selects D — why correct/wrong with reasoning |
| `quiz_take_away` | string | Key takeaway — shown after answering, alongside the explanations |

The local agent calls the LLM with this prompt for each (lesson, quiz_type) combination, then uploads the batch via `POST /api/quiz/questions` with a Bearer token.

### Upload Payload — `QuizQuestionCreate`

The upload payload sent to `POST /api/quiz/questions` includes all `QuizQuestionOutput` fields plus metadata resolved from `topics.json`:

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | string | Topic identifier (from `topics.json`) |
| `lesson_id` | integer | Lesson identifier (from `topics.json`) |
| `lesson_filename` | string | Filename of the lesson source |
| `topic_name` | string | Human-readable topic name (e.g. "Coach") |
| `lesson_name` | string | Human-readable lesson name (e.g. "Bloom: LLM-Augmented Behavior Change") |
| *(all QuizQuestionOutput fields)* | | |

## Backend — CRUD Layer

**crud_quiz_question:**
- `get_question(db, lesson_id, quiz_type, exclude_ids)` — SELECT a `QuizQuestion` matching the criteria, excluding already-seen IDs. Returns one question or `None`.
- `get_question_count(db, lesson_id)` — COUNT questions available for a lesson (used by eligibility check).
- `create_quiz_questions(db, questions)` — Bulk INSERT a list of question dicts using `db.add_all()`. Returns the count inserted.

**crud_quiz_log:**
- `create_quiz_log(db, username, quiz_question_id, topic_id, lesson_id, quiz_type)` — INSERT a new pending quiz log record.
- `record_quiz_answer(db, quiz_id, user_answer, assessment_result)` — UPDATE the quiz log with the user's answer (list of selected letters) and result.
- `get_seen_question_ids(db, username, lesson_id, quiz_type)` — SELECT question IDs the user has already been served for deduplication.
- `get_quiz_history(db, username, limit, offset)` — SELECT quiz logs ordered by `created_at` descending.
- `get_user_total_quiz_count(db, username)` — COUNT all quiz logs for this user (used in MEMORIZE calculations).

**crud_topic_memory:**
- `get_or_create_memory(db, username, topic_id)` — SELECT existing record or INSERT with the topic's initial forgetting rate.
- `update_memory_on_quiz_result(db, username, topic_id, is_correct, current_quiz_count)` — Apply alpha/beta to `forgetting_rate`, increment counters, set `last_review_quiz_count`.
- `get_all_memory_states(db, username)` — SELECT all `UserTopicMemory` records for a user.

**crud_lesson_memory:**
- `get_or_create_memory(db, username, topic_id, lesson_id)` — SELECT existing record or INSERT with the lesson's initial forgetting rate (defaults to parent topic rate).
- `update_memory_on_quiz_result(db, username, lesson_id, is_correct, current_quiz_count)` — Apply alpha/beta to `forgetting_rate`, increment counters, set `last_review_quiz_count`.
- `get_lesson_memories_for_topic(db, username, topic_id)` — SELECT all `UserLessonMemory` records for a user within one topic (used by lesson selection).
- `get_all_lesson_memories(db, username)` — SELECT all `UserLessonMemory` records for a user (used by recall dashboard).

## Frontend — Pages & Routes

| Route | Page | Description |
|-------|------|-------------|
| `/quiz` | QuizPage | Shows scope filter, current quiz or "Next Quiz" button. Displays question, options, and result after answering. |

## Frontend — Components

- **TopicLessonFilter** — Dropdown or selector allowing the user to choose scope: "All Topics" (default), a specific topic, or a specific lesson within a topic. When a topic is selected, its lessons are shown as a nested list.
- **QuizCard** — Renders the question text and 4 option buttons. For single-answer questions, selecting one option submits immediately. For multi-answer questions ("select all that apply"), the user toggles options and clicks a submit button. Disables options after submission.
- **QuizResult** — Shown after answering. Displays correct/incorrect badge, `quiz_learnt` as lesson context, the explanation for all 4 options (why each is correct/wrong), and the `quiz_take_away` as a highlighted insight.

## Frontend — Services & Hooks

- **api.js** — `getNextQuiz(topicId?, lessonId?)` calls GET `/api/quiz/next` with optional query params. `submitAnswer(quizId, answer[])` calls POST `/api/quiz/{id}/answer` with `{ answer: ["B"] }` or `{ answer: ["A", "C"] }`. `getQuizHistory(limit, offset)` calls GET `/api/quiz/history`. `getTopics()` calls GET `/api/quiz/topics`.
- **useQuiz** — Custom hook managing quiz state: `loading`, `quiz` (current question/options), `result` (after answer), `scope` (selected topic/lesson filter). Calls `getNextQuiz` and `submitAnswer` from api.js.

## Constraints & Edge Cases

- A user can only have one pending (unanswered) quiz at a time. Requesting a new quiz while one is pending replaces the old one.
- `forgetting_rate` must remain above 0 at both levels (enforced by CHECK constraint).
- `forgetting_rate` is capped at 1.5 at both levels to prevent runaway decay.
- Multi-answer quizzes require the user to select **all** correct options to be graded as correct. Partial matches count as incorrect.
- Quiz type rotation requires at least 4 quizzes before the full cycle repeats. With fewer than 4 historical quizzes, fewer types are excluded.
- If the question bank has no questions for the selected lesson + type, fall through to the next candidate lesson or return a 404.
- If the user specifies a `lesson_id`, `topic_id` is ignored.
- The question bank must be populated before the app is usable. An empty `QuizQuestion` table means no quizzes can be served. All lessons with questions in the bank are eligible for quizzing — there is no separate "introduction" step.
- When a user answers a quiz, **both** `UserTopicMemory` and `UserLessonMemory` are updated in the same transaction.

## Component Checklist

- [ ] Database model — `QuizQuestion` (pre-generated question bank, with `topic_id` + `lesson_id`)
- [ ] Database model — `QuizLog` (with `topic_id` + `lesson_id`)
- [ ] Database model — `UserTopicMemory`
- [ ] Database model — `UserLessonMemory`
- [ ] GET `/api/quiz/next` — accepts optional `topic_id` / `lesson_id`, selects quiz from bank
- [ ] POST `/api/quiz/{quiz_id}/answer` — grades answer, updates both memory levels
- [ ] GET `/api/quiz/history` — paginated quiz history
- [ ] GET `/api/quiz/stats` — total, correct, accuracy
- [ ] GET `/api/quiz/eligibility` — checks if questions exist
- [ ] GET `/api/quiz/topics` — returns topic list with nested lessons for filter
- [ ] POST `/api/quiz/questions` — bulk-create quiz questions via Bearer token auth
- [ ] QuizSelector service — two-level MEMORIZE (topic + lesson selection) + scope resolution + type rotation + question picking
- [ ] AnswerService — answer grading logic
- [ ] MemoryService — forgetting rate update at both topic and lesson level
- [ ] CRUD quiz_question — get question, count questions, bulk create
- [ ] CRUD quiz_log — create, record answer, seen IDs, history, count
- [ ] CRUD topic_memory — get/create, update on result, get all states
- [ ] CRUD lesson_memory — get/create, update on result, get by topic, get all
- [ ] Offline prompt — quiz_system_prompt.md + QuizQuestionOutput schema
- [ ] Frontend QuizPage — scope filter, next quiz button, question display, answer submission, result display
- [ ] Frontend TopicLessonFilter component — scope selector (all / topic / lesson)
- [ ] Frontend QuizCard component — question + 4 option buttons
- [ ] Frontend QuizResult component — correct/incorrect + explanation
- [ ] Frontend useQuiz hook — quiz state management with scope
- [ ] Frontend api.js — getNextQuiz, submitAnswer, getQuizHistory, getTopics

---

[< Prev: Authentication](./authentication.md) | [Parent](./index.md) | [Next: Recall Dashboard >](./recall_dashboard.md)
