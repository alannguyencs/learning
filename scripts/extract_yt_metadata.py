"""Extract metadata from a downloaded YouTube HTML page.

Usage:
    python3 scripts/extract_yt_metadata.py

Expects /tmp/yt_page.html to exist (from: curl -s "https://www.youtube.com/watch?v={VIDEO_ID}" -o /tmp/yt_page.html)
Prints JSON to stdout.
"""

import re
import json

with open("/tmp/yt_page.html", "r", errors="replace") as f:
    html = f.read()

# Title
m = re.search(r'<meta name="title" content="([^"]+)"', html)
title = m.group(1).rstrip(".").strip() if m else ""

# Channel
m = re.search(r'"ownerChannelName":"([^"]+)"', html)
channel = m.group(1) if m else ""
if not channel:
    m = re.search(r'<link itemprop="name" content="([^"]+)"', html)
    channel = m.group(1) if m else ""

# Channel URL
m = re.search(r'"channelId":"([^"]+)"', html)
channel_url = f"https://www.youtube.com/channel/{m.group(1)}" if m else ""

# Published date
m = re.search(r'"publishDate":"([^"]+)"', html)
pub_date = m.group(1)[:10] if m else ""

# Duration (convert lengthSeconds to MM:SS)
m = re.search(r'"lengthSeconds":"(\d+)"', html)
if m:
    secs = int(m.group(1))
    mins, s = divmod(secs, 60)
    duration = f"{mins}:{s:02d}"
else:
    duration = ""

# Description
m = re.search(r'"shortDescription":"((?:[^"\\]|\\.)*)"', html)
desc = m.group(1).encode().decode("unicode_escape") if m else ""

print(
    json.dumps(
        {
            "title": title,
            "channel": channel,
            "channel_url": channel_url,
            "published_date": pub_date,
            "duration": duration,
            "description": desc,
        },
        indent=2,
        ensure_ascii=False,
    )
)
