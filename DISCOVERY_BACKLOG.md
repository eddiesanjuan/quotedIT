# Discovery Backlog

**Last Updated**: 2026-01-05
**Source**: `/quoted-discover` autonomous discovery cycles

---

## Quick Reference

| Resource | Purpose |
|----------|---------|
| **This file** | Active work only (READY, DISCOVERED, COMPLETE) |
| **DISCOVERY_ARCHIVE.md** | All DEPLOYED tickets (historical reference) |

**State Hygiene**: This file is cleaned during each `/quoted-run`. DEPLOYED tickets are moved to archive after 2 weeks.

---

## Status Legend

| Status | Meaning |
|--------|---------|
| **READY** | Approved, ready for implementation |
| **DISCOVERED** | Proposed, awaiting founder review |
| **COMPLETE** | Implemented, pending deploy |

To approve: Change status from DISCOVERED → READY (or use `/add-ticket`)

---

## Summary

| Status | Count |
|--------|-------|
| READY | 10 |
| DISCOVERED | 18 |
| COMPLETE | 11 |
| **Active Total** | **39** |
| Archived (DEPLOYED) | 92+ |

**Autonomous AI Infrastructure**: DISC-101/102/104/106 DEPLOYED, DISC-103/105 READY
**Agent Reliability Engineering**: DISC-107/108 DEPLOYED, DISC-109 DISCOVERED
**Analytics Pipeline**: DISC-136/137/138/139/141/142/149/151 ALL DEPLOYED (Jan 3-5)
**Phase II Voice Control**: DISC-042 through DISC-049 (8 tickets) - DISCOVERED, awaiting founder review
**Competitive Defense**: DISC-060 through DISC-062 - DISCOVERED

*Last hygiene: 2026-01-05. DEPLOYED tickets migrated to DISCOVERY_ARCHIVE.md*

---

## Recently Deployed (Last 5)

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-135 | Post-Job Pricing Reflection Loop + Conversion Tracking | 2025-12-31 |
| DISC-133 | Clarification Answers Feed Into Learning System | 2025-12-30 |
| DISC-132 | Interactive Clarifying Questions for Demo | 2025-12-30 |
| DISC-131 | Demo Page Dictation Examples | 2025-12-30 |
| DISC-113 | Time Savings Calculator (partial) | 2025-12-30 |

*Full deployment history: See DISCOVERY_ARCHIVE.md*

---

## READY - Approved for Implementation

### DISC-113: "Handyman Mike" Workflow Storytelling System 🎬 CONVERSION (READY)

**Partial Deploy**: 2025-12-30 - Time Savings Calculator component only
**Remaining Work**: Story-based tour, pre-seeded demo data, workflow animation, marketing assets

**Source**: Founder Request (Eddie, 2025-12-27)
**Impact**: HIGH | **Effort**: L | **Score**: 1.5
**Sprint Alignment**: Conversion optimization for paid acquisition

**Problem**: Current tour shows features, not transformation. Users see buttons but don't viscerally understand the complete workflow value: voice quote → quick edit → send → auto-remind → track → e-signature → invoice → paid. They can't visualize the 5+ hours/week they'd save.

**The Handyman Persona**:
- "Mike" does furniture assembly, TV mounting, drywall patches, fixture installs
- 5-10 small jobs/day ($50-500 each)
- Works from his truck, quotes on-site
- Pain: spending evenings writing quotes instead of being with family
- **Time Math**: 5 jobs/day × 15 min saved = 75 min/day = **6.25 hours/week** = **27 hours/month**

**Proposed Work**:
1. **Story-Based Tour Redesign** - Transform Shepherd.js tour from "here's the button" to "follow Mike through a real day"
2. **Time Savings Calculator** - Widget: "How many quotes/day?" → Shows weekly/monthly hours saved
3. **Pre-Seeded Demo Data** - Demo mode shows Mike's existing quotes, customers, tasks (not empty state)
4. **Workflow Animation** - Visual showing the loop: Voice → Quote → Edit → Send → Remind → Sign → Invoice
5. **Marketing Asset Pack** - Same "Mike" story for: landing page, Google Ads, Reddit posts, email sequence

**Why Handyman**:
- Universally relatable (everyone knows one)
- High volume = obvious time savings
- Voice-first resonates (always on-site)
- Works for multiple marketing channels
- NOT a specialized trade (broad appeal)

**Success Metric**: Demo-to-signup conversion rate +25%; Time-on-demo-page +40%

**Reusable Assets**:
- Landing page hero video script
- Google Ads creative copy
- Reddit "As a handyman, I was skeptical..." post template
- Email welcome sequence with Mike's story

---

### DISC-033: Reddit Contractor Launch Post 🚀 FOUNDER ACTION (READY)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5

**Problem**: 410K+ contractors on Reddit, zero awareness of Quoted. Warm audience that complains daily about quoting friction.

**Proposed Work**:
1. Craft founder-story Reddit post for r/contractors, r/Construction, r/smallbusiness
2. Format: "I built a voice-to-quote tool because I was tired of 30-minute spreadsheets"
3. Include demo link, emphasize learning system
4. Post during peak hours (Tuesday-Thursday 9am-11am EST)

**Success Metric**: 5,000+ impressions; 150 demo views; 22 signups

---

### DISC-070: Voice-Driven PDF Template Customization 🎨 PRO/TEAM (READY)

**Source**: Founder Request (Eddie, 2025-12-07)
**Impact**: HIGH | **Effort**: XL | **Score**: 0.75

**Problem**: Contractors want personalized quotes but aren't designers. Can't say "make my logo bigger" - stuck with presets.

**Vision**: Voice/chat-driven template design. Lower barrier from "know CSS" to "talk about what you want."

**Example Commands**: "Move my logo to the center", "Change accent color to blue", "Make it less cluttered"

---

### DISC-074: Alternative User Acquisition Channels 📢 BRAINSTORM (READY)

**Source**: Founder Request (Eddie, 2025-12-08)
**Impact**: HIGH | **Effort**: M | **Score**: 2.0

**Problem**: Reddit/Facebook groups have strict anti-advertising rules. Need alternative acquisition channels.

---

### DISC-081: QuickBooks Integration Exploration 📊 BRAINSTORM (READY)

**Source**: Founder Request (Eddie, 2025-12-08)
**Impact**: HIGH | **Effort**: L-XL | **Score**: Strategic

**Problem**: Contractors already use QuickBooks for accounting. Integration would make Quoted stickier.

---


### DISC-103: Smart Complexity Detection for Task Routing 🎯 INFRASTRUCTURE (READY)

**Source**: Founder Request (Eddie, 2025-12-21) - Transcript Insights Analysis
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0

**Problem**: All tasks treated similarly. Simple tasks over-engineered, complex tasks under-scoped.

**Routing**: 85%+ confidence → Execute directly | 60-85% → Checkpoints | <60% → Plan first

---


### DISC-105: Learning Memory System - Dual Architecture 🧠 INFRASTRUCTURE (READY)

**Source**: Founder Request (Eddie, 2025-12-21) - Transcript Insights Analysis
**Impact**: HIGH | **Effort**: XL | **Score**: 1.0

**Problem**: Limited cross-session learning. Each cycle starts without context of past successes/failures.

**Architecture**: Graph Memory (entities, relationships) + Semantic RAG (past decisions, outcomes)

---




















### DISC-134: Social Login (Google, Apple, etc.) 🔐 AUTH (COMPLETE)

**Source**: Founder Request (Eddie, 2025-12-30)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Reduces signup friction, industry-standard auth option

**Problem**: Currently users must use magic link (email-based) authentication. While frictionless, many users expect and prefer OAuth/social login options they use everywhere else. "Sign in with Google" is often perceived as faster and more trustworthy than entering an email address.

**Proposed Work**:
1. **Google OAuth Integration** - Add "Sign in with Google" button to auth flow (highest priority, most common) [DONE]
2. **Apple Sign In** - Add Apple OAuth for iOS users (required for App Store if we ever go mobile) [FUTURE]
3. **UI Updates** - Auth form redesign with social buttons + "or continue with email" divider [DONE]
4. **Account Linking** - Handle edge case where user has both email and social accounts [DONE - uses same email]
5. **PostHog Tracking** - Track auth method chosen to measure adoption [DONE]

**Technical Notes**:
- Google: OAuth 2.0 via Google Cloud Console
- Apple: Sign in with Apple SDK
- Backend: Store OAuth provider + provider_id in contractor model
- Consider: passkey support for future (WebAuthn)

**Implementation**:
- Created `backend/api/social_auth.py` with Google OAuth endpoint (`POST /api/auth/google`)
- Added `google_oauth_client_id` config setting
- Updated `frontend/start.html` with Google Sign-In button and handlers
- Button gracefully hides if Google client ID not configured
- Tracks `google_signin_clicked`, `google_signup_completed`, `google_login_completed` events

**To Enable**:
1. Create Google Cloud Console project
2. Enable OAuth 2.0 and get Client ID
3. Set `GOOGLE_OAUTH_CLIENT_ID` in Railway environment variables
4. Add authorized origins: `https://quoted.it.com`, `https://www.quoted.it.com`

**Success Metric**: 30%+ of new signups use social login within 30 days of launch

---

### DISC-140: Autonomous Monitoring Agent 🤖 INFRASTRUCTURE (READY)

**Source**: Founder Request (Eddie, 2025-12-30)
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: AI civilization infrastructure

**Problem**: No autonomous system watching for anomalies. Founder must manually check everything.

**Vision**: An AI agent that continuously monitors Quoted and surfaces issues proactively.

**Proposed Work**:
1. **Monitoring Agent Architecture**
   - Scheduled runs (every 15 min for critical, hourly for trends)
   - State persistence (knows what's "normal")
   - Alert throttling (don't spam)

2. **Health Checks**:
   - API response times (alert if >2s average)
   - Error rates (alert if >1% of requests)
   - Demo generation success rate
   - PDF generation success rate
   - Payment processing health

3. **Business Metrics Watch**:
   - Traffic anomalies (up or down)
   - Conversion rate changes
   - Revenue alerts (payment failures)
   - Churn signals (users deleting accounts)

4. **Competitive Intelligence**:
   - Monitor competitor pricing changes
   - Track competitor feature releases
   - Alert on industry news mentioning "quoting"

5. **Weekly Summary Email**:
   - Key metrics vs. previous week
   - Anomalies detected
   - Recommended actions

**Success Metric**: Founder wakes up to a briefing, not a crisis

---

### DISC-144: Evolve Landing Page Messaging - Voice Hook + Depth Reveal 🎯 GROWTH (COMPLETE)

**Source**: Founder Request (Eddie, 2026-01-04)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Conversion optimization, differentiation preservation

**Problem**: Current "Voice to Quote" positioning is differentiating but undersells the full value. Product has evolved to include learning system, customer tracking, outcome-aware pricing, but marketing doesn't reveal this depth. Risk of being perceived as a single-feature tool.

**Strategic Insight**: Don't abandon the voice hook (it's the unfair advantage). Instead, evolve the narrative to reveal depth while keeping the differentiator.

**Proposed Work**:
1. **Hero Evolution** - A/B test headlines:
   - Current: "Voice to Quote"
   - Test A: "Describe your job. Get a professional quote in seconds."
   - Test B: "Talk. Quote. Get Paid."
   - Subtext expansion: "Quoted learns your pricing, tracks your customers, and gets smarter with every job."

2. **Value Depth Section** - Add section below hero showing:
   - Learning system ("Gets smarter with every quote you send")
   - Customer tracking ("Know your repeat customers automatically")
   - Outcome awareness ("Learn from what actually wins jobs")

3. **Trust Signal Enhancement** - Add:
   - "Powered by Claude" or similar AI credibility
   - Time savings calculator prominent placement
   - Testimonial/proof when available

4. **PostHog Experiment Setup** - Proper A/B test infrastructure for headline variants

**What NOT to Do**:
- Don't use "CRM" (sets wrong expectations)
- Don't abandon voice as primary hook
- Don't make it sound like every other SaaS

**Success Metric**: Demo page visits from landing +20%; Signup conversion rate improvement measurable via A/B test

---

### DISC-145: Fresh Blog Content Round - Organic Voice, Living Blog 📝 GROWTH (READY)

**Source**: Founder Request (Eddie, 2026-01-04)
**Impact**: MEDIUM | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: Content marketing, SEO diversification, brand authenticity

**Problem**: Current blog articles are SEO-optimized guides (useful but formulaic). The blog feels like a static SEO farm rather than a living publication. Need fresh content with varied tones to build authentic brand voice and attract different audience segments.

**Content Strategy Shift**:
- Move from "Ultimate Guide to X" formula to varied, authentic content
- Include founder perspective, industry insights, real contractor stories
- Create content people actually want to read (not just rank for)

**Proposed Topics** (3-5 articles):
1. **"Pricing Psychology: Why Contractors Undercharge"** - Behavioral insights, real data from learning system patterns
2. **"Lessons From Our First 100 Quotes"** - Founder perspective, what we learned building Quoted
3. **"The 5 Quoting Mistakes That Cost You Jobs"** - Practical, shareable, contractor voice
4. **"Seasonal Job Trends: What's Hot in Q1"** - Timely, industry insight piece
5. **"Why I Built a Voice-to-Quote App"** - Founder story, origin, vision

**Tone Guidelines**:
- Authentic, not corporate
- Opinionated where appropriate
- Include real examples/data when possible
- Varied lengths (some short takes, some deep dives)
- NO buzzword-heavy AI hype

**Proposed Work**:
1. Outline 3-5 article topics with angles
2. Write articles with varied tones/lengths
3. Add to blog with proper og:image tags
4. Cross-post/promote on relevant channels

**Success Metric**: Blog traffic diversity (not just SEO); social shares; time-on-page > existing articles

---

### DISC-154: Google Ads Creative Refresh - AI Learning + Tire Kicker Messaging 🎨📈 GROWTH (READY)

**Source**: Founder Request (Eddie, 2026-01-05)
**Impact**: HIGH | **Effort**: L | **Score**: 1.5
**Sprint Alignment**: Paid acquisition optimization, messaging evolution
**Related**: DISC-144 (Landing Page Messaging Evolution)

**Problem**: Current Google Ads creative doesn't communicate the evolved value proposition. Image ads perform best, but existing imagery focuses on generic "quoting" rather than the differentiating AI learning system and tire-kicker elimination. Need fresh creative that aligns with the messaging evolution strategy.

**Strategic Messaging Shift**:
- From: "Voice to Quote" (feature)
- To: "AI That Learns Your Pricing" + "Eliminate Tire Kickers" (outcomes)

**Hook Concepts to Test**:

| Hook | Pain Point | Angle |
|------|------------|-------|
| "Stop Chasing Tire Kickers" | Wasted time on unserious leads | Qualification/filtering |
| "Your Pricing Brain" | Uncertainty, leaving money on table | AI learning, confidence |
| "Quote in 30 Seconds, From Your Truck" | Time spent on admin | Speed + mobility |
| "AI That Learns How YOU Price" | Generic tools don't fit | Personalization |
| "Win More Jobs with Smarter Quotes" | Low close rates | Outcome focus |
| "Professional Quotes Without the Paperwork" | Admin burden | Ease/simplicity |

**Visual Concepts**:

1. **Before/After Split**: Messy handwritten estimate vs. clean professional PDF
2. **Time Visualization**: Clock/calendar showing hours saved per week
3. **Brain/Learning Visual**: Abstract AI learning graphic (not cheesy robot)
4. **Filter Funnel**: Tire kickers being filtered out, serious customers passing through
5. **Contractor on Job Site**: Relatable imagery - phone in hand, work truck background
6. **Money Stack**: Pricing confidence, "stop leaving money on the table"
7. **Speed Blur**: 30-second transformation from voice to PDF

**Google Ads Image Specifications**:
- Square: 1200x1200 (responsive display)
- Landscape: 1200x628 (standard display)
- Portrait: 960x1200 (mobile-optimized)

**Proposed Work**:
1. **Audit current creative** - What's running, performing, missing
2. **Design 10-15 image variations** across hook concepts
3. **Write headline/description copy** to match each visual theme
4. **Create A/B test structure** in Google Ads
5. **Align with DISC-144** - Ensure ad creative matches landing page messaging

**Creative Principles**:
- Show outcomes, not features
- Contractor-relatable imagery (not stock photo corporate)
- Bold, readable text overlays
- Clear value prop in first 2 seconds
- NO generic "AI" imagery (robots, neural networks)
- YES to concrete benefits (time, money, confidence)

**Success Metric**: CTR improvement on image ads; conversion rate improvement from ad → demo; identify top 3 performing hooks

---

## DISCOVERED - Awaiting Founder Review

### Agent Reliability Engineering (1 ticket remaining)

| Ticket | Title | Effort | Relates To |
|--------|-------|--------|------------|
| DISC-109 | Cadence-Based Human Checkpoints (Every N Cycles) | S | Complements DISC-102 |

**Source**: "Are Agent Harnesses Bringing Back Vibe Coding?" video analysis
**Note**: DISC-107 and DISC-108 implemented - see COMPLETE section

---

### DISC-109: Cadence-Based Human Checkpoints 🛑 INFRASTRUCTURE (DISCOVERED)

**Source**: YouTube research - Agent Harness Reliability
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0

**Problem**: Long autonomous runs can compound errors. Need strategic human-in-the-loop.

**Proposed Work**:
1. `/quoted-run` pauses every 3 cycles for founder review
2. Generate summary to DECISION_QUEUE.md with checkbox for continue/pause/stop
3. Summary includes: cycles completed, tasks done, test status, remaining backlog
4. Auto-continue after 30 minutes for Type 1-2 work only (Type 3-4 waits indefinitely)

**Relationship to DISC-102**: DISC-102 is risk-based (classify actions by risk level). This is cadence-based (checkpoint every N cycles regardless of content). Both are valid; cadence-based is simpler but less surgical.

**Success Metric**: Catch compound errors before they exceed 3 cycles.

---

### DISC-143: Configure Google Ads API Credentials 🔑 ANALYTICS (DISCOVERED)

**Source**: DISC-141 Phase 2 infrastructure (2025-01-04)
**Impact**: HIGH | **Effort**: S | **Score**: 2.5
**Urgency**: High - traffic declining, need visibility

**Problem**: Google Ads campaigns running but no visibility into performance via API. Currently requires manual dashboard checking which is overwhelming.

**Infrastructure Ready**: `backend/services/google_ads_analytics.py` is built and waiting for credentials.

**Setup Steps**:

1. **Get Developer Token** (5 min):
   - Go to https://ads.google.com/aw/apicenter
   - Apply for API access (Basic access is fine for read-only)
   - Copy the developer token

2. **Create OAuth Credentials** (10 min):
   - Go to https://console.cloud.google.com
   - Create new project or use existing
   - Enable "Google Ads API"
   - Go to APIs & Services → Credentials → Create OAuth Client ID
   - Type: Web application
   - Add authorized redirect: `https://quoted.it.com/auth/callback/google`
   - Copy Client ID and Client Secret

3. **Generate Refresh Token** (5 min):
   - Use Google's OAuth Playground: https://developers.google.com/oauthplayground
   - Configure with your Client ID/Secret
   - Authorize scope: `https://www.googleapis.com/auth/adwords`
   - Exchange for refresh token

4. **Add to Railway** (2 min):
   ```
   GOOGLE_ADS_DEVELOPER_TOKEN=<your token>
   GOOGLE_ADS_CLIENT_ID=<client id>
   GOOGLE_ADS_CLIENT_SECRET=<client secret>
   GOOGLE_ADS_REFRESH_TOKEN=<refresh token>
   GOOGLE_ADS_CUSTOMER_ID=<10-digit account ID, no dashes>
   ```

5. **Verify**: `GET /api/analytics/google-ads` should return campaign data

**Once Complete**:
- Daily reports will include Google Ads metrics
- AI recommendations for optimization
- Anomaly alerts for CPC/CTR issues

---

### DISC-150: Referral Credit Redemption Mechanism 💳 GROWTH (DISCOVERED)

**Source**: Code analysis - referral.py awards credits but no redemption path
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Referral system completion, user trust

**Problem**: The referral system awards `referral_credits` (1 month credit) when a referee subscribes, but there's no mechanism to REDEEM these credits against their subscription. This means:
- Users refer friends expecting rewards
- Credits accumulate but provide no value
- Referral incentive is effectively broken

**Current State**: `credit_referrer()` increments `referral_credits` counter, but billing system never checks/applies them.

**Proposed Work**:
1. Add credit redemption check in Stripe checkout/renewal
2. UI in Account Settings showing available credits
3. Auto-apply one credit per billing cycle
4. Notification when credit is applied

**Success Metric**: Referral credits redeemable; referral rate increases

---

### DISC-152: Win Factors Tracking for Quotes 📈 LEARNING (DISCOVERED)

**Source**: Code analysis - quotes.py line 3004 has `top_win_factors=[],  # TODO: Track win factors`
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Learning system enhancement, competitive moat

**Problem**: The quote analytics endpoint returns empty `top_win_factors`. This data could help contractors understand WHY quotes are accepted or rejected, enabling better pricing strategy.

**Proposed Work**:
1. Capture win/loss reasons from customer feedback
2. Analyze patterns (price sensitivity, timeline, scope clarity)
3. Display insights: "Your bathroom remodel quotes win 80% when under $5,000"
4. Feed into learning system

**Success Metric**: Win factor analysis available; actionable pricing insights

---

### DISC-153: Contractor Performance Dashboard Placeholder 📊 ANALYTICS (DISCOVERED)

**Source**: Code analysis - contractors.py line 431 has `# TODO: Calculate from actual quote history`
**Impact**: LOW | **Effort**: M | **Score**: 0.5
**Sprint Alignment**: Feature completeness

**Problem**: The contractor stats endpoint has placeholder logic instead of calculating real metrics from quote history (total_revenue, average_quote, win_rate).

**Current State**: Returns hardcoded/estimated values instead of actual data.

**Proposed Work**:
1. Implement proper aggregation from quotes table
2. Calculate: total quotes, win rate, avg quote value, total revenue
3. Cache for performance
4. Expose in dashboard

**Success Metric**: Accurate contractor performance metrics; contractor can track business growth

---

### Phase II Voice Control (8 tickets)

| Ticket | Title | Effort |
|--------|-------|--------|
| DISC-042 | Voice Command Interpreter Engine | L |
| DISC-043 | Continuous Listening Mode | M |
| DISC-044 | Quote Modification via Natural Language | L |
| DISC-045 | Customer & Address Memory System | M |
| DISC-046 | Prompt Tweaking & Quote Regeneration | M |
| DISC-047 | Voice Interpretation Correction UI | S |
| DISC-048 | Multi-Turn Conversational Interface | L |
| DISC-049 | Phase II Architecture & Technical Spike | M |

**Summary**: Voice-first quote workflow - speak to create, modify, and manage quotes without touching UI.

---

### Competitive Defense (3 tickets)

| Ticket | Title | Effort |
|--------|-------|--------|
| DISC-060 | RAG Learning System Implementation | L |
| DISC-061 | Category Ownership - "Voice Quote" | M |
| DISC-062 | Messaging Pivot: Learning-First Positioning | S |

**Summary**: Defensive moat against Buildxact and other competitors.

---

### Growth & Viral (2 tickets)

| Ticket | Title | Effort |
|--------|-------|--------|
| DISC-037 | Demo-to-Referral Incentive Bridge | S |
| DISC-039 | "Voice Quote" Category Positioning | M |

---

## COMPLETE - Pending Deploy

### DISC-101: LLM-as-Judge for Autonomous Cycles 🧠 INFRASTRUCTURE (COMPLETE)

**Summary**: Created evaluation framework with 5-criteria rubric (Strategic Alignment, Autonomy, Quality, Efficiency, Learning). Decision threshold: ≥4.0 auto-execute, <4.0 suggest-only. Documentation at `docs/LLM_JUDGE_FRAMEWORK.md`.

**PR**: quoted-run/DISC-101-107-108

---

### DISC-107: Session Context Continuity (HANDOFF.md) 📝 INFRASTRUCTURE (COMPLETE)

**Summary**: Created `HANDOFF.md` template for cross-session context. Structured sections: Last Session Summary, Failed & Fixed (lessons learned), Current Priorities, Watch Out For. Agents read this + git log before starting work.

**PR**: quoted-run/DISC-101-107-108

---

### DISC-108: Regression Gate Before Commits 🚦 INFRASTRUCTURE (COMPLETE)

**Summary**: Created regression gate protocol. Phase 3.5 checkpoint: pytest -x --tb=short must pass before commit. Failures logged to HANDOFF.md. Escalation path via DECISION_QUEUE.md. Documentation at `docs/REGRESSION_GATE_PROTOCOL.md`.

**PR**: quoted-run/DISC-101-107-108

---

### DISC-041: Prompt Injection Learning Optimization 🧠 BRAINSTORM (COMPLETE)

**Summary**: Learning system improvements via prompt injection approach. Design complete.

---

### DISC-073: Staging Environment & Safe Deployment Pipeline 🏗️ BRAINSTORM (COMPLETE)

**Summary**: Evaluated options. Decision: Railway Preview Environments + PostHog Feature Flags. Implementation tickets DISC-077/078/079 all DEPLOYED.

---

### DISC-085: Voice/Chat-Operated Simple CRM 💬 STRATEGIC (COMPLETE)

**Summary**: Design document complete at `/docs/DISC-085_VOICE_CRM_DESIGN.md`. Implementation tickets DISC-086 through DISC-092 all DEPLOYED.

---

### DISC-146: Founder Activity Notifications 📬 OPERATIONS (COMPLETE)

**Summary**: Comprehensive founder visibility into all Quoted activity:
- Email deliverability fix (removed emojis from subjects, added plain text alternatives)
- Quote creation notifications to founder (every real quote generated)
- Signup notifications (already existed, improved)
- Demo notifications (already existed, improved)

**Files**: `backend/services/email.py`, `backend/api/quotes.py`

---

### DISC-147: Automated Feedback Follow-up Drip 💭 RETENTION (COMPLETE)

**Summary**: Thoughtful pulse to gather product feedback from new users:
- Day 3: First impressions email
- Day 7: Workflow integration email
- Personal tone from Eddie, reply-to goes to founder
- Tracks `feedback_email_sent` on Contractor model

**Schedule**: Daily at 2pm UTC (9am EST)
**Files**: `backend/services/email.py`, `backend/services/scheduler.py`, `backend/models/database.py`

---

### DISC-148: Daily Quote Health Checks 🏥 MONITORING (COMPLETE)

**Summary**: Synthetic monitoring to catch quote generation failures before users do:
- Daily synthetic quote test via demo endpoint
- Validates line items and total returned
- Alerts founder immediately if anything fails

**Schedule**: Daily at 6am UTC (1am EST)
**Files**: `backend/services/scheduler.py`

---

### DISC-136: Try Page Analytics Gaps 📊 ANALYTICS (COMPLETE)

**Summary**: Full PostHog funnel tracking on try.html (demo page):
- `try_page_viewed` - fires on load with referrer, UTM params, gclid
- `demo_input_started` - fires when user starts typing (text mode)
- `demo_recording_started` - fires when user starts voice recording
- `demo_quote_generated` - fires on successful quote
- `demo_abandoned` - fires on page unload without generating

**Files**: `frontend/try.html`

---

### DISC-141: Google Ads Intelligence Agent 📈🤖 GROWTH (COMPLETE - Phase 1)

**Summary**: Phase 1 complete - daily marketing reports:
- `backend/services/marketing_analytics.py` - Daily metrics service
- Scheduled job: Daily at 8am UTC (3am EST)
- Email report: Signups, quotes, 7-day trend, sparkline visualization
- Config: `MARKETING_REPORTS_ENABLED` toggle

**Phase 2** requires PostHog read API key and Google Ads API credentials.

---

### DISC-142: Configure PostHog Read API Key 🔑 ANALYTICS (COMPLETE)

**Summary**: Funnel analytics endpoints deployed and working:
- Endpoints: `/api/analytics/funnel` and `/api/analytics/traffic-sources`
- Currently using database fallback
- Full 7-step funnel visibility requires `POSTHOG_READ_API_KEY` env var in Railway

---

### DISC-149: Payment Failure Email Notifications 📧 BILLING (COMPLETE)

**Summary**: Wired up `invoice.payment_failed` Stripe webhook to notify users and founder:
- User email: "Your payment failed - please update your card" with retry date and CTA
- Founder alert: Customer details with Stripe dashboard link
- Uses existing `EmailService.send_payment_failed_notification()` method

**PR**: [#39](https://github.com/eddiesanjuan/quotedIT/pull/39)

---

### DISC-151: Demo Generation Database Tracking 📊 ANALYTICS (COMPLETE)

**Summary**: Database tracking for demo quote generations enabling accurate conversion measurement:
- Added `DemoGeneration` model to track IP, transcription hash, quote metadata, UTM params
- Updated demo.py to insert records after quote generation
- Updated marketing_analytics.py to query actual count instead of hardcoded 0

**PR**: [#40](https://github.com/eddiesanjuan/quotedIT/pull/40)

---

## Closed (Previously Tracked)

See `DISCOVERY_ARCHIVE.md` for full history of 85+ deployed tickets including:
- UX Excellence Sprint (DISC-114-123, DISC-125-132, DISC-135)
- Autonomous Infrastructure (DISC-102, 104, 106)
- CRM System (DISC-085-092)
- Proposify Domination Waves 1-3
- And more...

---

*Last hygiene: 2026-01-05. File size: ~775 lines.*
