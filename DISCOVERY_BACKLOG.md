# Discovery Backlog

**Last Updated**: 2025-12-04
**Source**: `/quoted-discover` autonomous discovery cycles

---

## Status Legend

| Status | Meaning |
|--------|---------|
| **DEPLOYED** | Implemented and live in production |
| **COMPLETE** | Implemented, pending deploy |
| **READY** | Approved, ready for implementation |
| **DISCOVERED** | Proposed, awaiting founder review |

To approve: Change status from DISCOVERED → READY

---

## Summary

| Status | Count |
|--------|-------|
| DEPLOYED | 21 |
| COMPLETE | 2 |
| READY | 4 |
| DISCOVERED | 14 |
| **Total** | **41** |

---

## Ready for Implementation

### DISC-013: Animation Walkthrough Distribution Strategy (READY)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: L | **Score**: 0.75
**Sprint Alignment**: BETA_SPRINT targets 300 animation views × 10% = 30 users

**Problem**: Animation walkthrough built but no distribution strategy. Animation page is invisible.

**Proposed Work**:
1. Create /demo-promo landing variant focused on animation
2. Message: "See voice-to-quote in 60 seconds - no signup"
3. Add tracking: utm_source parameter for channel attribution
4. Start with 3 contractor subreddits + 2 Facebook groups
5. Target: 300 animation views in 14 days

**Success Metric**: 300 animation views; animation→signup conversion baseline

---

### DISC-014: Buildxact Competitive Defense (READY) ⚠️ Strategic

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: L | **Score**: 0.75
**Sprint Alignment**: Long-term - existential threat if not addressed in 2025

**Problem**: Main competitor Buildxact could add voice interface in 6-12 months.

**Proposed Work**:
1. Accelerate learning system development: move RAG from backlog to Q1 priority
2. After 100 users, plan vertical integrations (QuickBooks, Jobber) for lock-in
3. Emphasize "learns YOUR pricing" (personal moat) over "has voice" (replicable)

**Success Metric**: RAG implemented Q1 2025; at least 1 integration partnership

---

### DISC-028: PDF Quote Template Library (READY) 🎨 Premium Differentiation

**Source**: Founder's Wife (2025-12-03)
**Impact**: HIGH | **Effort**: L | **Score**: 0.75
**Sprint Alignment**: Premium tier value proposition

**Problem**: All PDF quotes look identical. No visual customization without logo.

**Proposed**: 8-10 professional template styles (Classic, Modern Minimal, Bold Professional, Elegant, Technical, Friendly, Craftsman, Corporate) + accent color picker for Pro tier.

**Success Metric**: 60%+ Pro users select non-default template

---

## Discovered (Awaiting Review)

### DISC-023: Contractor Community Outreach Plan 🚀 FOUNDER ACTION

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5

**Problem**: Product built but no distribution strategy. 5 users, need 95 more.

**Proposed Work (FOUNDER REQUIRED)**:
1. Reddit: Post in r/contractors, r/Construction, r/smallbusiness
2. Facebook Groups: 5 contractor groups
3. Blog/SEO: Create contractor-focused landing page

**Success Metric**: 200+ demo views; 20+ signups from community posts

---

### DISC-025: Landing Page Segment A/B Test 🧪 STRATEGIC

**Source**: Strategy Discovery Agent
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0

**Problem**: Segment B (ballpark-only) beats Segment A on every metric, but messaging serves neither.

**Proposed**: Create TWO landing pages, split 80/20 Segment B/A, measure and pick winner.

---

### DISC-026: Pricing A/B Test ($19 vs $49) 🧪 STRATEGIC

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5

**Problem**: Recent price drop signals value perception uncertainty. At 90%+ margin, pricing = positioning.

**Proposed**: A/B test value-based ($49) vs impulse ($19) pricing.

---

### DISC-027: LinkedIn Founder Content Blitz 🚀 FOUNDER ACTION

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5

**Proposed**: 6 daily LinkedIn posts with demo video, customer stories, urgency messaging.

**Success Metric**: 5,000+ impressions; 15-20 signups from LinkedIn

---

### DISC-029: Demo Quote Screenshot Sharing ⚡ QUICK WIN (DISCOVERED)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Converts 300+ demo sessions into viral acquisition channel

**Problem**: Demo users generate quotes but have no way to share them. Zero viral coefficient from demo sessions. Demo quotes disappear without creating any word-of-mouth.

**Proposed Work**:
1. Add "Share This Quote" button to demo results
2. Pre-populated social text: "Just generated a $X quote in 30 seconds with @QuotedApp - voice to quote is wild"
3. Screenshot preview for sharing
4. One-click share to LinkedIn, Twitter, or copy shareable image
5. Track shares via utm_source=demo_share

**Success Metric**: 20%+ demo users share (60 shares from 300 demos); 10% click-through = 6 additional signups

---

### DISC-030: Email Signature Viral Acceleration ⚡ QUICK WIN (DISCOVERED)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Activates existing 5 users as acquisition channel, multiplies founder network reach 10x

**Problem**: Email signature referral exists (DISC-021) but requires users to manually find it. Too much friction = low adoption. Referral program exists but not connected to daily workflow.

**Proposed Work**:
1. Auto-generate HTML email signature on first quote creation (not just available in settings)
2. Show preview modal: "Want more referrals? Add this to your email signature"
3. One-click "Copy to Clipboard" with instructions for Gmail/Outlook
4. Include in onboarding celebration
5. Pre-fill with user's referral code automatically

**Success Metric**: 60%+ users copy signature (vs current ~5%); each active user sends 20-50 emails/week = 300-500 signature impressions; 2-3% click-through = 6-15 signups from existing 5 users

---

### DISC-031: Voice Recording Fallback & Recovery (DISCOVERED)

**Source**: Product Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Voice failure is likely top cause of demo/first-quote abandonment. Fixing this could increase activation to 60% target.

**Problem**: Voice input has no error recovery or fallback when browser Speech API fails (iOS Safari, privacy-blocked microphones, network issues). Users hit dead-end and abandon if voice fails.

**Proposed Work**:
1. Pre-check Speech API availability with friendly warning if unsupported
2. "Having trouble? Switch to text input" button during voice recording
3. Auto-detect 10s silence or errors and offer text alternative
4. Add browser compatibility badge ("Voice works best on Chrome/Edge")

**Success Metric**: Reduce quote-generation-started → quote-abandoned rate by 20%; voice-attempt → text-fallback conversion rate 40%+

---

### DISC-032: Autosave Quote Drafts (Local Storage) (DISCOVERED)

**Source**: Product Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Removes anxiety around losing work, reduces rage-quit abandonment during critical first-quote experience

**Problem**: Users lose entire quote if they accidentally close tab, navigate away, or experience browser crash during editing. No draft recovery means they must restart from voice/text input.

**Proposed Work**:
1. Implement localStorage autosave every 10 seconds during quote generation/editing
2. On app load, detect unsaved draft and show recovery modal: "You have an unsaved quote from 15 minutes ago. Restore it?"
3. Store transcription text, generated quote data, and edit state
4. Clear draft after successful PDF download or explicit "Discard" action

**Success Metric**: Recovery modal shown 5-10% of sessions (proves value); quote-edit → PDF-download completion rate increases 15%

---

### DISC-033: Reddit Contractor Launch Post 🚀 FOUNDER ACTION (READY)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: 410K+ contractors on Reddit, single post could deliver 20%+ of beta goal

**Problem**: 410K+ contractors on Reddit, zero awareness of Quoted. Warm audience that complains daily about quoting friction. Demo ready but not distributed.

**Proposed Work**:
1. Craft founder-story Reddit post for r/contractors, r/Construction, r/smallbusiness
2. Format: "I built a voice-to-quote tool because I was tired of 30-minute spreadsheets - would love beta feedback"
3. Include demo link, emphasize learning system
4. Post during peak hours (Tuesday-Thursday 9am-11am EST)
5. Respond to every comment within 1 hour

**Success Metric**: 5,000+ impressions; 3% click demo (150 views); 15% convert = 22 signups

---

### DISC-035: Learning System Trust Indicators (DISCOVERED)

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Critical for retention post-beta. Without this, users subscribing in Week 1-2 will churn in Week 3-4 when they realize learning hasn't kicked in yet.

**Problem**: With <10 corrections per user in beta, learning system can't demonstrate value before subscription decision. Users paying for "AI that learns YOUR pricing" but won't see meaningful improvement until months in.

**Proposed Work**:
1. Track category-level correction count in backend
2. Visual indicator on quotes: "High Confidence (12 corrections)" vs "Learning (2 corrections)"
3. Make learning progress transparent to set realistic expectations
4. Show learning dashboard in Pricing Brain section

**Success Metric**: NPS correlation with correction count; "Trust in pricing accuracy" survey score improvement; Reduced churn for users with <5 total corrections

---

### DISC-036: Keyboard Shortcuts for Power Users (DISCOVERED)

**Source**: Product Discovery Agent
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Sprint Alignment**: Quick win that delights power users and positions product as professional tool

**Problem**: Quote generation workflow requires multiple mouse clicks through UI. No keyboard-driven workflow for users who generate 5-10 quotes/day. Extra clicks slow down expert users.

**Proposed Work**:
1. Add 5 essential shortcuts: Cmd/Ctrl+N = New quote, Cmd/Ctrl+E = Edit, Cmd/Ctrl+D = Download PDF, Cmd/Ctrl+S = Save, Cmd/Ctrl+Enter = Generate
2. Display shortcut hints on hover for discoverability
3. Add "Keyboard Shortcuts" help modal (Cmd/Ctrl+?)

**Success Metric**: Power users (5+ quotes/week) adopt shortcuts at 40%+ rate; avg time-per-quote decreases 20% for shortcut users

---

### DISC-037: Demo-to-Referral Incentive Bridge (DISCOVERED)

**Source**: Growth Discovery Agent
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Combines "Demo Conversion" + "Referral Viral Loop" strategies. Highest potential user acquisition from single feature.

**Problem**: Demo users see value but have low urgency to sign up. Referral program exists but demo users can't participate. Missing conversion bridge between "this is cool" and "I need this now".

**Proposed Work**:
1. After demo quote generated, show modal: "Love it? Get 14 days free (instead of 7) + refer 3 contractors for permanent 50% off"
2. Pre-fill referral targets with "Who would benefit from this?" text inputs (3 email fields)
3. On signup, automatically send referral invites to those 3 emails
4. Creates immediate viral loop from demo conversion moment

**Success Metric**: 40% of demo signups submit referral emails; 30% of referrals sign up = 3.6x viral coefficient

---

### DISC-038: Duplicate Quote Template Feature (DISCOVERED)

**Source**: Product Discovery Agent
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Increases engagement and retention for repeat users who quote similar jobs

**Problem**: Contractors often quote similar jobs (same customer repeat work, similar scope projects). Currently must re-record or re-type entire job description each time.

**Proposed Work**:
1. Add "Duplicate" button to quote detail view and quote history items
2. Creates new quote pre-filled with: customer info, job type, line items structure, notes template
3. User makes quick adjustments and regenerates
4. Track duplicate_source_quote_id for learning insights

**Success Metric**: 25%+ of quotes marked as duplicates within 30 days; users who duplicate generate 2.5x more quotes

---

### DISC-039: "Voice Quote" Category Positioning (DISCOVERED)

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: 6-12 month strategic horizon. Prevents Buildxact from stealing category in 2025.

**Problem**: "Voice-first contractor quotes" is an unclaimed category. Once Buildxact adds voice (6-12 months), first-mover advantage in category naming is lost.

**Proposed Work**:
1. Register voicequote.com domain, redirect to Quoted
2. Create "Voice Quote" buyer's guide comparing traditional estimating vs voice
3. SEO strategy around "voice quote software", "voice estimating", "voice bidding"
4. PR outreach: "Quoted Launches First Voice-Based Quoting Platform for Contractors"

**Success Metric**: Quoted ranks #1 for "voice quote software" within 90 days; Contractor survey: "When I think 'voice quote', I think ____" (target: 60%+ say Quoted)

---

### DISC-040: QuickBooks Integration for Lock-In (DISCOVERED)

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: XL | **Score**: 0.75
**Sprint Alignment**: Post-beta (Q1 2025). Critical for defensibility - creates switching costs.

**Problem**: Learning system is defensible but copyable. Integrations create real switching costs. Contractor using Quoted→QuickBooks sync won't switch to competitor without migration pain.

**Proposed Work**:
1. Prioritize ONE strategic integration for Q1 2025 (after 100-user beta)
2. Start with QuickBooks Online API integration
3. Auto-create invoice from accepted quote
4. This becomes "reason not to switch" even if competitor launches voice

**Success Metric**: 40%+ of Pro tier users enable QuickBooks sync; Users with integration active have 3x lower churn

---

### DISC-041: Prompt Injection Learning Optimization 🧠 BRAINSTORM (DISCOVERED)

**Source**: Founder Request (Eddie)
**Impact**: HIGH | **Effort**: M | **Score**: 0.85
**Sprint Alignment**: Core learning system enhancement. Next strategic R&D cycle.

**Problem**: Current learning system uses prompt injection to teach Claude about contractor pricing patterns. This works but could be significantly smarter. Need executive brainstorm on:
1. How to better structure injected context for model comprehension
2. Optimal format for learned adjustments (JSON vs natural language)
3. Memory efficiency - which patterns provide most signal per token
4. Feedback loop optimization - getting better faster with less data

**Proposed Work**:
1. Executive team brainstorm session on prompt engineering improvements
2. Research latest Claude prompt optimization techniques
3. A/B test different context injection formats
4. Measure quote accuracy delta per approach
5. Document optimal patterns for Quoted learning system

**Success Metric**: 15% improvement in quote accuracy; 20% reduction in prompt tokens needed

---

## Completed & Deployed

<details>
<summary>Click to expand completed items (20 items)</summary>

### DISC-001: First Quote Activation Flow ✅
**Commit**: 8628869 | Post-onboarding modal with voice/text paths

### DISC-002: Referral Program Early Visibility ✅
**Commit**: 5c1ebc3 | Referral section in celebration modal

### DISC-003: Landing Page CTA Clarity ✅
**Commit**: fd82e2f | Demo primary, signup secondary

### DISC-004: Analytics Funnel Gaps ✅
**Commit**: 9607ccf | Full conversion tracking events

### DISC-005: Trial→Upgrade Journey Friction ✅
**Commit**: 412f5da | Single-click upgrade from banner

### DISC-006: Animation Walkthrough→Signup Flow ✅
**Commit**: c8addfa | Conversion modal after animation

### DISC-007: Onboarding Path A/B Testing ✅
**Commit**: b5d55b1 | Track path selection and outcomes

### DISC-008: Learning System Visibility ✅
**Commit**: 57c3aff | Learning progress section in Pricing Brain

### DISC-009: First Quote Celebration Enhancement ✅
**Commit**: dd5c41e | Enhanced celebration with share/referral

### DISC-010: Testimonial Collection System ✅
**Commit**: fabe2c6 | 5-star rating modal after 3rd quote

### DISC-011: Voice-First Assumption Validation ✅
**Commits**: f1053b8, ecc2be1 | Text-first option, voice as enhancement

### DISC-012: Learning System Analytics ✅
**Commit**: 412f5da | Track correction patterns

### DISC-015: Social Proof Scarcity ✅
**Commit**: 3d8f8fa | Beta spots counter

### DISC-016: Premium PDF Branding (Logo) ✅
**Commit**: 94ba6dc | Custom logo upload

### DISC-017: Trial Abuse Prevention ✅
**Commit**: 8c88de2 | Email normalization + disposable blocking

### DISC-018: Trial Grace Period ✅
**Commit**: 136d244 | Soft warnings + 3 grace quotes

### DISC-019: "Try It First" Fast Activation ✅
**Commit**: 0ade9e9 | Skip interview, use industry defaults

### DISC-020: Exit-Intent Survey ✅
**Commit**: 048d173 | Capture why visitors leave

### DISC-021: Email Signature Referral Hack ✅
**Commit**: 8672a3e | Pre-written signature with referral link

### DISC-022: Customer Memory (Autocomplete) ✅
**Commit**: e3c8786 | Autofill returning customers

### DISC-024: Viral Footer Enhancement ✅
**Commit**: 1c3d0d3 | CTA in shared quote footer

### DISC-034: Pricing Sanity Check ✅
**Commit**: 926c135 | Statistical bounds on quote generation to prevent hallucinations

</details>

---

## Discovery Process

New discoveries are generated by `/quoted-discover` which spawns 3 parallel agents:
1. **Product Discovery Agent** - UX friction, feature gaps
2. **Growth Discovery Agent** - Acquisition, activation, retention opportunities
3. **Strategy Discovery Agent** - Competitive threats, market positioning

Each discovery is scored: **Impact/Effort Ratio** (higher = better)
- Impact: HIGH=3, MEDIUM=2, LOW=1
- Effort: S=1, M=2, L=3, XL=4
