# User Acquisition Strategy - DISC-074

**Generated**: 2025-12-08 | **Target**: 100 beta users by Dec 16

## Executive Summary

Design Council consensus: **Direct Founder Outreach + Referral Loop** as primary channel, supplemented by **Creator Partnerships** and **Low-Budget Paid Ads** testing.

### Priority Ranking (All Executives Aligned)

| Priority | Channel | CAC | Users (2 weeks) | Risk |
|----------|---------|-----|-----------------|------|
| **1. HIGH** | Direct Founder Outreach + Reddit | $0 | 20-35 | Time-intensive |
| **2. HIGH** | Creator Partnerships (YouTube) | $15-25 | 15-25 | Slow ramp (2-4 weeks) |
| **3. MEDIUM** | Low-Budget Paid Ads (Google only) | $12-18 | 10-20 | Higher churn |
| **4. LOW** | Content/SEO | $5-8 | 0-5 | 3-6 month horizon |
| **SKIP** | Facebook/Instagram Ads | - | - | Wrong audience fit |

## Ideal User Profile (CPO)

**Target**: Solo contractors and 2-3 person crews doing custom work (painting, carpentry, HVAC, roofing) who quote 5-20 jobs/month and struggle with quote accuracy consistency. They work from job sites, value speed, and want AI that learns their pricing over time.

**Key Insight**: Users who CORRECT quotes are gold. Acquisition channels matter less than feedback channels.

## Financial Constraints (CFO)

- **CAC Ceiling**: $38 (based on $152 blended LTV at 1:4 ratio)
- **Beta CAC Ceiling**: $19 (conservative, non-paying users)
- **Monthly Budget**: $350-500 maximum
- **Breakeven**: 4-5 paying users at $39/mo covers infrastructure

### Budget Allocation (December)

| Channel | Budget | Expected Users |
|---------|--------|----------------|
| Direct Outreach | $0 | 30 |
| Referral Loop | $0 | 30-40 |
| Google Ads Test | $100 | 5-10 |
| Creator Outreach | $0 upfront | 10-15 |
| Guerrilla/Print | $50 | 5-10 |
| **Total** | **$150** | **80-105** |

## Technical Infrastructure (CTO)

Existing systems support immediate launch:
- **Referral System**: Dual-sided rewards, UTM tracking, PostHog analytics
- **Landing Page**: `/demo.html` ready for traffic
- **Analytics**: Can segment by source, track quote generation rates

No new technical work required.

## Channel Playbooks

### 1. Direct Founder Outreach (Start Immediately)

**Actions**:
1. Identify 50 solo contractors on LinkedIn (painters, electricians, plumbers, HVAC)
2. Send 3-5 personalized DMs today: *"I built Quoted for contractors like you—30-second voice quotes. Try it?"*
3. Follow up with demo video link
4. Expect 10-15% response rate = 5-8 signups/week

**Tracking**: UTM `source=linkedin_dm`

### 2. Reddit Strategy (Careful Approach)

**Approved Subreddits**: r/contractors, r/electricians, r/HVAC, r/HomeImprovement

**Approach**:
- One genuine, helpful post per subreddit answering a real question
- NO direct pitch—add value first, mention Quoted only if relevant
- Link to demo.html, not landing page

**Example**: Post in r/contractors answering "How do you estimate roofing jobs?" with methodology, then mention "I built a tool that does this via voice"

### 3. Creator Partnerships (Week 2)

**Target Creators** (50K-200K subs sweet spot):
- Paul B Plumbing Tips
- Honest Plumbing
- Home improvement channels focused on contractors

**Offer**:
- Free Pro tier ($39/mo value) for 6 months
- 20% affiliate commission on conversions
- Authentic demo—not scripted read

**Expected**: $1-2K per partnership, 15-25 users per creator

### 4. Google Ads Test (If Budget Allows)

**Keywords**:
- "quote software for contractors"
- "estimate software electricians"
- "contractor quoting app"

**Budget**: $5/day × 20 days = $100
**Expected CAC**: $12-18
**Goal**: Validate if paid scales before investing more

### 5. What NOT To Do

- **Facebook/Instagram Ads**: Contractors don't buy SaaS while scrolling. Wrong fit.
- **TikTok Creators**: Short attention span, younger audience, high churn.
- **SEO/Content**: Great long-term, but won't hit Dec 16 goal.
- **Cold Email Blasts**: Spam, low quality, damages brand.

## Success Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| Signups | 100 by Dec 16 | PostHog event: `signup_completed` |
| Quote Generation | 60%+ generate quote in 48hrs | PostHog: `quote_generated` |
| Feedback Rate | 40%+ users provide corrections | PostHog: `quote_correction` |
| CAC | <$15 blended | Total spend / Total signups |

## Tracking Setup

All channels should use UTM parameters:
- `?utm_source=reddit&utm_campaign=contractors`
- `?utm_source=youtube&utm_medium=creator&utm_campaign=[creator_name]`
- `?utm_source=google&utm_medium=cpc&utm_campaign=quotes`
- `?utm_source=linkedin&utm_medium=dm&utm_campaign=founder_outreach`

## Risk Mitigation

1. **Tire-kickers from paid ads**: Track "quotes in first 48 hours"—if <1, channel is wrong fit
2. **Creator partnership fails**: Start with 2-3 creators in parallel, don't depend on one
3. **Reddit ban**: Don't post same content across subreddits; genuine engagement only
4. **Budget overrun**: Hard stop at $500/mo; reallocate if one channel underperforms

---

*Strategy synthesized from Design Council: CGO, CPO, CFO, CTO perspectives*
