# Quiz Generation & MEMORIZE Algorithm Reference

Reference from `/Users/alan/Documents/projects/coach_weight` — spaced repetition quiz system.

Based on: Tabibian et al., "Enhancing Human Learning via Spaced Repetition Optimization" (PNAS 2019)

## Core Concept

The system has **13 topics**, each containing multiple **principles** (131 total). It tracks a per-user, per-topic **forgetting curve** and always quizzes the weakest topic first.

## MEMORIZE Algorithm

### Memory Recall Formula

```
m(t) = exp(-n * quizzes_elapsed / QUIZ_DECAY_SCALE)

m(t)             = recall probability [0.0, 1.0]
n                = forgetting rate (per topic, adapts over time)
quizzes_elapsed  = total quizzes taken since last review of this topic
QUIZ_DECAY_SCALE = 10 (dampening constant)
```

Never-reviewed topics get `m(t) = 0.0` to force first review.

### Topic Selection (Step 1): Lowest Recall Wins

```python
for each topic:
    if reviewed before:
        recall = exp(-n * quizzes_elapsed / 10)
    else:
        recall = 0.0   # prioritize unreviewed topics

select topic with LOWEST recall
```

### Principle Selection (Step 2): Least Recently Quizzed

Within the selected topic, pick the principle that was quizzed **longest ago** (or never), filtering to only principles already introduced to the user.

### Quiz Type Rotation

Cycles through 4 types, avoiding the 3 most recently used:

```
recall → understanding → application → analysis → ...
```

### Memory Update on Answer

```python
alpha = 0.3   # strength multiplier
beta  = 0.2   # weakness multiplier
N_MAX = 1.5   # cap on forgetting rate

if correct:
    n *= (1 - alpha)   # n * 0.7 → decays slower → better retention
else:
    n *= (1 + beta)    # n * 1.2 → decays faster → needs more review
    n = min(n, N_MAX)
```

### Per-Topic Initial Forgetting Rates

Harder topics start with higher `n` (faster forgetting):

```python
TOPIC_N_INITIAL = {
    "behavior_change_and_habits":          0.20,  # easy
    "social_connections_and_community":     0.20,
    "nutrition_and_diet":                   0.25,
    "exercise_and_physical_activity":       0.25,
    "mental_health_and_mindset":            0.25,
    "lifestyle_and_work_life_balance":      0.25,
    "sleep_and_circadian_rhythm":           0.30,
    "stress_management":                    0.30,
    "gut_health":                           0.35,  # hard
    "fasting_and_meal_timing":              0.35,
    "environmental_health":                 0.35,
    "holistic_and_integrative_health":      0.35,
    "preventive_medicine_and_health_monitoring": 0.40,
}
```

## Quiz Generation Pipeline

```
1. select_topic_for_quiz()        → topic with lowest m(t)
2. select_principle_for_quiz()    → least-recently-quizzed principle in topic
3. select_quiz_type()             → rotate: recall/understanding/application/analysis
4. build_quiz_context()           → load principle content + 14 days of user conversations
5. LLM generates question         → 4 MCQ options + per-option explanations
6. log_quiz_asked()               → save to DB as pending
7. User answers                   → detect letter(s), grade, update memory
```

## Data Model

### UserTopicMemory (per user, per topic)

```
username              STR     unique with topic_id
topic_id              STR     one of 13 topics
forgetting_rate       FLOAT   n parameter (adapts on each answer)
last_review_at        DATETIME
last_review_quiz_count INT    global quiz count at last review
review_count          INT     total quizzes in this topic
correct_count         INT     correct answers in this topic
```

### QuizQuestion (pre-generated question bank)

All fields are top-level columns (no nested JSON except `correct_options`).

```
topic_id                    STR     one of 13 topics
lesson_id                   INT     1-131
lesson_filename             STR     source filename (e.g. "sleep_hygiene.md")
quiz_type                   STR     recall/understanding/application/analysis
question                    TEXT
quiz_learnt                 TEXT    what the user learns — shown after answering
option_A                    TEXT
option_B                    TEXT
option_C                    TEXT
option_D                    TEXT
correct_options             JSON    ["B"] or ["A", "C"]
response_to_user_option_A   TEXT    explanation if user picks A
response_to_user_option_B   TEXT    explanation if user picks B
response_to_user_option_C   TEXT    explanation if user picks C
response_to_user_option_D   TEXT    explanation if user picks D
quiz_take_away              TEXT    key takeaway shown after answering
created_at                  DATETIME
```

Always exactly 4 options (A–D). `correct_options` has one entry for single-answer, multiple for multi-answer. Per-user question history is tracked via `QuizLog.created_at`.

### QuizLog (per quiz served to a user)

```
username              STR
quiz_question_id      INT     FK → QuizQuestion
topic_id              STR     denormalized
lesson_id             INT     denormalized
quiz_type             STR     recall/understanding/application/analysis
user_answer           JSON    what the user selected, e.g. ["B"] or ["A", "C"] (nullable while pending)
assessment_result     STR     correct/incorrect (nullable while pending)
created_at            DATETIME
```

## Recall Map (Dashboard)

```
GET /api/quiz/recall-map

Response:
  topics[]           → per-topic: recall_probability, forgetting_rate, review_count, correct_count
  global_recall      → mean m(t) across all topics
  topics_at_risk     → count where m(t) < 0.5
```

Used for a heatmap: green (m > 0.7), yellow (0.5-0.7), red (m < 0.5).

## Backend File Map

```
service/quiz_coach/
├── quiz_selector.py           # MEMORIZE algorithm — topic & principle selection
├── quiz_service.py            # Core operations (generate, log, trigger check)
├── quiz_service_generate.py   # User-initiated quiz endpoint logic
├── quiz_prompt_builder.py     # Build LLM context with principle + user history
├── quiz_answer_processor.py   # Process user answer, trigger grading
├── quiz_assessor.py           # Grade answer (heuristic or LLM)
├── quiz_loader.py             # Load quiz templates & config
├── conversation_analyzer.py   # Extract struggles/wins from chat history
└── topic_lookup.py            # Static topic↔principle mapping

crud/
├── crud_topic_memory.py       # MEMORIZE state read/write + update logic
└── crud_quiz_log.py           # Quiz log CRUD + answer recording

api/
├── quiz_dashboard.py          # History, stats, principle-matrix endpoints
└── quiz_dashboard_memory.py   # Recall map, topic matrix, generate, answer endpoints
```

## Worked Example

```
User "john" has taken 47 quizzes total.

Topic memories:
  nutrition:  n=0.24, last_review_count=40 → m(t) = exp(-0.24 * 7/10)  = 0.85
  sleep:      n=0.35, last_review_count=35 → m(t) = exp(-0.35 * 12/10) = 0.65
  exercise:   n=0.40, last_review_count=20 → m(t) = exp(-0.40 * 27/10) = 0.34 ← LOWEST

→ Quiz selects exercise topic, picks least-recently-quizzed principle in it.

John answers correctly:
  exercise n: 0.40 * 0.7 = 0.28 (decays slower now)
  last_review_quiz_count = 48

Next trigger at quiz_count=60:
  exercise: exp(-0.28 * 12/10) = 0.71  (recovered)
  sleep:    exp(-0.35 * 25/10) = 0.41  ← now the weakest
→ Quiz shifts to sleep topic.
```
