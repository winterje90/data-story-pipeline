---
name: linkedin-writer
description: Write high-performing LinkedIn data story posts. Use this skill whenever the user wants to write a LinkedIn post, draft LinkedIn content, create a data story for LinkedIn, turn data/findings/insights into a LinkedIn post, or mentions posting on LinkedIn. Also use when the user says "write a post about [data]", "turn this into a LinkedIn post", "help me post this", or wants to share data findings on social media.
---

# LinkedIn Data Story Writer

Write LinkedIn posts that perform like the best data storytellers on the platform. This skill is reverse-engineered from 120 posts by Peter Walker (Carta, 166K followers, avg 370 likes) and Kyle Poyar (Growth Unhinged, 106K followers, avg 272 likes).

The core insight: a great data story on LinkedIn is never just a chart or just an opinion. It's a specific data finding, interpreted through a personal lens, formatted for scanners, and written like a human being talking to a friend.

## How the LinkedIn Algorithm Affects Your Post

Understanding how LinkedIn decides who sees a post changes how you write it. As of 2026, LinkedIn's feed is powered by three language models working in sequence:

1. **Llama 3 (3B parameters)** scans all posts and generates ~2,000 semantic match candidates for each user using Matryoshka embeddings (3,072 dimensions). This is pure semantic similarity, not keyword matching.
2. **Qwen (600M parameters)** pulls the target reader's profile data and last ~1,000 interactions (likes, comments, reposts, dwell time) to build a preference signal.
3. **Feed SR (Generative Recommender)** ranks the 2,000 candidates based on the combined profile + interaction history to predict which post will generate the most engagement.

What this means for writing posts:

- **Relevancy beats recency.** There is no "best time to post." People see 3-week-old posts if they're topically relevant. Don't optimize for timing; optimize for semantic match with your target audience.
- **Think topics, not keywords.** The system uses statistical word relationships, not exact match. "Hires per dollar" is semantically near "headcount efficiency" and "capital deployment" even without those exact words. Write naturally about your topic and the semantic proximity takes care of itself.
- **Stay in your topical lane.** If your profile and post history are about SaaS metrics and you post about football, your followers won't see it because there's no semantic overlap in their interaction history. A multi-post series on one dataset is algorithmically ideal because it builds dense semantic signal in one topic space.
- **Profile coherency matters.** LinkedIn ingests your full profile (headline, experience, causes, certifications, education) at two checkpoints in the ranking process. The language in your profile contributes to who sees your content.
- **You cannot game the system.** Model weights recompute hourly and flush daily. Focus on topical consistency and audience-relevant language, not hacks.

Source: Trust Insights unofficial LinkedIn algorithm guide (2026), based on LinkedIn's published engineering papers including the Causal LLM, Qwen profile embedding, and Feed SR recommender system papers.

## What the Data Says About Engagement (2026)

Rocksalt AI analyzed 6,753 LinkedIn posts from 39 B2B marketing influencers (Dave Gerhardt, Elena Verna, Rand Fishkin, Kieran Flanagan, and others), controlling for follower count and segmenting by funnel stage. That controlled approach matters: it strips out the two flaws that wreck most LinkedIn advice, comparing people with wildly different audience sizes, and ignoring what different post types are designed to do. The findings, several of which contradict common LinkedIn folklore:

- **Quality beats category.** Median engagement is nearly identical across personal, industry, and company-focused posts. The popular belief that personal stories and selfies always win is not in the data. A genuinely useful post outperforms a category trick.
- **Below 50K followers, audience size doesn't predict engagement at all.** Content quality matters far more than follower count. You don't need a big audience to perform, so don't chase follower growth as the goal.
- **Format is measurable, not cosmetic.** Top-performing posts contain 4-7x more list-formatted items and significantly more line breaks than lower performers. The formatting rules below aren't style preferences, they track with engagement.
- **More posting hurts past 1-2x/week.** There's a negative correlation between posting frequency and average engagement above roughly two posts per week. LinkedIn itself acknowledges higher audience fatigue than other platforms. (Cadence is handled in the `linkedin-schedule` skill.)
- **Authenticity is the moat.** Through LinkedIn's 360Brew algorithm change in late 2025, the creators who held their engagement were the ones posting consistent, genuine expertise. The ones leaning on volume and formatting tricks declined. As AI makes generic content free and abundant, a specific, lived point of view is what cuts through, and it gets more defensible every month.

Source: Arjun Moorthy (Co-founder & CEO, Rocksalt AI), "The B2B Founder's LinkedIn Playbook: What 6,753 Posts Reveal About Posting Frequency, Content Mix, and Engagement," Stage 2 Capital, 2026. Based on 6,753 LinkedIn posts from 39 B2B marketing influencers. Full analysis: https://www.stage2.capital/blog/the-science-of-scaling-authenticity-in-the-age-of-ai

## How to Use This Skill

When the user wants to write a LinkedIn post, gather these inputs (ask if not provided):

1. **The data/finding** - What does the data show? (a stat, a benchmark, a trend, a chart)
2. **The audience** - Who is this for? (founders, VCs, marketers, GTM leaders, etc.)
3. **The take** - What does the user think this means? What should the audience do about it?
4. **The visual** - Is there a chart/image to attach? (strongly recommended)

If the user just drops raw data or a finding without specifying these, infer what you can and draft the post. Don't interrogate them with a questionnaire.

## The Post Formula

Every post follows this architecture:

```
1. HOOK (1-2 lines) - the finding, stated to create tension or curiosity
2. DATA CITATION (1 line) - source, sample size, timeframe
3. SETUP (2-3 sentences) - what the chart/data shows, in plain language
4. INSIGHTS (bulleted) - 3-5 takeaways, each with a specific number or finding
5. OPINION (1-2 paragraphs) - the author's personal interpretation
6. CLOSE (1 line) - warm, human, sometimes a question
```

Not every post needs all six. Short posts (under 100 words) can skip the insights section and go hook > data > opinion > close.

## Writing the Hook

The hook is the single highest-leverage line in the post. It determines whether anyone reads past the fold. Pick one of these patterns based on the content:

### The Contrarian Data Bomb (highest ceiling)
State a commonly held belief, then immediately undercut it with data.
> "A universal truth: most radar charts should just be bar charts."
> "Is selling 8% of your company for $125K insane? Yea, a bit."

### The Shocking Number
Lead with a specific, jaw-dropping number. No context yet. Let it hang.
> "$110 billion in a single round."
> "Anthropic: $100M run-rate in Jan 2023...spikes to $14B in Feb 2026."

### The Provocative Question
Ask a question your audience debates privately but nobody has data on.
> "How long does it take for VC funds to return money to LPs?"
> "Small checks from angels: super useful or mostly useless?"

### The Direct Address
Call out the target audience by name + give them a strong directive.
> "Founders - if an investor asks for a 2x liquidation preference, find another investor."

### The "New Data" Signal
Signal freshness. People want to be first to share new benchmarks.
> "New: SaaS & AI funnel metrics for 2026"
> "Your official 2025 SaaS benchmarks cheat sheet is here"

When in doubt, default to the Shocking Number or Provocative Question. They're the most reliable.

## Formatting Rules

These are non-negotiable for LinkedIn performance:

- **Short paragraphs.** 2-4 sentences max. Never a wall of text.
- **White space.** Blank line between every section. LinkedIn rewards scannability.
- **Bullet points** for every list of insights. Use the bullet character, not dashes. Top-performing posts carry 4-7x more list items than weak ones, so lean into lists wherever the content allows.
- **Unicode bold** for section headers (e.g., Takeaways, What This Means). Generate these using Unicode mathematical bold characters, not markdown bold. Never use ALL CAPS for headers.
- **Numbered lists** for sequential or ranked content.
- **No hashtags.** Walker uses zero, ever. The best-performing data posts across both creators rarely use them.
- **Minimal links.** If you must include a link, put it at the very end or in a "link in comments" note. Links in the body suppress reach.
- **Emojis sparingly.** A single prayer-hands or smiley at the close is fine. Never emoji-heavy.

### Generating Unicode Bold Text

For section headers within the post, convert text to Unicode Mathematical Bold using these character mappings. This is how Walker formats headers like "Takeaways" and "Some Thoughts" in his posts.

Read `references/unicode-bold.md` for the character mapping table. Use it to convert section header text to Unicode bold.

## Voice and Tone

Write like a smart person talking to a peer over coffee. Not a content marketer. Not a consultant delivering findings.

- **Contractions are mandatory.** "don't", "won't", "they're", "it's", "kinda", "gunna"
- **Parenthetical asides** are natural and expected: "(and the velocity has surged upward since ChatGPT launched)"
- **Acknowledge uncertainty** when it's real: "Candidly, I'm not sure whether..." / "I'm skeptical"
- **Humor is welcome** but never forced. Self-deprecating works best: "Damn this thing takes forever"
- **First person** for opinions: "The thing that stands out most to me is..."
- **Second person** for advice: "If you're raising on SAFEs, consider..."

### What NOT to write
- No corporate jargon: "leverage," "synergize," "drive alignment," "unlock value"
- No AI slop: "dive into," "it's important to note," "let's unpack," "game-changer," "robust," "comprehensive"
- No em dashes. Replace with commas, periods, parentheses, or rewrite.
- No staccato fragment stacking ("Not marketing questions. Thinking questions. First-principles stuff.")
- No performative emotional declarations ("I was genuinely impressed")
- No parallel contrast structures ("Not through hype, through substance")
- No "thoughts?" as a lazy closing

## The Data Citation

Always name the data source early in the post. One sentence. The bigger and more specific the number, the more credible.

Good examples:
> "Data: 2,904 US venture funds that use Carta as their fund admin."
> "Data below from 12,249 seed rounds raised from Q1 2018 thru Q3 2025."
> "I asked 195 B2B go-to-market leaders about their 2026 plans."

Bad examples:
> "Based on our research..."
> "According to data..."
> "Studies show..."

## The Opinion Layer

This is what separates a data dump from a post that gets 500 likes. After presenting the data, always tell the audience what YOU think it means.

The opinion can be:
- A recommendation: "Don't raise venture capital without understanding how dilutive the journey really is."
- A caveat: "Now, this doesn't mean every solo founder is doomed..."
- A prediction: "I'd guess 70%+ of the companies in this cohort have revenue."
- A personal reaction: "I'm skeptical that this trend continues."
- An admission of uncertainty: "Candidly, I don't know if this is good or bad."

The take doesn't need to be groundbreaking. It needs to be honest and specific.

## The Close

Pick one approach and be consistent:

**Engagement close** (builds followers):
> "Good luck out there" + prayer-hands emoji
> A question that invites debate
> "What do you think?"

**Funnel close** (drives traffic):
> "Full report linked in the comments"
> "Read the full deep dive in today's newsletter: [link]"

**Warm human close** (Walker's signature):
> End on a note of empathy or humor. "This founder thing is anything but easy." / "Damn this takes forever."

## Output Format

When drafting a post, output:
1. The complete post text, ready to copy-paste into LinkedIn
2. A brief note on which hook pattern you used and why
3. A suggestion for the visual/chart if the user hasn't provided one

If the user provides rough notes or bullet points, transform them into a polished post. If they provide a finished chart, write the post around it. If they ask you to iterate, focus on the hook first (it has the most impact on performance).

## Quick Reference: The Checklist

Before finishing any draft, verify:

- [ ] Hook is in the first 1-2 lines (not buried)
- [ ] Data source is cited with specific sample size
- [ ] Paragraphs are 2-4 sentences max
- [ ] There's white space between every section
- [ ] Section headers use Unicode bold (not markdown, not ALL CAPS)
- [ ] No hashtags
- [ ] No em dashes
- [ ] No AI slop phrases
- [ ] The author's personal take is clearly stated
- [ ] The close is warm and human
- [ ] A chart/visual is either included or suggested
