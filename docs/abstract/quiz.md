# Quiz

[< Prev: Authentication](./authentication.md) | [Parent](./index.md) | [Next: Recall Dashboard >](./recall_dashboard.md)

**Status:** Plan

## Related Docs
- Technical: [technical/quiz.md](../technical/quiz.md)

## Problem

Users learn lessons across many topics but naturally forget material over time. Without a system that knows *what* each user is forgetting, quizzes either repeat what they already know or miss what they have forgotten. Users need quizzes that focus on their weakest areas and adapt as they improve. Topics and lessons are user-defined and cover a general domain — anything the user has studied and written lesson notes for.

## Solution

Each lesson is stored in the system with its topic, title, published date, and full content (in markdown format). Lessons are created via the API — for example, from a local agent or the lesson-youtube skill — and assigned a unique ID automatically.

All quiz questions are prepared in advance by a local AI agent and stored in a question bank. The agent generates questions from lesson content and uploads them to the app through its API, using a stored authentication token. This means questions can be uploaded to both local and remote servers without direct database access. Topics are automatically registered when quiz questions are uploaded — no server redeployment is needed to add new topics or lessons.

When a user requests a quiz, the app uses a spaced-repetition algorithm called MEMORIZE to pick the right question. The algorithm tracks recall at three levels — **topic level**, **lesson level**, and **question level** — and selects the question the user is most likely to have forgotten. Users can also choose to focus on a specific topic or lesson. After the user answers, the system updates their memory profile at all three levels — correct answers slow future forgetting; wrong answers accelerate it.

## User Flow

```
User opens quiz page (or clicks "Take Quiz" from a lesson page)
      |
      v
A quiz is loaded immediately using the current scope
  (defaults to "all topics"; pre-selected if arriving from a lesson page)
      |
      v
User can change scope at any time — a new quiz loads automatically
      |
      v
System selects a question using MEMORIZE or the user's selected scope:
  - Lesson scope: sliding window dedup, random order
  - Topic scope: question-level recall, lowest m(t) first, loop of min(10, total)
  - Global scope: question-level recall across all topics, loop of min(10, total)
      |
      v
System picks a pre-generated question from the question bank
  (4 options, one or more correct)
      |
      v
User sees the question and selects an answer
  (progress squares show status of each question in the loop:
   green = correct, red = incorrect, yellow = skipped, gray = not yet answered)
      |
      v
System grades the answer
      |
      v
User sees result: correct/incorrect + explanation
      |
      v
System updates the user's memory profile at all three levels
  (topic, lesson, and question)
      |
      v
After all questions in the loop have been answered:
  User sees a loop summary: correct count, incorrect count, accuracy
  User clicks "Next Loop" to begin another pass
```

## How Smart Selection Works (MEMORIZE)

The system tracks recall at **three levels**: topic, lesson, and question. Each level maintains its own recall score per user — a number between 0 and 1 representing how well the user likely remembers that material right now.

- **Score near 1.0** — the user reviewed this recently and is likely to remember it.
- **Score near 0.0** — the user has not reviewed this in a while and is likely forgetting it.
- **Never reviewed** — treated as 0.0 so the system prioritizes first exposure.

**For topic or global scope** — the system picks the individual question with the **lowest question-level recall score** within the selected scope. All quiz types (recall, understanding, application, analysis) compete equally — there is no type rotation.

**For lesson scope** — the system uses a sliding window to cycle through all questions in the lesson without repeats, in random order across all quiz types.

When the user answers, all three memory profiles are updated:

- **Correct** — the forgetting speed decreases by 30% at all three levels, meaning the user will retain it longer before the next review.
- **Incorrect** — the forgetting speed increases by 20% at all three levels, meaning the system will return to this material sooner.

## User-Selected Scope

Instead of relying on automatic selection, the user can choose to focus on:

- **All topics** (default) — the system picks the question with the lowest recall across all topics. Loop size = min(10, total questions).
- **A specific topic** — the system picks the question with the lowest recall within that topic. Loop size = min(10, total questions in topic).
- **A specific lesson** — the system cycles through all questions in the lesson using a sliding window (no repeats until all seen).

## What the User Sees

Each quiz is presented in two stages:

1. **The question** — a multiple-choice question with exactly 4 options (A–D). Colored progress squares show the status of each question in the loop: green for correct, red for incorrect, yellow for skipped, gray for not yet answered.
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

Questions test deep understanding, not surface-level memorization. All quiz types compete equally in selection — there is no type rotation.

## Scope

- **Included:**
  - Lesson records with topic, title, published date, and markdown content
  - Lesson dashboard with a table view, topic filter, sorting by topic or publish date, per-lesson recall score, and per-lesson accuracy (based on latest answer per unique question)
  - Lesson detail view rendering markdown content with syntax highlighting
  - Multiple-choice questions with 4 options (single or multi-answer)
  - Per-option explanations shown after answering
  - Three-level spaced-repetition: topic-level, lesson-level, and question-level recall tracking (MEMORIZE algorithm)
  - User-selected scope: all topics, specific topic, or specific lesson
  - Question-level recall selection for topic and global scopes (lowest m(t) first)
  - Memory profile updates at all three levels (topic, lesson, question) on each answer
  - Loop tracking for all scopes with progress squares and loop summary

- **Not included:**
  - On-the-fly question generation — all questions are pre-generated offline and uploaded via the API
  - Free-text or open-ended questions
  - Chat-based interaction — quizzes are standalone request/response
  - Timed quizzes or time pressure mechanics
  - Leaderboards or social features
  - Lesson editing in the web app — lessons are created via the API only

## Acceptance Criteria

- [ ] User can request a new quiz from the quiz page
- [ ] User can select scope: all topics, a specific topic, or a specific lesson
- [ ] The system selects the weakest topic and weakest lesson within it (or uses the user's scope)
- [ ] A multiple-choice question with 4 options is displayed
- [ ] After answering, the user sees whether they were correct or incorrect
- [ ] After answering, the user sees an explanation for the correct answer
- [ ] Correct answers reduce how quickly the topic, lesson, and question are forgotten
- [ ] Incorrect answers increase how quickly the topic, lesson, and question are forgotten
- [ ] For topic/global scope, the question with the lowest recall is prioritized
- [ ] User can browse all lessons from a lesson dashboard in a table with title, topic, and date columns
- [ ] User can filter the lesson table by topic
- [ ] User can sort the lesson table by topic name or publish date
- [ ] Each lesson in the table shows its current recall score and accuracy as percentages
- [ ] Accuracy is calculated from the latest answer per unique question: correct_last / K (where K = total questions)
- [ ] User can click a lesson to view its full markdown content with proper formatting
- [ ] User can click "Take Quiz" from a lesson page to start a quiz scoped to that lesson
- [ ] After completing all questions in a loop (any scope), user sees a loop summary with correct/incorrect counts and accuracy
- [ ] User can click "Next Loop" on the summary to start another pass
- [ ] Loop counter increments on each completed pass
- [ ] Loop size is min(10, total questions) for topic and global scopes

---

[< Prev: Authentication](./authentication.md) | [Parent](./index.md) | [Next: Recall Dashboard >](./recall_dashboard.md)
