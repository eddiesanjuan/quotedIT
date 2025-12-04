# Discovery Backlog

**Last Updated**: 2025-12-03
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
| DEPLOYED | 20 |
| COMPLETE | 2 |
| READY | 3 |
| DISCOVERED | 5 |
| **Total** | **30** |

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
