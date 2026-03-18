# 3C Compress Lesson Template

Save to: `data/lesson/{channel_slug}/{yymmdd}_{slug}.md`

See SKILL.md for the `{channel_slug}/{yymmdd}_{slug}` naming convention. Must match the metadata file.

Generate a document with sections separated by `---` horizontal rules. Most channels have 6 sections; theMITmonk lessons have 7 (extra "Do and Don't" section).

Use the Write tool (not Bash) to create the lesson file directly.

---

## Section 1: ## Material

```markdown
## Material

- **Video:** [Video Title](https://www.youtube.com/watch?v=VIDEO_ID)
- **Channel:** Channel Name
- **Published:** YYYY-MM-DD
- **Duration:** M:SS
- **Metadata:** [data/metadata/{channel_slug}/{yymmdd}_{slug}.json](data/metadata/{channel_slug}/{yymmdd}_{slug}.json)
```

---

## Section 2: ## Summary

Structure:
1. **Opening line** — 1-2 sentences with the key insight in **bold**
2. **Why it matters** — bullet points with specific numbers/stats from transcript
3. **Core framework** — if the video presents a model or comparison, use a markdown table
4. **Key Takeaways** — numbered list, 3-5 items, each a one-line compressed insight

### Guidelines
- Pull specific numbers, percentages, and quotes from the transcript
- Bold the most important phrases for scannability
- Tables work well for before/after comparisons, layer models, or protocol breakdowns
- Each takeaway should be self-contained — understandable without reading the rest

### Example

```markdown
## Summary

Hong Kong's 2025 graduate job market hit a 5-year low with vacancies dropping 55%, driven by
**a "jobless recovery" where AI replaces entry-level work faster than the economy creates new junior roles**.

**Why it matters:**
- Youth unemployment (ages 20-24) reached 12.3% — second highest on record
- Only ~30,000 full-time graduate jobs available, lowest in 5 years

**Corporate Structure Shift — Pyramid to Diamond:**

| Layer | Old (Pyramid) | New (Diamond) |
|-------|--------------|---------------|
| Top | Few executives | Few executives |
| Middle | Some managers | **Wide band of managers** |
| Bottom | **Many entry-level** | Small AI-powered base |

**Key Takeaways:**
1. "Jobless recovery" — GDP grows but jobs don't follow; profits outpace hiring
2. AI eliminated the corporate groundwork that trained juniors
3. Employers now demand "job-ready" graduates — no bandwidth for training from scratch
```

---

## Section 3: ## Connect to Known (ASCII format)

Map 3-5 new concepts to familiar experiences. Analogies should come from:
- **Software engineering** (preferred) — CI/CD, microservices, ORMs, Git, design patterns
- **Daily life** — cooking, driving, sports
- **Well-known frameworks** — Agile, TCP/IP, OSI model

### Box layout

Each concept is a pair: `[New Concept box] ------> [Familiar Experience box]`

- Left box: concept name + short subtitle (2-3 words)
- Right box: 1-2 bullet points explaining the analogy
- Aim for boxes that are visually consistent in width

```
+-----------------------------------------------------------------------------+
|                            CONNECT TO KNOWN                                 |
+-----------------------------------------------------------------------------+
|                                                                             |
|  +---------------------+         +------------------------------------+     |
|  | Jobless Recovery    |-------->| * Like a CI/CD pipeline that ships |     |
|  | GDP up, jobs flat   |         |   faster but needs fewer devs     |     |
|  +---------------------+         +------------------------------------+     |
|                                                                             |
|  +---------------------+         +------------------------------------+     |
|  | "Job-ready" demand  |-------->| * Like requiring production exp    |     |
|  | internships required|         |   for a "junior dev" role — the   |     |
|  |                     |         |   classic catch-22 paradox         |     |
|  +---------------------+         +------------------------------------+     |
|                                                                             |
+-----------------------------------------------------------------------------+
|  NEW CONCEPT --------------------------------> FAMILIAR EXPERIENCE          |
+-----------------------------------------------------------------------------+
```

---

## Section 4: ## Recommendation (ASCII flowchart)

An ASCII-style flowchart showing the recommended action plan based on the lesson content. This makes the video's advice concrete and sequential.

### Guidelines
- Start with `START HERE` at the top
- Use box-drawing characters (`┌ ─ ┐ │ └ ┘ ▼ ▶`) for clean boxes and arrows
- Show a clear step-by-step flow from top to bottom
- Branch into parallel paths when the content has distinct tracks (e.g., job vs freelance vs founder)
- Each box should have a numbered step name and 2-3 lines of actionable detail
- Include specific numbers, thresholds, or rules from the video (e.g., "< 5%", "3-6 months", "90%")
- Side boxes can show details or options (connected with `────>`)
- End with a memorable closing box (e.g., "REPEAT. COMPOUND. WAIT." or "STAY IN THE RACE.")
- Place this section between Connect to Known and Create Chunk

### Example

```markdown
## Recommendation

\```
+─────────────────────────────────────────────────────────────────────+
│              ACTION FLOWCHART: FROM $0 TO INVESTING                 │
+─────────────────────────────────────────────────────────────────────+

  START HERE
      │
      ▼
┌───────────────────────────┐
│ 1. SHIFT YOUR MINDSET     │
│    Read "Psychology of     │
│    Money". Investing is    │
│    systematic, not gambling│
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐     ┌──────────────────────────────┐
│ 2. BUILD EMERGENCY FUND   │     │  HIGH-YIELD SAVINGS ACCOUNT  │
│    3-6 months of living   │────>│  Do NOT invest until this    │
│    expenses. Non-negotiable│     │  is fully funded.            │
└─────────────┬─────────────┘     └──────────────────────────────┘
              │
              ▼
┌───────────────────────────┐
│ 3. DESIGN ASSET ALLOCATION│
│    This drives 90% of     │
│    your returns.           │
└─────────────┬─────────────┘
              │
       ┌──────┴──────────────────────────┐
       │                                  │
       ▼                                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  YOUNG       │  │  MID-CAREER  │  │  NEAR        │
│  (20s-30s)   │  │  (40s)       │  │  RETIREMENT  │
│ Stocks: 80%  │  │ Stocks: 60%  │  │ Stocks: 40%  │
│ Bonds:  15%  │  │ Bonds:  30%  │  │ Bonds:  50%  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       └──────────┬───────┘                 │
                  └─────────┬───────────────┘
                            │
                            ▼
               ┌──────────────┐
               │   REPEAT.    │
               │  COMPOUND.   │
               │   WAIT.      │
               └──────────────┘
\```
```

---

## Section 5: ## Create Chunk (ASCII format)

Two parts:

### Part A: One-Liners

- **Quotable one-liners** (2-3) — pithy, memorable phrases that compress the main insights
  - Use italics: *"The ladder didn't break — the bottom rungs were automated away."*

### Part B: Visual Chunk (ASCII workflow)

A single ASCII diagram that captures the main process/framework. Guidelines:
- Title the workflow clearly
- Show cause-and-effect or flow relationships
- Include 2-3 columns or lanes if comparing dimensions (e.g. Economy | Structure | Impact)
- Use arrows (`-->`, `v`, `|`) to show direction
- End with a `KEY:` line summarizing the core insight

```
+-----------------------------------------------------------------------------+
|                    THE GRADUATE JOB SQUEEZE (2025)                           |
+-----------------------------------------------------------------------------+
|                                                                             |
|   ECONOMY          CORPORATE STRUCTURE         GRADUATE REALITY             |
|                                                                             |
|   GDP Growth       Few Executives                                           |
|     +2.5%             /\                  400 applications                  |
|       |              /  \                     0 offers                      |
|       v             / Mgr \                     |                           |
|   But hiring       / Wide  \                    v                           |
|   is FLAT    +--->/ Band    \        "Entry level: 2 yrs exp"              |
|              |   /___________\               |                              |
|   "Jobless   |   |  AI Base  |               v                              |
|    Recovery" |   |  (small)  |        Salary: HK$21K/mo                    |
|              |   +-----+-----+        (0.5% growth YoY)                    |
|              |         |                                                    |
|              |         v                                                    |
|              |   Automates:                                                 |
|              |   - Data cleaning        WHAT GRADUATES NEED:               |
|              |   - Basic analysis       +--------------------------+       |
|              |   - Admin tasks     ---->| 1. AI literacy (tools)   |       |
|              |   - Creative work        | 2. Internship experience |       |
|              |                          | 3. "AI Plus" mindset     |       |
|              |   = Fewer junior         | 4. Soft skills + adapt   |       |
|              |     roles needed         +--------------------------+       |
|                                                                             |
+-----------------------------------------------------------------------------+
|  KEY: The bottom of the ladder is gone. Build skills above the AI line.     |
+-----------------------------------------------------------------------------+
```

---

## Section 6 (theMITmonk only): ## Do and Don't

**This section applies only to lessons from the theMITmonk channel.** Skip for all other channels.

A markdown table that contrasts what NOT to do vs. what TO do for each key concept in the video. This makes the lesson actionable at a glance.

### Structure

| Step | Don't | Do |
|------|-------|----|
| {concept name} | {common mistake or wrong approach} | {recommended action with specific example} |

### Guidelines
- One row per key concept or step from the video
- **Don't column**: the default/lazy/wrong approach people take
- **Do column**: the specific action the video recommends, with a concrete example where possible
- Keep each cell to 1-2 sentences max
- Pull specific numbers, quotes, and examples from the transcript
- Place this section after Create Chunk and before Story (theMITmonk only)

### Example

```markdown
## Do and Don't

| Step | Don't | Do |
|------|-------|----|
| Job Market | Apply through the front door (job portals); 2% interview rate | Find the side door — show you can do the job directly (72-hour modeling test → hired) |
| Job Search | Spam resumes online; treat it like Russian roulette | Use the 3R hack: Reach the hiring manager, get Referrals (85% of hires), optimize for Recruiters on LinkedIn |
| Resume | Write a generic biography with empty words | Treat it as a sales pitch — "I did X → impact Y → outcome Z"; AI-customize for every role |
| Freelancing | Stay at the bottom of the value chain (e.g., script writing at $200) | Move up — rare + valuable = high pay (e.g., video editing at $1K) |
| Perfectionism | Wait until your product/resume/portfolio is "perfect" before launching | Ship at 90% and iterate — "it's startup, not wait-up" |
```

---

## Section 7 (or 6 for non-theMITmonk): ## Story

Write a simple, engaging story that a high school student can read to understand the main content of the article. Guidelines:

- **Use a concrete analogy** — translate technical concepts into an everyday scenario (e.g., a pizza shop, a school club, a sports team)
- **Map each key concept** to a character or element in the story
- **Cover the full arc** — the problem, the trigger, the strategy, and the outcome
- **Keep it conversational** — short paragraphs, simple vocabulary, no jargon
- **End with a bold one-liner** summarizing the lesson: `**The lesson:** ...`

### Example

```markdown
## Story

Imagine there's a criminal gang that runs an illegal pizza delivery business. The boss bakes poisoned pizzas (that's the ransomware), and he recruits delivery drivers all over town (the affiliates) to drop them at people's doors. When someone eats a slice and gets sick, the only cure costs $600 — and the boss keeps 30% while the driver pockets 70%. Business is booming because 70% of victims just pay up.

One day, a delivery driver drops a poisoned pizza at the apartment of a girl named Elena. What the driver doesn't know is that Elena's boyfriend, Mihai, is the best hacker at a secret cybersecurity team. Mihai is furious.

Mihai and his team start reverse-engineering the poison. They figure out the antidote and publish the recipe online for free. The boss changes the recipe. They crack that too. Five times over two and a half years.

The delivery drivers start quitting — why deliver poisoned pizzas if every victim can just Google the free cure? Without drivers, the boss has no customers. He announces he's "retiring."

**The lesson:** Ransomware works like a franchise — break the trust between the boss and the delivery drivers, and the whole business collapses.
```
