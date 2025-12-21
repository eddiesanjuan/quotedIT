# Quoted Growth Playbook
## Applying Tibo's 12-Step SaaS Framework

**Source:** Tibo Louis-Lucas — 4 SaaS apps at $100K+ MRR, $700K/month total, $8M exit (Tweet Hunter/Tapio)

**Created:** 2025-12-17 | **For:** Executive Team Review

---

## Executive Summary

Tibo's core insight: **Builders hide in their caves coding features. Winners talk to customers every day.**

Quoted has a strong product. The gap is not features—it's customer intimacy and distribution. This document maps Tibo's proven 12-step framework to Quoted's specific context.

**Current State:** Live product, $19-79/month pricing, learning moat built-in

**Primary Opportunity:** We're likely somewhere between Step 4 (daily customer conversation) and Step 8 (stickiness validation). We need to nail retention before scaling acquisition.

---

## The 12-Step Playbook Applied to Quoted

### PHASE 1: VALIDATION (Steps 1-4)

#### Step 1: Build MVP in Days/Weeks ✅ COMPLETE
> *"90% failure rate is normal. Compress time to weeks, not years."*

**Status:** Done. Quoted is live at quoted.it.com with voice-to-quote, pricing interview, PDF generation.

**Quoted Advantage:** We compressed this using Claude + FastAPI + Railway. No 6-month build cycle.

---

#### Step 2: Find 5-10 Relevant Users
> *"If your mom tests your idea, there's no real knowledge gained. Target audience only."*

**Action for Quoted:**

| Criteria | Our Definition |
|----------|----------------|
| Trade | Deck builders, fence installers, painters, landscapers, remodelers |
| Size | Solo or 1-5 person crew |
| Current process | Word, Excel, or paper quotes |
| Quote volume | 8-20 quotes/month |
| Pain level | Hates admin, wants evenings back |

**Immediate Actions:**
- [ ] Identify our first 10 active users who match this profile exactly
- [ ] Reach out personally (not automated email)
- [ ] Ask: "Can we talk for 15 min about how quoting is going?"

**Channels to Find Them:**
- Contractor subreddits (r/Carpentry, r/landscaping, r/HomeImprovement - pro flair)
- Local Facebook groups ("Ohio Deck Builders", etc.)
- Home Advisor / Angi contractor forums
- Direct outreach to contractors who left us reviews/feedback

---

#### Step 3: Build True Relationships
> *"End up truly understanding what the person's life is about, what the pain is about."*

**Tibo's Insight:** Don't just collect feedback. Understand their WORKFLOW:
- When do they quote? (In the truck? At night?)
- What happens after they send a quote? (Follow-up? Ghosted?)
- What makes them lose jobs? (Too slow? Too expensive? Unprofessional?)
- What does "winning" look like for them?

**Quoted Implementation:**
- [ ] Create "Contractor Profile" doc for each of our 10 power users
- [ ] Include: Trade, crew size, quote volume, biggest friction points, ultimate goal
- [ ] Update after every conversation

**Template:**
```
## [Contractor Name] - [Trade]
**Setup date:**
**Quote volume:** X/month
**Current pain:**
**Ultimate goal:** (More jobs? Higher margins? Less stress? Grow crew?)
**Friction points with Quoted:**
**What would make them "love" us:**
**Last conversation:**
```

---

#### Step 4: Talk to Them Every Single Day ⭐ CRITICAL
> *"Until 10K MRR, the support link directs to my Twitter DMs."*

This is Tibo's secret weapon. **Direct founder access creates:**
1. Immediate feedback loop
2. Bug fixes in 5-10 minutes = "customers for life"
3. Deep understanding of real usage patterns
4. Word-of-mouth ("The founder texted me back in 2 minutes")

**Quoted Implementation:**

| Current State | Tibo's Model |
|---------------|--------------|
| Support goes to... ? | Support → Eddie's phone (SMS/WhatsApp) |
| Response time | Within 2 hours, ideally minutes |
| Until when | Until $10K MRR |

**Concrete Changes:**
- [ ] Update support link to go to direct channel (SMS? WhatsApp? iMessage?)
- [ ] Set up alerts so support messages buzz immediately
- [ ] Commit to responding to EVERY support request within 1 hour
- [ ] Log every conversation for pattern analysis

**Metric to Track:**
- Time to first response
- Issues resolved same-day
- Feedback that led to feature changes

---

### PHASE 2: STICKINESS (Steps 5-8)

#### Step 5: Understand Ultimate Goal
> *"By understanding how far you can go helping them achieve their ultimate goal, you can 10x-100x the value."*

**For Contractors, the Ultimate Goal is NOT "faster quotes."**

The REAL goals:
1. **More jobs won** (quotes are just the tool)
2. **Higher margins** (not just faster, but better pricing)
3. **Less stress** (evenings with family, not paperwork)
4. **Grow the business** (from solo to crew)

**Quoted Expansion Opportunities:**

| Feature | Ultimate Goal Served |
|---------|---------------------|
| Quote follow-up reminders | More jobs won |
| Win/loss tracking | Better pricing |
| Quick invoice from quote | Get paid faster |
| Customer database | Repeat business |
| Quote templates by job type | Even faster |

**Question for Team:**
> Which of these should we explore next? (Based on what users are ASKING for, not what we think is cool)

---

#### Step 6: Be the User of Your Own Product
> *"By being the user, I'm 10x more relevant with understanding the core problem."*

**Challenge:** We're not contractors. We don't send 15 quotes a month for deck jobs.

**Solutions:**
1. **Shadow users** — Watch them use Quoted in real time (screen share)
2. **Use it ourselves** — Send fake quotes for fake jobs to experience the flow
3. **Hire a contractor advisor** — Part-time contractor who uses it daily and gives feedback
4. **Read every quote** — Actually look at what users are generating

**Action:**
- [ ] Schedule 3 "shadow sessions" — watch contractors use Quoted live
- [ ] Founder uses Quoted weekly for test quotes to feel friction points

---

#### Step 7: Iterate with Constant Relationship
> *"By being active on socials, I was able to maintain constant relationship with people."*

**Quoted's Social Presence:**
- [ ] Twitter/X: Share contractor wins, quote screenshots (with permission)
- [ ] YouTube: "How I quoted a $20K deck job in 60 seconds" (real user)
- [ ] TikTok: Quick demo videos targeting contractor audience

**Content Ideas:**
- Before/after: "This used to take 90 minutes. Now takes 90 seconds."
- User testimonials (video if possible)
- Build in public: "We just shipped [feature] because [user] asked for it"
- Behind-the-scenes: "Here's how the AI learns your pricing"

---

#### Step 8: Repeat Until They Cannot Live Without It ⭐ CRITICAL
> *"Don't go broad too early. Focus on retention before acquisition."*

**The Leaky Bucket Problem:**
Going broad with bad retention = pouring water into a leaky bucket.

**How to Know We Have Stickiness:**
1. **Daily/weekly return rate** — Are users coming back?
2. **Complaints** — Users who complain are COMMITTED (they want it fixed)
3. **Referrals** — Would they recommend to another contractor?
4. **Churn interviews** — Why did they leave?

**Metrics to Track:**

| Metric | Weak | Strong |
|--------|------|--------|
| Weekly active users | <30% | >60% |
| Quotes per user/month | <4 | >10 |
| 30-day retention | <40% | >70% |
| NPS | <30 | >50 |

**Action:**
- [ ] Set up retention dashboard (PostHog)
- [ ] Call EVERY churned user to understand why
- [ ] Don't scale acquisition until retention is strong

---

### PHASE 3: DISTRIBUTION (Steps 9-12)

*Only proceed here after Phase 2 metrics are strong.*

#### Step 9: Go Broad — Test Acquisition Channels
> *"Try many things and see what actually works."*

**Free Channels (Until $10K MRR):**
- [ ] Product Hunt launch
- [ ] Build in public on X/Twitter
- [ ] Reddit posts in contractor communities
- [ ] YouTube tutorials
- [ ] Contractor forum participation

**Paid Channels (After $10K MRR):**
- [ ] Google Ads ("contractor quote software")
- [ ] Facebook/Instagram ads targeting contractor interests
- [ ] Affiliate program with contractor influencers
- [ ] Sponsorship of contractor YouTube channels

**Tibo's Note:** At this stage, you're TESTING. Track which channels bring users who stick, not just signups.

---

#### Step 10: Become a Media Company
> *"You need to have something to say about your industry."*

**Quoted's Media Strategy:**

| Content Type | Purpose |
|--------------|---------|
| Case studies | "How Mike doubled his quote-to-win ratio" |
| Industry voice | "Why contractors lose jobs (it's not price)" |
| Testimonials | Video preferred, screenshot minimum |
| Tutorials | "Quote a deck job in 60 seconds" |
| Build in public | "We just shipped X because you asked" |

**The Engine:**
- [ ] Publish 1 piece of content per week minimum
- [ ] Collect 1 testimonial per week
- [ ] Share 1 user win per week on socials

---

#### Step 11: Scale with Sustainable Channels
> *"SEO, ads, and affiliation. Set up once, scale to crazy high limits."*

**For Quoted:**

| Channel | Why It Fits |
|---------|-------------|
| **SEO** | Contractors Google "quote software for contractors", "estimate template [trade]" |
| **Google Ads** | High-intent search terms, measurable ROI |
| **Affiliate** | Contractor YouTubers, blog writers get commission |

**SEO Keywords to Own:**
- "contractor quote software"
- "estimate software for [trade]" (deck builders, painters, etc.)
- "voice to quote app"
- "AI quoting for contractors"
- "[trade] quote template"

**Action:**
- [ ] Build SEO content strategy (10 target keywords)
- [ ] Set up affiliate program (20% recurring?)
- [ ] Test Google Ads at $500/month, measure CAC vs LTV

---

#### Step 12: Scale What Works, Kill What Doesn't
> *"Growth is about 1-2 acquisition channels. Go all in on them."*

**Tibo's Insight:** Don't spread thin. Once you find what works, DOUBLE DOWN.

**Decision Framework:**

After 3 months of testing:
1. Which channel has lowest CAC?
2. Which channel brings users who RETAIN?
3. Which channel has room to 10x?

Kill everything else. Go all-in on the winners.

---

## Recommended Immediate Actions

### This Week
1. [ ] Identify 10 power users who match ideal profile
2. [ ] Route support to founder's direct channel (SMS/WhatsApp)
3. [ ] Schedule 3 user shadow sessions
4. [ ] Set up retention dashboard in PostHog

### This Month
1. [ ] Build "Contractor Profile" docs for top 10 users
2. [ ] Talk to every active user at least once
3. [ ] Call every churned user to understand why
4. [ ] Ship 1 feature requested by users in conversations

### Before Scaling Acquisition
1. [ ] Achieve >60% weekly active rate
2. [ ] Achieve >70% 30-day retention
3. [ ] Have 5+ genuine testimonials
4. [ ] Have 3+ case studies with specific numbers

---

## Key Questions for Team Discussion

1. **Are we ready for Phase 3?** Do we have stickiness, or are we still leaky bucket?

2. **Who are our 10 power users?** Names, not personas. Real people we can call.

3. **What's our support response time?** Are we at "text me and I'll respond in 5 minutes" level?

4. **What are users asking for?** What feature requests keep coming up in conversations?

5. **Why do users churn?** Have we called every single person who canceled?

---

## The Core Principle

> "Your job is to deeply understand the core need of your user. Talk to your user every day." — Tibo

Everything else flows from this. Features, pricing, marketing—all of it comes from understanding.

**We don't need more features. We need more conversations.**

---

*Based on: [I Built 4 SaaS Apps to $100K MRR: Here's My Exact Playbook](https://www.youtube.com/watch?v=xeUhKuJbeWQ)*

*Full video analysis: `knowledge_base/transcripts/2025-12-17_1226_I_Built_4_SaaS_Apps_to_$100K_MRR_Here's_My_Exact_Playbook.md`*
