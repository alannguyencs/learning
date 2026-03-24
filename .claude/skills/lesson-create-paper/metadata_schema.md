# Paper Metadata JSON Schema

Save the metadata to: `data/metadata/{topic_folder}/{yymmdd}_{slug}.json`

See SKILL.md for the `{topic_folder}/{yymmdd}_{slug}` naming convention.

## JSON Structure

```json
{
  "title": "LLM-based Conversational AI Therapist for Daily Functioning Screening",
  "authors": ["Jingping Nie", "Hanya (Vera) Shao", "Yuang Fan"],
  "published_date": "2024-03-16",
  "journal_or_conference": "arXiv preprint",
  "arxiv_id": "2403.10779",
  "arxiv_url": "https://arxiv.org/abs/2403.10779",
  "keywords": ["Large Language Models", "AI therapist", "Psychotherapy", "Cognitive Behavioral Therapy"],
  "abstract": "Full abstract text...",
  "source_file": "data/raw/coach/2403.10779v1.txt",
  "content": "Full paper text extracted from the .txt file..."
}
```

## Field Notes

- `published_date` — ISO format `YYYY-MM-DD`. Infer from:
  1. Explicit date in the paper text
  2. arXiv ID: first 4 digits = `YYMM` (e.g., `2403` = March 2024 → `2024-03-01`)
  3. Copyright year or submission note in the text
- `arxiv_id` — strip version suffix (e.g., `2403.10779v1` → `2403.10779`); set to `null` if not an arXiv paper
- `arxiv_url` — `https://arxiv.org/abs/{arxiv_id}`; omit field if `arxiv_id` is `null`
- `journal_or_conference` — full venue name, or `"arXiv preprint"` if only an arXiv ID exists
- `abstract` — the abstract section verbatim (not truncated)
- `content` — full paper text (all pages concatenated from the `.txt` file)

## How to Save

Use a Python script via Bash to build the JSON and write it with `json.dump()`:

```python
python3 << 'PYEOF'
import json

with open('data/raw/coach/2403.10779v1.txt', 'r', encoding='utf-8') as f:
    content = f.read().strip()

metadata = {
    "title": "...",
    "authors": ["..."],
    "published_date": "YYYY-MM-DD",
    "journal_or_conference": "...",
    "arxiv_id": "...",
    "arxiv_url": "https://arxiv.org/abs/...",
    "keywords": ["..."],
    "abstract": "...",
    "source_file": "data/raw/coach/2403.10779v1.txt",
    "content": content
}

with open('data/metadata/coach/240316_slug.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print("Saved.")
PYEOF
```

### Important Notes

- Use `ensure_ascii=False` so Unicode characters (curly quotes, em dashes, etc.) are preserved
- Use `indent=2` for readable JSON
- Read the content from the file rather than inlining — avoids shell escaping issues
- Ensure directories exist before writing: `mkdir -p data/metadata/{topic_folder}`
