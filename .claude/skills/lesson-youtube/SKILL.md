---
name: lesson-youtube
description: Fetch a YouTube video's metadata and transcript, save metadata as JSON, and generate a 3C Compress lesson note. Use when the user provides a YouTube video URL.
argument-hint: "[youtube-video-url]"
allowed-tools: Bash, WebFetch, Write, Read
---

# YouTube Video to Lesson

Given a YouTube video URL, fetch its metadata and transcript, save the metadata as JSON, and generate a 3C Compress lesson markdown file.

## Input

The user argument is: $ARGUMENTS

Extract the video ID from the input. It may be provided as:
- A full URL: `https://www.youtube.com/watch?v=VIDEO_ID`
- A short URL: `https://youtu.be/VIDEO_ID`
- Just the video ID: `VIDEO_ID`

## Execution Flow

### Phase 1: Fetch data (parallel)

Run these two Bash calls **in parallel** (same message, two tool calls):

```
Call 1: curl -s "https://www.youtube.com/watch?v={VIDEO_ID}" -o /tmp/yt_page.html
Call 2: youtube_transcript_api {VIDEO_ID} --format text
```

Read `.claude/skills/lesson-youtube/fetch.md` for extraction details and regex patterns.

### Phase 2: Extract metadata

Run a Python script via Bash to extract fields from the saved HTML. See `fetch.md` for the exact regex patterns and script.

### Phase 3: Save metadata JSON

Use Python `json.dump()` via Bash to write the JSON file. Read `.claude/skills/lesson-youtube/metadata_schema.md` for the schema and example.

Ensure `data/metadata/` exists first: `mkdir -p data/metadata data/lesson`

### Phase 4: Generate lesson file

Use the **Write tool** (not Bash) to create the lesson markdown. Read `.claude/skills/lesson-youtube/lesson_template.md` for the 4-section structure with examples.

### Phase 5: Display summary

After saving both files, display:

```
Metadata saved: data/metadata/{filename}.json
Lesson saved:   data/lesson/{filename}.md

Title:     {video title}
Channel:   {channel name}
Published: {published date}
Duration:  {duration}
```

## Naming Convention

Both files MUST use the same `{yymmdd}_{slug}` base name so they pair together:
- `{yymmdd}` — from the video published date (e.g. `260227` for 2026-02-27)
- `{slug}` — from the video title: lowercased, spaces replaced with `_`, special characters removed (apostrophes, quotes, colons, question marks), max 50 chars, no trailing underscores

### Example

Title: "Why are Hong Kong's fresh graduates struggling to find a job?"
Published: 2026-02-27

→ `260227_why_are_hong_kongs_fresh_graduates_struggling`

## Rules

1. Use the **transcript** as the primary source of content — it has the full detail
2. Use the **description** for metadata, links, and chapter structure
3. Extract 3-5 key concepts for "Connect to Known" and find relatable analogies from software engineering, daily life, or well-known frameworks
4. Create memorable chunks: metaphors, one-liners
5. Design an ASCII workflow that captures the main process visually
6. Keep Summary concise — this is the compressed 20% that gives 80% value
7. ASCII boxes should be properly aligned and visually clean
8. Separate sections with `---` horizontal rules
9. The transcript field in the JSON should contain the full unabridged transcript
10. Always `mkdir -p data/metadata data/lesson` before writing files
11. Use Python via Bash for JSON operations to avoid shell escaping issues with quotes and special characters
