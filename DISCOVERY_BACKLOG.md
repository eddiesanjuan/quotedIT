# Discovery Backlog

**Last Updated**: 2025-12-30
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
| DISCOVERED | 15 |
| COMPLETE | 6 |
| **Active Total** | **31** |
| Archived (DEPLOYED) | 65+ |

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
| DISC-132 | Interactive Clarifying Questions for Demo | 2025-12-30 |
| DISC-131 | Demo Page Dictation Examples | 2025-12-30 |
| DISC-113 | Time Savings Calculator (partial) | 2025-12-30 |
| DISC-128 | Founder Notifications for Signups & Demo Usage | 2025-12-30 |
| DISC-130 | PDF Line Spacing Polish - Improved Text Readability | 2025-12-30 |

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

## DISCOVERED - Awaiting Founder Review

### DISC-133: Clarification Answers Feed Into Learning System 🧠 LEARNING (DISCOVERED)

**Source**: DISC-132 Implementation Discovery (2025-12-30)
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Learning system enhancement, Anthropic showcase quality

**Problem**: When users answer clarifying questions and regenerate quotes, those Q&A pairs contain valuable pricing context that should be captured by the learning system. Currently:
- Demo mode: `/api/demo/regenerate` uses answers but doesn't persist them
- Auth mode: `/quotes/generate-with-clarifications` saves the quote but not the clarifications
- Learning service: `get_quote_refinement_prompt` handles corrections but not clarification context

**Proposed Work**:
1. Add `clarification_context` field to quote model (JSON with Q&A pairs)
2. Update `/quotes/generate-with-clarifications` to save clarifications with quote
3. Create `get_clarification_learning_prompt()` in learning service
4. Integrate clarification learning when quote outcomes are tracked (accepted/rejected)
5. Use clarification patterns to improve future question generation

**Why This Matters**:
- Clarification answers are *explicit* user intent (vs. implicit corrections)
- "How many square feet?" → "About 400" is valuable sizing context
- "Is this interior or exterior?" → "Interior, second floor" informs pricing
- This data compounds across all users to improve question quality

**Success Metric**: Learning statements include clarification-derived patterns; question relevance score improves

---

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
