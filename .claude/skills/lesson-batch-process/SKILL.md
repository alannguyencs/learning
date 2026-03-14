---
name: lesson-batch-process
description: Loop through all unchecked videos in data/youtube_channels/, generate a lesson for each using the lesson-youtube skill, mark it checked, and add it to data/to_learn.md. Use when the user says "batch process", "process channels", "batch lessons", "process all videos", or "lesson batch".
allowed-tools: Bash, Read, Write, Edit, Glob, Skill
---

# Batch Process YouTube Channel Videos

Loop through all unchecked videos across all channel files in `data/youtube_channels/`, generate a lesson for each one, mark it as done, and track it in `data/to_learn.md`.

## Input

No arguments required. Optionally the user may specify:
- A single channel file to process (e.g. `developers_digest`)
- A number limit (e.g. `3` to process only 3 videos then stop)

If no arguments given, process **all** unchecked videos across all channels.

The user argument is: $ARGUMENTS

## File Formats

### Channel file (`data/youtube_channels/{channel}.md`)

```markdown
# Channel Name

Channel: https://www.youtube.com/@handle

## Videos

- [ ] Unchecked Video - https://www.youtube.com/watch?v=VIDEO_ID
- [x] Already Processed - https://www.youtube.com/watch?v=VIDEO_ID
```

### To-learn file (`data/to_learn.md`)

```markdown
# To Learn

- [ ] Lesson Title - data/lesson/{yymmdd}_{slug}.md
- [x] Already Learnt - data/lesson/{yymmdd}_{slug}.md
```

## IMPORTANT

Process videos **one at a time, sequentially**. Complete the full cycle (lesson-youtube → mark checked → add to to_learn.md) for one video before starting the next. Do NOT parallelize or batch multiple videos simultaneously.

## Execution Flow

### Phase 1: Initialize to_learn.md

Check if `data/to_learn.md` exists. If not, create it with:

```markdown
# To Learn
```

### Phase 2: Build work queue

1. Use Glob to find all `.md` files in `data/youtube_channels/`
2. Read each file and collect all unchecked entries (`- [ ]`)
3. For each unchecked entry, extract:
   - `title` — text between `] ` and ` - https://`
   - `url` — the YouTube URL
   - `source_file` — the channel file path
   - `line_text` — the full original line (for editing later)

Display the queue:

```
Found {N} unchecked videos across {M} channels:

| # | Channel | Video Title (first 60 chars) |
|---|---------|------------------------------|
| 1 | Fireship | ... |
| 2 | Developers Digest | ... |
| ... | ... | ... |

Processing will begin. Use Ctrl+C to stop at any time.
```

If user specified a limit, note: `Processing first {limit} of {N} videos.`

### Phase 3: Process loop

For each unchecked video in the queue:

#### Step A: Generate lesson

Invoke the `lesson-youtube` skill with the video URL:

```
Skill: lesson-youtube
Args: {video_url}
```

This will create:
- `data/metadata/{yymmdd}_{slug}.json`
- `data/lesson/{yymmdd}_{slug}.md`

#### Step A2: Generate quiz questions

After the lesson is generated, invoke the `lesson-quiz-generate` skill:

```
Skill: lesson-quiz-generate
Args: data/lesson/{yymmdd}_{slug}.md
```

This will create:
- `data/quiz/{yymmdd}_{slug}.json`

If quiz generation fails, log the error but continue — the lesson is still valid without quiz questions.

#### Step B: Mark video as checked

After the lesson is successfully generated, use the **Edit tool** to update the channel file — replace the unchecked line with a checked one:

```
old_string: "- [ ] {title} - {url}"
new_string: "- [x] {title} - {url}"
```

#### Step C: Add to to_learn.md

Read `data/to_learn.md`, then use the **Edit tool** to append a new unchecked entry at the end:

```
- [ ] {lesson_title} ({channel_name}) - data/lesson/{yymmdd}_{slug}.md
```

Where:
- `{lesson_title}` — the video title
- `{channel_name}` — the channel name from the channel file heading
- `{yymmdd}_{slug}` — the lesson filename (derived from the lesson-youtube skill's naming convention)

#### Step D: Progress update

After each video, print:

```
[{current}/{total}] Done: {title}
  Lesson: data/lesson/{yymmdd}_{slug}.md
```

Then continue to the next unchecked video.

### Phase 4: Completion summary

After all videos are processed (or the limit is reached), display:

```
Batch complete.

Processed: {N} videos
Channels:  {list of channels touched}
Lessons:   {N} new lessons in data/lesson/

To learn list updated: data/to_learn.md
```

## Rules

1. **One video at a time** — process sequentially, not in parallel (each lesson generation is heavy)
2. **Mark checked immediately** — update the channel file right after each successful lesson, so progress is saved even if the process is interrupted
3. **Append to to_learn.md immediately** — same reason: save progress incrementally
4. **Skip on failure** — if lesson-youtube fails for a video (e.g. no transcript, fetch error), log the error, leave it unchecked, and continue to the next video
5. **Respect existing lessons** — if a lesson file already exists in `data/lesson/` for a video (matching video ID in any metadata JSON), mark the channel entry as checked and skip regeneration
6. **No duplicates in to_learn.md** — before appending, check if the lesson path already exists in `data/to_learn.md`
