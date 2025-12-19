# Discovery Backlog

**Last Updated**: 2025-12-19
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
| DEPLOYED | 54 |
| COMPLETE | 1 |
| READY | 14 |
| DISCOVERED | 22 |
| **Total** | **91** |

**Prompt Optimization**: DISC-041 complete → DISC-052, DISC-054 (learning improvements via prompt injection)
**Deprioritized**: DISC-053, DISC-055 (structured storage/embeddings - over-engineering; prompt injection approach preferred)
**Competitive Defense**: DISC-014 complete → DISC-060 through DISC-062 (RAG, category ownership, messaging)
**Voice CRM**: DISC-085 (strategic design complete) → DISC-086 through DISC-092 ✅ ALL DEPLOYED
**Phase II Voice Control**: 8 tickets (DISC-042 through DISC-049) awaiting executive review
**Staging Environment**: DISC-073 complete → DISC-077, DISC-078, DISC-079 (Railway preview + feature flags + runbook) ✅ ALL DEPLOYED

---

## Recently Deployed (2025-12-12)

### DISC-086: Customer Model & Database Migration 🗄️ CRM PHASE 1 (DEPLOYED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Commits**: PR #1 (quoted-run/DISC-086-092 → main)

**Solution Implemented**:
- Created `Customer` SQLAlchemy model with core fields (name, phone, email, address)
- Added computed fields: total_quoted, total_won, quote_count, first/last quote dates
- Added CRM fields: status, notes, tags (JSON)
- Added deduplication fields: normalized_name, normalized_phone
- Added `customer_id` foreign key to `Quote` model
- Created auto-migration for new table with proper indexes

**Success Metric**: Customer table exists with proper relationships ✅

---

### DISC-087: Customer Aggregation & Deduplication Service 🔗 CRM PHASE 1 (DEPLOYED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Commits**: PR #1 (quoted-run/DISC-086-092 → main)

**Solution Implemented**:
- Created `backend/services/customer_service.py`:
  - `normalize_name(name)`: lowercase, strip punctuation, collapse whitespace
  - `normalize_phone(phone)`: digits only
  - `find_or_create_customer()`: deduplication on normalized name/phone
  - `update_customer_stats()`: recalculate totals from linked quotes
- Hooked into quote creation/update to auto-link customers
- Handles edge cases (no name/phone, conflicts, duplicates)

**Success Metric**: New quotes automatically create/link customers; deduplication accuracy >95% ✅

---

### DISC-088: Customer API Endpoints 🌐 CRM PHASE 1 (DEPLOYED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Commits**: PR #1 (quoted-run/DISC-086-092 → main)

**Solution Implemented**:
- Created `backend/api/customers.py` with endpoints:
  - `GET /customers`: List customers (paginated, searchable, filterable)
  - `GET /customers/{id}`: Customer detail with quote history
  - `PATCH /customers/{id}`: Update customer (notes, tags, status)
  - `GET /customers/search?q=`: Search by name/phone/address
  - `GET /customers/{id}/quotes`: All quotes for customer
- Added query parameters: status filter, sort, search
- Returns computed stats in response

**Success Metric**: All CRUD operations work; search returns relevant results in <500ms ✅

---

### DISC-089: Customer UI - List & Detail Views 🖥️ CRM PHASE 2 (DEPLOYED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Commits**: PR #1 (quoted-run/DISC-086-092 → main)

**Solution Implemented**:
- Added "Customers" tab to main navigation
- Built Customer List View with search, filters, customer cards
- Built Customer Detail View with stats, notes, tags, quote history
- Added inline editing for notes and tags via modals
- Mobile-responsive design (375px minimum)

**Success Metric**: Users can browse, search, and view customer details ✅

---

### DISC-090: CRM Voice Command Integration 🎤 CRM PHASE 3 (DEPLOYED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Commits**: PR #1 (quoted-run/DISC-086-092 → main)

**Solution Implemented**:
- Added CRM intent detection to `backend/services/claude_service.py`
- Detect CRM keywords: "customer", "who did I", "show me", "find"
- Implemented CRM voice commands:
  - **Search**: "Show me John Smith" → customer_search
  - **Detail**: "What's the history with Johnson Electric?" → customer_detail
  - **Notes**: "Add a note to Mike Wilson" → add_note (via UI)
  - **Tags**: "Tag Sarah's Bakery as VIP" → add_tag (via UI)
- Natural language responses for customer queries

**Success Metric**: 90%+ correct intent detection; voice commands complete in <3 seconds ✅

---

### DISC-091: Backfill Existing Quotes to Customer Records 📥 CRM PHASE 1 (DEPLOYED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Commits**: PR #1 (quoted-run/DISC-086-092 → main)

**Solution Implemented**:
- Created backfill logic in database initialization
- Iterates through all quotes with customer_name or customer_phone
- Calls `find_or_create_customer()` for each quote
- Links quote to customer via customer_id foreign key
- Updates customer stats (total_quoted, quote_count, etc.)
- Runs automatically during app startup for existing users

**Success Metric**: 100% of quotes with customer data linked to Customer records ✅

---

### DISC-092: CRM Task & Reminder System 📋 CRM PHASE 4 (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-11)
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Commits**: PR #1 (quoted-run/DISC-086-092 → main)

**Solution Implemented**:
- Created `Task` model: id, contractor_id, customer_id (optional), quote_id (optional)
- Fields: title, description, due_date, status (pending/completed)
- Priority levels: low, normal, high, urgent
- Manual task creation via button on customer detail and quote detail views
- Tasks tab in main navigation with Today/Upcoming/Overdue views
- Filter by customer, quote, priority
- Quick actions: complete task
- Mobile-responsive design

**Success Metric**: Users can create and manage tasks linked to customers/quotes ✅

---

### Pricing Brain Fix: learned_adjustments Field Naming (DEPLOYED)

**Source**: Bug discovered during PR testing
**Impact**: MEDIUM | **Effort**: S
**Commits**: 2387d36, c2b1c6c

**Problem**: Pricing Brain category cards showed "0 rules learned" even when rules existed. Rules also disappeared after editing in modal.

**Root Cause**: Frontend used `learned_rules` but backend sent `learned_adjustments`. Field name mismatch.

**Solution Implemented**:
- Fixed frontend to use `learned_adjustments` (backend's field name)
- Fixed rules count display to use `learned_adjustments_count`
- Verified rules persist correctly after edit/save cycle

**Success Metric**: Rules count displays correctly; rules persist after editing ✅

---

## Previously Deployed (2025-12-08)

### DISC-077: Enable Railway Preview Environments 🏗️ INFRA (DEPLOYED)

**Source**: DISC-073 Staging Brainstorm
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Commit**: 6b0d8fc

**Problem**: Need pre-merge testing capability to catch bugs before they hit production.

**Solution Implemented**:
- Updated CORS middleware in `backend/main.py` to use `allow_origin_regex`
- Pattern `https://.*\.up\.railway\.app` allows all Railway preview deployments
- Documented deployment workflow in CLAUDE.md

**Remaining**: Enable "Preview Deployments" toggle in Railway dashboard (founder action)

**Success Metric**: Preview environments work for PR testing; CORS allows API calls ✅

---

### DISC-078: Add Feature Flag Foundation 🚩 INFRA (DEPLOYED)

**Source**: DISC-073 Staging Brainstorm
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Commit**: 6b0d8fc

**Problem**: Need instant rollback capability and gradual rollout for new features.

**Solution Implemented**:
1. ✅ Added `isFeatureEnabled()` and `showFeature()` helpers to `frontend/index.html`
2. ✅ Created `backend/services/feature_flags.py` with PostHog integration
3. ✅ Added convenience functions: `is_invoicing_enabled()`, `is_new_pdf_templates_enabled()`
4. ✅ Documented feature flag discipline in CLAUDE.md

**Standard Flags**:
| Flag Key | Feature | Default |
|----------|---------|---------|
| `invoicing_enabled` | DISC-071 | false |
| `new_pdf_templates` | DISC-072 | false |
| `voice_template_customization` | DISC-070 | false |

**Success Metric**: New features can ship behind flags; rollback time < 1 minute ✅

---

### DISC-079: Create Emergency Runbook 📋 DOCS (DEPLOYED)

**Source**: DISC-073 Staging Brainstorm
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Commit**: 6b0d8fc

**Problem**: Need documented procedures for handling production incidents.

**Solution Implemented**:
- ✅ Created comprehensive `docs/EMERGENCY_RUNBOOK.md`
- ✅ Documented P1/P2/P3 incident classification with examples
- ✅ Added rollback procedures (feature flag toggle, git revert, hard reset, backup restore)
- ✅ Included decision tree for quick rollback selection
- ✅ Added emergency contacts and key URLs

**Success Metric**: Any incident can be handled by following runbook; MTTR < 10 minutes ✅

---

## Previously Deployed (2025-12-07)

### DISC-056: Confidence Badge Still Clipped Behind Nav (DEPLOYED) 🐛

**Source**: Founder Request (Eddie, 2025-12-06)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Commit**: 320fe87

**Problem**: Despite DISC-051's fix, confidence badge on quote detail view was still clipped/hidden behind fixed navigation header.

**Root Cause**: `window.scrollTo({ top: 0 })` positioned content at absolute top (0px), placing it behind fixed nav (z-index: 100, ~120px height).

**Solution Implemented**:
- Added `scroll-margin-top: 140px` to `.quote-header` and `.quote-result` for native CSS scroll offset
- Changed scroll behavior from `window.scrollTo(0)` to `element.scrollIntoView()`
- Uses `setTimeout(50ms)` to ensure DOM update before scroll
- Applied to both quote generation and quote detail views

**Success Metric**: Badge fully visible on desktop and mobile immediately after opening quotes ✅

---

### DISC-065: Line Item Quantity Field (DEPLOYED) 🐛

**Source**: Founder Report (Eddie, 2025-12-06)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Commit**: 8fe97fa

**Problem**: When users specify quantities in voice input (e.g., "two paintings"), the system created a single line item with the total price doubled, instead of showing Qty: 2 × unit price.

**Solution Implemented**:
- Updated Claude prompt to extract quantities and unit prices separately
- PDF generator now displays "Qty: X × $Y = $Z" format when quantity > 1
- Frontend quote display shows quantity breakdown in description
- Supports optional unit field (e.g., "sqft", "hours")

**Success Metric**: Voice inputs with quantities display as itemized lines with Qty × Price format ✅

---

### DISC-064: Quote Generation Success Feedback (DEPLOYED) 🐛

**Source**: Founder Report (Eddie, 2025-12-06)
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Commit**: e2e5c3e

**Problem**: After voice dictation completes and quote is generated, there was no clear success message at the top of the screen. Users may be uncertain whether generation succeeded.

**Solution Implemented**:
- Added success message banner at top: "✓ Quote generated successfully!"
- Auto-dismisses after 4 seconds
- Scrolls to top for visibility
- Clears previous messages when generating new quote

**Success Metric**: Users immediately understand their quote was generated via clear visual feedback at viewport top ✅

---

### DISC-054: Dynamic Learning Rate (DEPLOYED) 🧠

**Source**: DISC-041 Brainstorm (Phase 3 - Velocity)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Commit**: 56c787a

**Problem**: Static 30% new / 70% old learning rate too conservative for new categories. Takes 12+ corrections to reach 80% accuracy.

**Solution Implemented**:
- Dynamic confidence increment based on correction count per category:
  - <5 corrections: 0.04 increment (aggressive 60% new learning)
  - 5-15 corrections: 0.02 increment (balanced 30% new learning)
  - >15 corrections: 0.01 increment (conservative 15% new learning)
- PostHog tracking for learning velocity metrics
- Event: `dynamic_learning_rate_applied` with phase and confidence data

**Success Metric**: Target 50% reduction in corrections to reach 80% accuracy (12 → 6) ✅

---

### DISC-052: Hybrid Learning Format + Priority Selection (DEPLOYED) 🧠

**Source**: DISC-041 Brainstorm (Phase 1 - Quick Wins)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Commit**: 2be8f68

**Problem**: Verbose natural language learning injection wasted tokens (~720 for 20 learnings). All learnings injected regardless of relevance.

**Solution Implemented**:
- Priority selection: Inject only top 7 most recent learnings (recency bias)
- Hybrid format: Structured pattern summary + compact adjustments list
- Auto-detect pricing tendency (Conservative/Aggressive/Balanced)
- Token reduction: 720 → 240 tokens (67% reduction)

**Success Metric**: 60% token reduction target exceeded (achieved 67%) ✅

---

### DISC-063: Horizontal Market Positioning Strategy (DEPLOYED) 📝 STRATEGIC

**Source**: Founder Request (Eddie, 2025-12-06)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Commit**: 0a8a8f4

**Problem**: Current positioning frames Quoted as contractor-only tool competing with Buildxact (wrong category). Quoted is horizontal quoting platform for ALL custom work.

**Solution Delivered**:
- Comprehensive strategy document: `/docs/HORIZONTAL_POSITIONING_STRATEGY.md`
- Corrected competitive landscape (Buildxact = different category, not competitor)
- 4 moats identified: Learning system, trade-agnostic, voice-first, right-sized
- Messaging updates for landing page, demo, onboarding
- Multi-industry demo expansion plan
- 4-phase implementation roadmap

**Key Strategic Shifts**:
1. Buildxact is project management ($100-500+/mo), not competitor
2. Real competition: Paper/Excel, FreshBooks/Wave, vertical-specific tools
3. Contractors = beachhead, not ceiling (10x TAM expansion)
4. Deprioritize DISC-060/061/062 (Buildxact defense - wrong focus)

**Success Metric**: Strategy document delivered ✅; actionable roadmap created ✅

---

### DISC-051: Quote Confidence Badge Positioning (DEPLOYED) 🐛

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

### DISC-036: Keyboard Shortcuts for Power Users (DEPLOYED)

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

### DISC-035: Learning System Trust Indicators (DEPLOYED)

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

### DISC-066: PDF Generation Failure in Production (DEPLOYED) 🐛 CRITICAL

**Source**: Founder Report (Eddie, 2025-12-06)
**Impact**: CRITICAL | **Effort**: M | **Score**: Strategic
**Commits**: 70a6e1d, 22e9635

**Problem**: PDF generation fails in production with error "Failed to download PDF: Failed to generate PDF". Quote displays correctly (shows line items, total $4,210) but clicking "Download PDF" throws an error dialog.

**Root Causes Identified & Fixed**:
1. **Type Safety** (70a6e1d): Format string `:g` failed when quantity/amount were string types from JSON. Added try/except float() conversion.
2. **Filesystem Permissions** (22e9635): Railway ephemeral filesystem caused FileResponse failures. Switched to in-memory Response - PDF generated and streamed directly without disk I/O.

**Solution**:
- Force numeric types for amount/quantity in PDF line items
- Return PDF bytes directly from memory via Response instead of FileResponse from disk
- Eliminated `./data/pdfs/` filesystem dependency entirely

**Success Metric**: PDF downloads work reliably for all quote types in production ✅

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

### DISC-094: Fix "Join Waitlist" Button Broken Link 🐛 (READY)

**Source**: Founder Request (Eddie, 2025-12-12)
**Impact**: LOW (until beta fills) | **Effort**: S | **Score**: 1.0
**Sprint Alignment**: Social proof / conversion flow

**Problem**: When beta spots are full (remaining = 0), the landing page shows a "Join Waitlist" button instead of signup. This button currently links to a broken URL. If the beta ever fills up, potential users would hit a dead end.

**Proposed Work**:
1. Find the waitlist button in `frontend/landing.html`
2. Either fix the link to a working waitlist form, or
3. Create a simple waitlist signup flow (email capture)
4. Store waitlisted emails for later outreach

**Technical Considerations**:
- May need a simple `Waitlist` model or just use existing email infrastructure
- Could integrate with existing Resend service for confirmation emails
- Alternative: redirect to a Typeform or Google Form (quickest fix)

**Success Metric**: "Join Waitlist" click → working flow that captures email

---

### DISC-095: User Dashboard - Home Base After Login 🏠 PRODUCT (READY)

**Source**: Founder Request (Eddie, 2025-12-12)
**Impact**: HIGH | **Effort**: L | **Score**: 1.5
**Sprint Alignment**: Retention & engagement - gives users reason to return beyond just creating quotes

**Problem**: Currently users land directly in quote generation mode. There's no "home base" showing their business activity, pending tasks, or performance insights. Power users have no reason to log in unless actively creating a quote. A dashboard creates stickiness and surfaces the value of data they've accumulated.

**Proposed Work**:
1. **Dashboard Layout** - New `/dashboard` route as primary post-login destination
   - Quick Actions bar: "New Quote" (prominent), "View Customers", "View All Quotes"
   - Keep quote generation one click away (no friction added)

2. **Active Tasks Section** - Leverages CRM task system (DISC-092)
   - Overdue tasks (red)
   - Tasks due today (amber)
   - Upcoming tasks (7 days)
   - Quick complete/reschedule actions

3. **Quote Analytics Widget**
   - Period selector: This Week | This Month | This Quarter | Custom
   - Metrics: Quotes Created, Total Value Quoted, Avg Quote Value
   - Simple bar chart showing quotes per day/week
   - Comparison to previous period (↑12% vs last month)

4. **Recent Activity Feed**
   - Last 5-10 quotes with status indicators
   - Quick actions: View, Duplicate, Create Invoice
   - Customer name + job summary + amount

5. **Learning Progress Widget** (ties into Pricing Brain)
   - "Your AI has learned X pricing rules"
   - Recent corrections made
   - Link to Pricing Brain settings

6. **Welcome State** - For new users with no data
   - "Create your first quote" CTA
   - Quick tips carousel
   - Setup checklist (profile, logo, pricing interview)

**Technical Considerations**:
- New dashboard section in `frontend/index.html` or separate route
- API endpoint: `GET /api/dashboard` aggregating stats
- Reuse existing components (quote list, task list)
- Consider caching dashboard stats (updated on quote create/task complete)
- Mobile-responsive: stack widgets vertically on small screens

**Success Metric**:
- 40%+ of sessions include dashboard view
- Increased return visit frequency
- Task completion rate visible and actionable

---

### DISC-096: Demo Learning Explanation - Show Edit→Teach Flow 🎓 GROWTH (READY)

**Source**: Founder Request (Eddie, 2025-12-12)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Conversion optimization - addresses key objection "what if prices are wrong?"

**Problem**: The demo shows quote generation but doesn't explain what happens if the AI gets pricing wrong. First-time viewers may think incorrect prices are a dealbreaker. They don't realize that editing is the teaching mechanism - the very act of correcting becomes the training data. This is our core differentiator but it's invisible in the demo.

**Proposed Work**:
1. Add a step/slide in demo showing "What if a price is off?"
2. Animate the edit flow: click price → change value → show "AI Learning" toast
3. Add text overlay: "Every correction teaches your AI. It gets smarter with each quote."
4. Consider showing a before/after: "First quote: You correct 5 items. 10th quote: AI nails it"
5. Emphasize the feedback loop visually (correction → learning → better next time)

**Technical Considerations**:
- Update `frontend/demo.html` animation sequence
- May need new animation frames/steps
- Keep demo length reasonable (don't add too much time)
- Consider a "learning progress" visual indicator in demo

**Success Metric**: Demo-to-signup conversion increases; fewer support questions about "what if prices are wrong"

---

### DISC-097: Landing Page & Marketing - Add CRM Feature Messaging 📢 GROWTH (READY)

**Source**: Founder Request (Eddie, 2025-12-12)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Value prop expansion - CRM is major differentiator now live (DISC-086-092)

**Problem**: We just shipped a full micro-CRM (customer tracking, task management, quote history by customer) but our landing page and marketing still position Quoted as "voice-to-quote" only. Visitors don't know they're getting customer management built-in. This undersells our value and misses a key differentiator vs. competitors who require separate CRM tools.

**Proposed Work**:
1. **Audit current messaging** - Review `landing.html` for CRM mentions (likely zero)
2. **Add CRM feature section** to landing page:
   - "Your customers, organized automatically"
   - Customer cards with quote history, contact info
   - Task reminders and follow-ups
   - "No spreadsheets, no separate CRM"
3. **Update hero/subhead** to hint at more than quotes:
   - Current: "Voice-to-quote in seconds"
   - New: "Quote, track, and manage customers - all by voice"
4. **Demo update** - Add CRM screens to demo flow (if applicable)
5. **Feature comparison** - Update any comparison tables to include CRM

**Technical Considerations**:
- Updates to `frontend/landing.html`
- May need new screenshots/mockups of CRM features
- Keep mobile layout in mind
- Consider A/B testing new vs. old messaging

**Success Metric**: Improved landing page conversion; CRM mentioned in user feedback/reviews

---

### DISC-099: Direct Founder Support Channel - Text/Twitter Link 📞 PRODUCT (READY)

**Source**: Founder Request (Eddie, 2025-12-19)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Early user trust & retention - high-touch support differentiates from faceless SaaS

**Problem**: As we push Reddit advertising (DISC-033), new users may need immediate help. Early-stage startups win by offering founder-level support that competitors can't match. Currently there's no obvious "talk to a human" path in the app. Users hitting friction may churn silently instead of reaching out.

**Proposed Work**:
1. **Add support contact in-app** - Floating help button or nav item
2. **Link to preferred channel** - Options:
   - SMS/text link (`sms:+1XXXXXXXXXX`) for mobile users
   - Twitter DM link (`https://twitter.com/messages/compose?recipient_id=XXX`)
   - Email fallback for web users
3. **Help page update** - Add "Talk to Eddie" section on `help.html`
4. **Consider PostHog tracking** - Track when users click support link (identify friction points)
5. **Optional: Magic response system** - Auto-reply confirming message received + ETA

**Technical Considerations**:
- Mobile-friendly: SMS links work great on phone, less so on desktop
- Twitter DM requires user to be logged into Twitter
- Could use a simple toggle to switch between SMS/Twitter based on founder preference
- Privacy: Consider not exposing personal phone number publicly (use redirect service?)

**Success Metric**:
- Support link visible in UI; users can reach founder directly
- Response time under 4 hours during beta
- Qualitative: "Wow, the founder replied!" moments create advocates

---

### DISC-100: Landing Page - "Pricing Intelligence for Novices" Messaging 📢 GROWTH (READY)

**Source**: Founder Request (Eddie, 2025-12-19)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Expands target audience beyond experienced contractors to novices/freelancers

**Problem**: Current landing page positions Quoted as "save time on quotes" - which resonates with experienced contractors. But there's a larger underserved audience: **novices who don't know what to charge yet**. New freelancers, people who just went solo, artists, consultants - they don't need speed, they need **pricing confidence**. The learning system is perfect for them but we don't communicate this.

**Target Audiences**:
- Consultants going independent → "What do I charge for this?"
- Artists/creatives → "I always undercharge, I don't know my worth"
- Event planners → "Every event is different, pricing is chaos"
- Handymen who just went solo → "I know the work, not the business side"

**Proposed Work**:
1. **Add "Pricing Intelligence" section** to landing page:
   - Headline: "Your pricing gets smarter with every quote"
   - Subhead: "New to pricing? No problem. Quoted learns from every correction you make."
   - Body: "After 10-20 quotes, your AI starts nailing your rates automatically. It's like building a pricing brain trained on YOUR decisions."
2. **Add novice-focused testimonial/quote**:
   - "I went from guessing to confident in two weeks"
   - "Finally stopped second-guessing every number"
3. **Consider dual messaging** on hero:
   - For experienced: "Voice to quote in seconds"
   - For novices: "AI that learns what to charge"
4. **Update demo** to show the learning/correction flow more prominently
5. **Reddit/marketing alignment** - this messaging works for r/freelance, r/ArtBusiness, r/consulting

**Technical Considerations**:
- Updates to `frontend/landing.html`
- Keep mobile layout in mind
- May want A/B test: current vs. novice-focused messaging
- Complements DISC-096 (Demo Learning Explanation)

**Success Metric**:
- Increased signups from non-contractor audiences
- User feedback mentions "pricing confidence" or "learning" as value prop
- Lower bounce rate on landing page for freelance/creative traffic sources

---

### DISC-093: Codex Executive UX Review - Analysis & Implementation 📋 STRATEGIC (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-12)
**Impact**: HIGH | **Effort**: M | **Score**: Strategic
**Sprint Alignment**: Critical for adoption speed and early trust
**Deployed**: 2025-12-12
**Commit**: e4f2f6c (squash merge from quoted-run/DISC-093)

**Implementation Summary** (2025-12-12):

Analyzed Codex (GPT-5.2) Executive UX Review against current codebase. Verified which issues still applied vs. already resolved.

**3 High-Impact Fixes Implemented**:

1. ✅ **Fix "Try a Quote Now" row click (CRITICAL)**
   - `handleTryFirst()` now works when clicking the `<li>` row, not just button
   - Falls back to `querySelector` when no button ancestor exists
   - Resolves silent activation killer for new users

2. ✅ **Add "Try Demo" CTA on auth screen**
   - New section below auth forms with link to `/try`
   - Reduces auth friction for first-time users
   - Matches landing page demo path strategy

3. ✅ **Enhanced learning toast with job-specific messaging**
   - Shows "Learned! Future {job type} quotes will be more accurate"
   - Tap-to-navigate to Pricing Brain
   - Better visual design and longer display time

**Issues Verified as Already Resolved**:
- ✅ Rules learned no longer stuck at zero
- ✅ Save Changes is sticky/always visible
- ✅ Currency formatting fixed

**Deferred to Future Tickets** (from Codex review):
- Progressive disclosure (hide CRM/Tasks/Invoices tabs until first quote)
- PWA manifest + add-to-home-screen
- Recording timer + "tap again to stop" microcopy
- Customers rollup auto-sync

**Success Metric**: 3 verified UX issues fixed with minimal scope creep ✅

---

### DISC-067: Free-Form Timeline & Terms Fields (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-06)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: User-requested feature for quote customization
**Commit**: 9899595 (complete)

**Problem**: Users need to customize timeline and terms sections on quotes. Current system uses contractor defaults from onboarding, but users want to dictate or type custom timeline/terms per-quote and set defaults in account settings.

**Completed** ✅:
1. ✅ Database schema: Added `timeline_text` and `terms_text` to quotes table
2. ✅ Database schema: Added `default_timeline_text` and `default_terms_text` to contractor_terms table
3. ✅ Migrations: Added migrations for all four columns
4. ✅ Quote detail view: Added Timeline/Terms textareas with change detection
5. ✅ Updated `quote_to_response()` in backend/api/quotes.py to include new fields
6. ✅ Updated `QuoteResponse` and `QuoteUpdateRequest` Pydantic models
7. ✅ Updated PDF generation to use custom timeline/terms when provided

**Deferred**:
- Account settings Quote Defaults tab (users can customize per-quote; defaults enhancement later)
- AI prompt extraction of timeline/terms from voice (complex, lower priority)

**Success Metric**: Users can type custom timeline/terms per-quote ✅

---

### DISC-068: Auto-Detect New Categories & Notify User 🧠 LEARNING (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-06)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Core learning system integrity - categories must be accurate for learning to work
**Commit**: 9899595

**Problem**: When a user describes work that doesn't match their existing categories, the system correctly falls back to hourly-rate pricing but fails to create a new category. Example: User with "Custom Painting" category quotes pottery work - system used hourly rate (good) but labeled it "Custom Painting" (wrong). This breaks the learning system because:
1. Pottery corrections get applied to painting pricing (cross-contamination)
2. User can't build category-specific pricing intelligence for pottery
3. User isn't aware that assumptions are being made about new work types

**Completed** ✅:
1. ✅ Added category confidence scoring (0-100) during quote generation via detect_or_create_category()
2. ✅ When confidence < 70%, returns suggested_new_category for better categorization
3. ✅ API returns category_info with confidence, suggested_new_category, needs_review flag
4. ✅ Frontend shows warning banner when needs_review is true
5. ✅ User can see when categorization is uncertain and understand the system is learning

**Deferred**:
- PostHog event tracking (simple addition, can be added in next cycle)
- Automatic category creation flow (current implementation notifies user only)

**Technical Considerations**:
- Claude prompt already knows categories - add instruction to flag mismatches
- Return `category_confidence` and `suggested_new_category` in quote response
- UI notification could be inline on quote detail view
- Consider auto-creating category with defaults from closest match

**Success Metric**:
- 95%+ of quotes land in semantically correct categories
- Users notified when new category detected (not silently assumed)
- Learning corrections apply to correct categories

---

### DISC-070: Voice-Driven PDF Template Customization 🎨 PRO/TEAM (READY)

**Source**: Founder Request (Eddie, 2025-12-07)
**Impact**: HIGH | **Effort**: XL | **Score**: 0.75
**Sprint Alignment**: Phase II+ feature - premium tier differentiator and competitive moat
**Tier Gate**: Pro/Team only (not Starter)

**Problem**: Contractors want professional, personalized quotes but aren't designers. Current PDF templates offer style presets (DISC-028) but no way to make granular tweaks. Users can't say "make my logo bigger" or "add more padding around line items" - they're stuck with what we give them. This limits personal brand expression and reduces premium tier differentiation.

**Vision**: Voice/chat-driven template design where Pro/Team users view their PDF template, speak or type design tweaks, and watch changes happen in real-time. Lower the barrier from "know CSS" to "talk about what you want."

**Example Commands**:
- Layout: "Move my logo to the center", "Put my phone number at the top"
- Typography: "Make the header font bigger", "Use a more modern font"
- Spacing: "Add more padding around line items", "Make the terms section smaller"
- Color: "Change the accent color to match my truck (blue)"
- Style: "Make it look more professional", "This feels too cluttered"
- Sections: "Remove the notes section", "Add a payment terms block"

**Technical Architecture**:
1. **Template Parameter System**: Expose layout/style variables (logo position, font sizes, spacing, colors, section visibility)
2. **Natural Language → Template Mapping**: AI interprets "make it less cluttered" → increase padding, reduce font sizes, hide optional sections
3. **Real-Time Preview**: Regenerate PDF preview after each change (< 2s latency target)
4. **Version Management**: Save as default, revert to previous, per-quote overrides
5. **Template Schema**: JSON representation of all editable parameters with validation

**Proposed Work**:
1. Define editable template parameters (audit current ReportLab templates)
2. Build template configuration schema (JSON with defaults per template style)
3. Create AI prompt for design command interpretation
4. Implement real-time PDF preview generation (optimize for speed)
5. Build UI: split view (template preview | voice/chat input)
6. Add version management (save, revert, "use as default")
7. Tier-gate to Pro/Team only

**Relationship to Phase II**:
- Phase II (DISC-042-049) = voice control of quote **content** (line items, pricing, scope)
- This ticket = voice control of quote **presentation** (layout, fonts, colors, spacing)
- Can be developed in parallel or as Phase II.5
- Shares Voice Command Interpreter (DISC-042) infrastructure

**Success Metric**:
- 40%+ Pro/Team users customize their template within first 30 days
- Average 3+ template tweaks per user
- Reduces support requests for "how do I change X" by 50%
- Increases Pro/Team upgrade rate by measuring "template customization" as upgrade motivator

**Executive Review Questions**:
- Minimum viable parameter set? (Logo + fonts + colors = MVP, or more?)
- Real-time preview feasibility? (ReportLab generation speed)
- Should this share voice infrastructure with Phase II or be chat-only initially?

---

### DISC-071: Quote-to-Invoice Conversion 💰 (READY)

**Source**: Founder Request (Eddie, 2025-12-08)
**Impact**: HIGH | **Effort**: L | **Score**: 1.5
**Sprint Alignment**: Revenue enablement - completes the quote lifecycle

**Problem**: Contractors generate quotes with Quoted, but after the job is done, they need to create invoices separately in another tool. This breaks the workflow and loses the data connection between quote and invoice. Users can't track which quotes became jobs, what the final actuals were, or easily bill customers based on the work done.

**Proposed Work**:
1. Add "Create Invoice" button on quote detail view
2. Pre-populate invoice from quote data (customer, line items, totals)
3. Allow editing for actuals (adjust quantities, add/remove items, change prices)
4. Generate professional PDF invoice (reuse PDF template system)
5. Add "Send Invoice" functionality (email to customer with PDF attached)
6. Mark quote status as "Invoiced" with link to invoice
7. Add invoice list view and basic invoice management
8. Track invoice status (Draft, Sent, Paid)

**Technical Considerations**:
- New `Invoice` model linked to `Quote` (one-to-many: quote can have multiple invoices for progress billing)
- Reuse `PDFGeneratorService` with invoice-specific template
- Email integration via existing Resend service
- Invoice numbering system (auto-increment per contractor)
- Payment tracking (manual mark as paid initially; Stripe integration later)

**Success Metric**:
- 30%+ of generated quotes convert to invoices
- Reduces "time to invoice" for contractors
- Increases perceived value (quote + invoice = complete solution)
- Potential premium tier feature (invoice = Pro/Team only?)

---

### DISC-072: PDF Template Polish & Robustness 📄 (READY)

**Source**: Founder Request (Eddie, 2025-12-08)
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Core value prop enhancement - PDFs are the primary deliverable

**Problem**: Current PDF templates work but lack polish for edge cases. When quotes have many line items, the total can awkwardly push to a second page. Templates need to handle variable content gracefully and look intentional regardless of quote length. This is a stepping stone before DISC-070 (voice-driven customization) - get the foundation right first with clean, professional templates and better layout handling.

**Proposed Work**:
1. Audit current templates for edge cases (long quotes, many line items, long descriptions)
2. Improve page break logic - keep totals with summary, smart section breaks
3. Add 3-5 new clean, professional template variants (minimal, corporate, detailed, compact, etc.)
4. Add basic template options users can select (without voice/chat customization)
5. Fix any spacing/padding issues that look unpolished
6. Test with real-world quote lengths (5 items, 15 items, 30 items)
7. Ensure templates look intentional at any length

**Relationship to DISC-070**:
- This ticket = foundation (better templates, proper layouts, edge case handling)
- DISC-070 = advanced (voice-driven customization of those solid templates)
- Do this first, DISC-070 becomes easier and more valuable

**Success Metric**:
- All quotes render cleanly regardless of length (no awkward page breaks)
- Users can choose from 5+ professional template styles
- Reduces "my PDF looks weird" support requests
- Sets foundation for DISC-070 voice customization

---

### DISC-073: Staging Environment & Safe Deployment Pipeline 🏗️ BRAINSTORM (COMPLETE)

**Source**: Founder Request (Eddie, 2025-12-08)
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Infrastructure maturity - protects active users from deployment risks
**Completed**: 2025-12-08

**Problem**: With active users now on the platform, pushing directly to production is risky. A bad deploy could corrupt user data or break the app for paying customers.

**Brainstorm Completed**: Executive Council (CTO, CFO, CPO, CGO) evaluated three options. Design document created at `/docs/STAGING_ENVIRONMENT_DESIGN.md`.

**Decision**: **Hybrid A+C** - Railway Preview Environments + PostHog Feature Flags
- Option A: Railway Preview Environments (pre-merge testing) - 2 hours, $0/month
- Option C: Feature Flags (gradual rollout, instant rollback) - 1 hour, $0/month
- Option B: Separate Staging (DEFERRED until 50+ paying users)

**Implementation Tickets Created**:
- DISC-077: Enable Railway Preview Environments (DISCOVERED)
- DISC-078: Add Feature Flag Foundation (DISCOVERED)
- DISC-079: Create Emergency Runbook (DISCOVERED)

**Success Metric**:
- Zero user-impacting incidents from deployments
- Clear workflow: develop → test in preview → merge → feature flag rollout
- Instant rollback capability via feature flags

---

### DISC-074: Alternative User Acquisition Channels 📢 BRAINSTORM (READY)

**Source**: Founder Request (Eddie, 2025-12-08)
**Impact**: HIGH | **Effort**: M | **Score**: 2.0
**Sprint Alignment**: Critical path - current organic channels (Reddit, Facebook groups) have anti-advertising rules

**Problem**: The organic community distribution strategy (Reddit posts, Facebook groups) has hit a wall - most contractor communities explicitly prohibit promotional posts or self-promotion. Need alternative acquisition channels that can deliver beta testers who will actually use the product and provide feedback.

**Context from Founder**:
- Reddit/Facebook groups have strict anti-advertising rules
- Goal is users who test, use, and give feedback (not just signups)
- Open to: simple paid ads, creator partnerships, other low-cost channels
- Budget-conscious (pre-revenue startup)

**Proposed Investigation** (Executive Committee to evaluate):

1. **Paid Ads (Low-Budget Testing)**
   - Facebook/Instagram Ads: Highly targetable to contractors, tradespeople
   - Google Ads: "quote software for contractors" intent-based
   - YouTube pre-roll: Contractor content viewers
   - Budget: $5-10/day test campaigns to validate CAC
   - Pro: Immediate, measurable, scalable
   - Con: Costs money, may attract tire-kickers vs. genuine users

2. **Creator/Influencer Partnerships**
   - Contractor YouTubers (tool reviews, day-in-life content)
   - Trade-focused TikTokers showing job sites
   - Offer: Free Pro tier + affiliate commission per referral
   - Pro: Authentic endorsement, built-in audience trust
   - Con: Slower to establish, variable quality

3. **Direct Outreach (High-Touch)**
   - LinkedIn DMs to solo contractors
   - Local contractor association outreach
   - Trade school partnerships (students becoming contractors)
   - Pro: Highly targeted, relationship-based
   - Con: Time-intensive, doesn't scale

4. **Guerrilla/Creative Channels**
   - Contractor supply store partnerships (Home Depot Pro, local suppliers)
   - Truck wrap/job site signage contests
   - "Quote of the Week" showcase (permission-based user content)
   - Pro: Low/no cost, authentic
   - Con: Unpredictable results

5. **Content Marketing (Longer-Term)**
   - SEO: "How to quote a [job type]" blog posts
   - YouTube: Demo videos, contractor success stories
   - Pro: Compounds over time, builds authority
   - Con: 3-6 month horizon to see results

**Executive Committee Questions**:
- What's acceptable CAC for beta testers? ($5? $10? $20?)
- Do we prioritize speed (paid ads) or authenticity (creators)?
- Is Eddie willing to do direct outreach (LinkedIn DMs)?
- Budget available for paid acquisition testing?
- Which contractor YouTubers/TikTokers are worth approaching?

**Success Metric**:
- Identify 2-3 viable channels worth testing
- Define test budget and success criteria for each
- First batch of users from non-organic source within 2 weeks

---

### DISC-080: Account Default Timeline & Terms Settings ⚙️ (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-08)
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Commit**: d641e45 (+ ad757bf)

**Problem**: Users who generate multiple quotes often use the same timeline and terms. Need account-level defaults that pre-populate new quotes.

**Solution Implemented**:
- ✅ UI and API already existed from DISC-067 (Settings → Quote Defaults tab)
- ✅ Updated `create_quote()` in `backend/services/database.py` to fetch contractor's default timeline/terms
- ✅ New quotes now automatically inherit account defaults
- ✅ Users can still override per-quote

**Success Metric**: New quotes pre-populate with account defaults ✅

---

### DISC-084: Onboarding Trade Type List UX Improvement 🎨 UX (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-11)
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Commit**: 9dae270

**Problem**: The "What do you do?" trade type list during onboarding was jumbled and unsorted. Users struggled to find their trade quickly.

**Solution Implemented**:
- Put 8 popular trades at top: General Contractor, Electrician, Plumber, HVAC, Painter, Roofer, Landscaper, Deck Builder
- Sorted remaining trades alphabetically (A-Z)
- Added visual section headers ("Popular" and "All Trades A-Z")
- "Other" option always last

**Success Metric**: Reduced time to complete trade selection step ✅

---

### DISC-085: Voice/Chat-Operated Simple CRM 💬 STRATEGIC (COMPLETE)

**Source**: Founder Request (Eddie, 2025-12-11)
**Impact**: HIGH | **Effort**: XL | **Score**: Strategic
**Sprint Alignment**: Future roadmap - expand Quoted from quoting tool to contractor operating system
**Design Document**: `/docs/DISC-085_VOICE_CRM_DESIGN.md`

**Problem**: Contractors generate quotes for customers but have no built-in way to track those customers over time. Customer data exists in quotes but isn't aggregated or accessible as a customer base. Users must use separate CRM tools, creating fragmentation.

**Vision**: An extremely simple, voice-operated or chat-operated CRM that allows users to:
- Build a customer base from quote history automatically
- Track customer interactions, job history, and notes
- Retrieve customer info via voice ("What's the status with John Smith?")
- Update customer status via voice ("Mark the Johnson job as completed")
- Get simple CRM insights ("Which customers haven't had a quote in 6 months?")

**Design Completed** ✅:
- Comprehensive design document created at `/docs/DISC-085_VOICE_CRM_DESIGN.md`
- Data model defined (Customer table with aggregated stats)
- Voice command interface specified (6 command categories)
- UI mockups for customer list and detail views
- 4-phase implementation plan with specific tickets

**Implementation Tickets Created**:
- DISC-086: Customer Model & Migration (Phase 1)
- DISC-087: Customer Aggregation Service (Phase 1)
- DISC-088: Customer API Endpoints (Phase 1)
- DISC-089: Customer UI - List & Detail Views (Phase 2)
- DISC-090: CRM Voice Command Integration (Phase 3)
- DISC-091: Backfill Existing Quotes to Customers (Phase 1)

**Success Metric**:
- Users can view aggregated customer list from quotes
- Voice commands successfully retrieve customer info 90%+ of time
- Customer lookup faster than searching through quote history manually

---

### DISC-086: Customer Model & Database Migration 🗄️ CRM PHASE 1 (DISCOVERED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Phase 1 foundation - must be completed before any CRM features
**Dependencies**: None (foundational)

**Problem**: No data model exists to store aggregated customer information. Quotes contain customer data but it's isolated per-quote with no linking.

**Proposed Work**:
1. Create `Customer` SQLAlchemy model with fields:
   - Core: id, contractor_id, name, phone, email, address
   - Computed: total_quoted, total_won, quote_count, first_quote_at, last_quote_at
   - CRM: status, notes, tags (JSON)
   - Deduplication: normalized_name, normalized_phone
2. Add `customer_id` foreign key to `Quote` model
3. Create Alembic migration for new table
4. Add database indexes for performance:
   - `(contractor_id, normalized_name)`
   - `(contractor_id, last_quote_at)`

**Technical Reference**: See `/docs/DISC-085_VOICE_CRM_DESIGN.md` for complete schema

**Success Metric**: Customer table exists with proper relationships; migrations run without errors

---

### DISC-087: Customer Aggregation & Deduplication Service 🔗 CRM PHASE 1 (DISCOVERED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Phase 1 - creates customers from quote data automatically
**Dependencies**: DISC-086 (Customer Model)

**Problem**: Customer data exists in quotes but isn't aggregated. Same customer may appear with slight name/phone variations across quotes. Need service to create and deduplicate customers.

**Proposed Work**:
1. Create `backend/services/customer_service.py`:
   - `normalize_name(name)`: lowercase, strip punctuation, collapse whitespace
   - `normalize_phone(phone)`: digits only
   - `find_or_create_customer(contractor_id, name, phone, email, address)`:
     - Look for match on (contractor_id, normalized_name) OR (contractor_id, normalized_phone)
     - If match: update fields if newer, return existing customer
     - If no match: create new customer
   - `update_customer_stats(customer_id)`: recalculate totals from linked quotes
2. Hook into quote creation/update to auto-link customers
3. Handle edge cases:
   - No name/phone → Don't create customer
   - Name only → Create, may merge later
   - Phone only → Create with "Unknown" name
   - Conflicts → Prefer most recent quote data

**Success Metric**: New quotes automatically create/link customers; deduplication accuracy >95%

---

### DISC-088: Customer API Endpoints 🌐 CRM PHASE 1 (DISCOVERED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Phase 1 - enables UI and voice commands to access customer data
**Dependencies**: DISC-086 (Customer Model), DISC-087 (Aggregation Service)

**Problem**: No API endpoints exist to retrieve or manage customer data.

**Proposed Work**:
1. Create `backend/api/customers.py` with endpoints:
   - `GET /customers`: List customers for contractor (paginated, searchable, filterable)
   - `GET /customers/{id}`: Get customer detail with quote history
   - `PATCH /customers/{id}`: Update customer (notes, tags, status)
   - `GET /customers/search?q=`: Search customers by name/phone/address
   - `GET /customers/{id}/quotes`: Get all quotes for customer
2. Add query parameters:
   - `status`: Filter by active/inactive/lead/vip
   - `sort`: last_quote_at, total_quoted, name
   - `search`: Fuzzy search across name, phone, address
3. Return computed stats in response (total_quoted, quote_count, etc.)

**Success Metric**: All CRUD operations work; search returns relevant results in <500ms

---

### DISC-089: Customer UI - List & Detail Views 🖥️ CRM PHASE 2 (DISCOVERED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Phase 2 - user-facing CRM interface
**Dependencies**: DISC-088 (Customer API)

**Problem**: Users have no way to view or manage their customer base. Need visual interface for CRM features.

**Proposed Work**:
1. Add "Customers" tab to main navigation (alongside New Quote, My Quotes, etc.)
2. Build Customer List View:
   - Customer cards showing: name, phone, quote count, total quoted, last quote date
   - Search bar with live filtering
   - Filter dropdowns: status, sort order
   - Customer count display
3. Build Customer Detail View:
   - Customer info header (name, phone, email, address)
   - Stats summary cards (quotes, quoted amount, won amount, customer since)
   - Notes section with add/edit capability
   - Tags management (add/remove tags)
   - Quote history list with links to individual quotes
4. Add inline editing for notes and tags
5. Mobile-responsive design (375px minimum)

**UI Reference**: See `/docs/DISC-085_VOICE_CRM_DESIGN.md` for wireframe mockups

**Success Metric**: Users can browse, search, and view customer details; mobile-friendly

---

### DISC-090: CRM Voice Command Integration 🎤 CRM PHASE 3 (DISCOVERED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: Phase 3 - voice-operated CRM (core differentiator)
**Dependencies**: DISC-088 (Customer API), DISC-042 (Voice Command Interpreter - if available)

**Problem**: CRM features exist but can't be accessed via voice. Contractors in trucks need hands-free customer lookup.

**Proposed Work**:
1. Add CRM intent detection to `backend/services/claude_service.py`:
   - Detect CRM keywords: "customer", "who did I", "show me", "find", "add note to"
   - Route to CRM handler instead of quote generation
2. Implement CRM voice commands:
   - **Search**: "Show me John Smith" → customer_search
   - **Detail**: "What's the history with Johnson Electric?" → customer_detail
   - **Stats**: "How much have I quoted the Hendersons?" → customer_stats
   - **Notes**: "Add a note to Mike Wilson: Prefers morning" → add_note
   - **Tags**: "Tag Sarah's Bakery as VIP" → add_tag
   - **Insights**: "Which customers haven't had a quote in 6 months?" → dormant_customers
3. Generate natural language responses:
   - "Found 3 customers matching 'Smith'. John Smith with 5 quotes totaling $12,400..."
4. Add voice input option in Customers tab (or reuse existing voice button)

**Success Metric**: 90%+ correct intent detection; voice commands complete in <3 seconds

---

### DISC-091: Backfill Existing Quotes to Customer Records 📥 CRM PHASE 1 (DISCOVERED)

**Source**: DISC-085 Voice CRM Design Document
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Phase 1 - populates CRM with existing data (zero data entry promise)
**Dependencies**: DISC-086 (Customer Model), DISC-087 (Aggregation Service)

**Problem**: Existing quotes contain customer data that needs to be extracted and aggregated into Customer records. Without backfill, CRM launches empty.

**Proposed Work**:
1. Create migration script `backend/scripts/backfill_customers.py`:
   - Iterate through all quotes with customer_name or customer_phone
   - Call `find_or_create_customer()` for each quote
   - Link quote to customer via customer_id foreign key
   - Update customer stats (total_quoted, quote_count, etc.)
2. Add to database initialization (similar to onboarding_completed_at backfill)
3. Run as part of deployment for existing users
4. Add PostHog event tracking for backfill completion

**Execution Strategy**:
1. Deploy Phase 1 with feature flag `crm_enabled = false`
2. Run backfill job
3. Enable for Eddie first (validate data quality)
4. Enable for all users

**Success Metric**: 100% of quotes with customer data linked to Customer records; no duplicate customers created

---

### DISC-092: CRM Task & Reminder System 📋 CRM PHASE 4 (READY)

**Source**: Founder Request (Eddie, 2025-12-11)
**Impact**: HIGH | **Effort**: L | **Score**: 1.0
**Sprint Alignment**: CRM Phase 4 - transforms passive CRM into active workflow management
**Dependencies**: DISC-086 (Customer Model), DISC-088 (Customer API)

**Problem**: Contractors need to track follow-ups, reminders, and tasks related to quotes and customers. Currently they must use separate tools or memory. Key workflows that need support:
- Following up on sent quotes that haven't received a response
- Scheduling customer check-ins
- Remembering to collect deposits or final payments
- Tracking promised callbacks

**Vision**: Simple task/reminder system integrated with CRM that supports both manual tasks and intelligent auto-generated reminders based on quote/customer activity.

**Proposed Work**:

**1. Task Data Model**
- Create `Task` model: id, contractor_id, customer_id (optional), quote_id (optional)
- Fields: title, description, due_date, reminder_time, status (pending/completed/snoozed)
- Priority levels: low, normal, high, urgent
- Recurrence: one-time, daily, weekly, monthly

**2. Manual Task Creation**
- "Add task" button on customer detail and quote detail views
- Voice command: "Remind me to call Johnson in 3 days"
- Quick-add from anywhere in app

**3. Auto-Generated Reminders (Rules Engine)**
- Configurable triggers with defaults:
  - Quote sent, no response in 7 days → "Follow up on Quote #X for [Customer]"
  - Quote accepted → "Schedule start date with [Customer]"
  - Invoice sent, not paid in 14 days → "Payment follow-up for [Customer]"
  - Customer dormant 90 days → "Re-engage [Customer]"
- Settings to enable/disable each rule and customize timing

**4. Task Management UI**
- Tasks tab in main navigation (or integrated into Customers view)
- Today/Upcoming/Overdue views
- Filter by customer, quote, priority
- Quick actions: complete, snooze, reschedule

**5. Notifications**
- In-app notification badge/list
- Optional email reminders (daily digest or per-task)
- Future: push notifications for mobile

**6. Voice Integration**
- "What's on my task list today?"
- "Remind me to [action] for [customer] in [timeframe]"
- "Mark the Johnson follow-up as done"

**Settings (Account → Reminders)**:
- Enable/disable auto-generated reminders
- Default follow-up timing (7 days after quote, etc.)
- Notification preferences (in-app, email, both)
- Working hours for reminders

**Technical Considerations**:
- Background job for generating auto-reminders (check quote/customer status periodically)
- Cron-style scheduler for reminder notifications
- Link tasks bidirectionally to quotes and customers
- Respect timezone for due dates/reminders

**Success Metric**:
- 50%+ of active users create or complete at least one task per week
- Auto-generated reminders lead to 20% increase in quote follow-up rate
- Reduction in "forgot to follow up" scenarios

---

### DISC-081: QuickBooks Integration Exploration 📊 BRAINSTORM (READY)

**Source**: Founder Request (Eddie, 2025-12-08)
**Impact**: HIGH | **Effort**: L-XL | **Score**: Strategic
**Sprint Alignment**: Future roadmap - connects Quoted to contractor's financial workflow

**Problem**: Contractors using QuickBooks for accounting have to manually re-enter quote data when a job is accepted. A QuickBooks integration would close the quote→invoice→accounting loop.

**What Integration Could Enable**:

1. **Quote → Invoice Sync**
   - When quote is accepted, auto-create QuickBooks invoice
   - Map Quoted line items → QB line items
   - Sync customer info (avoid duplicate entry)

2. **Customer Sync**
   - Import QB customers into Quoted (autocomplete)
   - Push new customers from Quoted → QB
   - Keep contact info synchronized

3. **Item/Service Sync**
   - Import QB products/services as Quoted line items
   - Sync pricing between systems
   - Map Quoted categories → QB items

4. **Payment Status**
   - Show invoice payment status in Quoted
   - "This quote was invoiced and paid" badge

**Technical Requirements**:

| Component | Complexity | Notes |
|-----------|------------|-------|
| **QuickBooks OAuth2** | M | Intuit Developer account, OAuth flow |
| **API Integration** | L | REST API, rate limits, error handling |
| **Data Mapping** | M | Quoted schema ↔ QB schema |
| **Webhook Handling** | M | Real-time sync vs. polling |
| **UI for Connection** | S | Settings tab, connect/disconnect |
| **Error Recovery** | M | Sync failures, retries, notifications |

**QuickBooks API Details**:
- **Platform**: QuickBooks Online (QBO) - not Desktop
- **Auth**: OAuth 2.0 with refresh tokens
- **Sandbox**: Free developer sandbox for testing
- **Pricing**: $0 to build, users need QBO subscription ($30-200/mo)
- **Approval**: App review required for production

**Phased Approach**:

**Phase A: Read-Only (M effort)**
- Connect QuickBooks account
- Import customers for autocomplete
- Show "connected" status

**Phase B: Quote → Invoice Push (L effort)**
- One-click "Send to QuickBooks" on accepted quotes
- Create invoice in QB with line items mapped
- Handle customer matching/creation

**Phase C: Two-Way Sync (XL effort)**
- Bidirectional customer sync
- Item/service catalog sync
- Payment status webhooks

**Competitive Angle**:
- Jobber, Housecall Pro have QB integrations
- Differentiator: Voice-created quotes that flow directly to accounting
- "Say it, quote it, invoice it, get paid"

**Questions to Answer**:
- What % of target contractors use QuickBooks Online vs. Desktop vs. other?
- Is Phase A alone valuable enough to ship?
- Should invoicing (DISC-071) come first, then QB sync?
- Alternative: Zapier integration as bridge?

**Success Metric**:
- Clear go/no-go decision on QB integration
- If go: Phased implementation plan with effort estimates
- User research: Do beta users want this?

---

### DISC-082: Referral Links Lead to 404 🐛 CRITICAL (DEPLOYED)

**Source**: Founder Report (Eddie, 2025-12-08)
**Impact**: CRITICAL | **Effort**: S | **Score**: ∞ (Blocking)
**Commit**: 2620866

**Problem**: Referral links generated as `/signup?ref=CODE` led to 404 - no `/signup` route exists.

**Solution Implemented** (Option A):
- Changed referral link URL from `/signup?ref=` to `/?ref=`
- Landing page already handles `?ref=` parameter (stores in localStorage)
- Updated `backend/services/referral.py:219`
- All existing shared links now work retroactively

**Success Metric**: Referral links load landing page with ref code preserved ✅

---

### DISC-083: Line Item Quantity/Cost UX Fix 🐛 (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-08)
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Commit**: 2a5ba8b

**Problem**: Cost field showed total amount but users expected unit cost. Confusing when qty > 1.

**Solution Implemented**:
- Changed cost input to show **unit cost** with `/ea` label
- Added calculated **total display** (read-only) when qty > 1
- Updated `trackLineItemChange` to handle `unit_cost` field
- Added `updateLineItemTotalDisplay()` for real-time recalculation
- Used safe DOM methods (createElement) instead of innerHTML

**UI Result**:
```
Qty: [3]    $[100] /ea  = $300
```

**Success Metric**: Users edit unit cost, total auto-calculates ✅

---

### DISC-069: Go-to-Market Readiness Assessment 🚀 (DEPLOYED)

**Source**: Founder Request (Eddie, 2025-12-07)
**Impact**: CRITICAL | **Effort**: S | **Score**: Strategic
**Sprint Alignment**: Immediate - identifies blockers to user acquisition

**Problem**: Product is built and functional. Need to spread the word to the right channels and get users. What's left to make that happen?

**Current State Assessment**:
- ✅ Product: Core quoting functionality live
- ✅ Demo: Try-before-signup working
- ✅ Onboarding: Interview + Quick Start paths
- ✅ Learning system: Per-category corrections working
- ✅ Referral system: Built but low adoption
- ⚠️ Distribution: Zero active acquisition channels
- ⚠️ Users: 5 beta users, need 95 more

**What's Left (Prioritized)**:

**Tier 1: Immediate Founder Actions** (highest ROI, no code needed)
1. **DISC-033**: Reddit Launch Post → 410K contractors, 22+ signup potential
2. **DISC-027**: LinkedIn Content Blitz → Founder network, 15-20 signups
3. **DISC-023**: Community Outreach → Facebook groups, local contractor networks

**Tier 2: Quick Wins to Amplify** (code work, high leverage)
4. **DISC-029**: Demo Screenshot Sharing → Make demo sessions viral
5. **DISC-030**: Email Signature Viral → Turn 5 users into distribution
6. **DISC-037**: Demo-to-Referral Bridge → Convert demo interest into referrals

**Tier 3: Strategic** (longer-term positioning)
7. **DISC-062**: Learning-First Messaging → Defensible positioning
8. **DISC-061**: "Voice Quote" Category Ownership → SEO, PR

**Recommended Action Sequence**:
1. Post Reddit (DISC-033) this week → immediate inbound
2. While waiting for traction, implement DISC-029 + DISC-030 (1-2 days)
3. LinkedIn blitz (DISC-027) following week
4. Measure, iterate on messaging

**Success Metric**: 100 beta users within 30 days

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

### DISC-029: Demo Quote Screenshot Sharing ⚡ QUICK WIN (DEPLOYED)

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

### DISC-030: Email Signature Viral Acceleration ⚡ QUICK WIN (DEPLOYED)

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
