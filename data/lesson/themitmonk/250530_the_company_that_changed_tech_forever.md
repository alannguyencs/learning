## Material

- **Video:** [The Company That Changed Tech Forever](https://www.youtube.com/watch?v=trCYZF0guAs)
- **Channel:** theMITmonk
- **Published:** 2025-05-30
- **Duration:** 21:53
- **Metadata:** [data/metadata/themitmonk/250530_the_company_that_changed_tech_forever.json](data/metadata/themitmonk/250530_the_company_that_changed_tech_forever.json)

---

## Summary

The Nvidia story in five acts: **Denny's origin (1993), near-death and the Sega gamble, GPU invention and CUDA bet, the AlexNet miracle (2012), and the AI explosion** — plus three massive threats and three life lessons about grit, impermanence, and risk.

**Why it matters:**
- Started at Denny's in 1993 → valued at **$6M** → now worth **$3T+** (500,000x return)
- Sold 250,000 NV1 chips, **249,000 came back** — first product was a near-total failure
- Had only **one payroll's worth of cash** left when their survival chip shipped in 1997
- AlexNet (2012): ran on **two Nvidia GPU cards** → shattered ImageNet benchmarks → proved GPUs = future of AI
- Revenue: **$27B → $61B → $130B** in consecutive years; 65% gross margin; 80% market share

**The Five Acts:**

| Act | What Happened | Key Lesson |
|-----|--------------|------------|
| 1: Denny's Origin (1993) | Three engineers sketched a chip on a napkin; wanted to bring cinematic graphics to PCs | "If you build it, they will come" — bet on an industry (gaming) that didn't exist yet |
| 2: Near-Death (1995-97) | NV1 and NV2 both obsolete; chose wrong standard (quads vs triangles); 9 months of runway | The "third choice": Jensen told Sega the truth, asked to be paid anyway; honesty saved the company |
| 3: GPU + CUDA (1999-2006) | GeForce launched as first GPU; CUDA enabled scientific computing on GPUs | Built for a market that didn't exist yet; stock fell 80% because Wall Street didn't get it |
| 4: AlexNet Miracle (2012) | Deep neural network on 2 Nvidia GPUs shattered ImageNet; proved GPUs = AI future | "Survive long enough to catch the right wave" — the miracle Nvidia needed |
| 5: AI Explosion (2017-now) | Tensor cores, DGX boxes, cloud partnerships; donated DGX to OpenAI | Revenue: $27B → $130B in 2 years; 65% gross margin; full-stack dominance |

**Three Threats:**

| # | Threat | Detail |
|---|--------|--------|
| 1 | Biggest customers building own chips | Google (TPUs), Amazon (Trainium), Microsoft (Maia) — billion-dollar moonshots |
| 2 | Geopolitical fracture | US banned Nvidia chips in China; $5.5B unsellable inventory; domestic competitors emerging |
| 3 | Scale itself | 80% market share = every victory invites 100 battles; AMD's pitch: "We're not Nvidia" |

**Key Takeaways:**
1. "My will to survive exceeds almost everybody else's will to kill me" — Jensen; Nvidia failed its first two products, laid off 75%, shipped a survival chip in 6 months (normally 18-24), had one payroll left
2. CUDA was built for a market that didn't exist — no demand, Wall Street hated it, stock fell 80%; but Jensen believed the future would need it; 6 years later AlexNet proved him right
3. CPU = a chef cooking a complex gourmet meal; GPU = an army of line cooks each flipping burgers simultaneously (parallel computing)
4. Success is not a destination — "as soon as you achieve what you wanted, you or the world will want more"; holding the lead takes more energy than earning it
5. Risk and reward are joined at the hip — sometimes it's okay to ask for the impossible; you might find out what is possible

---

## Connect to Known

```
+-----------------------------------------------------------------------------+
|                            CONNECT TO KNOWN                                 |
+-----------------------------------------------------------------------------+
|                                                                             |
|  +---------------------+         +------------------------------------+     |
|  | CPU vs GPU          |-------->| * CPU = single-threaded execution   |     |
|  | Chef vs line cooks  |         |   (one complex task well); GPU =  |     |
|  |                     |         |   massively parallel (thousands   |     |
|  |                     |         |   of simple tasks simultaneously) |     |
|  +---------------------+         +------------------------------------+     |
|                                                                             |
|  +---------------------+         +------------------------------------+     |
|  | CUDA = Platform     |-------->| * Like creating an SDK/API before   |     |
|  | Built for market    |         |   anyone needs it — developers   |     |
|  | that didn't exist   |         |   eventually build on it and     |     |
|  |                     |         |   you become the standard         |     |
|  +---------------------+         +------------------------------------+     |
|                                                                             |
|  +---------------------+         +------------------------------------+     |
|  | NV1 Failure         |-------->| * Like betting on the wrong API    |     |
|  | (Quads vs triangles)|         |   standard — your tech works but |     |
|  |                     |         |   the ecosystem chose a different |     |
|  |                     |         |   standard and you're obsolete   |     |
|  +---------------------+         +------------------------------------+     |
|                                                                             |
|  +---------------------+         +------------------------------------+     |
|  | Biggest customers = |-------->| * Like cloud providers building     |     |
|  | biggest threats     |         |   their own databases (Aurora,   |     |
|  |                     |         |   Spanner) to reduce dependency  |     |
|  |                     |         |   on Oracle/MongoDB              |     |
|  +---------------------+         +------------------------------------+     |
|                                                                             |
+-----------------------------------------------------------------------------+
|  NEW CONCEPT --------------------------------> FAMILIAR EXPERIENCE          |
+-----------------------------------------------------------------------------+
```

---

## Recommendation

```
┌─────────────────────────────────────────────────────────────┐
│        ACTION FLOWCHART: NVIDIA'S STARTUP SURVIVAL PLAYBOOK │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                 ┌──────────────────────┐
                 │      START HERE      │
                 └──────────────────────┘
                              │
                              ▼
         ┌──────────────────────────────────────┐
         │ 1. BET ON A FUTURE MARKET            │
         │    - Identify an industry that        │
         │      doesn't exist yet but will       │
         │    - Build the platform/SDK now,      │
         │      before anyone asks for it        │
         │    - Accept: Wall Street (or your     │
         │      board) won't get it — stock      │
         │      may fall 80% before validation   │
         └──────────────────────────────────────┘
                              │
                              ▼
         ┌──────────────────────────────────────┐
         │ 2. EXPECT YOUR FIRST PRODUCT TO FAIL │
         │    - NV1: 250K sold, 249K returned   │
         │    - Budget for a 99%+ failure rate   │
         │      on v1                            │
         │    - Don't bet everything on one      │
         │      standard — validate early        │
         └──────────────────────────────────────┘
                              │
                              ▼
         ┌──────────────────────────────────────┐
         │ 3. WHEN FACING DEATH, FIND THE       │
         │    "THIRD CHOICE"                     │
         │    - Option A: pivot away             │
         │    - Option B: keep burning cash      │
         │    - Option C: tell the truth to your │
         │      partner/customer and ask for     │
         │      what you actually need           │
         │    - Jensen told Sega the truth and   │
         │      asked to be paid anyway — it     │
         │      saved the company                │
         └──────────────────────────────────────┘
                              │
                              ▼
         ┌──────────────────────────────────────┐
         │ 4. COMPRESS THE IMPOSSIBLE TIMELINE  │
         │    - Nvidia shipped a survival chip   │
         │      in 6 months (normally 18-24)     │
         │    - Cut staff to 35, focus 100% on   │
         │      the one thing that keeps you     │
         │      alive                            │
         │    - One payroll of cash left =       │
         │      maximum clarity                  │
         └──────────────────────────────────────┘
                              │
                              ▼
         ┌──────────────────────────────────────┐
         │ 5. SURVIVE LONG ENOUGH TO CATCH      │
         │    THE RIGHT WAVE                     │
         │    - CUDA: built 2006, validated 2012 │
         │      (6 years of patience)            │
         │    - AlexNet on 2 Nvidia GPUs proved  │
         │      GPUs = AI future                 │
         │    - You can't predict the wave —     │
         │      but you can be in the water      │
         └──────────────────────────────────────┘
                              │
                              ▼
    ┌────────────────────┬─────────────────────────┐
    │   ONCE YOU WIN:    │   WATCH FOR 3 THREATS   │
    │                    │                         │
    │ ▶ Revenue can go   │ ▶ Customers build own   │
    │   $27B → $130B in  │   chips (Google TPUs,   │
    │   2 years          │   Amazon Trainium)      │
    │ ▶ 65% gross margin │ ▶ Geopolitics: $5.5B    │
    │ ▶ 80% market share │   in unsellable stock   │
    │                    │ ▶ 80% share = 100       │
    │                    │   battles at once       │
    └────────────────────┴─────────────────────────┘
                              │
                              ▼
         ┌──────────────────────────────────────┐
         │ "My will to survive exceeds almost   │
         │  everybody else's will to kill me."  │
         │                        — Jensen Huang │
         └──────────────────────────────────────┘
```

---

## Create Chunk

*"My will to survive exceeds almost everybody else's will to kill me." — Jensen Huang*

*"CPU is a chef cooking a gourmet meal. GPU is an army of line cooks each flipping burgers at once."*

*"Sometimes you have to survive long enough to catch the right wave."*

```
+-----------------------------------------------------------------------------+
|              NVIDIA: FROM DENNY'S TO $3 TRILLION                            |
+-----------------------------------------------------------------------------+
|                                                                             |
|   1993: DENNY'S               1995-97: NEAR DEATH                         |
|   (Pancakes + ambition)       (Two failed chips)                          |
|                                                                             |
|   3 engineers, napkin sketch   NV1: 250K sold, 249K returned             |
|   $2M Sequoia funding          NV2: obsolete before release              |
|   $6M valuation                Chose quads (world chose                   |
|   Goal: cinematic graphics     triangles/DirectX)                        |
|   on PCs                       9 months runway left                      |
|                                                                             |
|   Jensen: ex-dishwasher        "Third choice": told Sega                 |
|   at Denny's                   truth → asked for payment                 |
|                                → honesty saved company                   |
|                                Laid off 75% (down to 35)                 |
|                                Shipped chip in 6 months                  |
|                                (normally 18-24)                           |
|                                One payroll of cash left                   |
|                                                                             |
|   1999: GPU INVENTION          2012: ALEXNET MIRACLE                      |
|   +----------------------------+----------------------------+              |
|   | GeForce = first GPU        | ImageNet competition        |              |
|   | CPU: chef (sequential)     | 2 Nvidia GPU cards          |              |
|   | GPU: army of cooks         | Shattered all benchmarks    |              |
|   |      (parallel)            | "If others drove a Prius,   |              |
|   |                            | AlexNet showed up in F1     |              |
|   | CUDA: SDK for scientific   | with jet boosters"          |              |
|   | computing on GPUs          |                             |              |
|   | Built for future market    | Proved GPUs = AI future     |              |
|   | Stock fell 80% (no demand) | The miracle Nvidia needed   |              |
|   +----------------------------+----------------------------+              |
|                                                                             |
|   2017-NOW: AI EXPLOSION + THREE THREATS                                   |
|   +-----------------------------------------------------------+           |
|   | Revenue: $27B → $61B → $130B | 65% gross margin           |           |
|   | Tensor cores, DGX, cloud     | 80% market share           |           |
|   | Donated DGX to OpenAI        |                            |           |
|   |                              | Threats:                   |           |
|   | "Every king sits on a throne | 1. Customers building own  |           |
|   |  made of swords"             |    chips (Google, Amazon)  |           |
|   |                              | 2. Geopolitics ($5.5B loss)|           |
|   |                              | 3. Scale invites battles   |           |
|   +-----------------------------------------------------------+           |
|                                                                             |
+-----------------------------------------------------------------------------+
|  KEY: True belief beats true brilliance. Survive long enough to catch the  |
|  right wave. Build for markets that don't exist yet. Success is not a      |
|  destination — holding the lead takes more energy than earning it.         |
+-----------------------------------------------------------------------------+
```

---

## Story

Imagine three friends sitting in a Denny's. Not a boardroom. Not a venture capital office. A Denny's -- the kind of place where you order pancakes at midnight. It is 1993, and they are sketching a chip design on a napkin.

They want to bring cinematic graphics to personal computers. The gaming industry barely exists. Most people think of PCs as beige boxes for spreadsheets. A venture firm gives them two million dollars anyway. The company is valued at six million.

This is the start of Nvidia. And for the next four years, it almost dies -- twice.

Think of it like a noodle shop. You open with a bold new recipe. You sell two hundred and fifty thousand bowls. But two hundred and forty-nine thousand customers bring them back. Your recipe was built on the wrong base stock. The whole industry chose a different one, and you are left holding thousands of bowls nobody wants.

That was the NV1 chip. And the NV2 was no better -- obsolete before it even shipped. The company had nine months of runway. Seventy-five percent of the staff got laid off. Thirty-five people remained.

Here is where the story gets interesting. The founder, Jensen Huang, faced two obvious choices: pivot away from the failed product, or keep burning cash on a sinking ship. He chose a third option. He went to his partner, Sega, told them the truth -- "Our technology is not going to work the way we promised" -- and then asked to be paid anyway so his team could build something else entirely. It was audacious. And Sega said yes.

With one payroll's worth of cash left, the team shipped a survival chip in six months. The normal timeline was eighteen to twenty-four months. When your back is truly against the wall, you find out what is possible.

That chip saved the company. And then Jensen did something that made Wall Street think he was crazy. He built CUDA -- a software platform that let scientists and researchers use graphics cards for general computing. The problem? Nobody wanted it yet. The market did not exist. The stock fell eighty percent.

For a 35-year-old engineer, this might feel familiar. You build an SDK or an internal tool at your startup, and your manager asks, "Who is going to use this?" You say, "People who do not exist yet." That is what Jensen said for six years.

Then, in 2012, a miracle happened. Two researchers entered the ImageNet competition -- a contest to see which software could best recognize images. Their neural network ran on two Nvidia GPU cards. If every other competitor drove a Prius, this entry showed up in a Formula 1 car with jet boosters strapped on. It shattered every benchmark. The system was called AlexNet, and it proved that GPUs were the future of artificial intelligence.

Jensen did not predict AlexNet. But he was in the water when the wave came. That is the difference between luck and preparation.

From there, the numbers went vertical. Revenue: twenty-seven billion, then sixty-one billion, then one hundred and thirty billion -- in consecutive years. Sixty-five percent gross margins. Eighty percent market share.

But the throne is made of swords. Nvidia's biggest customers -- Google, Amazon, Microsoft -- are now building their own chips. Geopolitics locked Nvidia out of China, leaving five and a half billion dollars of unsellable inventory. And eighty percent market share means every competitor in the world is gunning for you. AMD's sales pitch to customers is literally: "We are not Nvidia."

The story of Nvidia is not really about chips. It is about a dishwasher at Denny's who became a CEO, failed his first two products, laid off most of his team, told the truth when he could have lied, built a platform for a market that did not exist, survived long enough to catch the right wave, and then discovered that holding the lead takes more energy than earning it.

**The lesson:** Survive long enough to catch the right wave -- build for markets that do not exist yet, tell the truth when your back is against the wall, and remember that success is not a destination but a seat on a throne made of swords.

