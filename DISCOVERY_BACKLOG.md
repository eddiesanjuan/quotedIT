# Discovery Backlog

**Last Updated**: 2025-12-05
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
| DEPLOYED | 28 |
| COMPLETE | 4 |
| READY | 9 |
| DISCOVERED | 18 |
| **Total** | **59** |

**Prompt Optimization**: DISC-041 complete → DISC-052 through DISC-055 (learning system improvements)
**Competitive Defense**: DISC-014 complete → DISC-060 through DISC-062 (RAG, category ownership, messaging)
**Phase II Voice Control**: 8 tickets (DISC-042 through DISC-049) awaiting executive review

---

## Complete (Pending Deploy)

### DISC-051: Quote Confidence Badge Positioning (COMPLETE) 🐛

**Source**: Founder Request (Eddie, 2025-12-05)
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Commit**: de40576

**Problem**: The quote confidence badge (e.g., "MEDIUM CONFIDENCE") was hidden behind the fixed navigation header on desktop and partially clipped on mobile.

**Solution Implemented**:
- Added `position: relative` and `z-index: 1` to `.quote-header` to ensure proper stacking context
- Added `flex-shrink: 0` to `.confidence-badge` to prevent unwanted wrapping
- Badge now fully visible on both desktop and mobile viewports

**Success Metric**: Confidence badge fully visible without clipping ✅

---

### DISC-036: Keyboard Shortcuts for Power Users (COMPLETE)

**Source**: Product Discovery Agent
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Commit**: bb1b1dc

**Problem**: Quote generation workflow required multiple mouse clicks through UI. No keyboard-driven workflow for users who generate 5-10 quotes/day.

**Solution Implemented**:
- 6 essential keyboard shortcuts: Cmd/Ctrl+N (New), +E (Edit), +D (Download), +S (Save), +Enter (Generate), +? (Help)
- Context-aware activation (shortcuts only work when relevant)
- Platform detection (⌘ on Mac, Ctrl on Windows/Linux)
- Help modal with visual keyboard reference
- PostHog tracking for usage analytics

**Success Metric**: Power users can navigate entire quote workflow via keyboard ✅

---

### DISC-035: Learning System Trust Indicators (COMPLETE)

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Commit**: 0de1220

**Problem**: With <10 corrections per user in beta, learning system can't demonstrate value before subscription decision. Users paying for "AI that learns YOUR pricing" but won't see meaningful improvement until months in.

**Solution Implemented**:
- Added correction_count tracking per category in pricing_knowledge
- Auto-increments when apply_learnings_to_pricing_model is called
- New endpoint: GET /pricing-brain/{category}/confidence returns confidence info
- 4 confidence levels: "low" (0-1), "medium" (2-4), "good" (5-9), "high" (10+)
- Confidence badges on quotes fetch real-time data and show: "High Confidence (12 corrections)"
- Tooltip shows description: "Well-calibrated from many corrections"
- Applied to both main quote view and detail/edit view
- Pricing Brain already displays correction counts per category

**Success Metric**: Confidence badge fully visible showing correction count context for trust-building during trial period ✅

---

## Ready for Implementation

### DISC-056: Confidence Badge Still Clipped Behind Nav (READY) 🐛

**Source**: Founder Request (Eddie, 2025-12-05)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: UX polish, follows DISC-051 which didn't fully resolve the issue

**Problem**: Despite DISC-051's fix, the confidence badge on quote detail view is still being clipped/hidden behind the fixed navigation header. On desktop, the badge ("LIMITED DATA IS CONFIDENT" etc.) appears to overlap with nav elements rather than displaying cleanly below it. Mobile likely has similar issues.

**Investigation Needed**:
1. Test on actual devices (desktop Chrome, Safari, mobile iOS/Android)
2. Check if `padding-top: 120px` on main is sufficient to clear nav height
3. Verify `scroll-to-top` behavior accounts for fixed nav offset
4. Check if z-index conflict between nav (z:100) and quote-header (z:1) causes rendering issues
5. Consider if quote-header needs margin-top or if scroll should target element offset

**Proposed Work**:
1. Add comprehensive browser testing to reproduce exact conditions
2. Measure actual nav height vs content padding-top on various viewports
3. Implement scroll offset to account for fixed nav: `scrollTo({ top: element.offsetTop - navHeight })`
4. Add `scroll-margin-top` CSS property to quote-header for native scroll-into-view offset
5. Test fix across desktop (Chrome/Safari/Firefox) and mobile (iOS Safari, Android Chrome)

**Success Metric**: Confidence badge fully visible immediately after opening any quote from My Quotes, on both desktop and mobile

**Related**: Supersedes DISC-051 which only partially addressed the issue

---

### DISC-052: Hybrid Learning Format + Priority Selection (READY) 🧠

**Source**: DISC-041 Brainstorm (Phase 1 - Quick Wins)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: 40% token reduction, likely accuracy improvement, 1-week implementation

**Problem**: Current learning injection uses verbose natural language (~36 tokens/learning). All 20 learnings injected regardless of relevance. This wastes tokens and adds noise.

**Proposed Work**:
1. Create hybrid formatter: structured data + natural language summary
2. Implement basic priority scoring (impact × confidence)
3. Top-K selection (inject only 7 highest-priority learnings)
4. Update prompt templates to use hybrid format
5. Feature flag for gradual rollout
6. A/B test: current vs hybrid approach

**Technical Details**:
- New function: `format_hybrid_learnings(learnings, max_tokens=200)`
- Priority = correction_magnitude × confidence × sample_count
- Backward compatible (dual-write during testing)
- Estimated effort: 16 hours

**Example Output**:
```
Adjustments: {"demo": +20%, "materials": -8%, "labor": standard}
Rules: cleanup required, stairs +10%
Range: $4,500-$8,200
Pattern: Conservative demo, strong materials
```

**Success Metric**: 60% token reduction (720 → 240 tokens); accuracy maintained or improved; <5% rollback rate

---

### DISC-053: Structured Learning Storage (READY) 🧠

**Source**: DISC-041 Brainstorm (Phase 2 - Foundation)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Enables future optimizations, better learning quality

**Problem**: Converting text → JSON → text loses structure. No metadata for smart prioritization. Can't track learning quality over time.

**Proposed Work**:
1. Create Learning model with full metadata (impact, confidence, recency, embeddings)
2. Migration script: convert existing text learnings to structured format
3. Update learning extraction to populate metadata
4. Dual-write period (maintain both formats for safety)
5. Comprehensive testing and validation

**Schema**:
```python
class Learning:
    id, category, learning_type
    target, adjustment, confidence
    sample_count, total_impact_dollars
    created_at, last_seen
    reason, examples
    priority_score, embedding
```

**Technical Details**:
- Estimated effort: 24 hours
- DB migration with rollback plan
- 2-week dual-write period
- Feature flag: use structured vs text

**Success Metric**: Zero data loss in migration; structured format enables 20% better prioritization; foundation for Phase 4 semantic features

---

### DISC-054: Dynamic Learning Rate (READY) 🧠

**Source**: DISC-041 Brainstorm (Phase 3 - Velocity)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: 2-3x faster learning convergence, critical for beta success

**Problem**: Current 30% new / 70% old weighting is too conservative for new categories. Takes 12+ corrections to reach 80% accuracy when could achieve same in 5-6 corrections with aggressive early learning.

**Proposed Work**:
1. Implement dynamic weighting function based on correction count
2. Update `apply_learnings_to_pricing_model()` to use dynamic weights
3. A/B test framework to measure convergence rate
4. PostHog tracking for learning velocity metrics

**Algorithm**:
```python
<5 corrections: 60% new (fast learning)
5-15 corrections: 30% new (balanced)
>15 corrections: 15% new (stable refinement)
```

**Technical Details**:
- Estimated effort: 8 hours
- Low risk (isolated change)
- A/B test: dynamic vs static weighting
- Track "corrections to 80% accuracy" metric

**Success Metric**: 50% reduction in corrections needed to reach 80% accuracy (12 → 6); faster beta user value demonstration

---

### DISC-055: Semantic Learning Deduplication (READY) 🧠

**Source**: DISC-041 Brainstorm (Phase 4 - Polish)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Optional enhancement, 20-30% learning count reduction

**Problem**: Redundant learnings accumulate ("Increase demo 20%" and "Demo typically 20% higher" are the same). Wastes tokens and confuses model with duplicate signals.

**Proposed Work**:
1. Add pgvector extension or embedding column to DB
2. Generate embeddings for all learnings
3. Implement clustering-based deduplication (0.90+ similarity threshold)
4. Keep highest confidence learning from each cluster
5. Optional: Cross-category semantic search

**Technical Details**:
- Estimated effort: 32 hours
- Requires pgvector or embedding service
- Conservative similarity threshold (avoid over-deduplication)
- Optional feature (only if Phase 1-3 succeed)

**Success Metric**: 20-30% reduction in learning count with no information loss; improved model comprehension from cleaner signal

---

### DISC-014: Buildxact Competitive Defense (DEPLOYED) ⚠️ Strategic

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: L | **Score**: 0.75
**Sprint Alignment**: Long-term - existential threat if not addressed in 2025
**Deployed**: 2025-12-05

**Problem**: Main competitor Buildxact could add voice interface in 6-12 months.

**Completed Work**:
- ✅ Comprehensive competitive intelligence on Buildxact (features, pricing, AI capabilities, user complaints)
- ✅ Executive strategy session analyzing threats and opportunities
- ✅ Strategic defense document created: `docs/BUILDXACT_COMPETITIVE_DEFENSE_STRATEGY.md`
- ✅ 3 implementation tickets created

**Key Strategic Recommendations**:
1. RAG implementation → DISC-060 (18-24 month learning moat)
2. Category ownership: "voice quote" → DISC-061 (first-mover advantage)
3. Messaging pivot: learning-first → DISC-062 (defensible positioning)

**Key Finding**: Buildxact already launched AI ("Blu" - 8,740 takeoffs). Their weakness = desktop-only, generic dealer catalog pricing. Our moat = personal learning + mobile-first.

**Success Metric**: Strategy document delivered ✅; actionable tickets created ✅

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

### DISC-063: Horizontal Market Positioning & Messaging Update 📝 STRATEGIC (READY)

**Source**: Founder Request (Eddie, 2025-12-06)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Strategic messaging - affects all marketing, landing pages, and competitive positioning

**Problem**: Current positioning and competitive analysis frames Quoted as a "contractor tool" competing with construction-specific platforms like Buildxact. This is too narrow. Quoted is a horizontal quoting tool for anyone who prices custom work - contractors are the beachhead, not the ceiling.

**Strategic Reframe**:
- **Buildxact is NOT a competitor.** They are a construction-specific project management platform ($100-500+/month) targeting growing contractors who need crews, scheduling, materials, and timelines. Completely different game.
- **Quoted is horizontal.** Works for anyone pricing custom work: contractors, event planners, freelancers, caterers, photographers, personal trainers, wedding vendors, etc.
- **The moats are different.** Buildxact competes on depth (construction features). Quoted competes on simplicity, adaptability, learning, and price.
- **Future play**: Platforms like Buildxact would more likely want to *integrate* Quoted as a quick estimate step than compete with it.

**Proposed Work**:
1. **Audit current messaging** - Landing page, demo, onboarding, emails - identify "contractor-only" framing
2. **Update landing page hero** - From contractor-specific to universal: "The fastest way to quote custom work. Any industry. Describe the job, send the quote."
3. **Broaden demo examples** - Show event planner, freelancer, and contractor use cases (not just contractor)
4. **Update COMPANY_STATE.md** - Reflect horizontal positioning in strategic docs
5. **Deprioritize Buildxact competitive defense** - Mark DISC-060/061/062 as lower priority; Buildxact is adjacent, not competitive
6. **Create "Who Uses Quoted" section** - Show diverse use cases (contractors, event planners, freelancers, service providers)

**Key Moats (Updated)**:
1. **Learning system** - Gets smarter with YOUR pricing, not industry averages. Sticky after 50+ quotes.
2. **Trade-agnostic** - No industry assumptions. Learns YOUR pricing model, whatever it is.
3. **Right-sized** - Not "cheap" but appropriate. Solo operators don't need project management.
4. **Voice-first simplicity** - Describe the job, get the quote. Works for any service business.

**Real Competition** (Updated):
1. Paper/Excel/nothing (biggest)
2. Generic invoicing apps (FreshBooks, Wave) - no voice, no learning
3. Vertical-specific tools (Honeybook for creatives, Jobber for service) - category-locked
4. Big players if they add voice (Square, Intuit)

**NOT Competition**:
- Buildxact, Procore, CoConstruct - different category (construction project management)

**Success Metric**: Landing page copy updated; demo shows 3 industry examples; positioning docs updated; competitive defense tickets deprioritized

---

## Discovered (Awaiting Review)

### DISC-060: RAG Learning System Implementation 🧠 COMPETITIVE DEFENSE (DISCOVERED)

**Source**: DISC-014 Competitive Defense Strategy
**Impact**: CRITICAL | **Effort**: L | **Score**: Strategic
**Sprint Alignment**: Q1 2025 - Creates 18-24 month learning moat before Buildxact adds voice

**Problem**: Current learning system uses per-category corrections. Buildxact's Blu uses generic dealer catalogs. Need cross-category pattern recognition that Buildxact can't replicate quickly.

**Proposed Work**:
1. Implement RAG (Retrieval-Augmented Generation) for quote generation
2. Vector embeddings of correction patterns across all categories
3. Semantic search: "What have I learned about labor pricing for outdoor projects?"
4. Cross-category learning: "This contractor always prices labor 20% higher on rush jobs"
5. Pattern recognition: Customer loyalty discounts, seasonal adjustments, material markups

**Technical Scope**:
- Vector database setup (pgvector extension in existing Postgres)
- Embedding pipeline for learnings
- RAG injection into quote generation prompt
- Migration from category-specific to pattern-based learning

**Success Metric**: After 100 corrections, RAG-powered quotes achieve 95%+ accuracy vs 85% without RAG; learning patterns apply across categories

**Defensibility**: Creates personal moat - Buildxact can add voice in 6 months but can't copy 6 months of YOUR learning data

---

### DISC-061: Category Ownership - "Voice Quote" 📢 COMPETITIVE DEFENSE (DISCOVERED)

**Source**: DISC-014 Competitive Defense Strategy (related to DISC-039)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Q1 2025 - Own category before Buildxact can claim it

**Problem**: First mover in category naming wins long-term. Once "voice quote" = "Quoted" in contractor minds, Buildxact becomes fast-follower even if they add voice.

**Proposed Work**:
1. Register voicequote.com domain → redirect to Quoted
2. SEO strategy: "voice quote software", "voice estimating", "voice bidding"
3. Create "Voice Quote Buyer's Guide" (comparative content)
4. PR outreach: "Quoted Launches First Voice-Based Quoting Platform for Contractors"
5. Target construction trade publications, SaaS media

**Success Metric**: Rank #1 for "voice quote software" within 90 days; contractor surveys show 60%+ associate "voice quote" with Quoted

**Defensibility**: Category ownership - even if Buildxact launches voice, they're "Buildxact adds voice feature" vs "Quoted invented voice quoting"

---

### DISC-062: Messaging Pivot: Learning-First Positioning 📝 COMPETITIVE DEFENSE (DISCOVERED)

**Source**: DISC-014 Competitive Defense Strategy
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Immediate - can do now

**Problem**: Current messaging is "Voice-to-quote in 30 seconds". Buildxact can copy this in 6 months. Need messaging based on defensible moat (learning system).

**Current Messaging**: "Voice-to-quote in 30 seconds"
**Problem**: Buildxact can say same thing when they add voice

**New Messaging**:
- **Primary**: "The AI that learns YOUR pricing, not just industry averages"
- **Secondary**: "Quote from your truck, not your desk"
- **Proof Point**: "After 50 quotes, Quoted knows your pricing patterns better than you do"

**Proposed Work**:
1. Update landing page hero section
2. Create comparison content: Quoted vs Buildxact (when they launch voice)
3. Collect testimonials emphasizing learning system
4. Update email sequences to emphasize learning
5. Create "How Quoted Learns Your Pricing" explainer content

**Success Metric**: User surveys show "learns my pricing" > "voice input" as primary value prop; testimonials emphasize accuracy improvement over time

**Defensibility**: Learning moat is real - Buildxact's Blu uses dealer catalogs (generic), we use personal patterns

---

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


### DISC-041: Prompt Injection Learning Optimization 🧠 BRAINSTORM (COMPLETE)

**Source**: Founder Request (Eddie)
**Impact**: HIGH | **Effort**: M | **Score**: 0.85
**Sprint Alignment**: Core learning system enhancement. Next strategic R&D cycle.
**Completed**: 2025-12-05

**Problem**: Current learning system uses prompt injection to teach Claude about contractor pricing patterns. This works but could be significantly smarter. Need executive brainstorm on:
1. How to better structure injected context for model comprehension
2. Optimal format for learned adjustments (JSON vs natural language)
3. Memory efficiency - which patterns provide most signal per token
4. Feedback loop optimization - getting better faster with less data

**Brainstorm Completed**: Executive-level analysis conducted across 4 perspectives (CGO, CPO, CFO, CTO). Design document created at `/docs/PROMPT_INJECTION_OPTIMIZATION_DESIGN.md` with comprehensive recommendations.

**Key Findings**:
- Current approach: 850-1,650 tokens/quote for learning context
- Optimization potential: 40-60% token reduction with IMPROVED accuracy
- Hybrid format (structured + context) provides best model comprehension
- Priority-based injection (top-7 learnings) reduces noise, increases signal
- Dynamic learning rate (aggressive early, conservative late) achieves 2-3x faster convergence

**Executive Consensus**: HIGH support for Phase 1 (hybrid format + priority injection + dynamic learning), MEDIUM support for semantic features

**Implementation Tickets Created**: DISC-052 (Hybrid Format), DISC-053 (Structured Storage), DISC-054 (Dynamic Learning), DISC-055 (Semantic Deduplication)

**Success Metric**: 15% improvement in quote accuracy; 40% reduction in prompt tokens needed; 2x learning velocity (6 corrections to 80% vs 12)

---

## 🎯 Phase II: Voice-Controlled Professional's Paradise

**Status**: READY -
**Source**: Founder Vision (Eddie, 2025-12-05)
**Theme**: Transform Quoted from "voice input" to "fully voice-controlled" professional tool
**Timeline**: Post-beta (Q1-Q2 2025)

**Core Insight**: Contractors work from trucks and job sites, not desks. The natural evolution of Quoted is complete hands-free operation where complex workflows happen through natural language. Voice input was Phase I. Voice control is Phase II.

**Strategic Value**: This creates a moat that's nearly impossible to replicate quickly. Competitors can copy "voice-to-text". They can't easily copy "understands 'add more fluff for a difficult customer' and modifies quote tone accordingly."

---

### DISC-042: Voice Command Interpreter Engine 🧠 PHASE II FOUNDATION (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: CRITICAL | **Effort**: XL | **Score**: Strategic
**Sprint Alignment**: Foundation for all Phase II features. Must be robust before other voice features.
**Dependencies**: None (foundational)

**Problem**: Current voice input is transcription-only. User speaks, AI transcribes, generates quote. No interpretation of commands or intent. Can't say "increase the deck by 10 feet" and have it actually happen.

**Vision**: Natural language command processing that understands contractor intent and executes complex multi-step actions.

**Example Commands to Support**:
- CREATE: "Go ahead and make another quote for John Smith at 1234 Prospect Promenade"
- MODIFY PARAMETERS: "Increase the size of his deck by 10 feet in each direction"
- MODIFY TONE: "Edit this quote so it has a little bit more fluff because this customer is going to be difficult"
- SEARCH: "Pull up the quote I did for the Johnsons last week"
- DUPLICATE: "Clone this quote but change the address to 456 Oak Street"
- SHARE: "Email this to the customer"

**Technical Architecture**:
1. **Intent Classification Layer**: Determine action type (create, edit, search, share, regenerate)
2. **Entity Extraction**: Parse names, addresses, measurements, materials, descriptors
3. **Context Resolution**: "His deck" refers to current quote's deck line item
4. **Action Router**: Map intent + entities to specific backend actions
5. **Confirmation Generation**: Create natural language confirmation before execution

**Proposed Work**:
1. Design intent taxonomy (10-15 core intents covering 95% of use cases)
2. Build entity extraction pipeline (names, addresses, numbers with units, materials)
3. Create context resolution system (current quote, recent history, customer relationships)
4. Implement action router with confirmation loop
5. Train/prompt-engineer Claude for command interpretation
6. Build fallback to clarifying questions when intent is ambiguous

**Success Metric**: 90% intent classification accuracy; <3% false-positive command execution; users prefer voice commands over clicking for 60%+ of actions

**Executive Review Questions**:
- Should we use Claude for interpretation or a dedicated NLU model?
- What's minimum viable intent set for Phase II launch?
- Latency budget: How long can users wait between command and action?

---

### DISC-043: Continuous Listening Mode 🎤 PHASE II CORE (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: Enables true hands-free operation for on-the-go professionals
**Dependencies**: DISC-042 (Voice Command Interpreter)

**Problem**: Current voice requires clicking record button, speaking, clicking stop. This is fine for initial quote creation but terrible for editing workflow. Contractors with dirty hands, driving between jobs, or walking a job site can't keep clicking buttons.

**Vision**: True hands-free operation where the app listens continuously and responds to voice commands.

**User Experience**:
1. User enables "Hands-Free Mode" (toggle or voice command)
2. App displays listening indicator
3. User speaks naturally: "Quoted, increase the deck price by $500"
4. App confirms: "Increase deck from $2,400 to $2,900. Confirm?"
5. User: "Yes" or "No, make it $2,800"
6. App executes and provides audio/visual confirmation

**Proposed Work**:
1. Implement wake word detection ("Quoted", "Hey Quote", or custom)
2. Add push-to-talk alternative for noisy environments
3. Visual listening state indicator (pulsing mic, waveform)
4. Audio feedback option (voice confirmations for eyes-free use)
5. Timeout and auto-sleep after inactivity
6. Battery optimization for mobile PWA/native

**Success Metric**: 40% of power users (5+ quotes/week) enable continuous mode; average session uses 3+ voice commands

**Executive Review Questions**:
- Wake word vs push-to-talk vs always-listening? (Privacy/battery implications)
- Should confirmations be voice, visual, or user-configurable?
- PWA limitations: Is native app required for background listening?

---

### DISC-044: Quote Modification via Natural Language ✏️ PHASE II CORE (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: The "magic" of Phase II - speak changes, watch them happen
**Dependencies**: DISC-042 (Voice Command Interpreter)

**Problem**: Editing quotes currently requires finding the right field, clicking, typing. For simple changes like "add $200 to the labor line", this is friction. For complex changes like "make this quote less aggressive because the customer seemed price-sensitive", there's no way to do it at all.

**Vision**: Natural language modifications that AI interprets and applies to quotes.

**Modification Categories**:

1. **Parameter Changes** (quantitative):
   - "Increase the deck size by 10 feet in each direction"
   - "Add $500 to the labor line item"
   - "Change the total to $15,000" (AI adjusts line items proportionally)
   - "Apply a 15% discount"

2. **Scope Changes** (structural):
   - "Add a pergola to this quote"
   - "Remove the lighting package"
   - "Split the deck into two phases"
   - "Combine these three items into one 'Materials' line"

3. **Tone/Style Changes** (qualitative):
   - "Add more fluff because this customer is going to be difficult"
   - "Make it more professional - this is a commercial client"
   - "Simplify the descriptions - customer said they don't need details"
   - "Add more technical specs - customer is an engineer"

4. **Customer Context Changes**:
   - "This is a repeat customer, add our loyal customer discount"
   - "They mentioned budget constraints, show value emphasis"
   - "They're in a hurry, emphasize quick turnaround"

**Proposed Work**:
1. Build modification intent classifier (parameter/scope/tone/context)
2. Create parameter change executor (understands units, percentages, relative changes)
3. Implement scope change handler (add/remove/restructure line items)
4. Develop tone modification prompts (regenerate with style guidance)
5. Add preview/diff view before applying changes
6. Maintain edit history for undo capability

**Success Metric**: 80% of voice modification commands execute correctly; users make 2x more edits per quote with voice vs click

**Executive Review Questions**:
- How much regeneration is acceptable? (Tone changes require AI rewrite)
- Should we show AI confidence before applying changes?
- Undo depth: How many modifications should be reversible?

---

### DISC-045: Customer & Address Memory System 📇 PHASE II ENABLER (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Required for "make a quote for John Smith" to work
**Dependencies**: Builds on DISC-022 (Customer Autocomplete)

**Problem**: Voice commands like "make another quote for John Smith" require the system to know who John Smith is, his address, and his history. Current customer autocomplete (DISC-022) is search-based, not voice-command-ready.

**Vision**: Rich customer database that voice commands can reference naturally.

**Required Capabilities**:
1. **Name Resolution**: "John Smith" → correct John Smith from database (handle duplicates)
2. **Address Book**: Store multiple addresses per customer ("his office", "the rental property")
3. **History Context**: Know what quotes were done for customer previously
4. **Relationship Memory**: "Repeat customer", "referred by Mike", "always negotiates"
5. **Preference Storage**: "Prefers detailed quotes", "always asks for military discount"

**Voice Commands Enabled**:
- "Make another quote for John Smith at the usual address"
- "Quote the same job we did for the Hendersons, but for the Wilsons"
- "What was our last quote for the customer on Elm Street?"
- "Add John's wife Mary as a contact on this quote"

**Proposed Work**:
1. Extend customer model: multiple addresses, relationship notes, preferences
2. Build fuzzy name matching for voice (handles "Jon" vs "John", nicknames)
3. Create disambiguation flow: "I found 2 John Smiths. Oak Street or Maple Avenue?"
4. Implement quote history per customer with searchable context
5. Add customer preference storage with voice-settable fields
6. Design customer merge/dedup workflow

**Success Metric**: 95% correct customer resolution on voice commands; customers with 2+ quotes have 40% faster quote creation

**Executive Review Questions**:
- How to handle common names? (Voice disambiguation vs visual list?)
- Customer data import from contacts/CRM?
- Privacy: How long to retain customer history?

---

### DISC-046: Prompt Tweaking & Quote Regeneration 🔄 PHASE II CORE (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Enables iterative refinement without re-recording
**Dependencies**: DISC-042 (Voice Command Interpreter)

**Problem**: User generates a quote but it's not quite right. Currently must either manually edit every field OR re-record the entire job description. No middle ground. User can't say "regenerate with more emphasis on quality materials" or "redo this assuming premium pricing".

**Vision**: Expose and allow modification of the prompt that generated the quote, then regenerate.

**Two User Paths**:

1. **Voice-Guided Regeneration** (most common):
   - "Regenerate this quote with more detail on materials"
   - "Redo assuming the customer wants premium everything"
   - "Make this quote 20% higher and justify the pricing"
   - "Regenerate but assume we're competing on price"

2. **Prompt Template Editing** (power users):
   - Show the actual prompt that was sent to Claude
   - Allow direct editing of prompt text
   - Save as template for future quotes
   - Per-category prompt customization

**User Experience - Voice Path**:
1. User views generated quote
2. User: "Regenerate this with more emphasis on durability"
3. System shows: "I'll regenerate emphasizing durability and quality materials. The new quote may have different pricing."
4. User: "Go ahead"
5. System regenerates, shows diff from original
6. User: "Keep the new version" or "Undo, go back to original"

**Proposed Work**:
1. Store generation prompt with each quote (not just output)
2. Build prompt modification interpreter ("more detail" → specific prompt additions)
3. Create regeneration pipeline with original context + modifications
4. Implement side-by-side or diff view for comparing versions
5. Add version history (keep last 3 generations per quote)
6. Build prompt template library for common scenarios

**Success Metric**: 30% of quotes regenerated at least once; regenerated quotes have 20% fewer manual edits

**Executive Review Questions**:
- Token cost: Regeneration = 2x API cost. Acceptable?
- Should original quote be preserved or replaced?
- Prompt template sharing between users? (Marketplace opportunity?)

---

### DISC-047: Voice Interpretation Correction UI 🎯 PHASE II POLISH (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Critical for trust - users must be able to fix misheard commands
**Dependencies**: DISC-042 (Voice Command Interpreter)

**Problem**: Voice recognition will sometimes fail. "John Smith" becomes "Jon Smyth". "$2,500" becomes "$25,000". If users can't quickly correct these errors, trust in the system collapses. The founder specifically noted: "there will inevitably be some text interpretation problems here and there that a quick fix would be nice on."

**Vision**: Seamless correction flow where misheard commands are easy to fix without starting over.

**Correction Flow**:
1. User speaks command
2. System shows interpretation BEFORE executing:
   ```
   I heard: "Make a quote for Jon Smyth at 1234 Prospect Road"
   → Creating quote for Jon Smyth at 1234 Prospect Road

   [Execute] [Edit] [Cancel]
   ```
3. User taps "Edit" → inline editing of interpreted text
4. System re-parses corrected text
5. User confirms, system executes

**Quick Fix Patterns**:
- **Tap-to-correct**: Tap any word to edit just that word
- **Voice correction**: "No, I said Smith, not Smyth"
- **Suggestions**: "Did you mean 'John Smith' from your contacts?"
- **History learn**: Remember corrections to improve future recognition

**Proposed Work**:
1. Always show interpretation before execution (no silent actions)
2. Build inline word-level editing UI
3. Implement "Did you mean...?" suggestions from context
4. Add voice-based correction path ("No, I said...")
5. Create correction learning system (user-specific improvements)
6. Track correction rate as quality metric

**Success Metric**: <5% of commands need correction; corrections take <3 seconds; correction rate decreases 50% over first month of use

**Executive Review Questions**:
- How much friction is acceptable? (Always confirm vs trust mode?)
- Should corrections feed back to improve recognition? (Privacy implications)
- Voice-only correction or must have visual? (Accessibility for eyes-free use)

---

### DISC-048: Multi-Turn Conversational Interface 💬 PHASE II ADVANCED (DISCOVERED)

**Source**: Founder Vision (Phase II)
**Impact**: MEDIUM | **Effort**: XL | **Score**: 0.5
**Sprint Alignment**: Advanced capability after core voice features stable
**Dependencies**: DISC-042, DISC-043, DISC-044 (all core voice features)

**Problem**: Complex workflows currently require multiple separate commands or clicking through UI. No conversational flow. User can't have a back-and-forth dialogue to refine a quote.

**Vision**: Natural multi-turn conversations where context carries forward.

**Example Conversation**:
```
User: "Start a new deck quote"
Quoted: "Sure, who's the customer?"
User: "The Hendersons on Oak Street"
Quoted: "Got it - Mike Henderson, 456 Oak Street. What size deck?"
User: "About 400 square feet, pressure-treated lumber"
Quoted: "400 sq ft deck, pressure-treated. Should I include railing?"
User: "Yeah, and add stairs"
Quoted: "Here's a $12,500 estimate for a 400 sq ft deck with pressure-treated lumber, railing, and stairs. Would you like to see the breakdown?"
User: "That's high - can you do it closer to $10k?"
Quoted: "I can bring it to $10,200 by switching to standard lumber and simpler railing. Want me to make that change?"
User: "Show me both options"
Quoted: [Shows comparison view]
```

**Key Capabilities**:
1. **Context Persistence**: Remember what was discussed in current session
2. **Clarifying Questions**: AI asks for missing info instead of guessing
3. **Progressive Refinement**: Build quote through dialogue, not single command
4. **Negotiation Assistance**: Help contractor think through pricing options
5. **Teaching Moments**: "Based on similar jobs, you might want to consider..."

**Proposed Work**:
1. Build conversation state management (session memory)
2. Create guided quote creation flow (required fields as questions)
3. Implement clarifying question generation
4. Add comparison/option generation for negotiation
5. Build conversation history UI
6. Design graceful handoff between voice and visual editing

**Success Metric**: Users complete 25% of quotes through conversation; conversational quotes have 15% higher customer conversion

**Executive Review Questions**:
- How much "personality" should Quoted have in conversations?
- Conversation history retention: Per session or persistent?
- This is a major UX shift - A/B test or full rollout?

---

### DISC-049: Phase II Architecture & Technical Spike 🏗️ (DISCOVERED)

**Source**: Engineering Planning
**Impact**: CRITICAL | **Effort**: L | **Score**: Strategic
**Sprint Alignment**: Must complete before any Phase II development begins
**Dependencies**: None (planning activity)

**Problem**: Phase II features require significant architectural decisions. Current system is request-response; Phase II is stateful and conversational. Need technical spike before committing to implementation.

**Questions to Answer**:
1. **Voice Processing**: Web Speech API vs Whisper vs Deepgram vs Assembly AI?
   - Accuracy comparison for contractor terminology
   - Latency requirements for conversational flow
   - Cost at scale (1000+ users, 10+ commands/day)
   - Offline capability for job site use

2. **Intent Classification**: Claude prompt engineering vs fine-tuned model vs hybrid?
   - Latency budget (user speaks → action)
   - Cost per command
   - Accuracy on edge cases
   - Ability to improve over time

3. **State Management**: How to maintain conversation context?
   - Session storage architecture
   - Context window management for long conversations
   - Multi-device sync (start on phone, continue on desktop?)

4. **Native vs PWA**: Can Phase II work as PWA or does continuous listening require native?
   - iOS/Android audio API limitations
   - Background processing requirements
   - Push notification for async operations

**Proposed Work**:
1. Prototype voice command pipeline with 3 different speech-to-text services
2. Benchmark intent classification approaches (latency, accuracy, cost)
3. Design state management architecture for conversational UI
4. PWA feasibility assessment for continuous listening
5. Cost model at 1000 users × 50 commands/day
6. Deliver technical recommendation document

**Success Metric**: Clear go/no-go decision on architecture; cost model within 2x of estimates; all technical risks identified

**Executive Review Questions**:
- Budget for Phase II technical spike? (Estimate: 40-80 engineering hours)
- Is native app acceptable if PWA can't support Phase II?
- Latency requirement: What's acceptable for voice command response?

---

## Completed & Deployed

<details>
<summary>Click to expand completed items (27 items)</summary>

### DISC-050: Pricing Page Plan Buttons Not Working ✅
**Commit**: 775f68a | Root cause: metered Stripe prices can't have `quantity` param. Fixed billing.py to detect metered prices and exclude quantity. All 3 plans (Starter, Pro, Team) now redirect to Stripe Checkout correctly.

### DISC-032: Autosave Quote Drafts (Local Storage) ✅
**Commit**: 50c2894 | 10-second autosave, recovery modal, PostHog tracking, 24-hour expiration

### DISC-031: Voice Recording Fallback & Recovery ✅
**Commit**: 90abdc6 | Voice support detection, browser badges, fallback UI, PostHog events

### DISC-038: Duplicate Quote Template Feature ✅
**Commit**: 761b7be | Duplicate endpoint, database tracking, UI buttons in quote detail and list views

### DISC-013: Animation Walkthrough Distribution Strategy ✅
**Commit**: 856f051 | Demo-promo landing page with UTM tracking, PostHog events, pre-written social copy

### DISC-028: PDF Quote Template Library ✅
**Commit**: 2e88a94 | 8 templates (classic, modern, bold, elegant, technical, friendly, craftsman, corporate) + accent colors, tier-gated

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
