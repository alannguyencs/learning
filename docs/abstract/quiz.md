# Quiz

[< Prev: Authentication](./authentication.md) | [Parent](./index.md) | [Next: Recall Dashboard >](./recall_dashboard.md)

**Status:** Plan

## Related Docs
- Technical: [technical/quiz.md](../technical/quiz.md)

## Problem

Users learn lessons across many topics but naturally forget material over time. Without a system that knows *what* each user is forgetting, quizzes either repeat what they already know or miss what they have forgotten. Users need quizzes that focus on their weakest areas and adapt as they improve. Topics and lessons are user-defined and cover a general domain — anything the user has studied and written lesson notes for.

## Solution

All quiz questions are prepared in advance by a local AI agent and stored in a question bank. The agent generates questions from lesson content and uploads them to the app through its API, using a stored authentication token. This means questions can be uploaded to both local and remote servers without direct database access. Topics are automatically registered when quiz questions are uploaded — no server redeployment is needed to add new topics or lessons.

When a user requests a quiz, the app uses a spaced-repetition algorithm called MEMORIZE to pick the right question. The algorithm tracks recall at two levels — **topic level** and **lesson level** — and selects the topic the user is most likely to have forgotten, then the weakest lesson within it. Users can also choose to focus on a specific topic or lesson. After the user answers, the system updates their memory profile at both levels — correct answers slow future forgetting; wrong answers accelerate it.

## User Flow

```
User opens quiz page
      |
      v
User selects scope: all topics, a specific topic, or a specific lesson
  (defaults to "all topics")
      |
      v
Requests a new quiz
      |
      v
System selects weakest topic and lesson (MEMORIZE)
  or uses the user's selected scope
      |
      v
System picks a pre-generated question from the question bank
  (4 options, one or more correct)
      |
      v
User sees the question and selects an answer
      |
      v
System grades the answer
      |
      v
User sees result: correct/incorrect + explanation
      |
      v
System updates the user's memory profile for both the topic and the lesson
```

## How Smart Selection Works (MEMORIZE)

The system tracks recall at **two levels**: topic and lesson (user-defined, general domain). Each level maintains its own recall score per user — a number between 0 and 1 representing how well the user likely remembers that material right now.

- **Score near 1.0** — the user reviewed this recently and is likely to remember it.
- **Score near 0.0** — the user has not reviewed this in a while and is likely forgetting it.
- **Never reviewed** — treated as 0.0 so the system prioritizes first exposure.

**Step 1 — Pick the weakest topic.** Each topic has a difficulty-based forgetting speed. Easier topics (e.g. habits, social connections) decay slowly. Harder topics (e.g. gut health, preventive medicine) decay faster. The system picks the topic with the **lowest topic-level recall score**.

**Step 2 — Pick the weakest lesson within that topic.** Each lesson also has its own recall score and forgetting speed. The system picks the lesson with the **lowest lesson-level recall score** within the selected topic.

When the user answers, both the topic and lesson memory profiles are updated:

- **Correct** — the forgetting speed decreases by 30% at both levels, meaning the user will retain it longer before the next review.
- **Incorrect** — the forgetting speed increases by 20% at both levels, meaning the system will return to this material sooner.

## User-Selected Scope

Instead of relying on automatic selection, the user can choose to focus on:

- **All topics** (default) — the system picks the weakest topic and lesson automatically.
- **A specific topic** — the system picks the weakest lesson within that topic.
- **A specific lesson** — the system serves a question for that lesson directly.

## What the User Sees

Each quiz is presented in two stages:

1. **The question** — a multiple-choice question with exactly 4 options (A–D).
2. **After answering** — the result (correct/incorrect), a brief summary of the lesson being tested, an explanation for each option covering why the correct answer is right and why the wrong answers don't fit, and a **key takeaway** — a concise insight the user should internalize from this quiz.

## Quiz Types

Each question uses one of two formats, randomly assigned:

- **Multiple Choice** — 4 options, exactly 1 correct answer.
- **Multiple Selection** — 4 options, 2 or more correct answers ("select all that apply"). All correct options must be selected to count as fully correct.

The system rotates through four cognitive levels to test different depths of understanding:

1. **Recall** — Does the user know the basic facts?
2. **Understanding** — Can the user explain the concept and compare ideas?
3. **Application** — Can the user apply the knowledge to a situation?
4. **Analysis** — Can the user identify relationships, compare, or contrast?

Questions test deep understanding, not surface-level memorization. The system avoids repeating the same cognitive level in consecutive quizzes.

## Scope

- **Included:**
  - Multiple-choice questions with 4 options (single or multi-answer)
  - Per-option explanations shown after answering
  - Two-level spaced-repetition: topic-level and lesson-level recall tracking (MEMORIZE algorithm)
  - User-selected scope: all topics, specific topic, or specific lesson
  - Quiz type rotation across 4 styles
  - Memory profile updates at both topic and lesson level on each answer

- **Not included:**
  - On-the-fly question generation — all questions are pre-generated offline and uploaded via the API
  - Free-text or open-ended questions
  - Chat-based interaction — quizzes are standalone request/response
  - Timed quizzes or time pressure mechanics
  - Leaderboards or social features

## Acceptance Criteria

- [ ] User can request a new quiz from the quiz page
- [ ] User can select scope: all topics, a specific topic, or a specific lesson
- [ ] The system selects the weakest topic and weakest lesson within it (or uses the user's scope)
- [ ] A multiple-choice question with 4 options is displayed
- [ ] After answering, the user sees whether they were correct or incorrect
- [ ] After answering, the user sees an explanation for the correct answer
- [ ] Correct answers reduce how quickly the topic and lesson are forgotten
- [ ] Incorrect answers increase how quickly the topic and lesson are forgotten
- [ ] Quiz types rotate and do not repeat the same style consecutively

---

[< Prev: Authentication](./authentication.md) | [Parent](./index.md) | [Next: Recall Dashboard >](./recall_dashboard.md)
