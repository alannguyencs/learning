# System Pipelines

[Parent](./index.md) | [Next: Authentication >](./authentication.md)

## Login Pipeline — [details](./authentication.md)

```
User submits login form
  │
  ▼
POST /api/login (username, password)
  │
  ▼
bcrypt.verify(password, hashed_password)
  │
  ▼
create_access_token(90d expiry, HS256 JWT)
  │
  ▼
Set-Cookie (HttpOnly, access_token)
  │
  ▼
Navigate to /quiz
```

## Session Restore Pipeline — [details](./authentication.md)

```
Page load / refresh
  │
  ▼
AuthContext calls GET /api/me
  │
  ▼
Read access_token cookie → decode JWT
  │
  ▼
get_user(username) from DB
  │
  ▼
Return {authenticated, user} to frontend
  │
  ▼
authenticated? ──No──> Redirect to /login
      │
     Yes
      │
      ▼
Render protected page
```

## Quiz Selection Pipeline — [details](./quiz.md)

```
User selects scope (all topics / topic / lesson)
  │
  ▼
GET /api/quiz/next?topic_id=X&lesson_id=Y  (params optional)
  │
  ▼
QuizSelector: resolve scope
  ├── lesson_id provided → use directly
  ├── topic_id provided → select weakest lesson in topic
  └── neither → select weakest topic, then weakest lesson
  │
  ▼
QuizSelector.select_topic_for_quiz()  (if no scope)
  ├── Load all UserTopicMemory records for user
  ├── Calculate topic-level m(t) for each topic (all user-defined topics)
  └── Select topic with lowest m(t)
  │
  ▼
QuizSelector.select_lesson_for_quiz()  (if no lesson_id)
  ├── Load all UserLessonMemory for lessons in topic
  ├── Calculate lesson-level m(t) for each lesson
  └── Select lesson with lowest m(t)
  │
  ▼
QuizSelector.select_quiz_type()
  └── Rotate through 4 types, skip 3 most recent
  │
  ▼
CRUD: SELECT QuizQuestion from question bank
  └── Match lesson + type, exclude already-seen questions
  │
  ▼
CRUD: INSERT QuizLog (pending, no answer yet)
  │
  ▼
Return quiz question + options to frontend
```

## Quiz Answer Pipeline — [details](./quiz.md)

```
User selects answer (A / B / C / D, or multiple for "select all that apply")
  │
  ▼
POST /api/quiz/{id}/answer  { answer: ["B"] }
  │
  ▼
AnswerService.grade_answer()
  ├── Load QuizLog + linked QuizQuestion
  ├── Compare user answer list to correct_options (exact match, order-independent)
  ├── Store user_answer on QuizLog
  └── Set assessment_result: "correct" or "incorrect"
  │
  ▼
MemoryService.update_memory()  (BOTH levels)
  ├── Update UserTopicMemory for topic
  │   ├── Correct:  n *= 0.7
  │   └── Incorrect: n *= 1.2  (capped at 1.5)
  └── Update UserLessonMemory for lesson
      ├── Correct:  n *= 0.7
      └── Incorrect: n *= 1.2  (capped at 1.5)
  │
  ▼
CRUD: UPDATE QuizLog + UserTopicMemory + UserLessonMemory
  │
  ▼
Return result + quiz_learnt + explanations (all 4 options) + quiz_take_away to frontend
```

## Quiz Upload Pipeline — [details](./quiz.md)

```
Local agent generates quiz questions from lesson file (LLM call)
  │
  ▼
Agent reads .env for WEBAPP_ACCESS_TOKEN and WEBAPP_API_URL
  │
  ▼
Agent writes questions to temp JSON file
  │
  ▼
POST /api/quiz/questions  (Authorization: Bearer <token>)
  │
  ▼
authenticate_user_from_request()
  ├── Cookie not present → check Authorization header
  └── Decode Bearer token as JWT → look up user
  │
  ▼
Validate List[QuizQuestionCreate] request body
  │
  ▼
CRUD: db.add_all(QuizQuestion objects) → bulk INSERT
  │
  ▼
Return { inserted, lesson_id, topic_id }
```

## Recall Dashboard Pipeline — [details](./recall_dashboard.md)

```
User opens Recall Dashboard page
  │
  ▼
GET /api/quiz/recall-map
  │
  ▼
RecallService.get_recall_map()
  ├── Load all UserTopicMemory records for user
  ├── Load all UserLessonMemory records for user
  ├── Get total quiz count for user
  ├── Calculate topic-level m(t) for each topic
  ├── Calculate lesson-level m(t) for each lesson
  ├── Compute global_recall = mean of all topic m(t)
  ├── Count topics_at_risk where topic m(t) < 0.5
  └── Count lessons_at_risk where lesson m(t) < 0.5
  │
  ▼
Return topics (with nested lessons) + global stats to frontend
```

## Topic Matrix Pipeline — [details](./recall_dashboard.md)

```
User views topic matrix on dashboard
  │
  ▼
GET /api/quiz/topic-matrix
  │
  ▼
RecallService.get_topic_matrix()
  ├── Load all QuizLog records for user
  ├── Group by topic_id
  ├── Assign chronological column_index to each quiz
  └── Build grid: rows=topics, columns=quiz attempts
      Each cell includes lesson_id for tooltip
  │
  ▼
Return matrix rows with per-cell result to frontend
```

---

[Parent](./index.md) | [Next: Authentication >](./authentication.md)
