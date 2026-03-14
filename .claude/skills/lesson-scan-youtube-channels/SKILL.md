---
name: lesson-scan-youtube-channels
description: Scan all YouTube channel files in data/youtube_channels/, fetch the latest 10 videos per channel, and merge with existing entries to avoid duplicates. Use when the user says "scan youtube channels", "update youtube channels", "refresh channels", or "scan channels".
allowed-tools: Bash, Read, Write, Edit, Glob
---

# Scan YouTube Channels

Scan all channel files in `data/youtube_channels/`, fetch the latest 10 videos for each channel from YouTube, and merge new videos into the existing checklist without duplicates.

## Input

No arguments required. The skill automatically discovers all `.md` files in `data/youtube_channels/`.

## Channel File Format

Each channel file follows this structure:

```markdown
# Channel Name

Channel: https://www.youtube.com/@handle

## Videos

- [ ] Video Title - https://www.youtube.com/watch?v=VIDEO_ID
- [x] Already Watched Video - https://www.youtube.com/watch?v=VIDEO_ID
```

## Execution Flow

### Phase 1: Discover channel files

Use the Glob tool to find all `.md` files in `data/youtube_channels/`.

### Phase 2: Parse existing entries

For each channel file, use the Read tool to read it and extract:
1. **Channel name** — from the `# ` heading on line 1
2. **Channel URL** — from the `Channel: ` line (extract the `@handle`)
3. **Existing video entries** — all lines matching `- [x] ` or `- [ ] `, preserving their checked/unchecked state
4. **Existing video IDs** — extract the `v=VIDEO_ID` from each entry's URL to build a dedup set

### Phase 3: Fetch latest videos (parallel)

Fetch all channel pages **in parallel** — use one Bash tool call per channel, all in the same message:

```bash
curl -s "https://www.youtube.com/@{handle}/videos" -o /tmp/yt_scan_{slug}.html
```

Where `{slug}` is the channel file's basename (without `.md`).

### Phase 4: Extract and merge

Run a **single Python script** via Bash that processes all channels at once:

```python
python3 << 'PYEOF'
import re, json, glob

# For each channel HTML file:
# 1. Extract latest 10 videos using the videoRenderer regex
# 2. Compare video IDs against existing entries
# 3. Prepend new videos (unchecked) above existing entries
# 4. Preserve checked state of existing entries
PYEOF
```

**Video extraction regex:**
```python
pattern = r'"videoRenderer":\{"videoId":"([^"]+)".*?"title":\{"runs":\[\{"text":"((?:[^"\\]|\\.)*)"\}'
```

**Merge rules:**
- **New videos** (ID not in existing set): prepend as `- [ ] Title - URL` at the top of the Videos section
- **Existing videos**: keep as-is, preserving `[x]` or `[ ]` state
- **Order**: new videos first (in YouTube's order), then existing entries in their original order

### Phase 5: Write updated files

Use the **Write tool** to overwrite each channel file with the merged content. Preserve the original file structure:

```markdown
# {Channel Name}

Channel: {Channel URL}

## Videos

- [ ] New Video 1 - https://www.youtube.com/watch?v=NEW_ID_1
- [ ] New Video 2 - https://www.youtube.com/watch?v=NEW_ID_2
- [ ] Existing Unchecked - https://www.youtube.com/watch?v=EXISTING_ID
- [x] Already Watched - https://www.youtube.com/watch?v=WATCHED_ID
```

### Phase 6: Display summary

Print a summary table:

```
| Channel | Existing | New | Total |
|---------|----------|-----|-------|
| Developers Digest | 10 | 2 | 12 |
| Fireship | 10 | 0 | 10 |
| ... | ... | ... | ... |

Scan complete. {N} new videos found across {M} channels.
```

## Rules

1. **Never remove** existing entries — only add new ones
2. **Preserve checked state** — `[x]` entries must stay checked
3. **Deduplicate by video ID** — compare the `v=` parameter, not the title
4. **New videos go on top** — prepend above existing entries within the Videos section
5. **Parallel fetches** — fetch all channel pages in parallel for speed
6. **Decode Unicode** — use `.encode().decode('unicode_escape')` on extracted titles to handle special characters (smart quotes, em dashes, etc.)
8. **Clean titles** — after decoding, strip trailing dots/ellipsis with `.rstrip('.').strip()` so titles are stored in full without truncation artifacts
7. If a channel page fails to fetch (empty HTML or no videos found), skip it and note the failure in the summary
