---
name: lesson-upload
description: Upload Lesson and Quiz Questions via API
---

# Upload Lesson and Quiz Questions via API

Upload a lesson and its pre-generated quiz questions to the webapp. Reads files produced by `lesson-youtube` and `lesson-quiz-generate` skills.

**Argument:** base filename without extension (e.g. `260227_why_are_hong_kongs_fresh_graduates_struggling`)

## Instructions

Run the upload script:

```bash
python3 .claude/skills/lesson-upload/upload.py <base_filename> --project-root .
```

Where `<base_filename>` is extracted from `$ARGUMENTS` (the filename without extension).

The script handles all steps automatically:
1. Loads token and API URL from `.env`
2. Reads lesson, metadata, and quiz files from `data/`
3. Resolves topic from metadata channel field
4. Uploads the lesson via API
5. Enriches and uploads quiz questions one at a time
6. Ticks off the lesson in `data/to_learn.md`
7. Displays the result summary

If the script fails, report the error output to the user.
