# Discovery Backlog

**Last Updated**: 2026-01-04
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
| READY | 16 |
| DISCOVERED | 15 |
| COMPLETE | 9 |
| **Active Total** | **40** |
| Archived (DEPLOYED) | 66+ |

**Autonomous AI Infrastructure**: DISC-101 COMPLETE, DISC-102-106 READY
**Agent Reliability Engineering**: DISC-107, DISC-108 COMPLETE, DISC-109 DISCOVERED
**UX Excellence Fixes**: DISC-114-123, DISC-125-130 - DEPLOYED (backlog reconciliation 2025-12-30)
**Phase II Voice Control**: DISC-042 through DISC-049 (8 tickets) - DISCOVERED, awaiting founder review
**Competitive Defense**: DISC-060 through DISC-062 - DISCOVERED

**Note**: State hygiene pending - 15 DEPLOYED tickets in file need migration to DISCOVERY_ARCHIVE.md

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

### DISC-113: "Handyman Mike" Workflow Storytelling System 🎬 CONVERSION (DEPLOYED - partial)

**Deployed**: 2025-12-30 - Time Savings Calculator component only
**Remaining**: Story-based tour, pre-seeded demo data, workflow animation, marketing assets

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

### DISC-102: Suggestions vs Updates Framework - Action Risk Classification 🛡️ INFRASTRUCTURE (READY)

**Source**: Founder Request (Eddie, 2025-12-21) - Transcript Insights Analysis
**Impact**: HIGH | **Effort**: M | **Score**: 1.5

**Problem**: Current autonomous execution is binary (execute or don't). Need risk classification.

**Risk Classification**:
- **LOW**: Internal analysis, drafts, DB reads → Auto-execute
- **MEDIUM**: Content updates, comms to known contacts → Execute + log
- **HIGH**: External comms, financial, publishing → Suggest only
- **PROHIBITED**: Security changes, credentials → Block + alert

---

### DISC-103: Smart Complexity Detection for Task Routing 🎯 INFRASTRUCTURE (READY)

**Source**: Founder Request (Eddie, 2025-12-21) - Transcript Insights Analysis
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0

**Problem**: All tasks treated similarly. Simple tasks over-engineered, complex tasks under-scoped.

**Routing**: 85%+ confidence → Execute directly | 60-85% → Checkpoints | <60% → Plan first

---

### DISC-104: Work Isolation via Git Worktrees 🌳 INFRASTRUCTURE (READY)

**Source**: Founder Request (Eddie, 2025-12-21) - Transcript Insights Analysis
**Impact**: HIGH | **Effort**: L | **Score**: 2.0

**Problem**: Tasks execute in shared context. Failures contaminate other work. Can't run parallel.

**Solution**: Each task gets isolated git worktree. Merge only on success. Easy rollback.

---

### DISC-105: Learning Memory System - Dual Architecture 🧠 INFRASTRUCTURE (READY)

**Source**: Founder Request (Eddie, 2025-12-21) - Transcript Insights Analysis
**Impact**: HIGH | **Effort**: XL | **Score**: 1.0

**Problem**: Limited cross-session learning. Each cycle starts without context of past successes/failures.

**Architecture**: Graph Memory (entities, relationships) + Semantic RAG (past decisions, outcomes)

---

### DISC-106: Safety Net Architecture - Defense in Depth 🛡️ INFRASTRUCTURE (READY)

**Source**: Founder Request (Eddie, 2025-12-21) - Transcript Insights Analysis
**Impact**: HIGH | **Effort**: L | **Score**: 2.0

**Problem**: Autonomous systems need defense-in-depth.

**Five Layers**: Cooldowns, Threshold Scores, Version History, Human Override, Anomaly Detection

---

### DISC-114: Add Terms/Privacy to Quick Signup Form ⚖️ LEGAL (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: S | **Score**: 4.0
**Sprint Alignment**: Critical legal exposure fix
**Deployed**: 2025-12-27 | **PR**: #22

**Implementation Summary**: Added Terms/Privacy links to `/start` signup form with required acknowledgment checkbox.

---

### DISC-115: Display Loyalty Tier Badges on CRM Cards 🏅 CRM (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: MEDIUM | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: CRM polish for retention
**Deployed**: 2025-12-27 | **PR**: #22

**Implementation Summary**: Added color-coded loyalty tier badges to CRM cards (list and detail views).

---

### DISC-116: Add Outstanding Invoices Dashboard Widget 💰 DASHBOARD (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: S | **Score**: 4.0
**Sprint Alignment**: Revenue visibility
**Deployed**: 2025-12-27 | **PR**: #22

**Implementation Summary**: Added Outstanding Invoices widget to dashboard showing count, total amount, and oldest overdue.

---

### DISC-117: Send Quote Rejection Notifications Always 📧 QUOTES (DEPLOYED)

**Deployed**: Already implemented (verified 2025-12-30) - Rejection email sent in share.py line 298

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: MEDIUM | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: User feedback improvement

**Problem**: Rejection email only sent if customer provides a reason. Silent rejections = missed market intelligence. Contractors don't know a quote was rejected.

**Proposed Work**:
1. Modify rejection handler to always send notification email
2. Email content: "Quote rejected" with or without reason
3. Track rejection analytics

**Success Metric**: 100% of rejections trigger notification

---

### DISC-118: Add og:image Tags to Blog Articles 🖼️ SEO (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: MEDIUM | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: SEO & social sharing
**Deployed**: 2025-12-27 | **PR**: #22

**Implementation Summary**: Added og:image meta tags to all 8 blog articles for social media preview images.

---

### DISC-119: Mobile WCAG 2.5.5 Touch Target Compliance 📱 ACCESSIBILITY (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Critical accessibility fix - legal risk
**Deployed**: 2025-12-27 | **PR**: #22

**Implementation Summary**: Added 44x44px minimum touch targets via CSS for all interactive elements at mobile breakpoints.

---

### DISC-120: Unified Auth Flow with Legal Compliance 🔐 AUTH (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Critical legal and UX fix
**Deployed**: 2025-12-27 | **PR**: #22

**Implementation Summary**: Added password strength indicator and legal compliance to auth flows.

---

### DISC-121: Learning System Outcome Loop (Win/Loss Tracking) 📊 LEARNING (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: L | **Score**: 1.5
**Sprint Alignment**: Core moat enhancement
**Deployed**: 2025-12-27 | **PR**: #22

**Implementation Summary**: Added outcome tracking (won/lost), win rate per category in Pricing Brain, outcome boost/penalty for learning. Database tracks won_count, lost_count, win_rate per category.

---

### DISC-122: Delete Line Item with Learning 🗑️🧠 BUG (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-27) - Testing
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Core functionality + learning fix
**Deployed**: 2025-12-27 | **PR**: #22

**Implementation Summary**: Added delete button to line items with tracking for learning. Deleted items are tracked in corrections for future quote improvement.

---

### DISC-123: Quantity/Unit Edits Should Trigger Learning + Save 🧠 BUG (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-27) - Testing
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Core learning system fix
**Deployed**: 2025-12-27 | **PR**: #22

**Implementation Summary**: Quantity/unit changes now tracked in corrections and included in learning prompt. Format: `[qty: X → Y, unit: 'A' → 'B']`

---

### DISC-126: Customer Identification UX - Bulletproof Matching 🎯 VOICE/CRM (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-28) - Voice workflow friction concern
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Voice-first UX excellence, CRM reliability
**Deployed**: 2025-12-29 | **PR**: #25

**Implementation Summary**:
- Phone-based customer matching with confidence scoring
- Auto-link on high confidence (≥0.95), confirmation modal on moderate (0.70-0.95)
- Fuzzy name matching via Levenshtein distance
- Safe DOM manipulation (no innerHTML for user data)

**Backend Changes**:
- `customer_service.py`: `find_customer_matches()`, `link_quote_to_customer_explicit()`, `get_recent_customers()`
- `customers.py`: POST `/customers/match`, GET `/customers/recent`
- `quotes.py`: POST `/quotes/{id}/link-customer`, POST `/quotes/{id}/check-customer-match`

**Frontend Changes**:
- Customer Match Confirmation Modal
- Repeat Customer Picker Modal
- Customer link status indicator ("✓ Linked" badge)

**Production Verified**: Phone matching correctly deduplicates customers (tested with same phone, different names → single customer with 2 quotes)

---

### DISC-127: Logo Aspect Ratio Squished on Upload 🐛 BUG (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-28) - User testing
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Sprint Alignment**: Professional branding - logos must look correct on quotes
**Deployed**: 2025-12-28 | **PR**: #26

**Implementation Summary**: Fixed logo aspect ratio with `object-fit: contain` in UI and proportional scaling in PDF output.

---

### DISC-128: Founder Notifications for Signups & Demo Usage 📬 GROWTH (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-29)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Early-stage founder visibility into user acquisition
**Deployed**: 2025-12-30

**Implementation Summary**:
- `send_founder_signup_notification()` - Emails on new account creation (email, business name, trade)
- `send_founder_demo_notification()` - Emails on demo quote generation (job description, total, line items, IP)
- Integrated into auth.py (signup) and demo.py (quote generation)
- Sends to `eddie@granular.tools` via Resend

**Note**: Emails landing in spam - may need SPF/DKIM review for improved deliverability

---

### DISC-131: Demo Page Dictation Examples 🎤 CONVERSION (DEPLOYED)

**Deployed**: 2025-12-30 - Added "What Should You Say?" section with 3 example prompts (Simple, Detailed, Pro Tip)

**Source**: Founder Request (Eddie, 2025-12-29)
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Sprint Alignment**: Demo conversion optimization

**Problem**: Most users don't realize the level of detail they can provide when dictating a quote. They give minimal input ("bathroom remodel") when they could give rich context (customer name, address, specific materials, timeline, etc.) that would produce more accurate quotes and better demonstrate the product's value.

**Proposed Work**:
1. Add 2-3 example dictation prompts on demo.html
2. Show range from simple ("Install ceiling fan in bedroom") to detailed ("Install 52-inch Hunter ceiling fan for Mrs. Johnson at 123 Oak Street, includes running new wire from switch, budget around $400, can start Tuesday")
3. Position examples near or below the voice input area
4. Make examples clickable to auto-fill as starter text (optional)

**Success Metric**: Higher quality demo inputs; demo-to-signup conversion rate improvement

---

### DISC-132: Interactive Clarifying Questions 🎯 PRODUCT (DEPLOYED)

**Deployed**: 2025-12-30 - Backend /api/demo/regenerate endpoint, frontend interactive inputs with regenerate button

**Source**: Founder Request (Eddie, 2025-12-29)
**Impact**: HIGH | **Effort**: L | **Score**: 1.5
**Sprint Alignment**: Core product differentiation, learning system enhancement

**Problem**: The AI generates "Clarifying Questions" at the bottom of each quote, but they're currently static/informational only. Users can't answer them to improve the quote. This is a missed opportunity for accuracy improvement and learning system enhancement.

**Vision**: Transform static questions into an interactive refinement loop. User answers questions → quote regenerates with additional context → responses feed into learning system for future quotes.

**Proposed Work**:
1. Make clarifying questions section interactive (input fields or buttons)
2. Allow users to answer each question with text input
3. On submit, regenerate quote with answers added to original context
4. Track which questions get answered and what answers are given
5. Feed Q&A pairs into learning system for future quote generation
6. Show before/after comparison (optional: "Your answers improved this quote")

**Example Flow**:
> AI asks: "What brand of faucet do you want to install?"
> User answers: "Moen Align in brushed nickel"
> Quote regenerates with specific Moen Align pricing instead of generic faucet

**Success Metric**: Quote accuracy improvement (fewer post-generation edits); learning system captures Q&A pairs; user engagement with clarifying questions

---

### DISC-130: PDF Line Spacing Polish - Improved Text Readability 📄 UX (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-29)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Professional polish for customer-facing documents
**Deployed**: 2025-12-30 | **PR**: #29

**Implementation Summary**:
Improved line spacing across PDF text sections for better readability:
- QuoteBody: leading 18→20pt (1.82x ratio for 11pt font)
- QuoteBodyLight: leading 18→20pt with spaceAfter 4→6pt
- LineItem ItemCell: leading 14→16pt for multi-line descriptions
- FinePrint: leading 11→13pt for comfortable legal text reading

Changes apply to all PDFs (quotes, invoices, demo) while maintaining compact template behavior.

---

### DISC-129: Demo Premium Template - Ultra-Polished First Impression ✨ CONVERSION (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-29)
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Demo conversion optimization - first impression is everything
**Deployed**: 2025-12-29

**Implementation Summary**:
- Created `DemoPremiumLogo` Flowable class with navy hexagon + gold diamond geometric design
- Added `demo_premium` template to PDF_TEMPLATES with deep navy header (#1a365d) and gold accents (#d69e2e)
- Updated demo API endpoints to use premium template
- Typography: "YOUR BUSINESS" with letter-spacing + "Professional Services" tagline

**Outcome**: Demo PDFs now render with sophisticated agency-quality placeholder design

---

### DISC-125: Blog Article Formatting Fixes 📝 UX (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-28) - Blog QA review
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Sprint Alignment**: Professional content presentation for SEO/credibility

**Problem**: Blog articles have two formatting issues that hurt polish:
1. **Blank CTA buttons**: "Try Now" buttons in article body appear empty/blank (no text visible)
2. **TOC overlap**: The "In This Guide" table of contents covers too much of the top content area, obscuring article text

**Note**: Overall design looks good - just these specific polish items need fixing.

**Proposed Work**:
1. Find and fix blank CTA buttons in blog article templates - add "Try Now" or appropriate text
2. Adjust TOC positioning/sizing to not obscure article content
3. Test on multiple blog articles to ensure consistent fix
4. Verify mobile rendering of both fixes

**Success Metric**: Blog CTA buttons display text; TOC doesn't obscure article content

---

### DISC-134: Social Login (Google, Apple, etc.) 🔐 AUTH (READY)

**Source**: Founder Request (Eddie, 2025-12-30)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Reduces signup friction, industry-standard auth option

**Problem**: Currently users must use magic link (email-based) authentication. While frictionless, many users expect and prefer OAuth/social login options they use everywhere else. "Sign in with Google" is often perceived as faster and more trustworthy than entering an email address.

**Proposed Work**:
1. **Google OAuth Integration** - Add "Sign in with Google" button to auth flow (highest priority, most common)
2. **Apple Sign In** - Add Apple OAuth for iOS users (required for App Store if we ever go mobile)
3. **UI Updates** - Auth form redesign with social buttons + "or continue with email" divider
4. **Account Linking** - Handle edge case where user has both email and social accounts
5. **PostHog Tracking** - Track auth method chosen to measure adoption

**Technical Notes**:
- Google: OAuth 2.0 via Google Cloud Console
- Apple: Sign in with Apple SDK
- Backend: Store OAuth provider + provider_id in contractor model
- Consider: passkey support for future (WebAuthn)

**Success Metric**: 30%+ of new signups use social login within 30 days of launch

---

### DISC-135: Post-Job Pricing Reflection Loop 💰🧠 LEARNING (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-30)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Learning system excellence, Anthropic showcase quality

**Problem**: Current learning captures quote acceptance/rejection (DISC-121), but not actual job profitability. A quote can be accepted but leave money on the table, or be accepted but take longer than expected. The contractor knows this after the job - we should capture it.

**The Insight**: Contractors always know in hindsight "I should have charged more for that" or "that was perfect pricing." This is the most valuable signal possible for the learning system - real profit margin feedback, not just acceptance rates.

**Proposed Work**:
1. **Post-Invoice Prompt** - After invoice is marked paid (or 7 days after creation), trigger reflection UI
2. **Simple 3-Option UI** - "How did this pricing feel?" → "Too Low (left money)" | "Just Right" | "Too High (lucky it sold)"
3. **Optional Numeric Input** - "What would you price this at next time?" → captures ideal price
4. **Learning Integration** - Feed reflection data into category-specific pricing adjustments
5. **Dashboard Insight** - Show pattern: "Your bathroom remodels tend to be underpriced by ~15%"

**Why This Is Unique**:
- No competitor does this - they all stop at "quote sent"
- Creates compounding accuracy over time
- Contractors WANT to tell you this (it's cathartic)
- Anthropic showcase: Human-AI collaboration at its finest

**Technical Notes**:
- New table: `pricing_reflections` (invoice_id, feeling, ideal_price, created_at)
- Trigger: Invoice status change to "paid" or age > 7 days
- Learning weight: Higher than acceptance signal (actual outcome vs. customer behavior)

**Success Metric**: 40%+ reflection completion rate; measurable improvement in pricing confidence scores for categories with 5+ reflections

---

### DISC-136: Try Page Analytics Gaps 📊 ANALYTICS (COMPLETE)

**Source**: Founder Request (Eddie, 2025-12-30)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: CRITICAL - 80 clicks, 0 conversions, blind to funnel

**Problem**: try.html (demo page) had no page view event. Couldn't see funnel.

**Implementation (2025-12-31)**:
- ✅ `try_page_viewed` - fires on load with referrer, UTM params, gclid
- ✅ `demo_input_started` - fires when user starts typing (text mode)
- ✅ `demo_recording_started` - fires when user starts voice recording
- ✅ `demo_quote_generated` - fires on successful quote with total, line items
- ✅ `demo_abandoned` - fires on page unload if left without generating

**Full Funnel Now Visible**:
Landing → Try Page View → Input/Recording Started → Quote Generated (or Abandoned)

**Files Modified**: `frontend/try.html`

---

### DISC-137: Exit Intent Survey Reporting 📧 ANALYTICS (READY)

**Source**: Founder Request (Eddie, 2025-12-30)
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Sprint Alignment**: Understand why users leave

**Problem**: Exit intent survey data goes to PostHog but founder has to manually check. Need proactive reporting.

**Current State**:
- `exit_survey_completed` captures reasons and other_text
- Data exists but requires PostHog dashboard login

**Proposed Work**:
1. Daily email digest: "Yesterday's Exit Survey Summary"
   - Count by reason (Not my industry, Too expensive, etc.)
   - Any verbatim "Other" responses (most valuable)
   - Trend vs. previous day/week
2. Instant alert for specific keywords ("bug", "broken", "doesn't work")
3. Add to founder notification service (alongside DISC-128)

**Success Metric**: Founder receives daily exit survey digest; can read user feedback without logging into PostHog

---

### DISC-138: Google Ads → Conversion Funnel Dashboard 📈 ANALYTICS (READY)

**Source**: Founder Request (Eddie, 2025-12-30)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Understand paid acquisition performance

**Problem**: 80 ad clicks, 4000 impressions, 0 conversions. No visibility into where users drop off.

**Proposed Work**:
1. **PostHog Dashboard**: Create "Acquisition Funnel" dashboard
   - Landing page views (by UTM source)
   - CTA clicks (Try Demo vs Sign Up)
   - Try page views
   - Demo generation attempts
   - Demo completions
   - Signup attempts
   - Signup completions
2. **Conversion Tracking Integration**
   - Verify Google Ads conversion pixel fires on signup
   - Add conversion tracking for demo completion (micro-conversion)
3. **Funnel Visualization**
   - Step-by-step drop-off visualization
   - Segment by ad campaign, device, time of day

**Success Metric**: Can answer "where do ad visitors drop off?" in 30 seconds

---

### DISC-139: Real-Time Traffic Spike Alerts 🚨 MONITORING (READY)

**Source**: Founder Request (Eddie, 2025-12-30)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Don't miss viral moments

**Problem**: If Quoted goes viral (HN, Reddit, tweet), founder needs to know immediately to:
- Monitor for issues
- Engage with community
- Scale infrastructure if needed

**Proposed Work**:
1. **Hourly traffic check** (backend scheduler)
   - Compare current hour page views to 7-day average
   - If 3x+ normal: send founder alert
2. **Demo generation spike alert**
   - If 5+ demo quotes in an hour (vs. typical ~1)
   - Immediate Slack/email notification
3. **Signup velocity alert**
   - Any signup triggers notification (DISC-128 already does this)
   - But also alert on 3+ signups in an hour = potential viral
4. **Infrastructure pre-emptive warning**
   - Monitor Railway metrics
   - Alert if approaching limits

**Success Metric**: Founder knows within 1 hour if traffic spikes 3x or more

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

### DISC-141: Google Ads Intelligence Agent 📈🤖 GROWTH (COMPLETE - Phase 1)

**Source**: Founder Request (Eddie, 2025-12-31)
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Paid acquisition optimization, autonomous marketing

**Problem**: 80 clicks, 4000 impressions, 0 conversions. No automated system to:
- Track ad spend vs. conversions in real-time
- Detect when ads are underperforming
- Recommend bid/targeting adjustments
- Alert when cost-per-acquisition is too high

**PHASE 1 COMPLETE** (2025-12-31):
- ✅ `backend/services/marketing_analytics.py` - Daily metrics service
- ✅ Scheduled job: Daily marketing report at 8am UTC (3am EST)
- ✅ Email report: Signups, quotes, 7-day trend, sparkline visualization
- ✅ Config: `MARKETING_REPORTS_ENABLED` toggle

**First report**: Tomorrow 8am UTC (3am EST)

**PHASE 2 (Pending - requires API keys)**:
- PostHog read API key (`POSTHOG_READ_API_KEY=phx_*`) - enables funnel tracking
- Google Ads API integration - enables spend correlation

**PHASE 3 (Future)**:
- Automated bid/targeting recommendations
- Anomaly detection alerts
- Weekly strategy memos

**Success Metric**: CPA (cost per acquisition) improves 50% within 30 days; founder receives actionable recommendations, not just data

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

### DISC-142: Configure PostHog Read API Key 🔑 ANALYTICS (COMPLETE)

**Source**: DISC-138 deployment verification (2025-01-04)
**Impact**: LOW | **Effort**: XS | **Score**: 3.0

**Problem**: The funnel analytics endpoints (DISC-138) are deployed and working, but return `posthog_configured: false`. Full funnel visibility requires a PostHog Read API key.

**Proposed Work**:
1. Generate PostHog Personal API Key with read-only access from PostHog dashboard
2. Add `POSTHOG_READ_API_KEY` environment variable to Railway production
3. Verify funnel endpoint returns real data: `GET /api/analytics/funnel?days=7`

**Current State**:
- Endpoints work: `/api/analytics/funnel` and `/api/analytics/traffic-sources`
- Database fallback active (only shows signups/quotes, not page views)
- Full funnel (landing → CTA → demo → signup) requires PostHog API

**Success Metric**: `posthog_configured: true` in API response; full 7-step funnel visible.

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

## Closed (Previously Tracked)

See `DISCOVERY_ARCHIVE.md` for full history of 45+ deployed tickets including:
- CRM System (DISC-085-092)
- Learning System (DISC-052, DISC-054, DISC-068)
- PDF & Templates (DISC-028, DISC-067, DISC-072)
- Infrastructure (DISC-077, DISC-078, DISC-079)
- And more...

---

*File size target: <800 lines. Current: ~200 lines. If this file exceeds 500 lines, run state hygiene.*
