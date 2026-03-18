---
name: lesson-upload
description: Upload Lesson and Quiz Questions via API
---

# Upload Lesson and Quiz Questions via API

Upload a lesson and its pre-generated quiz questions to the webapp. Reads files produced by `lesson-youtube` and `lesson-quiz-generate` skills.

**Argument:** base filename without extension (e.g. `250218_20_quantum_cheat_codes_that_i_wish_i_knew_in_my_2`)

## Instructions

Run the upload script from the **project root**:

```bash
python3 .claude/skills/lesson-upload/upload.py <base_filename> --project-root .
```

Where `<base_filename>` is extracted from `$ARGUMENTS` (the filename without extension).

The script **auto-discovers files** across channel subdirectories. All of these work:

```bash
# Just the bare filename — script searches data/lesson/*/, data/metadata/*/, data/quiz/*/
python3 .claude/skills/lesson-upload/upload.py 250218_20_quantum_cheat_codes --project-root .

# With channel prefix — also works
python3 .claude/skills/lesson-upload/upload.py themitmonk/250218_20_quantum_cheat_codes --project-root .
```

### File discovery

The script searches for each file (lesson `.md`, metadata `.json`, quiz `.json`) in this order:
1. `data/{type}/{filename}` (flat layout)
2. `data/{type}/*/{filename}` (channel subdirectory layout)

This means quiz files can be in either `data/quiz/` or `data/quiz/{channel}/` — both work.

### What the script does

1. Loads token and API URL from `.env`
2. Auto-discovers lesson, metadata, and quiz files from `data/`
3. Resolves topic from metadata channel field
4. Uploads the lesson via API
5. Enriches and uploads quiz questions one at a time
6. Ticks off the lesson in `data/to_learn.md`
7. Displays the result summary

### Important

- Always run from the **project root directory** (where `.env` lives), not from `backend/`
- The `.env` must have a valid `WEBAPP_ACCESS_TOKEN` — generate one via `POST /auth/token` with form data: `username=<user>&password=<pass>`
- The webapp server must be running at `WEBAPP_API_URL` (default: `http://localhost:8999`)

If the script fails, report the error output to the user.
