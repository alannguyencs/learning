# Metadata JSON Schema

Save the metadata to: `data/metadata/{channel_slug}/{yymmdd}_{slug}.json`

See SKILL.md for the `{channel_slug}/{yymmdd}_{slug}` naming convention.

## JSON Structure

```json
{
  "video_id": "oVQHVsbCUSg",
  "video_url": "https://www.youtube.com/watch?v=oVQHVsbCUSg",
  "title": "Why are Hong Kong's fresh graduates struggling to find a job?",
  "channel": "South China Morning Post",
  "channel_url": "https://www.youtube.com/channel/UC4SUWizzKc1tptprBkWjX2Q",
  "published_date": "2026-02-27",
  "duration": "8:53",
  "description": "Full video description including links...",
  "transcript": "Full unabridged transcript text..."
}
```

## Field Notes

- `published_date` — ISO format `YYYY-MM-DD` (extract first 10 chars from YouTube's date string)
- `duration` — human-readable `M:SS` or `MM:SS` format (convert from `lengthSeconds`)
- `transcript` — full unabridged transcript text from `youtube_transcript_api --format text`
- `description` — full video description including subscribe links, chapter markers, social links
- `channel_url` — build from channelId: `https://www.youtube.com/channel/{channelId}`

## How to save

Use a Python script via Bash to build the JSON and write it with `json.dump()`:

```python
python3 << 'PYEOF'
import json

with open('/tmp/yt_transcript.txt', 'r') as f:
    transcript = f.read().strip()

metadata = {
    "video_id": "...",
    "video_url": "https://www.youtube.com/watch?v=...",
    "title": "...",
    "channel": "...",
    "channel_url": "...",
    "published_date": "YYYY-MM-DD",
    "duration": "M:SS",
    "description": "...",
    "transcript": transcript
}

with open('data/metadata/{channel_slug}/{yymmdd}_{slug}.json', 'w') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
PYEOF
```

### Important notes

- Use `ensure_ascii=False` so Unicode characters (e.g. curly quotes, em dashes) are preserved as-is
- Use `indent=2` for readable JSON
- Read the transcript from the temp file rather than trying to inline it — avoids shell escaping issues
- Ensure the channel subdirectory exists before writing: `mkdir -p data/metadata/{channel_slug}`
