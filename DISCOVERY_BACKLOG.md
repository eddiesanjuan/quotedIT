# Discovery Backlog

**Last Updated**: 2025-12-28
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
| READY | 18 |
| DISCOVERED | 14 |
| COMPLETE | 6 |
| **Active Total** | **38** |
| Archived (DEPLOYED) | 46+ |

**Autonomous AI Infrastructure**: DISC-101 COMPLETE, DISC-102-106 READY
**Agent Reliability Engineering**: DISC-107, DISC-108 COMPLETE, DISC-109 DISCOVERED
**UX Excellence Fixes**: DISC-114-121 (8 tickets) - READY, quick wins + big gaps
**Phase II Voice Control**: DISC-042 through DISC-049 (8 tickets) - DISCOVERED, awaiting founder review
**Competitive Defense**: DISC-060 through DISC-062 - DISCOVERED

---

## Recently Deployed (Last 5)

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-124 | Quote Email Template Audit | 2025-12-28 |
| DISC-100 | Pricing Intelligence for Novices Messaging | 2025-12-21 |
| DISC-099 | Direct Founder Support Channel | 2025-12-19 |
| DISC-098 | Simplified Single-Tier Pricing ($9/mo) | 2025-12-19 |
| DISC-097 | Landing Page CRM Feature Messaging | 2025-12-18 |

*Full deployment history: See DISCOVERY_ARCHIVE.md*

---

## READY - Approved for Implementation

### DISC-113: "Handyman Mike" Workflow Storytelling System 🎬 CONVERSION (READY)

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

### DISC-114: Add Terms/Privacy to Quick Signup Form ⚖️ LEGAL (READY)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: S | **Score**: 4.0
**Sprint Alignment**: Critical legal exposure fix

**Problem**: The `/start` quick signup form lacks Terms of Service and Privacy Policy links. Users completing signup via this path have no legal acknowledgment, exposing Quoted to compliance risk.

**Proposed Work**:
1. Add Terms/Privacy checkbox or link text below password field in `/start` form
2. Ensure consistent legal language with `/app` signup form
3. Make checkbox required before form submission

**Success Metric**: 100% of signups have Terms/Privacy acknowledgment

---

### DISC-115: Display Loyalty Tier Badges on CRM Cards 🏅 CRM (READY)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: MEDIUM | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: CRM polish for retention

**Problem**: Backend calculates customer loyalty tiers (new, returning, loyal, VIP) but frontend doesn't display them. Users can't see customer value at a glance.

**Proposed Work**:
1. Add tier badge component (color-coded: gray/blue/gold/purple)
2. Display badge on customer cards in CRM list view
3. Show tier on customer detail view

**Success Metric**: Loyalty tiers visible on all customer cards

---

### DISC-116: Add Outstanding Invoices Dashboard Widget 💰 DASHBOARD (READY)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: S | **Score**: 4.0
**Sprint Alignment**: Revenue visibility

**Problem**: Backend has `/api/invoices?status=outstanding` endpoint but no UI aggregates outstanding invoices. Users can't see total money owed at a glance.

**Proposed Work**:
1. Add "Outstanding Invoices" card to dashboard
2. Show: count, total amount, oldest overdue
3. Link to filtered invoice list

**Success Metric**: Dashboard shows outstanding invoice total

---

### DISC-117: Send Quote Rejection Notifications Always 📧 QUOTES (READY)

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

### DISC-118: Add og:image Tags to Blog Articles 🖼️ SEO (READY)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: MEDIUM | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: SEO & social sharing

**Problem**: Blog articles missing og:image meta tags. Shared links on social media show no preview image, reducing click-through rates.

**Proposed Work**:
1. Create 1200x630 preview image template for blog posts
2. Add og:image meta tag to all blog articles
3. Use article-specific or category-based images

**Success Metric**: All blog articles have og:image tags

---

### DISC-119: Mobile WCAG 2.5.5 Touch Target Compliance 📱 ACCESSIBILITY (READY)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Critical accessibility fix - legal risk

**Problem**: 78% of mobile interactive elements fail WCAG 2.5.5 minimum 44x44px touch target requirement. This includes nav links (73x23px, 30x23px), tour buttons (74x16px), and example chips (0x0px). Creates accessibility lawsuit risk.

**Proposed Work**:
1. Audit all mobile touch targets with JS measurement
2. Add 44px minimum CSS for all interactive elements
3. Convert desktop nav to hamburger menu on mobile (375px breakpoint)
4. Fix 0x0px hidden elements (example chips)
5. Add 375px breakpoint to all pages

**Success Metric**: 100% of touch targets meet 44x44px minimum at 375px viewport

---

### DISC-120: Unified Auth Flow with Legal Compliance 🔐 AUTH (READY)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Critical legal and UX fix

**Problem**: Two different signup paths (`/start` quick vs `/app` detailed) with different fields and different legal exposure. Confusing UX and compliance risk.

**Proposed Work**:
1. Merge `/start` and `/app` signup into single unified flow
2. Ensure Terms/Privacy acknowledgment on all paths
3. Add progressive disclosure (basic info → business details)
4. Add password strength indicator
5. Consider Google OAuth for faster signup

**Success Metric**: Single signup path with consistent legal compliance

---

### DISC-121: Learning System Outcome Loop (Win/Loss Tracking) 📊 LEARNING (READY)

**Source**: Founder Request (Eddie, 2025-12-27) - UX Excellence Audit
**Impact**: HIGH | **Effort**: L | **Score**: 1.5
**Sprint Alignment**: Core moat enhancement

**Problem**: Learning system captures corrections but doesn't track quote outcomes (won/lost). Can't learn which pricing approaches lead to closed deals vs lost customers.

**Proposed Work**:
1. Add quote outcome tracking (won/lost/no_response)
2. Persist outcome with quote record
3. Apply outcome boost to learnings from won quotes
4. Apply negative weight to learnings from lost quotes
5. Add "Why did they reject?" prompt on lost quotes
6. Surface win rate by category in Pricing Brain

**Success Metric**: Outcome data influences future quote generation; win rate visible per category

---

### DISC-122: Delete Line Item with Learning 🗑️🧠 BUG (READY)

**Source**: Founder Request (Eddie, 2025-12-27) - Testing
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Core functionality + learning fix

**Problem**: When editing a quote, there's no way to delete a line item. More importantly, deletions are learning opportunities - if a user removes a "Materials" line item because they prefer to bake material costs into labor, the AI should learn this preference for future quotes.

**Example Use Case**:
> Quote generates "Materials - $150" line item. User deletes it and explains "I bake material costs into my labor rates, don't show materials separately." Future quotes in that category should NOT include separate materials line items.

**Proposed Work**:
1. Add delete (trash) icon button to each line item row in edit mode
2. On delete, prompt: "Why are you removing this item?" (optional but encouraged)
3. Generate learning statement from deletion + reason
4. Example learning: "For [category], contractor prefers NOT to show materials as separate line item - bake into labor costs"
5. Update quote total after deletion
6. Apply learning to future quotes in same category

**Success Metric**:
- Users can delete any line item
- Deletions with reasons create learning statements
- Future quotes reflect learned preferences (e.g., no separate materials line)

---

### DISC-123: Quantity/Unit Edits Should Trigger Learning + Save 🧠 BUG (READY)

**Source**: Founder Request (Eddie, 2025-12-27) - Testing
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Core learning system fix

**Problem**: Adjusting the quantity or units of a line item doesn't trigger AI learning and doesn't show as an edit requiring "Save". Price corrections are learned, but quantity/unit corrections are silently ignored. This breaks the learning loop for a common edit type.

**Proposed Work**:
1. Track quantity/unit changes as editable fields (dirty state)
2. Show "Save" button when quantity/unit is modified
3. On save, generate learning statement for quantity/unit corrections
4. Example learning: "For drywall patching, customer corrected quantity from 3 patches to 5 patches"
5. Apply learning to future quotes in same category

**Success Metric**: Quantity/unit edits trigger save flow and create learning statements

---

### DISC-125: Blog Article Formatting Fixes 📝 UX (READY)

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
