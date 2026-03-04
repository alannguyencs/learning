# Recall Dashboard

[< Prev: Quiz](./quiz.md) | [Parent](./index.md)


**Status:** Plan

## Related Docs
- Technical: [technical/recall_dashboard.md](../technical/recall_dashboard.md)

## Problem

Users take quizzes over time but have no way to see which topics and lessons they are strong in and which are slipping. Without visibility into their overall learning state, they cannot make informed decisions about what to study next.

## Solution

A dashboard page that shows the user's current recall strength across all topics and lessons at a glance. Each topic is displayed with a color-coded indicator showing how well the user likely remembers it right now. Users can expand a topic to see the recall strength of each lesson within it. The dashboard also highlights topics and lessons at risk of being forgotten and shows overall learning progress.

## User Flow

```
User opens the recall dashboard
      |
      v
System calculates current recall score for each topic and lesson
      |
      v
Dashboard displays all topics with color-coded recall strength
      |
      v
User expands a topic to see lesson-level recall scores
      |
      v
User sees which topics and lessons are strong, weakening, or at risk
      |
      v
User can navigate to take a quiz
  (all topics, a specific topic, or a specific lesson)
```

## What the User Sees

### Recall Heatmap

Each topic is displayed as a card or cell with a color based on the user's current recall score:

- **Green** (score above 0.7) — well-remembered, no action needed.
- **Yellow** (score 0.5 to 0.7) — weakening, review soon.
- **Red** (score below 0.5) — at risk of being forgotten, review recommended.

Each topic card can be expanded to show lesson-level recall scores within it, using the same color scheme.

### Summary Stats

- **Overall recall** — average recall score across all topics.
- **Topics at risk** — count of topics scoring below 0.5.
- **Lessons at risk** — count of lessons scoring below 0.5.
- **Per-topic details** — number of quizzes taken and accuracy rate for each topic.

### Topic Quiz History Matrix

A grid view showing quiz attempts over time:

- **Rows** — one per topic.
- **Columns** — each quiz attempt in chronological order.
- **Cells** — colored by result (correct, incorrect, or not yet answered).

This lets users see patterns — for example, a topic that was consistently correct but has had no recent activity, or a topic with a streak of incorrect answers.

## Scope

- **Included:**
  - Recall heatmap with color-coded topic cards
  - Expandable topics showing lesson-level recall scores
  - Overall recall score, topics-at-risk count, and lessons-at-risk count
  - Per-topic and per-lesson quiz count and accuracy
  - Topic quiz history matrix (grid of attempts over time)
  - Navigation to start a quiz from the dashboard (all topics, specific topic, or specific lesson)

- **Not included:**
  - Recall trend graphs over time (line charts)
  - Comparison with other users
  - Export or sharing of progress data
  - Push notifications for at-risk topics

## Acceptance Criteria

- [ ] Dashboard displays all topics with their current recall strength
- [ ] Topics are color-coded: green (above 0.7), yellow (0.5–0.7), red (below 0.5)
- [ ] User can expand a topic to see lesson-level recall scores with the same color coding
- [ ] Overall recall score is shown as a single number
- [ ] Number of topics at risk (below 0.5) is shown
- [ ] Number of lessons at risk (below 0.5) is shown
- [ ] Each topic shows how many quizzes were taken and the accuracy rate
- [ ] A history matrix shows past quiz results per topic over time
- [ ] User can navigate from the dashboard to start a quiz for all topics, a specific topic, or a specific lesson

---

[< Prev: Quiz](./quiz.md) | [Parent](./index.md)

