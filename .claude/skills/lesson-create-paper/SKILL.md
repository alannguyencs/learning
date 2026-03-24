---
name: lesson-create-paper
description: Read a paper .txt file, extract metadata, save metadata as JSON, and generate a 3C Compress lesson note. Use when the user provides a path to a paper .txt file.
argument-hint: "[path/to/paper.txt]"
allowed-tools: Bash, Write, Read
---

# Paper to Lesson

Given a `.txt` paper file, extract its metadata, save it as JSON, and generate a 3C Compress lesson markdown file.

## Input

The user argument is: $ARGUMENTS

Parse the argument as a file path to a `.txt` paper file (e.g., `data/raw/coach/2403.10779v1.txt`).

## Naming Convention

The **topic folder** is the **name of the parent directory** of the `.txt` file:
- `data/raw/coach/2403.10779v1.txt` → topic folder = `coach`
- `data/raw/finance/paper.txt` → topic folder = `finance`

Files are saved as:
- Lesson:    `data/lesson/{topic_folder}/{yymmdd}_{slug}.md`
- Metadata:  `data/metadata/{topic_folder}/{yymmdd}_{slug}.json`

Where:
- `{yymmdd}` — from the paper's published date (e.g., `240316` for 2024-03-16)
- `{slug}` — from the paper title: lowercased, spaces → `_`, special chars removed, max 50 chars, no trailing underscores

### Example

File: `data/raw/coach/2403.10779v1.txt`
Title: "LLM-based Conversational AI Therapist for Daily Functioning Screening"
Published: 2024-03-16

→ `data/lesson/coach/240316_llm_based_conversational_ai_therapist_for_daily.md`
→ `data/metadata/coach/240316_llm_based_conversational_ai_therapist_for_daily.json`

---

## Execution Flow

### Phase 1: Read the paper

Use the **Read tool** to read the full `.txt` file. The file has page markers (`--- Page N ---`).

### Phase 2: Extract metadata

From the paper text, extract:
- `title` — paper title (usually on page 1, before authors)
- `authors` — list of author names
- `published_date` — ISO format `YYYY-MM-DD`; infer from arXiv ID if present (e.g., `2403.10779` → March 2024 → `2024-03-16`), or from a submission date in the text
- `journal_or_conference` — venue name, or `"arXiv preprint"` if only an arXiv ID is present
- `arxiv_id` — arXiv ID if present (e.g., `2403.10779`), else `null`
- `abstract` — the abstract section text
- `keywords` — key words/phrases from the paper (from the keywords section or CCS concepts)
- `source_file` — the input `.txt` file path

Read `.claude/skills/lesson-create-paper/metadata_schema.md` for the full JSON schema and how to save.

### Phase 3: Save metadata JSON

Ensure directories exist first:
```bash
mkdir -p data/metadata/{topic_folder} data/lesson/{topic_folder}
```

Use Python via Bash to write the JSON (avoids shell escaping issues). See `metadata_schema.md` for the exact script pattern.

### Phase 4: Generate lesson file

Read the user's background at `.claude/skills/personal_background.md` — use it to personalize:
- **Connect to Known**: Draw analogies from the user's real experience (computer vision, trademark detection, startup R&D, FastAPI/React stack, Hong Kong life, PhD-level AI/ML)
- **Story**: The story does NOT need to be about the user. Use the user's background as a reference point so the characters, scenarios, and stakes feel relatable.

Use the **Write tool** (not Bash) to create the lesson markdown. Read `.claude/skills/lesson-create-youtube/lesson_template.md` for the 4-section structure with examples.

**Adapt the Material section for papers** (see below).

### Phase 5: Display summary

After saving both files, display:

```
Metadata saved: data/metadata/{topic_folder}/{yymmdd}_{slug}.json
Lesson saved:   data/lesson/{topic_folder}/{yymmdd}_{slug}.md

Title:      {paper title}
Authors:    {author list}
Published:  {published date}
Venue:      {journal or conference}
```

---

## Lesson Template Adaptations for Papers

The lesson follows the same 3C Compress template as YouTube lessons (`lesson-create-youtube/lesson_template.md`) with one adaptation:

### Material Section (replace Video fields with Paper fields)

```markdown
## Material

- **Paper:** {title}
- **Authors:** {author list}
- **Published:** {YYYY-MM-DD}
- **Venue:** {journal or conference name}
- **arXiv:** https://arxiv.org/abs/{arxiv_id}   ← omit if no arXiv ID
- **Source:** [{source_file}]({source_file})
- **Metadata:** [data/metadata/{topic_folder}/{yymmdd}_{slug}.json](data/metadata/{topic_folder}/{yymmdd}_{slug}.json)
```

All other sections (Summary, Connect to Known, Recommendation, Create Chunk, Story) follow the same rules as YouTube lessons. Use the **paper's full text** as the primary content source — treat it like the transcript.

---

## Rules

1. Use the **full paper text** as the primary content source (equivalent to the transcript)
2. Use the **abstract and introduction** for framing the Summary opening
3. Extract 3-5 key technical concepts for "Connect to Known" — map to analogies from software engineering or daily life
4. ASCII diagrams should visualize the paper's core architecture, framework, or process
5. The Story should make the paper's findings relatable to a high school student
6. Keep Summary concise — the compressed 20% that gives 80% value
7. Always `mkdir -p` both directories before writing files
8. Use Python via Bash for JSON operations to avoid shell escaping issues
9. The `content` field in the JSON stores the full paper text
