# Generate Blog Post - Autonomous Publishing

Generate and publish a blog post from the content calendar without human review.

**Arguments**: $ARGUMENTS (optional: specific post ID like "post-008", or leave blank for next in queue)

---

## Philosophy: Not AI Slop

This is NOT about churning out generic content. Every post must feel like it was written by a real person with opinions, experience, and a specific voice. The goal is building genuine SEO value and reader trust over time.

**Anti-AI Detection Markers** (incorporate naturally):
- Variable paragraph lengths (2 sentences to 6 sentences)
- Strong opinions stated without hedging
- Personal pronouns ("I've seen this..." not "It has been observed...")
- Specific numbers over vague claims ("$127/hour" not "higher rates")
- Incomplete sentences. Fragments. Real talk.
- Tangential thoughts that get pulled back
- Self-aware humor about the topic
- Admissions of uncertainty ("Honestly, I'm not 100% sure if...")

---

## Content Calendar Location

`backend/data/blog-content-calendar.json`

---

## Process

### Step 1: Read Content Calendar

Read `backend/data/blog-content-calendar.json` and understand:
- **metadata**: Recently used pillars, industries, total published count
- **voices**: The 4 voice personas and their markers/styles
- **pillars**: Content types with target word counts
- **queue**: Pending posts to choose from

### Step 2: Select Post Using Anti-Repetition Logic

If specific post ID provided in `$ARGUMENTS`, use that post.

Otherwise, select the next post using these rules:
1. **Never same pillar twice in a row** - Check `metadata.pillars_used_recently[0]`
2. **Rotate industries** - Prefer industries not in `metadata.industries_covered_recently`
3. **Respect frequency weights** - Higher weight pillars (quick_tactical: 40%) should appear more often
4. **Seasonal awareness** - If current month matches a seasonal_hook, prioritize that post

Select the first queued post that passes all anti-repetition rules.

### Step 3: Understand the Voice

Based on the selected post's `voice` field, internalize that voice completely:

**practical** (From-the-trenches):
- Short sentences. Fragments allowed.
- Markers: "I've seen this a hundred times", "Here's what actually works", "Let me be real"
- Style: Direct, no-BS, speaks from experience

**strategic** (Business-minded):
- Uses numbers, percentages, frameworks
- Markers: "The data shows", "When you think about it strategically", "The math is simple"
- Style: Structured but conversational

**casual** (Like texting a friend):
- Starts mid-thought, uses "you" constantly
- Markers: "So here's the thing", "Look", "Real talk", "Honestly?"
- Style: Rhetorical questions, tangents, strong opinions

**storyteller** (Narrative-driven):
- Opens with scene or anecdote
- Markers: "Last month I talked to", "Picture this", "True story"
- Style: Builds to the lesson, specific details

### Step 4: Generate the Post

Using the voice, pillar, and angle from the selected post:

1. **Generate a full-length article** matching the `target_words` from the pillar
2. **Create an engaging title** - Can modify `title_seed` but keep the core idea
3. **Write compelling subtitle** - 1-2 sentences that hook readers
4. **Estimate read time** - words / 200, rounded to nearest minute

**Content Structure Based on Pillar**:

- **quick_tactical** (500-800 words): Hook → Problem → One Big Solution → 3 Concrete Steps → Wrap
- **deep_guide** (1500-2500 words): Hook → Overview → 5-7 Sections with H2s → Summary → CTA
- **opinion_take** (800-1200 words): Hot Take Statement → "Here's why..." → Counter-arguments → Why I'm right → Conclusion
- **case_study** (1000-1500 words): The Situation → The Problem → What They Tried → The Breakthrough → Results → Your Takeaways
- **seasonal** (600-1000 words): Timely Hook → 3-5 Seasonal Tips → How to Prepare → CTA

### Step 5: Generate the HTML File

Create the complete HTML file following this exact template structure (from existing posts):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Title] — Quoted</title>
    <meta name="description" content="[Subtitle as description - 150-160 chars]">
    <meta name="keywords" content="[5-8 relevant keywords]">
    <meta name="author" content="Quoted">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://quoted.it.com/blog/[filename].html">

    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230a0a0a'/%3E%3Ctext x='16' y='23' font-family='serif' font-size='20' font-weight='600' fill='white' text-anchor='middle'%3EQ%3C/text%3E%3C/svg%3E">

    <!-- Open Graph -->
    <meta property="og:title" content="[Title]">
    <meta property="og:description" content="[Short description]">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://quoted.it.com/blog/[filename].html">

    <!-- Schema.org Article -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "[Title]",
        "description": "[Description]",
        "author": {"@type": "Organization", "name": "Quoted"},
        "publisher": {"@type": "Organization", "name": "Quoted", "url": "https://quoted.it.com"},
        "datePublished": "[YYYY-MM-DD]",
        "dateModified": "[YYYY-MM-DD]"
    }
    </script>

    [Full CSS from existing blog posts - copy exactly]
</head>
<body>
    <!-- Navigation -->
    <nav>
        <a href="/" class="logo">quoted.<span>it</span></a>
        <div class="nav-links">
            <a href="/use-cases">Use Cases</a>
            <a href="/blog/">Blog</a>
            <a href="/app" class="nav-cta">Start Quoting</a>
        </div>
    </nav>

    <!-- Article Header -->
    <header class="article-header">
        <a href="/blog/" class="back-link">&larr; Back to Blog</a>
        <p class="article-category">[Industry or "Business" if general]</p>
        <h1 class="article-title">[Title]</h1>
        <p class="article-subtitle">[Subtitle]</p>
        <div class="article-meta">
            <span>[Month YYYY]</span>
            <span>[X] min read</span>
        </div>
    </header>

    <!-- Article Content -->
    <article class="article-content">
        [Content with proper HTML structure:
         - <p> for paragraphs
         - <h2> for major sections
         - <h3> for subsections
         - <ul>/<ol> for lists
         - <strong> for emphasis
         - <div class="callout tip/warning/success"> for callouts
         - <div class="example-box good/bad"> for examples
         - <table class="content-table"> for data
         - <div class="cta-box"> near the end
        ]
    </article>

    <!-- Footer -->
    <footer>
        <a href="/" class="footer-logo">quoted.<span>it</span></a>
        <div class="footer-links">
            <a href="/use-cases">Use Cases</a>
            <a href="/blog/">Blog</a>
            <a href="/help">Help</a>
            <a href="/privacy">Privacy</a>
            <a href="/terms">Terms</a>
        </div>
        <p class="footer-copy">&copy; 2025 Quoted, Inc.</p>
    </footer>
</body>
</html>
```

### Step 6: Generate Filename

Create SEO-friendly filename from title:
- Lowercase
- Replace spaces with hyphens
- Remove special characters
- Keep under 50 chars
- End with `.html`

Example: "The Follow-Up Email That Actually Gets Responses" → `follow-up-email-gets-responses.html`

### Step 7: Write the File

Write the complete HTML file to: `frontend/blog/[filename].html`

### Step 8: Update Blog Index

Read `frontend/blog/index.html` and add the new post to the grid.

Find the articles grid (class="articles-grid") and add a new article card:

```html
<article class="article-card">
    <a href="/blog/[filename].html">
        <p class="article-category">[Industry]</p>
        <h3>[Title]</h3>
        <p class="article-excerpt">[First 150 chars of subtitle/description]...</p>
        <span class="article-meta">[Month YYYY] · [X] min</span>
    </a>
</article>
```

Add the new card AFTER the featured article and any recent posts (position it appropriately based on date).

### Step 9: Update Sitemap

Read `frontend/sitemap.xml` and add a new URL entry in the Blog section:

```xml
<url>
    <loc>https://quoted.it.com/blog/[filename].html</loc>
    <lastmod>[YYYY-MM-DD]</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
</url>
```

Also update the lastmod date on `/blog/` entry to today's date.

### Step 10: Update Content Calendar Metadata

Update `backend/data/blog-content-calendar.json`:

1. Set `metadata.last_generated` to current ISO date
2. Increment `metadata.total_published` by 1
3. Add the pillar used to beginning of `metadata.pillars_used_recently` (keep max 5)
4. Add the industry to beginning of `metadata.industries_covered_recently` (keep max 5)
5. Remove the published post from the `queue` array

### Step 11: Commit and Deploy

Run these git commands:

```bash
git add frontend/blog/[filename].html frontend/blog/index.html frontend/sitemap.xml backend/data/blog-content-calendar.json
git commit -m "$(cat <<'EOF'
Publish blog post: [Title]

Voice: [voice] | Pillar: [pillar] | Industry: [industry]
Word count: [X] | Read time: [X] min

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
git push origin main
```

### Step 12: Confirm Publication

Output a summary:

```
Published: [Title]
URL: https://quoted.it.com/blog/[filename].html

Voice: [voice]
Pillar: [pillar] ([word count] words)
Industry: [industry]
Read time: [X] min

Deployment initiated. Post will be live in ~2 minutes.

Next in queue: [next post title_seed]
Posts remaining in queue: [count]
```

---

## Example Run

**Input**: `/generate-blog-post`

**Process**:
1. Read content calendar
2. Last pillar was "deep_guide", so skip those
3. Select "post-008: The Follow-Up Email That Actually Gets Responses" (quick_tactical, practical voice)
4. Generate ~700 word article in practical voice
5. Write `frontend/blog/follow-up-email-gets-responses.html`
6. Update blog index with new card
7. Update sitemap
8. Update metadata (last_generated, pillars_used_recently)
9. Commit and push

**Output**:
```
Published: The Follow-Up Email That Actually Gets Responses
URL: https://quoted.it.com/blog/follow-up-email-gets-responses.html

Voice: practical
Pillar: quick_tactical (687 words)
Industry: general
Read time: 3 min

Deployment initiated. Post will be live in ~2 minutes.

Next in queue: Why I Stopped Giving Detailed Quotes to First-Time Callers
Posts remaining in queue: 32
```

---

## Content Quality Checks

Before writing the file, verify:

- [ ] Opening hook is specific and engaging (not generic)
- [ ] Voice markers appear naturally throughout (2-4 per section)
- [ ] At least one callout box or example box used
- [ ] CTA box appears near the end
- [ ] No hedging language ("might", "could potentially", "in some cases")
- [ ] At least 2 specific numbers/stats included
- [ ] Word count matches pillar target (±15%)
- [ ] Title is different from existing posts (check index)

---

## Scheduling (Future)

For automated scheduling, this command can be triggered via:
- **Cron job on server** - Run weekly
- **GitHub Actions** - Scheduled workflow calling Claude API
- **Manual trigger** - `/generate-blog-post` when desired

The metadata tracking ensures anti-repetition works across scheduled runs.

---

## Emergency: Regenerate from Seed

If a post needs regeneration with different angle:

```
/generate-blog-post post-008 --regenerate --angle="focus more on subject line formulas"
```

This will generate a new version of the specified post with the custom angle, overwriting if it exists.
