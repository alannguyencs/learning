---
name: lesson-quiz-generate
description: Generate Quiz Questions from Lesson File
---

# Generate Quiz Questions from Lesson File

Read a lesson file and generate quiz questions, then save them as a JSON file in `data/quiz/`.

**Argument:** `[N quizzes for] <path to lesson markdown file>`

- `N` is an optional number of questions to generate (default: **10**)
- Examples: `data/lesson/sample_lesson_1.md` (generates 10), `20 quizzes for data/lesson/sample_lesson_1.md` (generates 20)

## Instructions

1. Parse `$ARGUMENTS` to extract the **lesson file path** and the **quiz count** (N). If a number appears before the path (e.g. `20 quizzes for ...`), use it as N. Otherwise default N to **10**.
2. Read the lesson file at the extracted path.
3. Read the corresponding metadata file at `data/metadata/{lesson_base_name}.json` to get the better context.
4. Read the quiz system prompt at `.claude/skills/lesson-quiz-generate/quiz_system_prompt.md`
5. Generate exactly **N** quiz questions from the lesson content following the system prompt rules:
   - Mix quiz types across: `recall`, `understanding`, `application`, `analysis`
   - Alternate between single-answer and multiple-answer questions
   - Test deep understanding, not surface-level recall
6. Save all N questions as a JSON array to `data/quiz/{lesson_filename}.json` (where `{lesson_filename}` is the lesson file's name without extension, e.g. `sample_lesson_1.json`). Create the `data/quiz/` directory if it doesn't exist.

## Quiz Question Fields

Each question must have all these fields (matching the `QuizQuestion` model):

| Field | Type | Description |
|-------|------|-------------|
| `lesson_title` | str | Title from the metadata JSON |
| `quiz_type` | str | One of: recall, understanding, application, analysis |
| `question` | str | The question text |
| `quiz_learnt` | str | What the user learns from this question |
| `option_a` | str | Option A text |
| `option_b` | str | Option B text |
| `option_c` | str | Option C text |
| `option_d` | str | Option D text |
| `correct_options` | list | e.g. ["A"] or ["A", "C"] |
| `response_to_user_option_a` | str | Explanation for option A |
| `response_to_user_option_b` | str | Explanation for option B |
| `response_to_user_option_c` | str | Explanation for option C |
| `response_to_user_option_d` | str | Explanation for option D |
| `quiz_take_away` | str | Key takeaway from this question |

## Save to JSON

Write all N questions as a JSON array to `data/quiz/{lesson_filename}.json` (strip the `.md` extension from the lesson filename). Create the `data/quiz/` directory if it doesn't exist. Use the Write tool to create the file.

## Output

After saving, print the output file path and a summary table:

| # | Type | Question (first 60 chars) | Correct |
|---|------|--------------------------|---------|
| 1 | recall | ... | A |
| 2 | understanding | ... | B, C |
| ... | ... | ... | ... |

## Rules

- Generate exactly N questions per invocation (N defaults to 10)
- Distribute quiz types roughly evenly across the N questions
- Do NOT generate duplicate or near-duplicate questions
- Every explanation must explain WHY the option is correct or incorrect
- Verify the file exists before proceeding
