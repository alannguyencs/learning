# Upload Quiz Questions via API

Generate quiz questions from a lesson file and upload them to the webapp via the API.

**Argument:** path to a lesson markdown file (e.g. `backend/resources/lessons/sample_lesson_1.md`)

## Instructions

### Step 0: Load Token

Read the `.env` file and extract the `WEBAPP_ACCESS_TOKEN` value. If it is empty or missing, stop and tell the user:

> "Set WEBAPP_ACCESS_TOKEN in .env first. Generate one via POST /auth/token."

Also check for `WEBAPP_API_URL` — if present use it as the API base URL, otherwise default to `http://localhost:8000`.

### Step 1: Read Lesson

Read the lesson file at the path: $ARGUMENTS

If the file does not exist, stop and inform the user.

### Step 2: Resolve Metadata

Read `backend/resources/topics.json` to resolve `topic_id`, `lesson_id`, and `lesson_filename` for this file by matching the filename.

If the filename is not found in `topics.json`, stop and inform the user they need to register the lesson first.

### Step 3: Generate Questions

Read the quiz system prompt at `backend/resources/prompts/quiz_system_prompt.md`.

Generate exactly **10** quiz questions from the lesson content following the system prompt rules:
- Mix quiz types across: `recall`, `understanding`, `application`, `analysis`
- Alternate between single-answer and multiple-answer questions
- Test deep understanding, not surface-level recall
- Distribute quiz types roughly evenly (2-3 of each type)
- Do NOT generate duplicate or near-duplicate questions
- Every explanation must explain WHY the option is correct or incorrect

Each question must have all these fields:

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

### Step 4: Confirm with User

Show a summary table of all generated questions:

| # | Type | Question (first 60 chars) | Correct |
|---|------|--------------------------|---------|
| 1 | recall | ... | A |
| 2 | understanding | ... | B, C |
| ... | ... | ... | ... |

Ask the user to confirm before uploading.

### Step 5: Upload via API

Write the questions array as JSON to a temp file, then POST to the API:

```bash
curl -s -X POST "${API_URL}/api/quiz/questions" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d @/tmp/quiz_upload.json
```

Delete the temp file after the request completes (whether it succeeded or failed).

### Step 6: Display Result

Show the API response. On success, display:
- Number of questions inserted
- lesson_id and topic_id

On failure, display the error message from the API response.
