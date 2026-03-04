# Generate Quiz Questions from Lesson File

Read a lesson file and generate 10 quiz questions, then insert them into the `quiz_questions` database table.

**Argument:** path to a lesson markdown file (e.g. `backend/resources/lessons/sample_lesson_1.md`)

## Instructions

1. Read the lesson file at the path: $ARGUMENTS
2. Read `backend/resources/topics.json` to resolve the `lesson_id`, `topic_id`, and `lesson_filename` for this file by matching the filename
3. If the filename is not found in `topics.json`, stop and inform the user they need to register the lesson first
4. Read the quiz system prompt at `backend/resources/prompts/quiz_system_prompt.md`
5. Generate exactly **10** quiz questions from the lesson content following the system prompt rules:
   - Mix quiz types across: `recall`, `understanding`, `application`, `analysis`
   - Alternate between single-answer and multiple-answer questions
   - Test deep understanding, not surface-level recall
6. Insert all 10 questions into the `quiz_questions` table by running a Python script via Bash from the `backend/` directory

## Quiz Question Fields

Each question must have all these fields (matching the `QuizQuestion` model):

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | str | From topics.json |
| `lesson_id` | int | From topics.json |
| `lesson_filename` | str | From topics.json |
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

## Database Insert

Run a Python script from the `backend/` directory using the project venv:

```bash
cd /Users/alan/Documents/projects/learning/backend && source ../venv/bin/activate && python -c "
from src.configs import settings
from src.database import SessionLocal
from src.models.quiz_question import QuizQuestion

db = SessionLocal()
questions = [ ... ]  # list of QuizQuestion objects
db.add_all(questions)
db.commit()
print(f'Inserted {len(questions)} questions')
db.close()
"
```

## Output

After inserting, print a summary table:

| # | Type | Question (first 60 chars) | Correct |
|---|------|--------------------------|---------|
| 1 | recall | ... | A |
| 2 | understanding | ... | B, C |
| ... | ... | ... | ... |

## Rules

- Generate exactly 10 questions per invocation
- Distribute quiz types roughly evenly (2-3 of each type)
- Do NOT generate duplicate or near-duplicate questions
- Every explanation must explain WHY the option is correct or incorrect
- Verify the file exists before proceeding
