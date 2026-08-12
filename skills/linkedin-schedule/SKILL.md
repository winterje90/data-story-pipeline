---
name: linkedin-schedule
description: Create a multi-post LinkedIn content schedule from a data analysis. Decomposes findings into 3-7 posts with different angles, hook patterns, and chart assignments, then writes each post via the linkedin-writer skill. Use when the user wants multiple LinkedIn posts from one dataset, says "create a posting schedule", "turn this into a series", "make a LinkedIn content plan", "give me a week of posts from this", or after /write-story produces an article and charts. Also triggers on "schedule posts", "LinkedIn schedule", "content calendar", "post series", or "posting plan". Works with findings.md or article.md output from /analyze-data and /write-story. Always use this instead of writing a single LinkedIn post when a full findings document is available.
---

# LinkedIn Posting Schedule Generator

Turn one data analysis into a full LinkedIn content series. Instead of extracting a single post from a dataset, this skill identifies every viable angle, builds a publishing calendar, and writes each post individually using the `linkedin-writer` skill.

The approach is modeled on how Peter Walker (Carta) and Kyle Poyar (Growth Unhinged) work: both regularly mine a single dataset for multiple angles across different posts. A strong findings document typically has 5-6 headline stats, 3+ narrative angles, and several anomalies. That's two to three weeks of content at 2x/week, not one post.

## Where a Data-Story Series Fits in the Overall Mix

Rocksalt AI's analysis of 6,753 LinkedIn posts from 39 B2B marketing influencers found the strongest presences follow a rough **50/30/20 content mix**:

- **~50% industry insight** (informed takes on what's happening in the market) — MOFU
- **~30% personal / career perspective** (lessons learned, hard-won experience, honest reflection) — TOFU
- **~20% company / product** (self-promotion) — BOFU

Most people invert this and over-index on self-promotion, which makes them easy to scroll past. A data-story series sits almost entirely in the 50% industry-insight bucket. That's the right bucket to be heavy in, but it shouldn't be the *only* thing posted. When scheduling a series, leave room in the calendar for personal/career posts so the overall feed doesn't read as all-data-all-the-time. Flag this to the user if the series would otherwise consume every available slot for weeks.

Source: Arjun Moorthy, "The B2B Founder's LinkedIn Playbook," Stage 2 Capital, 2026 — https://www.stage2.capital/blog/the-science-of-scaling-authenticity-in-the-age-of-ai

## Before You Start

**Announce:** "I'm running `/linkedin-schedule`. Reading the findings and building a posting plan."

## Step 1: Find the Input

**If coming from `/write-story`:** The findings document and article are already written. Use the same story directory that write-story created.

**If running standalone:** Read `output_dir` from `~/.data-story-pipeline.json` (falling back to `./config.json`), then look for the most recently modified `findings.md` under it:

```bash
ls -lt "$OUTPUT_DIR"/*/findings.md 2>/dev/null | head -5
```

Also check for `article.md` in the same directory. Both inform the schedule, but `findings.md` is the primary input (it has the structured findings, narrative angles, and anomalies that map to posts).

Confirm the story directory path. All output will go here.

## Step 2: Decompose Findings into Post Candidates

Read `findings.md` and extract these raw materials:

1. **Headline Findings** (usually 4-6, numbered in findings.md). Each is a potential standalone post.
2. **Narrative Angles** (usually 2-3, in findings.md). These are alternative framings of the same data, each with a different "so what."
3. **Anomalies & Surprises** (in findings.md). Data points that contradict conventional wisdom or expectations. These make strong contrarian posts.
4. **Implications** (from article.md if available, or the narrative angles). Actionable takeaways for practitioners.
5. **Available Charts** in the `charts/` directory. List what exists so you can assign visuals to posts.

Now map each piece of raw material to a post type. Read `references/post-types.md` for the full taxonomy, but here's the quick version:

| Post Type | Best Source Material | Hook Pattern |
|---|---|---|
| **Hero Data Post** | The single most surprising headline finding | Shocking Number or Contrarian Data Bomb |
| **Deep Dive** | An individual finding with enough depth to stand alone | Provocative Question or "New Data" Signal |
| **Contrarian / Myth Buster** | An anomaly that challenges what people assume is true | Contrarian Data Bomb |
| **Tactical Takeaway** | Implications section, practical "what to do about it" | Direct Address |
| **Thread Closer** | Summary of the series + link to full article | "New Data" Signal or warm close |

**How many posts:** Aim for 3-7, based on the material. The formula:
- 1 hero post (always)
- 1-3 deep dives (one per finding that can genuinely stand alone)
- 0-1 contrarian/myth-buster (only if the anomalies section has real material)
- 1 tactical takeaway
- 0-1 thread closer (only for series of 5+ posts)

Not every finding deserves its own post. If a finding only works as a supporting bullet inside another post, don't force it into a standalone. Fewer strong posts beat more weak ones.

## Step 3: Build the Schedule

Assign actual dates starting from the next available Tuesday or Thursday after today. Default cadence: **2x/week (Tue/Thu)**.

**A note on cadence:** The default is 2x/week, not more. The same analysis found a negative correlation between posting frequency and average engagement above roughly two posts per week, and LinkedIn itself acknowledges higher audience fatigue than other platforms. More is not better. A series should stretch across more weeks rather than cram more posts into one. One genuinely useful post beats five average ones.

**A note on timing:** LinkedIn's algorithm is relevancy-based, not recency-based. The specific day and time you post doesn't matter algorithmically. People see 3-week-old posts if they're topically relevant. The Tue/Thu cadence is for the author's consistency and workflow, not because the algorithm rewards specific days. What DOES matter is that a multi-post series on one topic builds dense semantic signal in one topic space, which is exactly what LinkedIn's language models reward (see the algorithm section in the `linkedin-writer` skill for the technical details).

**Sequencing rules** (read `references/post-types.md` for the reasoning behind each):

1. **Hero post goes first.** It casts the widest net and establishes the dataset's authority.
2. **Never put two deep dives back-to-back.** Alternate with a contrarian or tactical post to keep the series feeling varied.
3. **Contrarian/myth-buster goes mid-series** (slot 3 or 4). By then, the audience has seen the hero stat and one deep dive, so they have context. The contrarian post sparks debate and comments, which boosts visibility for the remaining posts.
4. **Tactical takeaway goes near the end.** It converts "interesting data" into "here's what to do about it." Readers need the earlier posts as context.
5. **Thread closer goes last** (if included). It ties the series together and drives traffic to the full article.

**Chart assignment:** Map each post to the most relevant chart from `charts/`. Some posts may share a chart (the hero and thread closer often reference the same visual). Some may not need one (the tactical takeaway might work better with a simple table or list). Note the chart assignment in the schedule.

## Step 4: Present the Plan for Approval

Show the user a schedule table. Do NOT write any posts yet. The user reviews and adjusts before you generate anything.

Format the plan like this:

```
## Proposed LinkedIn Schedule: [Topic]

Source: findings.md ([sample size], [time period])
Total posts: [N]
Cadence: 2x/week (Tue/Thu)
Series runs: [start date] to [end date]

| # | Date | Post Type | Hook Pattern | Angle / Finding | Chart |
|---|------|-----------|-------------|-----------------|-------|
| 1 | Tue, Apr 1 | Hero Data Post | Shocking Number | [1-line description] | finding-1.png |
| 2 | Thu, Apr 3 | Deep Dive | Provocative Question | [1-line description] | finding-2.png |
| ... | ... | ... | ... | ... | ... |

### Series Narrative Arc
[2-3 sentences on how the posts build on each other]

### Cross-Referencing Notes
- Post 2 can open by referencing Post 1's hero stat
- Post 3 is designed to provoke debate
- [etc.]
```

Wait for the user to approve, adjust the plan, add/remove posts, or change the sequence. Then proceed.

## Step 5: Generate Each Post

For each post in the approved plan, invoke the `linkedin-writer` skill via the Skill tool. Package these specific inputs:

- **The data/finding:** The specific finding, angle, or anomaly assigned to this post. Include the relevant numbers, not just a summary. Pull the actual data from findings.md so linkedin-writer has concrete stats to work with.
- **The audience:** Inferred from the dataset (founders, VCs, GTM leaders, etc.). Should be consistent across the series but can narrow for specific posts (e.g., the tactical takeaway might target "founders building a hiring plan").
- **The take:** What should the reader conclude from this specific post? Pull from the narrative angles or implications.
- **The visual:** Which chart file to reference.
- **Hook pattern suggestion:** Tell linkedin-writer which hook pattern to use (from the schedule table). This ensures variety across the series.
- **Series context:** If this is post 2+, tell linkedin-writer: "This is post [N] of [total] in a series about [topic]. The hero post (post 1) led with [hero stat]. This post should be able to stand alone but can optionally reference the earlier data." This context helps linkedin-writer write posts that feel connected without being dependent.

After linkedin-writer returns each post, save it to:
`$STORY_DIR/linkedin-posts/[NN]-[type]-[slug].md`

Each file should contain:
```markdown
---
post_number: [N]
post_type: [Hero Data Post / Deep Dive / etc.]
hook_pattern: [Shocking Number / etc.]
scheduled_date: [YYYY-MM-DD]
chart: charts/[filename]
---

[Full LinkedIn post text from linkedin-writer, ready to copy-paste]

---
## Notes
- Hook pattern: [which one and why]
- Chart: [which chart to attach when posting]
- Cross-reference: [any notes about referencing other posts in the series]
```

## Step 6: Save the Schedule Overview

After all posts are generated, write `linkedin-schedule.md` to the story directory. This is the master calendar:

```markdown
# LinkedIn Posting Schedule: [Topic]

Generated: [today's date]
Source: findings.md
Total posts: [N]
Cadence: 2x/week (Tue/Thu)

## Schedule

| # | Date | Post Type | Hook Pattern | Angle | Chart | File |
|---|------|-----------|-------------|-------|-------|------|
| 1 | Wed, Apr 2 | Hero Data Post | Shocking Number | [description] | finding-1.png | 01-hero-[slug].md |
| ... | ... | ... | ... | ... | ... | ... |

## Series Narrative Arc
[How the posts build on each other]

## Cross-Referencing Guide
[Which posts can reference which, with suggested language]

## Posting Checklist
For each post:
- [ ] Copy text from the post file
- [ ] Attach the assigned chart image
- [ ] Post at the scheduled date
- [ ] After posting, note any comments worth responding to (engagement in the first hour matters most)
```

Verify all files exist:

```bash
ls "$STORY_DIR/linkedin-schedule.md"
ls "$STORY_DIR/linkedin-posts/"
```

## Step 7: Confirm Everything

Tell the user:

"Posting schedule complete.
- **[N] posts** saved to `linkedin-posts/` — one markdown file each, ready to copy-paste
- **Master calendar** at `linkedin-schedule.md` with dates and chart assignments

Review and edit the post files directly. When you post, copy the text from the file and attach the assigned chart image from `charts/`."

## Reminders and review surfaces

This skill writes markdown files and stops there. It does not create calendar events, task-tracker
issues, or a shared review document — those were removed before publishing because they were wired
to one author's private tooling. See "What it can't do" in the repo README for what you'd need to
build to get them back. The `scheduled_date` field in each post's frontmatter and the dated table in
`linkedin-schedule.md` are the hooks to build against.
