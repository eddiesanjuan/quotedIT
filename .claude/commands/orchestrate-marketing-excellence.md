# Marketing Excellence Orchestrator (v1.0)

## Purpose

A comprehensive marketing audit and strategic analysis system that acts as an **experienced AI CMO** to:
1. Audit every aspect of Quoted's marketing presence
2. Analyze customer feedback collection and utilization
3. Identify holes in marketing logic and missed opportunities
4. Produce an executive-ready report with prioritized recommendations

---

## Architecture

**Problem**: Marketing efforts often happen in silos without holistic visibility into what's working, what's missing, and where the biggest opportunities lie.

**Solution**: This orchestrator performs a systematic 8-phase audit covering:
- Strategy & positioning
- Customer voice (feedback, testimonials, insights)
- Competitive landscape
- Acquisition funnels
- Content & messaging
- Retention & engagement
- Analytics & measurement
- Growth opportunities

**State File**: `.claude/marketing-excellence-state.md`
**Output**: Executive report saved to `reports/MARKETING_AUDIT_[DATE].md`

---

## Quick Start

```bash
# Full audit (continues from state file)
/orchestrate-marketing-excellence

# Run specific phase
/orchestrate-marketing-excellence --phase=3

# Status only
/orchestrate-marketing-excellence --status

# Generate report from current findings
/orchestrate-marketing-excellence --report

# Fresh start (ignore previous state)
/orchestrate-marketing-excellence --fresh
```

---

## Phase Overview

| Phase | Name | Focus | Time |
|-------|------|-------|------|
| 1 | Context Loading | Load all state files, marketing assets, analytics | 5 min |
| 2 | Strategy Audit | Positioning, ICP, differentiation, GTM | 15 min |
| 3 | Customer Voice | Feedback mechanisms, testimonials, insights utilization | 20 min |
| 4 | Competitive Analysis | Positioning vs competitors, messaging gaps | 15 min |
| 5 | Funnel Analysis | Acquisition channels, conversion paths, onboarding | 20 min |
| 6 | Content & Messaging | Brand consistency, SEO, content strategy | 15 min |
| 7 | Retention & Growth | Engagement, upsell, referral, churn prevention | 15 min |
| 8 | Executive Report | Synthesize findings, prioritize recommendations | 20 min |

---

## Phase 1: Context Loading

### Required Reading
Load and analyze these files to understand current state:

**State Files:**
- `COMPANY_STATE.md` - Overall company status and strategy
- `PRODUCT_STATE.md` - Product features and roadmap
- `ENGINEERING_STATE.md` - Technical capabilities
- `DISCOVERY_BACKLOG.md` - Pending features and ideas

**Marketing Assets:**
- `MARKETING_PLAYBOOK.md` - Current marketing strategy
- `QUOTED_TIBO_PLAYBOOK.md` - Influencer/creator strategy (if exists)
- `marketing/` directory - All marketing tools and assets
- `knowledge/marketing-learning.md` - Marketing learnings

**Product Marketing:**
- `frontend/landing.html` - Landing page messaging
- `frontend/demo.html` - Demo experience
- `frontend/index.html` - App messaging and onboarding
- `frontend/help.html` - Support/help content
- `frontend/blog/` - Content marketing

**Customer Data:**
- Review testimonial collection system (DISC-010)
- Review feedback mechanisms in the app
- Check PostHog for analytics setup

### Output
- [ ] All files loaded and analyzed
- [ ] Current marketing strategy understood
- [ ] Customer feedback mechanisms identified
- [ ] Analytics coverage assessed

---

## Phase 2: Strategy Audit

### 2.1 Positioning Analysis
Evaluate current positioning against market reality:

| Dimension | Questions to Answer |
|-----------|---------------------|
| **ICP Definition** | Is the ideal customer clearly defined? Are we targeting too broad/narrow? |
| **Value Proposition** | Is "voice-to-quote in seconds" compelling? Does it differentiate? |
| **Competitive Position** | How do we position vs Proposify, Jobber, Buildxact, Excel? |
| **Price Positioning** | Is $9/mo positioned correctly? Does pricing reinforce value? |
| **Brand Voice** | Is messaging consistent across all touchpoints? |

### 2.2 Go-To-Market Assessment
- [ ] Primary acquisition channels identified?
- [ ] Channel-market fit validated?
- [ ] Sales motion defined (PLG vs sales-assisted)?
- [ ] Launch strategy documented?

### 2.3 Multi-Segment Awareness
Per orchestrator constraints, Quoted targets multiple segments:
- Trades (HVAC, plumbing, electrical, roofing)
- Home services (cleaning, landscaping, pest control)
- Auto (body shops, mechanics, detailing)
- Events (photographers, caterers, DJs, florists)
- Creative (freelance designers, videographers)
- Professional services (consultants, coaches)

**Audit Questions:**
- [ ] Is messaging segment-neutral or contractor-biased?
- [ ] Do case studies/testimonials span segments?
- [ ] Does onboarding accommodate different industries?

### Output
Document findings in state file with:
- Positioning strengths and weaknesses
- ICP clarity score (1-10)
- Competitive differentiation gaps
- Recommended positioning refinements

---

## Phase 3: Customer Voice Analysis

### 3.1 Feedback Collection Mechanisms

**Inventory all feedback touchpoints:**

| Touchpoint | Exists? | Quality | Utilization |
|------------|---------|---------|-------------|
| In-app feedback (quotes) | ? | ? | ? |
| Testimonial collection (DISC-010) | ? | ? | ? |
| Issue reporter (?) | ? | ? | ? |
| Email feedback channel | ? | ? | ? |
| Social listening (@QuotedIT_app) | ? | ? | ? |
| PostHog surveys | ? | ? | ? |
| NPS/satisfaction tracking | ? | ? | ? |
| Churn exit surveys | ? | ? | ? |
| Feature request tracking | ? | ? | ? |

### 3.2 Voice of Customer Utilization

**Audit how customer voice feeds back into:**
- [ ] Product decisions - Are features driven by customer feedback?
- [ ] Marketing copy - Do we use customer language?
- [ ] Testimonials - Are we actively collecting and displaying?
- [ ] Case studies - Do we have customer success stories?
- [ ] Objection handling - Do we address common concerns?

### 3.3 Testimonial System Deep Dive

Review DISC-010 implementation:
- [ ] When are testimonials requested? (optimal timing)
- [ ] What's the collection rate?
- [ ] Where are testimonials displayed?
- [ ] Are testimonials segmented by industry?
- [ ] Is there a review pipeline to external sites (G2, Capterra)?

### 3.4 Feedback Loop Gaps

Identify missing feedback mechanisms:
- [ ] No way to capture "why did you choose us?"
- [ ] No win/loss analysis on quotes
- [ ] No feature voting/prioritization
- [ ] No customer health scoring
- [ ] No proactive outreach to at-risk customers

### Output
- Customer voice health score (1-10)
- Gap analysis with prioritized recommendations
- Quick wins for improving feedback collection

---

## Phase 4: Competitive Analysis

### 4.1 Competitive Landscape

Map Quoted's position in the market:

```
                    HIGH COMPLEXITY
                         │
           Buildxact     │      Proposify
           JobTread      │      PandaDoc
                         │
    ─────────────────────┼─────────────────────
    LOW PRICE            │            HIGH PRICE
                         │
           Quoted ◄──────│      Jobber
           Excel         │      ServiceTitan
                         │
                    LOW COMPLEXITY
```

### 4.2 Messaging Comparison

For each major competitor, analyze:
- [ ] How do they position themselves?
- [ ] What benefits do they emphasize?
- [ ] What customer segments do they target?
- [ ] What's their pricing model?
- [ ] Where are they vulnerable?

### 4.3 Feature Parity Check

| Feature | Quoted | Proposify | Jobber | Gap? |
|---------|--------|-----------|--------|------|
| Voice input | ✅ | ❌ | ❌ | Advantage |
| AI pricing | ✅ | ❌ | ❌ | Advantage |
| E-signatures | ✅ | ✅ | ✅ | Parity |
| Templates | ✅ | ✅ | ✅ | Parity |
| CRM | ✅ | ✅ | ✅ | Parity |
| Invoicing | ✅ | ✅ | ✅ | Parity |
| Payments | ? | ✅ | ✅ | Gap? |
| Scheduling | ❌ | ❌ | ✅ | Intentional gap |

### 4.4 Competitive Messaging Opportunities

Identify claims we can make that competitors can't:
- [ ] "Built by a contractor, not a tech company"
- [ ] "Speak your quote, don't type it"
- [ ] "AI that learns your pricing"
- [ ] "$9/mo, not $49/mo"

### Output
- Competitive positioning map
- Messaging differentiation opportunities
- Feature gaps to address or highlight

---

## Phase 5: Funnel Analysis

### 5.1 Acquisition Channel Audit

For each channel, assess:

| Channel | Investment | Volume | CAC | Quality | Verdict |
|---------|------------|--------|-----|---------|---------|
| Organic Search | ? | ? | ? | ? | ? |
| Reddit | ? | ? | ? | ? | ? |
| Cold Email | ? | ? | ? | ? | ? |
| Social (X/Twitter) | ? | ? | ? | ? | ? |
| Referrals | ? | ? | ? | ? | ? |
| Content/Blog | ? | ? | ? | ? | ? |
| Paid Ads | ? | ? | ? | ? | ? |

### 5.2 Landing Page Analysis

Review `frontend/landing.html`:
- [ ] Hero message clarity (< 3 seconds to understand)
- [ ] Social proof placement (testimonials, logos)
- [ ] CTA clarity and prominence
- [ ] Objection handling (pricing, trust, ease)
- [ ] Mobile optimization
- [ ] Page speed

### 5.3 Demo Experience

Review `frontend/demo.html`:
- [ ] Time to value (how quickly do they see the magic?)
- [ ] Friction points in the flow
- [ ] Conversion from demo to signup
- [ ] Demo → Paid conversion tracking

### 5.4 Onboarding Flow

Review signup → first quote journey:
- [ ] Time to first value
- [ ] Drop-off points
- [ ] Activation rate (% who create first quote)
- [ ] Pricing model setup success rate
- [ ] Quick setup vs interview path performance

### 5.5 Conversion Funnel Metrics

Map the full funnel:
```
Visitor → Demo → Signup → Activated → Paid → Retained
  ?    →  ?%  →   ?%   →    ?%     →  ?%  →   ?%
```

### Output
- Funnel visualization with conversion rates
- Biggest drop-off points identified
- Channel ROI analysis
- Prioritized optimization recommendations

---

## Phase 6: Content & Messaging Audit

### 6.1 Brand Consistency

Check messaging consistency across:
- [ ] Landing page headlines
- [ ] App onboarding copy
- [ ] Email communications
- [ ] Help center tone
- [ ] Blog voice
- [ ] Social media presence
- [ ] Error messages and microcopy

### 6.2 SEO Analysis

- [ ] Target keywords identified?
- [ ] Blog content aligned with keywords?
- [ ] Technical SEO (meta tags, schema, speed)?
- [ ] Backlink profile?
- [ ] Local SEO (for trades)?

### 6.3 Content Strategy

Review `frontend/blog/`:
- [ ] Content calendar exists?
- [ ] Topics aligned with customer journey?
- [ ] Mix of educational, promotional, SEO content?
- [ ] Content distribution strategy?
- [ ] Content performance tracking?

### 6.4 Email Marketing

Review email touchpoints:
- [ ] Welcome sequence
- [ ] Activation emails
- [ ] Feature announcements
- [ ] Re-engagement campaigns
- [ ] Transactional emails (quote sent, payment, etc.)

### 6.5 Social Presence

Review @QuotedIT_app and other social:
- [ ] Posting frequency
- [ ] Engagement rates
- [ ] Content mix (educational, product, community)
- [ ] Response time to mentions

### Output
- Brand consistency score (1-10)
- Content gap analysis
- SEO opportunity assessment
- Email marketing maturity level

---

## Phase 7: Retention & Growth Analysis

### 7.1 Retention Mechanics

Identify what keeps users engaged:
- [ ] Daily/weekly active use cases
- [ ] Habit-forming features
- [ ] Switching costs (data lock-in)
- [ ] Community/network effects

### 7.2 Churn Analysis

- [ ] Churn rate by cohort
- [ ] Churn reasons (if tracked)
- [ ] At-risk indicators
- [ ] Win-back campaigns

### 7.3 Expansion Revenue

- [ ] Upsell paths (pricing tiers)
- [ ] Cross-sell opportunities
- [ ] Usage-based expansion
- [ ] Add-on features

### 7.4 Referral Program

- [ ] Referral mechanism exists?
- [ ] Incentive structure
- [ ] Referral rate
- [ ] Viral coefficient

### 7.5 Customer Success

- [ ] Proactive outreach cadence
- [ ] Health scoring
- [ ] Success milestones tracked
- [ ] Advocacy program (reviews, testimonials)

### Output
- Retention health assessment
- Churn risk factors
- Growth lever prioritization
- Referral program recommendations

---

## Phase 8: Executive Report Generation

### Report Structure

Generate `reports/MARKETING_AUDIT_[DATE].md` with:

```markdown
# Marketing Excellence Audit Report
**Date**: [DATE]
**Prepared by**: AI Marketing Orchestrator
**For**: Quoted Executive Team

## Executive Summary
[2-3 paragraph overview of findings]

## Marketing Health Scorecard

| Dimension | Score | Status |
|-----------|-------|--------|
| Positioning & Strategy | X/10 | 🟢/🟡/🔴 |
| Customer Voice | X/10 | 🟢/🟡/🔴 |
| Competitive Position | X/10 | 🟢/🟡/🔴 |
| Acquisition Funnel | X/10 | 🟢/🟡/🔴 |
| Content & Messaging | X/10 | 🟢/🟡/🔴 |
| Retention & Growth | X/10 | 🟢/🟡/🔴 |
| Analytics & Measurement | X/10 | 🟢/🟡/🔴 |
| **OVERALL** | **X/10** | **STATUS** |

## Critical Gaps (Must Fix)
[Prioritized list of critical issues]

## Missed Opportunities (High Impact)
[Opportunities ranked by potential impact]

## Quick Wins (< 1 week effort)
[Low-effort, high-value improvements]

## Strategic Initiatives (1-3 month horizon)
[Longer-term strategic recommendations]

## Detailed Findings by Phase
[Full findings from each audit phase]

## Recommended 30-60-90 Day Plan
[Phased implementation roadmap]

## Appendix
- Raw data and metrics
- Competitive screenshots
- Customer feedback samples
```

### Scoring Rubric

| Score | Meaning |
|-------|---------|
| 9-10 | Best-in-class, competitive advantage |
| 7-8 | Strong, minor improvements needed |
| 5-6 | Adequate, significant room for improvement |
| 3-4 | Weak, requires urgent attention |
| 1-2 | Critical gap, business risk |

---

## State File Format

`.claude/marketing-excellence-state.md`:

```markdown
# Marketing Excellence Orchestrator State

**Last Updated**: [TIMESTAMP]
**Current Phase**: [1-8]
**Status**: [IN_PROGRESS | COMPLETE | BLOCKED]

## Phase Completion

| Phase | Status | Completed | Notes |
|-------|--------|-----------|-------|
| 1. Context Loading | ✅/🔄/⏳ | [DATE] | |
| 2. Strategy Audit | ✅/🔄/⏳ | [DATE] | |
| 3. Customer Voice | ✅/🔄/⏳ | [DATE] | |
| 4. Competitive Analysis | ✅/🔄/⏳ | [DATE] | |
| 5. Funnel Analysis | ✅/🔄/⏳ | [DATE] | |
| 6. Content & Messaging | ✅/🔄/⏳ | [DATE] | |
| 7. Retention & Growth | ✅/🔄/⏳ | [DATE] | |
| 8. Executive Report | ✅/🔄/⏳ | [DATE] | |

## Findings Summary

### Phase 2: Strategy
[Key findings]

### Phase 3: Customer Voice
[Key findings]

[... etc for each phase]

## Blockers & Questions
- [Any items needing founder input]

## Next Actions
- [Immediate next steps]
```

---

## Execution Instructions

### Starting the Audit

1. **Read state file** (if exists) to understand progress
2. **Continue from last phase** or start fresh if `--fresh`
3. **For each phase:**
   - Announce phase start
   - Read all relevant files
   - Perform analysis using checklist
   - Document findings in state file
   - Mark phase complete
4. **Generate report** when all phases complete or `--report` flag

### Quality Standards

- **Evidence-based**: Every finding must cite specific source
- **Actionable**: Every recommendation must have clear next steps
- **Prioritized**: Use impact/effort matrix for recommendations
- **Honest**: Call out both strengths and weaknesses
- **Specific**: Avoid vague recommendations like "improve marketing"

### Tool Usage

- Use `Read` for all file analysis
- Use `Grep` to search across codebase for patterns
- Use `Glob` to find relevant files
- Use `WebFetch` for live site analysis if needed
- Use `Task` with `subagent_type=Explore` for deep codebase exploration

### Report Delivery

After generating the report:
1. Save to `reports/MARKETING_AUDIT_[DATE].md`
2. Create summary for founder with top 3 findings
3. Identify any items requiring founder decision
4. Propose next steps

---

## Constraints & Guidelines

### From Proposify Domination Orchestrator

**These constraints apply to marketing recommendations:**

- **Pricing Philosophy**: $9/mo strategy is intentional margin moat - don't recommend price increases
- **Multi-Segment**: Recommendations must work across all target segments, not just contractors
- **Cost Efficiency**: Marketing recommendations should consider CAC constraints
- **Network Effects**: Consider future platform/marketplace opportunities

### Marketing-Specific Guidelines

- **Authenticity**: Eddie's founder story is a core asset - recommendations should leverage, not diminish it
- **Blue-collar audience**: Messaging should be direct and practical, not corporate-speak
- **PLG-first**: Product-led growth is primary - minimize recommendations requiring sales team
- **Bootstrap mindset**: Prefer organic/content strategies over paid acquisition at this stage

---

## Example Findings Format

### Good Finding (Specific, Actionable)
```
**Finding**: Demo page has no social proof
**Evidence**: frontend/demo.html has 0 testimonials, no trust badges, no user count
**Impact**: HIGH - Demos likely have lower conversion without credibility signals
**Recommendation**: Add 2-3 testimonials from beta users, "X quotes generated" counter
**Effort**: LOW (< 2 hours)
**Priority**: P1 - Quick win
```

### Bad Finding (Vague, Not Actionable)
```
**Finding**: Marketing could be better
**Recommendation**: Do more marketing
```

---

## Success Criteria

The audit is successful when:
1. [ ] All 8 phases completed with documented findings
2. [ ] Overall health score calculated with supporting evidence
3. [ ] At least 5 critical gaps identified (or confirmed none exist)
4. [ ] At least 10 missed opportunities ranked by impact
5. [ ] At least 5 quick wins identified (< 1 week effort each)
6. [ ] 30-60-90 day plan created
7. [ ] Executive report generated and saved
8. [ ] Founder briefed on top findings

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-25 | Initial version |
