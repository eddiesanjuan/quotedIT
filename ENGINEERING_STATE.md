# Engineering State

**Last Updated**: 2025-12-03 03:30 PST
**Updated By**: CEO (AI) - Autonomous Cycle 3

---

## Current Sprint

**Sprint**: 2 (100 Users)
**Goal**: 100 active beta testers by December 16
**Dates**: 2025-12-02 to 2025-12-16
**Strategy Doc**: `BETA_SPRINT.md`

---

## Deployment Status

| Environment | URL | Status | Version |
|-------------|-----|--------|---------|
| **Production** | https://web-production-0550.up.railway.app | LIVE | a1e6e66 |
| **Custom Domain** | https://quoted.it.com | LIVE (SSL ACTIVE) | a1e6e66 |

**Railway Project**: Connected to main branch, auto-deploys on push

**Environment Variable**: `ENVIRONMENT=production` is set ✓ (HTTPS redirect and CORS active)

---

## In Progress

| Ticket | Description | Assignee | Status | Blockers |
|--------|-------------|----------|--------|----------|
| ~~PAY-001~~ | ~~Payment Infrastructure (Stripe)~~ | ~~Backend Engineer~~ | **COMPLETE** | Committed cb1e311 |
| ~~PAY-002~~ | ~~Trial Logic & Quote Limits~~ | ~~Backend Engineer~~ | **COMPLETE** | Included in PAY-001 |
| ~~PAY-003~~ | ~~Billing UI~~ | ~~Frontend Engineer~~ | **COMPLETE** | Committed b4e9fdc |
| ~~PAY-004~~ | ~~Email System (Resend)~~ | ~~Backend Engineer~~ | **COMPLETE** | Committed 33fa641 |
| ~~PAY-005~~ | ~~Referral System~~ | ~~Backend Engineer~~ | **REPLACED** | See GROWTH-002 |
| ~~PAY-006~~ | ~~Terms of Service + Privacy Policy~~ | ~~CTO~~ | **COMPLETE** | Deployed 325fb25 |
| ~~FEAT-001~~ | ~~Pricing Brain Management~~ | ~~Backend + Frontend~~ | **COMPLETE** | Committed 1361539 + 6c7c94a |
| ~~FEAT-002~~ | ~~Edit Customer Info on Existing Quotes~~ | ~~Frontend + Backend~~ | **COMPLETE** | Committed fa0f7a4 + 28a98f9 |
| ~~FIX-001~~ | ~~Randomize Slot Animation Order~~ | ~~Frontend~~ | **COMPLETE** | Committed 59883ef |
| ~~GROWTH-001~~ | ~~Demo Mode (Try Before Signup)~~ | ~~Backend~~ | **COMPLETE** | Committed c7a91d3 (backend done, frontend needed) |
| ~~GROWTH-002~~ | ~~Referral System with Rewards~~ | ~~Backend + Frontend~~ | **COMPLETE** | Committed 7bc67db + 2db4d5d |
| ~~GROWTH-003~~ | ~~Share Quote (Email/SMS/Link)~~ | ~~Backend + Frontend~~ | **COMPLETE** | Committed 408586f |
| ~~GROWTH-004~~ | ~~Landing Page Testimonials~~ | ~~Frontend~~ | **COMPLETE** | Committed 21f3291 |
| ~~GROWTH-005~~ | ~~"Powered by Quoted" Branding~~ | ~~Frontend~~ | **COMPLETE** | Committed 21f3291 |
| ~~CONVERT-001~~ | ~~Analytics (PostHog)~~ | ~~Backend + Frontend~~ | **COMPLETE** | Committed 75eac78 |
| ~~CONVERT-002~~ | ~~Enhanced Empty States~~ | ~~Frontend~~ | **COMPLETE** | Committed 8f7b635 |
| ~~CONVERT-003~~ | ~~First Quote Celebration~~ | ~~Frontend~~ | **COMPLETE** | Committed 21f3291 |
| ~~RETAIN-001~~ | ~~Engagement Email Series~~ | ~~Backend~~ | **COMPLETE** | Committed 732c643 |
| ~~RETAIN-002~~ | ~~Dormancy Re-engagement Emails~~ | ~~Backend~~ | **COMPLETE** | Committed d9b7a36 |
| ~~INFRA-001~~ | ~~Sentry Error Tracking~~ | ~~Backend + Frontend~~ | **COMPLETE** | Committed 75eac78 |
| ~~INFRA-002~~ | ~~Mobile Responsiveness Audit~~ | ~~Frontend~~ | **COMPLETE** | Committed c6b266a |
| ~~INFRA-003~~ | ~~FAQ/Help Section~~ | ~~Frontend~~ | **COMPLETE** | Committed 7d4c86e |
| ~~ONBOARD-001~~ | ~~Industry/Trade Selection Step~~ | ~~Frontend + Backend~~ | **COMPLETE** | Committed 5d0e693 + 19e304f |
| ~~ONBOARD-002~~ | ~~Guided Quick Setup with Templates~~ | ~~Frontend + Backend~~ | **COMPLETE** | Committed a1e6e66 |
| ~~ONBOARD-003~~ | ~~Industry Pricing Template Library~~ | ~~Backend~~ | **COMPLETE** | Committed 18284c6, 9eba403 |
| ~~ONBOARD-004~~ | ~~Interview Type C Coaching Mode~~ | ~~Backend (prompts)~~ | **COMPLETE** | Committed 5219509 |
| ~~ONBOARD-005~~ | ~~Expand Trade Defaults (20+ industries)~~ | ~~Backend~~ | **COMPLETE** | Committed 48cb784 |
| ~~UX-001~~ | ~~Improve Quote Input Placeholder Text~~ | ~~Frontend~~ | **COMPLETE** | Committed 5610036 |
| ~~FEAT-003~~ | ~~Pricing Brain Global Settings Editor~~ | ~~Frontend + Backend~~ | **COMPLETE** | Committed a7b12c2 |
| ~~BUG-002~~ | ~~Share Quote Email Fails to Send~~ | ~~Backend~~ | **COMPLETE** | Committed 709111d |
| ~~BUG-003~~ | ~~Demo Page Frontend Missing~~ | ~~Frontend~~ | **COMPLETE** | Committed 8a6770f |
| ~~UX-002~~ | ~~Reframe Onboarding to Recommend Interview~~ | ~~Frontend~~ | **COMPLETE** | Committed 2460980 |
| ~~BUG-001~~ | ~~Help Button Navigation Broken~~ | ~~Frontend~~ | **COMPLETE** | Committed e0cb0e5 |
| ~~ONBOARD-006~~ | ~~Expand Industries Beyond Construction~~ | ~~Frontend + Backend~~ | **COMPLETE** | Committed 03993dd |
| ~~ONBOARD-007~~ | ~~Quick Setup Form/Tips Mismatch~~ | ~~Frontend + Backend~~ | **COMPLETE** | Committed 03993dd |
| ~~ONBOARD-008~~ | ~~Ensure Onboarding Path Consistency~~ | ~~Backend~~ | **COMPLETE** | Committed 1fc11fe |
| ~~UX-003~~ | ~~Improve Landing Page Headline~~ | ~~Frontend~~ | **COMPLETE** | Committed 66b25b9 |
| ~~UX-004~~ | ~~Add Product Demo Animation to Landing Page~~ | ~~Frontend~~ | **COMPLETE** | Committed 2c7244e |
| ~~BUG-004~~ | ~~Demo Page Broken + Strategic Review~~ | ~~Frontend + Executive~~ | **BUG FIXED** | Strategic direction pending DECISION-005 |
| ~~BUG-005~~ | ~~Mobile Formatting & Layout Issues~~ | ~~Frontend~~ | **COMPLETE** | App nav + landing page mobile fixes |
| DISC-020 | Exit-Intent Survey on Landing Page | Frontend | **COMPLETE** | Committed (pending push) |

---

## BUG-004: Demo Page Broken + Strategic Review (BUG FIXED - DECISION PENDING)

**Scope**: Frontend (2h) + Executive Council Review
**Priority**: HIGH (broken feature + strategic concern from Founder)
**Reported By**: Founder (2025-12-02)

**Bug**: ~~JavaScript error on demo page load~~ **FIXED**
- Root cause: Frontend used `item.total` and `item.item` but API returns `item.amount` and `item.name`
- Fix: Updated demo.html to use correct field names + null safety

**Strategic Concern from Founder**:
> "When I think about it, I don't know how much I really love the idea without at least a big disclaimer stating that it would not work nearly as good as it would if you had done the interview. To be honest, I don't really know how it would work without an interview."

**Current Status**:
- ✅ Bug fixed (correct field names, null safety)
- ✅ Disclaimer added: "Demo uses generic pricing. Sign up for personalized quotes that learn YOUR pricing."
- ⏳ Strategic direction: DECISION-005 in DECISION_QUEUE.md

**Executive Council Result (2-2 Split)**:
- CGO + CPO: Option B (Video/Animation) - better conversion without accuracy risk
- CFO + CMO: Option C (Remove Demo) - focus on interview as competitive advantage

**Awaiting**: Founder decision on B vs C in DECISION_QUEUE.md

---

## BUG-005: Mobile Formatting & Layout Issues (COMPLETE)

**Scope**: Frontend (3-4h)
**Priority**: HIGH (user-facing visual bugs)
**Reported By**: Founder (2025-12-02)

**Problem**: Multiple mobile layout issues identified after recent feature additions (beta counter, trial banners, modals). Elements overlapping, z-index conflicts, and content being covered.

### ✅ FIXED (2025-12-02)

**App Interface (index.html) - Nav Overlapping**
- **Issue**: Desktop nav tabs were showing on mobile due to inline JS styles overriding CSS media query
- **Fix**: Added `!important` to mobile media query, created mobile bottom navigation bar
- **Details**:
  - Desktop nav hidden on ≤640px with `!important` to override inline styles
  - Added bottom nav bar with icons (New Quote, My Quotes, Account)
  - Synced active states between desktop and mobile nav
  - Added safe-area-inset-bottom for notched phones
  - Added extra padding to main content on mobile for nav bar

### ✅ FIXED (2025-12-02) - Landing Page

**Landing Page Mobile Layout (landing.html)**
- **Issue**: Beta counter overlapping hero content on mobile
- **Fix**: Added progressive hero padding and beta counter adjustments at all breakpoints
- **Details**:
  - Hero padding-top: 120px (600px), 110px (480px), 100px (375px)
  - Beta counter position/sizing adjustments at each breakpoint
  - Referral banner offset handling via `.has-banner` class
  - Z-index stacking verified correct (nav: 100, beta: 99)

**Commits**:
- `fe99329` - App nav mobile fix (bottom nav bar)
- `687d026` - Landing page mobile layout fixes

---

## ~~BUG-001: Help Button Navigation Broken~~ (COMPLETE ✓)

**Scope**: Frontend (1h)
**Priority**: HIGH (broken user-facing feature)
**Reported By**: Founder (2025-12-02)

**Problem**: The Help button in the navigation doesn't lead anywhere when clicked. The help.html page exists but the navigation isn't wired up correctly.

**Implementation**:
1. [ ] Find Help button in frontend navigation
2. [ ] Ensure it links to /help or help.html
3. [ ] Verify navigation works on all pages (index, landing, etc.)
4. [ ] Test on mobile

---

## BUG-002: Share Quote Email Fails to Send (READY)

**Scope**: Backend (2h)
**Priority**: HIGH (blocks viral growth feature)
**Reported By**: Founder (2025-12-02)

**Problem**: When users try to share a quote via email (GROWTH-003), the email fails to send. This breaks the viral loop.

**Investigation**:
1. [ ] Check Resend API key is configured in Railway
2. [ ] Check email service error handling in `backend/api/share.py`
3. [ ] Verify email template renders correctly
4. [ ] Check Resend dashboard for failed sends
5. [ ] Add better error logging/reporting

---

## BUG-003: Demo Page Frontend Missing (READY)

**Scope**: Frontend (4h)
**Priority**: HIGH (blocks "try before signup" conversion)
**Reported By**: Founder (2025-12-02)

**Problem**: GROWTH-001 implemented the demo backend (c7a91d3) but the frontend was never built. The demo page doesn't exist, so users can't try the product before signing up.

**What Exists**:
- `POST /api/demo/quote` - Backend endpoint (rate limited, no auth)
- Demo uses generic contractor profile

**What's Missing**:
- `/demo` route in frontend
- Demo page UI with:
  - Voice recorder OR text input
  - Quote generation (using demo endpoint)
  - "DEMO" watermark on output
  - CTA: "Create free account to save this quote"

**Implementation**:
1. [ ] Create `frontend/demo.html`
2. [ ] Copy quote input UI from main app
3. [ ] Wire to `/api/demo/quote` endpoint
4. [ ] Add "DEMO" watermark to results
5. [ ] Add prominent signup CTA
6. [ ] Link from landing page ("Try it now - no signup required")

---

## ONBOARD-006: Expand Industries Beyond Construction (READY)

**Scope**: Frontend + Backend (3h)
**Priority**: MEDIUM (market expansion)
**Requested By**: Founder (2025-12-02)

**Problem**: The industry selection is too construction-centric. Quoted could work for many service businesses that need to quote jobs, not just contractors:
- Freelancers (designers, developers, writers)
- Event services (DJs, photographers, caterers, planners)
- Personal services (tutors, coaches, trainers)
- Creative services (videographers, musicians)

**Implementation**:
1. [ ] Add new industry categories to `backend/api/onboarding.py`:
   - Freelance/Creative
   - Event Services
   - Personal Services
2. [ ] Add specific trades under each:
   - Photographer, Videographer, Graphic Designer, Web Developer
   - DJ, Caterer, Event Planner, Florist
   - Personal Trainer, Tutor, Coach, Consultant
3. [ ] Create pricing templates for these industries in `backend/data/pricing_templates.py`
4. [ ] Add appropriate icons for new categories
5. [ ] Update trade defaults for new industries

---

## ONBOARD-007: Quick Setup Form/Tips Mismatch (READY)

**Scope**: Frontend + Backend (4h)
**Priority**: HIGH (confuses users during onboarding)
**Requested By**: Founder (2025-12-02)

**Problem**: The Quick Setup form fields don't match the pricing approach recommended in the tips. For example:
- Tips say: "Cabinet makers use linear foot pricing at $400-800/LF"
- Form asks: Hourly rate, material markup, minimum job

This creates cognitive dissonance - the advice doesn't match what you're being asked to enter.

**Solution**: Make Quick Setup form fields DYNAMIC based on industry template's `recommended_approach`:

**Hourly-Based Industries** (electrician, plumber, handyman):
- Hourly Labor Rate
- Helper Rate (optional)
- Service Call Minimum
- Material Markup %

**Linear Foot Industries** (cabinet maker, countertops):
- Base Rate per Linear Foot
- Material Tier Adjustments
- Minimum Project Amount

**Square Foot Industries** (painter, flooring):
- Rate per Square Foot
- Complexity Multipliers
- Minimum Project Amount

**Per-Unit Industries** (roofer - per square, tree service - per tree):
- Rate per Unit
- Unit Type
- Minimum Job

**Implementation**:
1. [ ] Add `recommended_approach` field handling in Quick Setup JS
2. [ ] Create field templates for each approach type
3. [ ] Render appropriate fields based on industry template
4. [ ] Update `quick_setup()` backend to accept varied field structures
5. [ ] Map varied fields to consistent pricing_model storage

---

## ONBOARD-008: Ensure Onboarding Path Consistency (READY)

**Scope**: Backend (4h)
**Priority**: HIGH (data quality/user experience)
**Requested By**: Founder (2025-12-02)

**Problem**: Quick Setup and Interview should produce CONSISTENT pricing profiles, just with different levels of completeness:
- Interview → Comprehensive profile (all fields filled, nuanced)
- Quick Setup → Essential profile (core fields, learns more over time)

Currently, it's unclear if both paths produce pricing_models that work the same way in quote generation.

**Acceptance Criteria**:
1. Both paths store data in same `pricing_model` format
2. Quote generation works identically regardless of onboarding path
3. Quick Setup users have clear path to "complete" their profile later
4. Interview users don't have redundant/conflicting data

**Implementation**:
1. [ ] Audit `quick_setup()` output format vs interview output format
2. [ ] Ensure both write to same `pricing_model` schema
3. [ ] Document which fields are "essential" vs "learned over time"
4. [ ] Add "Complete Your Profile" prompt for Quick Setup users after first 5 quotes
5. [ ] Verify quote generation uses both profiles consistently

---

## UX-003: Improve Landing Page Headline (READY)

**Scope**: Frontend (1h)
**Priority**: MEDIUM (brand/messaging polish)
**Requested By**: Founder (2025-12-02)

**Problem**: The current headline "Turn Voice Notes into Professional Budget Quotes in Seconds" doesn't read well. It's functional but not memorable or evocative.

**Current Headline**:
> "Turn Voice Notes into Professional Budget Quotes in Seconds"

**Proposed Change**:
Lead with something more evocative, then follow with the functional description:

**Option A** (Founder's suggestion):
> **"Your quotes, spoken into existence."**
> Turn voice notes into professional quotes in seconds.

**Option B**:
> **"Speak it. Quote it. Done."**
> Turn job site voice notes into professional quotes instantly.

**Option C**:
> **"From voice to invoice."**
> Describe the job, get the quote. That simple.

**Implementation**:
1. [ ] Review current headline in `frontend/landing.html`
2. [ ] Implement two-line headline structure (evocative + functional)
3. [ ] Adjust typography hierarchy (larger evocative line, smaller functional line)
4. [ ] Test on mobile to ensure readability

---

## UX-004: Add Product Demo Animation to Landing Page (READY)

**Scope**: Frontend (6h)
**Priority**: MEDIUM (conversion optimization)
**Requested By**: Founder (2025-12-02)

**Problem**: The landing page shows static content. A visual demo of the product flow would help visitors understand the value proposition immediately.

**What to Build**: A ~15-second looping animation showing the complete product flow:

**Animation Sequence**:
1. **Interview/Onboarding** (~3s) - Quick chat setting up pricing
2. **Recording a Job** (~3s) - User clicks record, speaks job description
3. **Quote Generated** (~3s) - Professional PDF appears with line items
4. **Editing/Feedback** (~3s) - User adjusts a price, system learns
5. **Pricing Brain View** (~3s) - Show the learned pricing model
6. **Loop restart** - Seamless transition back to step 1

**Technical Approach Options**:

**Option A: CSS/JS Animation (Recommended)**
- Create simplified UI mockups as SVG or HTML elements
- Animate with CSS keyframes or GSAP
- Lightweight, no video loading
- Easy to update

**Option B: Pre-recorded GIF/Video**
- Screen record the actual product
- Fast-forward/edit to 15 seconds
- Higher fidelity but larger file size
- Harder to update

**Option C: Lottie Animation**
- Design in After Effects, export as Lottie JSON
- Smooth, scalable, small file size
- Requires design tool expertise

**Implementation**:
1. [ ] Decide on technical approach (recommend Option A)
2. [ ] Create simplified UI mockup frames for each step
3. [ ] Build animation sequence with smooth transitions
4. [ ] Add to landing page hero section (beside or below headline)
5. [ ] Ensure animation doesn't slow page load
6. [ ] Add pause-on-hover or reduced-motion support for accessibility
7. [ ] Test on mobile (may need simplified version)

---

## UX-002: Reframe Onboarding to Recommend Interview (READY)

**Scope**: Frontend (2h)
**Priority**: HIGH (affects onboarding conversion)
**Requested By**: Founder (2025-12-02)

**Problem**: The current onboarding page makes "Quick Setup" seem like the default/preferred path. This is backwards - the voice interview should be the RECOMMENDED method because it produces a better pricing profile.

**Current Issues**:
1. Quick Setup appears more prominent than Interview
2. Interview sounds slow/intimidating ("5-10 minute interview")
3. No mention that Interview can be TYPED as simple chat
4. Users default to Quick Setup and miss the better experience

**Messaging Changes Needed**:

**Interview Option** (should be PRIMARY):
- Rename to: "Quick Chat Setup" or "Guided Setup"
- Emphasize: "~3 minutes • Voice OR text • Recommended"
- Subtext: "Answer a few questions and we'll build your complete pricing profile"
- Make this the visually prominent option (larger, primary color)

**Quick Setup Option** (should be SECONDARY):
- Rename to: "Manual Setup" or "DIY Setup"
- Emphasize: "For users who know exactly what they want"
- Subtext: "Enter your rates directly - you can always refine later"
- Make this visually secondary (smaller, muted styling)

**Implementation**:
1. [ ] Swap visual prominence of Interview vs Quick Setup buttons
2. [ ] Update Interview copy to emphasize speed ("~3 min") and flexibility ("voice or type")
3. [ ] Add "Recommended" badge to Interview option
4. [ ] Update Quick Setup copy to position as "advanced/manual" option
5. [ ] Consider: Interview as default with "Skip to manual setup" link

---

## ONBOARD-001: Industry/Trade Selection Step (READY)

**Scope**: Frontend + Backend (3h)
**Priority**: HIGH (affects all new users)
**Requested By**: Founder (2025-12-02)

**Problem**: The onboarding doesn't explicitly ask users what industry/trade they're in. It assumes this from registration, but users may have selected inaccurately or the options weren't granular enough.

**Solution**: Add a dedicated industry selection step at the START of onboarding with:
1. Visual industry picker (cards with icons)
2. Granular sub-categories (e.g., "Construction" → "Deck Builder", "Framing", "Concrete", etc.)
3. "Other" option with free-text
4. Store this properly to drive the rest of the experience

**Implementation**:
1. [ ] Create industry picker component in frontend
2. [ ] Update onboarding flow to start with industry selection
3. [ ] Store selected industry on contractor record
4. [ ] Pass industry to interview prompts and quick setup

---

## ONBOARD-002: Guided Quick Setup with Templates (READY)

**Scope**: Frontend + Backend (6h)
**Priority**: HIGH (improves activation for "quick path" users)
**Requested By**: Founder (2025-12-02)

**Problem**: Current quick setup only asks for labor_rate, material_markup, and minimum_job. This is too bare-bones for users who don't have established pricing. They need GUIDANCE, not just empty fields.

**Current Quick Setup Fields**:
- Labor rate (hourly)
- Material markup %
- Minimum job amount
- Pricing notes (free text)

**New Guided Quick Setup**:

Based on their selected industry, show a RECOMMENDED pricing template with sensible defaults:

**Example - Cabinet Company**:
```
Recommended Approach: Linear Foot Pricing

Base Rate per Linear Foot: $____/LF (suggested: $150-300)

Material Tier Adjustments:
  Budget materials: +$0/LF
  Mid-range materials: +$50/LF
  Premium materials: +$120/LF

Finishes Budget: $____/LF (suggested: $15-30)
Hardware Budget: $____/LF (suggested: $20-50)

Minimum Project: $___ (suggested: $2,500)
```

**Example - Handyman**:
```
Recommended Approach: Hourly + Small Job Flat Rates

Hourly Rate: $____/hr (suggested: $65-95)
Helper Rate: $____/hr (suggested: $35-50)

Small Job Flat Rates:
  Quick fix (under 1hr): $____ (suggested: $125-175)
  Half-day job: $____ (suggested: $300-450)
  Full-day job: $____ (suggested: $550-750)

Minimum Service Call: $____ (suggested: $85-125)
```

**Implementation**:
1. [ ] Create pricing template component that adapts to selected industry
2. [ ] Pre-fill with sensible defaults based on industry
3. [ ] Add helper text explaining each field
4. [ ] Show "typical range" hints for each input
5. [ ] Allow users to adjust and save
6. [ ] Update backend `quick_setup()` to accept richer data structure

---

## ONBOARD-003: Industry Pricing Template Library (READY)

**Scope**: Backend (4h)
**Priority**: HIGH (foundation for ONBOARD-002)
**Requested By**: Founder (2025-12-02)

**Problem**: We only have 4 trade defaults in `_get_trade_defaults()`. Need comprehensive templates for 20+ industries with RECOMMENDED PRICING STRUCTURES, not just numbers.

**Philosophy**: Many contractors don't have a pricing system. We should offer them a **simplified approach** they can adopt immediately and refine over time.

**Template Structure Per Industry**:
```python
{
    "industry_key": "cabinet_maker",
    "display_name": "Cabinet Maker / Millwork",
    "recommended_approach": "linear_foot",  # or hourly, project_based, sqft, etc.
    "approach_description": "Price cabinets by linear foot with material tier adjustments",

    "primary_pricing": {
        "unit": "linear_foot",
        "base_rate_range": [150, 300],
        "suggested_default": 200,
    },

    "adjusters": [
        {
            "name": "material_tier",
            "type": "tiered",
            "tiers": {
                "budget": {"modifier": 0, "description": "Melamine, basic laminates"},
                "mid_range": {"modifier": 50, "description": "Wood veneer, solid wood fronts"},
                "premium": {"modifier": 120, "description": "Hardwoods, custom finishes"},
            }
        },
        {
            "name": "finishes_budget",
            "type": "per_unit",
            "unit": "linear_foot",
            "range": [15, 30],
            "description": "Paint, stain, lacquer per LF"
        },
        {
            "name": "hardware_budget",
            "type": "per_unit",
            "unit": "linear_foot",
            "range": [20, 50],
            "description": "Hinges, pulls, soft-close per LF"
        }
    ],

    "minimum_project": {"range": [2500, 5000], "suggested": 3000},

    "common_project_types": [
        "Kitchen cabinets (full remodel)",
        "Kitchen cabinets (refacing)",
        "Bathroom vanity",
        "Built-in bookshelves",
        "Entertainment center",
        "Garage cabinets"
    ],

    "pricing_tips": [
        "Linear foot pricing simplifies quoting - one number clients understand",
        "Material tiers let you adjust without recalculating everything",
        "Track your actual costs for 5-10 jobs to refine these rates"
    ]
}
```

**Industries to Cover**:
- Cabinet maker / Millwork
- Kitchen & bath remodeler
- General contractor
- Electrician
- Plumber
- HVAC
- Roofer
- Flooring installer
- Tile installer
- Concrete contractor
- Framing contractor
- Drywall/plastering
- Window/door installer
- Siding contractor
- Gutters
- Insulation contractor
- Garage door installer
- Pool/spa contractor
- Masonry/stone
- Tree service
- Pressure washing
- Home organizer/closets
- Solar installer

**Implementation**:
1. [ ] Create `backend/data/pricing_templates.py` with full template library
2. [ ] Create function to get template by industry key
3. [ ] Include at least 20 industries with complete templates
4. [ ] Each template should have recommended approach + adjusters + tips

---

## ONBOARD-004: Interview Type C Coaching Mode (READY)

**Scope**: Backend prompts (4h)
**Priority**: MEDIUM (helps users who don't know how to price)
**Requested By**: Founder (2025-12-02)

**Problem**: The current interview detects "Type C" users (don't know how to price) but just asks vague questions like "what do you need to make per hour to be profitable?" This isn't helpful for someone who genuinely doesn't know.

**Solution**: When detecting a Type C user, the interview should:
1. **Acknowledge their situation** - "No worries, let's build something simple together"
2. **Suggest a simplified approach** based on their industry
3. **Walk them through setting initial rates** with concrete guidance
4. **Explain the "learn as you go" approach** - "Start here, adjust based on how quotes feel"

**New Interview Behavior for Type C**:

Instead of:
> "What do you need to make per hour/day to be profitable?"

Say:
> "No problem - let's build you a simple pricing system you can refine over time.
>
> For [cabinet makers], most people start with **linear foot pricing** - it's easy to calculate and clients understand it. Something like $150-250 per linear foot of cabinets, depending on materials.
>
> Does that approach sound right for your work? Or do you price things differently?"

If they agree:
> "Great! Let's set your starting rates. For **mid-range materials** (wood veneer, solid fronts), what feels like a fair price per linear foot? Most cabinet makers in your area charge $180-220/LF."

**Implementation**:
1. [ ] Update `setup_interview.py` prompts with industry-specific coaching
2. [ ] Add template injection when Type C is detected
3. [ ] Include concrete number ranges for their industry
4. [ ] Make it conversational, not robotic

---

## ONBOARD-005: Expand Trade Defaults (READY)

**Scope**: Backend (2h)
**Priority**: MEDIUM (improves default experience)
**Requested By**: Founder (2025-12-02)

**Problem**: `_get_trade_defaults()` only covers 4 trades. Need 20+.

**Current Coverage**:
- deck_builder ✓
- painter ✓
- fence_installer ✓
- landscaper ✓

**Trades to Add**:
- electrician
- plumber
- hvac
- roofer
- flooring
- tile
- concrete
- framing
- drywall
- window_door
- siding
- gutters
- insulation
- garage_door
- pool_spa
- masonry
- tree_service
- pressure_washing
- closet_organizer
- cabinet_maker
- general_contractor

**Implementation**:
1. [ ] Expand `_get_trade_defaults()` with 20+ trades
2. [ ] Each trade gets 3-5 common service categories with pricing
3. [ ] Use realistic industry pricing ranges

---

## UX-001: Improve Quote Input Placeholder Text (READY)

**Scope**: Frontend (30m)
**Priority**: LOW (polish)
**Requested By**: Founder (2025-12-02)

**Problem**: The quote input text box needs better placeholder/shadow text that shows users exactly what to say when dictating a quote.

**Current State**: Generic placeholder that doesn't demonstrate the expected format.

**Goal**: Create compelling example text that:
- Sounds natural (like someone actually talking)
- Shows key elements: customer name, job description, location/context, pricing hints
- Is concise enough to read at a glance
- Motivates users to start typing/speaking

**Example Direction**:
```
"Quote for John Smith at 123 Oak Street - painting the living room and hallway, about 400 sq ft total, standard prep work, they want it done by next Friday..."
```

**Implementation**:
1. [ ] Find current placeholder text in `frontend/index.html`
2. [ ] Draft 2-3 improved alternatives
3. [ ] Implement the best one
4. [ ] Verify placeholder displays correctly in empty input

---

## FEAT-003: Pricing Brain Global Settings Editor (READY)

**Scope**: Frontend + Backend (4h)
**Priority**: MEDIUM (user control)
**Requested By**: Founder (2025-12-02)

**Problem**: Global pricing settings (labor rate, material markup, minimum job, etc.) are displayed but not editable in the Pricing Brain UI. Users need to be able to modify these values.

**Current API**:
- `GET /api/pricing-brain/settings/global` - Returns GlobalSettings (read-only)

**GlobalSettings Model** (from `backend/api/pricing_brain.py`):
```python
class GlobalSettings(BaseModel):
    labor_rate_hourly: Optional[float]
    helper_rate_hourly: Optional[float]
    material_markup_percent: Optional[float]
    minimum_job_amount: Optional[float]
    pricing_notes: Optional[str]
```

**Requirements**:

1. **Backend: PUT endpoint**
   - Create `PUT /api/pricing-brain/settings/global`
   - Accept GlobalSettings body
   - Update pricing_model record
   - Return updated settings

2. **Frontend: Editable Settings Section**
   - Display current global settings in Pricing Brain tab
   - Add "Edit" button to open edit modal (or inline editing)
   - Input validation (rates positive, percentages 0-100)
   - Save/Cancel buttons
   - Success/error feedback

3. **Contractor-Specific Variables** (if applicable)
   - If contractor has custom variables in `pricing_knowledge`, display those too
   - Allow editing custom variables
   - Consider: ability to add new custom variables?

**Implementation**:
1. [ ] Add `PUT /api/pricing-brain/settings/global` endpoint in backend
2. [ ] Add global settings section to Pricing Brain UI (below categories)
3. [ ] Create edit modal or inline editing for settings
4. [ ] Add input validation
5. [ ] Wire up save functionality with API
6. [ ] Handle contractor-specific variables if they exist

---

## FEAT-001: Pricing Brain Management (COMPLETE ✓)

**Commits**: `1361539` (Backend) + `6c7c94a` (Frontend)
**Design Doc**: `docs/plans/2025-12-02-pricing-brain-design.md`
**Priority**: HIGH (user trust + transparency)
**Approved By**: Founder (2025-12-02)

**Summary**: New "Pricing Brain" tab in Account section where users can view what the AI learned about their pricing and make corrections with AI assistance.

**Implementation Summary**:
- ✅ Backend API: 6 endpoints for category management + AI analysis
- ✅ Frontend UI: Pricing Brain tab with category cards, edit modals, AI insights
- ✅ Haiku integration for on-demand category analysis (~$0.001/call)
- ✅ Pattern-based hints (instant, no API cost)
- ✅ Empty states, confirmations, error handling

**New Files**:
- `backend/api/pricing_brain.py` - REST API routes (307 lines)
- `backend/services/pricing_brain.py` - Business logic + Haiku (280 lines)

**API Endpoints**:
```
GET  /api/pricing-brain              - All categories + stats
GET  /api/pricing-brain/{category}   - Single category detail
PUT  /api/pricing-brain/{category}   - Update category
DELETE /api/pricing-brain/{category} - Delete category
POST /api/pricing-brain/{category}/analyze - AI analysis (Haiku)
GET  /api/pricing-brain/settings/global - Global pricing settings
```

---

## FEAT-002: Edit Customer Info on Existing Quotes (COMPLETE ✓)

**Commits**: `fa0f7a4` (Frontend) + `28a98f9` (Backend)
**Priority**: MEDIUM (usability)
**Reported By**: Founder (2025-12-02)

**Problem**: Once a quote is created, users cannot edit customer information (name, address, phone). If AI didn't detect customer info from transcription, or user wants to add it later, they're stuck.

**Implementation Summary**:
- ✅ Customer info section added to quote detail view
- ✅ Edit button with pencil icon opens modal
- ✅ Modal with customer_name, customer_address, customer_phone fields
- ✅ Backend: `PUT /api/quotes/{quote_id}/customer` endpoint
- ✅ Frontend wired to API with cache refresh

**New API Endpoint**:
```
PUT /api/quotes/{quote_id}/customer - Update customer info only
```

---

## FIX-001: Randomize Slot Animation Order (COMPLETE ✓)

**Commit**: `59883ef`
**Priority**: LOW (polish)
**Reported By**: Founder (2025-12-02)

**Problem**: Landing page slot animation always shows the same two industry words when page loads.

**Solution**: Added Fisher-Yates shuffle on page load before animation starts.

**Implementation**:
- ✅ Fisher-Yates shuffle function added to landing.html
- ✅ Words array shuffled on DOMContentLoaded
- ✅ Repeat visitors now see variety

---

## PAY-001 Implementation (COMPLETE ✓)

**Commit**: `cb1e311` - "Add: Stripe payment infrastructure for subscription billing"

**Implementation Summary**:
- ✅ Stripe SDK added (`stripe==11.1.1`)
- ✅ Billing routes created (`/api/billing/*`)
- ✅ User model extended with billing fields
- ✅ Trial auto-initialization (7 days, 75 quotes)
- ✅ Quote limits enforced (402 responses when exceeded)
- ✅ Usage tracking integrated into quote generation

**New API Endpoints**:
```
POST /api/billing/create-checkout - Start subscription
POST /api/billing/webhook - Stripe webhook handler
POST /api/billing/portal - Customer portal access
GET /api/billing/status - Current subscription status
GET /api/billing/plans - Available pricing (public)
```

**New Files**:
- `backend/services/billing.py` - BillingService class
- `backend/api/billing.py` - API routes

---

## PAY-004 Implementation (COMPLETE ✓)

**Commit**: `33fa641` - "Add: Resend email service for transactional emails"

**Implementation Summary**:
- ✅ Resend SDK added (`resend==2.4.0`)
- ✅ Email service created with 5 email types
- ✅ Welcome email integrated with registration
- ✅ Dark premium HTML templates

**Emails Ready**:
- ✅ Welcome email (sends on registration)
- 🔜 Trial starting email (hook into first quote)
- 🔜 Trial ending reminder (hook into day 5 cron)
- 🔜 Subscription confirmation (hook into Stripe webhook)
- 🔜 Payment failed notification (hook into Stripe webhook)

**New Files**:
- `backend/services/email.py` - EmailService class (455 lines)

---

## GROWTH-001: Demo Mode (Try Before Signup) (READY)

**Scope**: Backend + Frontend (6h)
**Impact**: Removes biggest conversion barrier - users can try before committing

**Problem**: Users must signup and complete 5-15 min onboarding before seeing if product works.

**Solution**: 2-minute demo that generates a real quote without signup.

**Demo Flow**:
1. Landing page: "Try it now - no signup required" button
2. Demo page with pre-filled contractor profile (General Contractor)
3. Voice recorder OR text input
4. Generate real quote (no auth)
5. Show quote with "DEMO" watermark
6. CTA: "Create free account to save this quote"

**Implementation**:
1. [ ] Create `/demo` route in frontend
2. [ ] Create `POST /api/demo/quote` endpoint (no auth, rate limited 3/hour/IP)
3. [ ] Demo uses generic contractor profile with standard pricing
4. [ ] Quote generates but doesn't save to database
5. [ ] Watermarked PDF output
6. [ ] Prominent signup CTA after quote generation
7. [ ] Track: demo_started, demo_quote_generated, demo_to_signup

---

## GROWTH-002: Referral System with Rewards (READY)

**Scope**: Backend + Frontend (6h)
**Impact**: Each user becomes a growth engine with incentives

**Referral Program**:
- Referrer gets: 1 free month credit when referral subscribes
- Referee gets: Extended trial (14 days instead of 7)
- Tracking: Unique referral codes per user (e.g., JOHN-A3X9)

**Implementation**:
1. [ ] Add to User model: `referral_code`, `referred_by`, `referral_count`, `referral_credits`
2. [ ] Auto-generate referral code on registration
3. [ ] API endpoints:
   - `GET /api/referral/code` - Get user's code
   - `GET /api/referral/stats` - Count, rewards earned
   - `POST /api/referral/apply` - Apply code during signup
4. [ ] Frontend: Referral section in Account tab with share buttons
5. [ ] Signup flow: Optional referral code field
6. [ ] Stripe integration: Apply credit on referee subscription
7. [ ] Referral landing shows banner: "John invited you - get 14 days free"

---

## GROWTH-003: Share Quote (Email/SMS/Link) (READY)

**Scope**: Backend + Frontend (4h)
**Impact**: Every shared quote is free marketing

**Problem**: Contractors manually export PDF and email. Friction + missed marketing.

**Share Options**: Email, SMS, Copy Link, WhatsApp

**Implementation**:
1. [ ] Add "Share" button to quote detail (prominent)
2. [ ] Share modal with recipient input + channel selection
3. [ ] API endpoints:
   - `POST /api/quotes/{id}/share/email` - Send via Resend
   - `POST /api/quotes/{id}/share` - Generate shareable token
   - `GET /api/quotes/shared/{token}` - Public view (read-only)
4. [ ] Professional email template with PDF + "Powered by Quoted" footer
5. [ ] Public quote view: Branded, contractor info, "Get Quoted" CTA
6. [ ] Track: quote_shared, share_method, shared_quote_viewed

---

## GROWTH-004: Landing Page Testimonials (READY)

**Scope**: Frontend (2h)
**Impact**: Social proof increases conversion

**Implementation**:
1. [ ] Add testimonials section to landing page (3-4 quotes)
2. [ ] Each has: Quote text, name, business type, star rating
3. [ ] Mobile-friendly layout
4. [ ] Placeholder testimonials until real ones collected

---

## GROWTH-005: "Powered by Quoted" Branding (READY)

**Scope**: Frontend (1h)
**Impact**: Free marketing on every shared quote

**Implementation**:
1. [ ] Add subtle footer to PDF exports
2. [ ] Add to public shared quote view
3. [ ] Style: Logo + "Voice-to-quote for contractors" + link

---

## CONVERT-001: Analytics (PostHog) (COMPLETE ✓)

**Commit**: `75eac78`
**Scope**: Backend + Frontend (4h)
**Impact**: Can't optimize what you can't measure

**Implementation Summary**:
- ✅ PostHog SDK integrated (backend: posthog==3.7.4)
- ✅ PostHog JS SDK integrated (frontend)
- ✅ Backend events tracked:
  - signup_completed (with user identification)
  - onboarding_completed
  - quote_generated (with category, confidence, subtotal)
  - quote_edited (with change type and magnitude)
  - subscription_activated (with plan tier and interval)
- ✅ Frontend events tracked:
  - landing_page_view
  - cta_clicked (with button text and location)
  - quote_generated (with quote_id and total)
  - quote_edited (with quote_id and correction notes flag)
  - upgrade_modal_opened
- ✅ Graceful degradation: missing POSTHOG_API_KEY logs warnings but doesn't crash
- ✅ Defensive tracking: all events wrapped in try/except or window.posthog checks

**Environment Variables**:
- POSTHOG_API_KEY (optional - degrades gracefully)

---

## CONVERT-002: Enhanced Empty States (READY)

**Scope**: Frontend (2h)

**Empty States to Enhance**:
- My Quotes (no quotes): Illustration + "Create your first quote" + big CTA
- Pricing Brain (no data): "Generate quotes and AI will learn"

---

## CONVERT-003: First Quote Celebration (READY)

**Scope**: Frontend (1h)
**Impact**: Reinforce activation moment, prompt referral

**Implementation**: Modal after first quote with confetti, "You generated your first quote!" + referral CTA

---

## RETAIN-001: Engagement Email Series (READY)

**Scope**: Backend (4h)
**Dependencies**: PAY-004 (email service - COMPLETE)

**Email Series**:
1. Day 1 (post-first-quote): "Your first quote is ready!" + tip
2. Day 3: "Pro tip: Rush job pricing" + invite CTA
3. Day 5: "Did you know? Edit quotes anytime" + invite CTA
4. Day 10: "You've generated X quotes!" + referral prompt

**Key**: Every email includes referral CTA at bottom.

---

## RETAIN-002: Dormancy Re-engagement (READY)

**Scope**: Backend (2h)

**Triggers**:
- 7 days inactive: "Quick check-in" email
- 14 days inactive: "We've made improvements" email

**Implementation**: Track last_active_at, daily cron checks for inactive users

---

## INFRA-001: Sentry Error Tracking (COMPLETE ✓)

**Commit**: `75eac78`
**Scope**: Backend + Frontend (2h)

**Implementation Summary**:
- ✅ Sentry SDK integrated (backend: sentry-sdk[fastapi]==2.18.0)
- ✅ Sentry JS SDK integrated (frontend: v8.38.0)
- ✅ FastAPI integration with StarletteIntegration
- ✅ Performance monitoring: 100% transaction sampling
- ✅ Environment-aware (development vs production)
- ✅ Graceful degradation: missing SENTRY_DSN logs warnings but doesn't crash
- ✅ Frontend error tracking with tracesSampleRate: 0.1 (10%)

**Environment Variables**:
- SENTRY_DSN (optional - degrades gracefully)

---

## INFRA-002: Mobile Responsiveness Audit (READY)

**Scope**: Frontend (4h)

**Checklist**:
1. [ ] Voice recording works on iOS Safari, Android Chrome
2. [ ] Touch targets minimum 44x44px
3. [ ] Modals fit on small screens
4. [ ] Test on iPhone SE, iPhone 14, iPad

---

## INFRA-003: FAQ/Help Section (READY)

**Scope**: Frontend (3h)

**Topics**: Getting started, pricing/billing, using Quoted, troubleshooting

**Implementation**: /help route, accordion FAQ, link from navigation

---

## Code Review Queue

| PR | Author | Reviewer | Status |
|----|--------|----------|--------|
| - | No open PRs | - | - |

---

## Discovery Backlog (DISCOVERED - Awaiting Founder Review)

*Generated by `/quoted-discover` cycle on 2025-12-02. Status `DISCOVERED` means proposed but not approved.*
*Change status to `READY` to approve for implementation. Delete or mark `REJECTED` if not pursuing.*

### ~~DISC-001: First Quote Activation Flow~~ (DEPLOYED) ⭐ Priority #1

**Commit**: 8628869
**Source**: Product + Growth Discovery Agents
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Critical for activation - users complete onboarding but don't generate first quote

**Implementation Summary**:
- ✅ Post-onboarding modal: "You're all set up!" with celebration icon
- ✅ Two paths: "Record a job description" (voice) or "Type an example" (text)
- ✅ Pre-filled sample job for text option (cabinet refacing example)
- ✅ PostHog tracking: first_quote_modal_shown, first_quote_modal_skipped, first_quote_started
- ✅ One-time display via localStorage flag
- ✅ Integrates with existing onboarding completion flow

**Success Metric**: 80% of users who complete onboarding generate first quote within 5 minutes

---

### ~~DISC-002: Referral Program Early Visibility~~ (DEPLOYED) ⭐ Priority #2

**Commit**: 5c1ebc3
**Source**: Product + Growth Discovery Agents
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Referral is key to reaching 100 users via 1.3x viral coefficient

**Implementation Summary**:
- ✅ Referral section added to first quote celebration modal
- ✅ Messaging: "Invite a friend, you both get rewards" with "1 free month / 14 extra days"
- ✅ Referral code display with copy button
- ✅ Share buttons: email and copy link
- ✅ Referral banner added to quote share modal
- ✅ PostHog tracking: referral_shown_at_celebration, referral_code_copied, referral_link_copied, referral_shared

**Success Metric**: 25%+ users share referral code; viral coefficient increases from 1.0 to 1.3+

---

### ~~DISC-003: Landing Page CTA Clarity~~ (DEPLOYED) ⭐ Priority #3

**Commit**: fd82e2f
**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Landing page is primary acquisition funnel for 100 users

**Problem**: Landing page has competing CTAs ("Try Demo" vs "Get Started") without clear differentiation. Users don't know which path is faster or better for their needs.

**Implementation Summary**:
- ✅ Hero CTAs swapped: Demo now primary (filled button), Signup secondary (outline)
- ✅ New button text: "Try 2-Minute Demo" (primary) + "Start Free Trial" (secondary)
- ✅ Added subtext: "No signup required for demo"
- ✅ Demo section CTA updated: "Ready to try it yourself?" + "Try the Demo Now"
- ✅ Final CTA section now has both buttons (Demo primary, Signup secondary)
- ✅ Enhanced PostHog tracking with cta_type, section, and is_primary properties

**Changes**:
- Hero: Demo primary, Signup secondary with "No signup required" subtext
- Demo section: Updated CTA copy to encourage trying the demo
- Final CTA: Both buttons with clear hierarchy
- Analytics: Granular tracking for A/B comparison

**Success Metric**: +15-20% landing page → signup conversion; establish demo→signup baseline

---

### ~~DISC-004: Analytics Funnel Gaps~~ (DEPLOYED) ⭐ Priority #4

**Commit**: 9607ccf
**Source**: Product + Growth Discovery Agents
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Can't optimize what you can't measure - blocks data-driven decisions

**Implementation Summary**:
- ✅ Onboarding events: `onboarding_path_selected`, `onboarding_started` with path property
- ✅ Enhanced `onboarding_completed` with `onboarding_type` property for segmentation
- ✅ Activation events: `first_quote_attempt`, `first_quote_generated` (checks quotes_used === 0)
- ✅ Conversion events: `quote_limit_reached`, `upgrade_modal_viewed`, `upgrade_clicked`
- ✅ All events include relevant properties for PostHog segmentation

**Now Measurable**:
- Onboarding completion rate by path (Interview vs Quick Setup)
- First quote conversion rate
- Time to first quote
- Trial→subscription funnel drop-offs

**Success Metric**: Can measure onboarding completion rate, first quote rate, funnel drop-off points

---

### ~~DISC-005: Trial→Upgrade Journey Friction~~ (DEPLOYED)

**Commit**: 412f5da
**Source**: Product Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Trial conversion is revenue foundation

**Implementation Summary**:
- ✅ Trial banner: Added "Upgrade Now" single-click button
- ✅ Urgency state: Red gradient + pulse when <3 days remaining
- ✅ Quote limit warning: Purple banner when <10 quotes left in trial
- ✅ Improved quote limit modal: Quick upgrade buttons at top (Monthly/Annual)
- ✅ PostHog tracking: trial_banner_upgrade_clicked, quote_limit_warning_shown, quote_limit_modal_upgrade_clicked

**Friction Reduction**:
- Before: Banner → Navigate → Modal → Checkout (4 steps)
- After: Banner → Checkout (1 click)

**Success Metric**: 30%+ trial→subscription conversion; banner CTR >20%

---

### ~~DISC-006: Animation Walkthrough→Signup Conversion Flow~~ (DEPLOYED)

**Commit**: c8addfa
**Source**: Product + Growth Discovery Agents
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Animation walkthrough is acquisition lever showing product value before signup

**Implementation Summary**:
- ✅ Conversion modal overlay after animation walkthrough completes
- ✅ Title: "Your quote is ready!" with trial benefits
- ✅ Primary CTA: "Save This Quote & Start Free Trial" → signup
- ✅ Secondary: "Continue exploring demo" dismisses modal
- ✅ PostHog tracking: demo_quote_generated, demo_signup_cta_shown, demo_signup_cta_clicked
- ✅ Glassmorphism styling matching brand (#00ff88 accents)
- ✅ Shows once per session to avoid annoyance

**Note**: The /demo page shows an **animated walkthrough** of how Quoted works (not an interactive demo). This modal captures viewers at the end of the animation.

**Success Metric**: 20%+ animation viewer→signup conversion (vs current unknown)

---

### ~~DISC-007: Onboarding Path A/B Testing~~ (DEPLOYED)

**Commit**: b5d55b1
**Source**: Product + Growth Discovery Agents
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Sprint Alignment**: Activation optimization - ensures users choose best onboarding path

**Implementation Summary**:
- ✅ Added `onboarding_path` field to User model ("interview" or "quick_setup")
- ✅ Added `onboarding_completed_at` timestamp to User model
- ✅ Backend: `/onboarding/start` tracks `onboarding_path_selected` with `path="interview"`
- ✅ Backend: `/onboarding/quick` tracks `onboarding_path_selected` with `path="quick_setup"`
- ✅ Backend: Both completion endpoints save path to User record
- ✅ All `onboarding_completed` events include `onboarding_path` property
- ✅ Database migrations applied

**Now Measurable in PostHog**:
- Path selection rate (% choose each path)
- Activation rate by path (first_quote conversion)
- Edit rate by path (quote quality proxy)
- Time to first quote by path

**Success Metric**: Clear data on which path produces better activation and retention

---

### ~~DISC-008: Learning System Visibility~~ (DEPLOYED)

**Commit**: 57c3aff
**Source**: Growth + Strategy Discovery Agents
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Learning system is key differentiator - users can now see it working

**Implementation Summary**:
- ✅ Backend: `GET /api/learning/progress` - Returns comprehensive learning stats
- ✅ Calculates: total_quotes, total_corrections, categories_learned, learning_progress_percent
- ✅ Per-category: confidence score, quote count, correction count
- ✅ Learning velocity classification: fast/steady/slow/starting
- ✅ Frontend: Learning Progress section in Pricing Brain tab
- ✅ Large progress bar: "AI knows X% of your pricing"
- ✅ 4-stat dashboard: Quotes, Corrections, Categories, Speed
- ✅ Category cards with confidence badges and mini progress bars
- ✅ Motivational messaging based on progress level
- ✅ Auto-hides for new users with no quotes
- ✅ Mobile responsive design

**Confidence Algorithm**: `min(100, base_confidence + corrections_boost + quotes_boost)`

**Success Metric**: Users understand learning; correction rate increases 30%; edit_rate trends down after 5+ quotes

---

### ~~DISC-009: First Quote Celebration Enhancement~~ (DEPLOYED)

**Commit**: dd5c41e
**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Peak emotional moment for referral and retention hooks

**Implementation Summary**:
- ✅ Enhanced celebration modal with 3-CTA hierarchy
- ✅ Primary CTA: "Share Your First Quote" with Web Share API / clipboard fallback
- ✅ Secondary: Referral section (from DISC-002) made more prominent
- ✅ Tertiary: "View Quote" and "Create Another" buttons
- ✅ Social proof badge: "You're in the first 100 beta testers!"
- ✅ Progress indicator: "Your AI is Learning - Building your pricing intelligence"
- ✅ Larger celebration icon with drop shadow and bounce animation
- ✅ PostHog tracking: celebration_shown, celebration_share_clicked, celebration_share_completed, celebration_dismissed
- ✅ Mobile responsive (buttons stack, icon scales)

**Success Metric**: +30% retention; +20% referral awareness from celebration flow

---

### ~~DISC-010: Testimonial Collection System~~ (DEPLOYED)

**Commit**: fabe2c6
**Source**: Growth Discovery Agent
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: Social proof increases landing page conversion

**Implementation Summary**:
- ✅ Database: `Testimonial` model with rating, quote_text, name, company, approved fields
- ✅ Backend API: `POST /api/testimonials/` - Submit testimonial
- ✅ Backend API: `GET /api/testimonials/?approved_only=true` - Fetch for landing page
- ✅ Backend API: `GET /api/testimonials/check-submitted` - Prevent duplicate submissions
- ✅ Frontend: Collection modal triggers after 3rd quote
- ✅ 5-star rating system with interactive gold stars
- ✅ Optional attribution (name/company) with checkbox reveal
- ✅ 500-character limit with live counter
- ✅ Shows once per user (localStorage + API check)
- ✅ PostHog tracking: testimonial_modal_shown, testimonial_submitted

**Admin Workflow**: Update `approved=true` in database, then fetch via API for landing page.

**Success Metric**: 5+ real testimonials collected; +15% landing page conversion with real testimonials

---

### ~~DISC-011: Voice-First Assumption Validation~~ (DEPLOYED) ⚠️ Strategic

**Commits**: f1053b8, ecc2be1
**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Core assumption - if wrong, entire positioning must shift

**Implementation Summary**:
- ✅ Frontend: `quote_input_method` event fires with `method: "voice"` or `"text"`
- ✅ Frontend: `quote_generated` and `first_quote_generated` include `input_method` property
- ✅ Backend: `/generate` tracks `input_method: "text"` in PostHog
- ✅ Backend: `/generate-from-audio` tracks `input_method: "voice"` in PostHog
- ✅ Consistent terminology: "voice" (not "audio") for all analytics

**Now Measurable in PostHog**:
- Voice vs text usage breakdown (pie chart)
- Input method trends over time (line chart)
- Edit rates by input method (correlation analysis)

**Success Metric**: Know actual voice adoption rate; can segment by input method

---

### ~~DISC-012: Learning System Critical Mass Risk~~ (DEPLOYED) ⚠️ Strategic

**Commit**: f1053b8
**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Must validate learning system works before scaling

**Implementation Summary**:
- ✅ `learning_correction_recorded` event with category, correction_magnitude, line_item_change_count
- ✅ `quote_generated` enhanced with user_quote_count, user_edit_count, user_edit_rate
- ✅ `quote_generated` includes category_quote_count, category_edit_count, category_edit_rate
- ✅ `quote_edited` enhanced with subtotal_change_percent, corrections_for_category, user_total_corrections
- ✅ Learning service now passes contractor_id, category, user_id for analytics

**Now Measurable in PostHog**:
- Edit rate trend: Does `user_edit_rate` decrease as `user_quote_count` increases?
- Category learning: Which categories have highest correction magnitudes?
- User learning velocity: Cohort analysis by quote count
- Learning effectiveness: Scatter plot of `correction_magnitude` vs `user_quote_count`

**Success Metric**: Can measure if edit rate decreases over time; can validate learning is working

---

### DISC-013: Animation Walkthrough Distribution Strategy (READY)

**Source**: Growth Discovery Agent
**Impact**: HIGH | **Effort**: L | **Score**: 0.75
**Sprint Alignment**: BETA_SPRINT targets 300 animation views × 10% = 30 users from animation walkthrough

**Problem**: Animation walkthrough is built (DECISION-005), conversion modal added (DISC-006), but no distribution strategy. Animation page is accessible but invisible - no outreach to drive views.

**Evidence**:
- Frontend: /demo page with animation walkthrough
- Conversion: DISC-006 added signup modal after animation completes
- Distribution: Zero strategy documented
- No social media, Reddit, or contractor community outreach planned

**Proposed Work**:
1. Create /demo-promo landing variant focused on animation
2. Message: "See voice-to-quote in 60 seconds - no signup"
3. Add tracking: utm_source parameter for channel attribution
4. Start with 3 contractor subreddits + 2 Facebook groups
5. Target: 300 animation views in 14 days

**Success Metric**: 300 animation views; animation→signup conversion baseline established

---

### DISC-014: Buildxact Competitive Defense (READY) ⚠️ Strategic

**Source**: Strategy Discovery Agent
**Impact**: HIGH | **Effort**: L | **Score**: 0.75
**Sprint Alignment**: Long-term - existential threat if not addressed in 2025

**Problem**: Main competitor Buildxact could add voice interface in 6-12 months, neutralizing Quoted's positioning. No defensive strategy in place.

**Evidence**:
- Buildxact is 30-second estimate tool (competitive on speed)
- Buildxact has 5+ year contractor relationship head start
- Adding Whisper + Claude is 3-4 week engineering lift
- Quoted's learning system (planned RAG) is only real moat
- Vector Embeddings (RAG) currently in post-beta backlog

**Proposed Work**:
1. Accelerate learning system development: move RAG from backlog to Q1 priority
2. After 100 users, plan vertical integrations (QuickBooks, Jobber) for lock-in
3. Emphasize "learns YOUR pricing" (personal moat) over "has voice" (replicable)
4. Track if users cite "learning" vs "voice" as value driver

**Success Metric**: RAG implemented Q1 2025; at least 1 integration partnership in 2025

---

### ~~DISC-015: Social Proof Scarcity for Beta Launch~~ (DEPLOYED) ⭐ Founder Strategic Direction

**Commit**: 3d8f8fa
**Source**: Founder (2025-12-02)
**Impact**: HIGH | **Effort**: S | **Score**: 3.0
**Sprint Alignment**: Creates urgency and social proof for beta recruitment

**Implementation Summary**:
- ✅ Backend: Created `/api/beta/spots` endpoint in `backend/api/beta.py`
- ✅ Configuration: BETA_TOTAL_SPOTS=100, BETA_OFFSET=68
- ✅ Returns: `{total, claimed, remaining, is_full}` with real user count + offset
- ✅ Frontend: Beta counter added to landing page after navigation
- ✅ Styling: Glassmorphism design with pulsing green indicator, mobile responsive
- ✅ Live updates: Counter fetches from API on page load
- ✅ Messaging: "X spots remaining" with "Join the Beta" CTA

**Success Metric**: Higher conversion rate vs. no scarcity; beta fills faster than organic would

---

### ~~DISC-016: Premium PDF Branding Features~~ (COMPLETE ✅) 🏆 Paid Tier Differentiation

**Commit**: 94ba6dc
**Source**: Founder (2025-12-03)
**Status**: **MVP COMPLETE** - Custom logo upload implemented
**Impact**: HIGH | **Effort**: L | **Score**: 0.75

**Implementation Summary (MVP - Logo Upload)**:
- ✅ Backend: POST/GET/DELETE /api/contractors/logo endpoints
- ✅ Database: logo_data field on Contractor model (base64 storage)
- ✅ PDF: Custom logo appears in header when set (48x48, top-left)
- ✅ Frontend: Logo upload UI in Account tab with preview
- ✅ Validation: PNG/JPG only, 2MB max
- ✅ Analytics: PostHog events (logo_uploaded, logo_removed)

**Remaining Features (Future Phases)**:
- Voice-Driven Template Customization (Pro tier) - Q1 2025
- White-Label / Remove Quoted Branding (Team tier) - Q1 2025

**Executive Council Decision**:
- Logo: Available at all tiers (drives upgrade psychology)
- Voice templates: Pro tier ($39/mo)
- White-label: Team tier ($79/mo)

**Success Metric**: Increased trial→paid conversion; reduced churn on paid tiers

---

### ~~DISC-017: Trial Abuse Prevention~~ (COMPLETE ✅) 🔒 Revenue Protection

**Commit**: 8c88de2
**Source**: Founder (2025-12-03)
**Status**: **MVP COMPLETE** - Email normalization + disposable blocking
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0

**Implementation Summary (Minimal Scope)**:
- ✅ Email Normalization: Strips Gmail dots and plus aliases
  - `j.ohn+trial@gmail.com` → `john@gmail.com`
  - `john@googlemail.com` → `john@gmail.com`
- ✅ Disposable Email Blocking: 20+ known temp email domains blocked
  - mailinator.com, 10minutemail.com, tempmail.com, guerrillamail.com, etc.
- ✅ Database: normalized_email field on User model
- ✅ Registration validation with friendly error messages
- ✅ Test coverage: 14 tests, 100% pass

**Deferred to Q1 2025 (per Executive Council)**:
- Device fingerprinting
- IP rate limiting
- Phone verification

**Executive Council Decision**:
- Aggressiveness: Moderate (soft blocks, friendly errors)
- Timing: Implement now (before abuse patterns establish)
- Response: Block at registration with helpful message

**Success Metric**: <5% trial abuse rate; no viral "how to get unlimited Quoted trials" posts

---

### DISC-018: Trial Grace Period & Soft Warnings (DISCOVERED) ⭐ Priority #1

**Source**: Product Discovery Agent (2025-12-03)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Direct conversion impact - prevents revenue loss at trial expiration

**Problem**: When trial expires (7 days, 75 quotes), users are immediately hard-blocked. No warning before the wall. User discovers limitation at worst moment (on job site, customer waiting) - creates bad UX and lost conversions.

**Evidence**:
- `backend/api/quotes.py` lines 251-278: Raises 402 error immediately when trial_expired or trial_limit_reached
- No soft warning at 5/7 quotes remaining
- No "Generate 1 more quote to upgrade" offer
- DISC-005 added upgrade modal but not grace mechanics

**Proposed Work**:
1. Soft warning at 90% quota (67/75 quotes): Banner "You have 8 quotes remaining"
2. At 95% (71/75): Modal after quote generation: "Trial ending soon - upgrade to unlock unlimited"
3. At 100%: Allow 3 grace quotes with watermark "TRIAL EXPIRED" on PDF
4. Grace quote CTA: "Upgrade to remove watermark and continue"
5. Track: How many users convert during grace vs. hard block

**Success Metric**: Trial→paid conversion +10-15pp; <5% of users hit hard block without warning

---

### DISC-019: "Try It First" Fast Activation Path (DISCOVERED) ⭐ Priority #2

**Source**: Product Discovery Agent (2025-12-03)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Removes biggest new user friction - accelerates time to first quote

**Problem**: New users must complete full onboarding (5-15 min interview OR quick setup) before generating first quote. This delays activation and increases drop-off. Demo mode exists for anonymous users but not for logged-in activation.

**Evidence**:
- `/api/onboarding/start` and `/api/onboarding/quick` both require completing full setup before first quote
- No "Skip for now" option to generate sample quote with default pricing
- BETA_SPRINT targets 60% activation rate - likely hurt by this friction

**Proposed Work**:
1. After signup, offer choice: "Set up my pricing (5-10 min)" OR "Try a quote now (2 min)"
2. "Try It First" → Pre-filled generic pricing for their trade (from pricing_templates)
3. User generates first quote immediately
4. After first quote: "Want better accuracy? Complete pricing setup now"
5. Track which path users choose and activation rates for each

**Success Metric**: Activation rate 70%+ (up from 60% baseline); Time to first quote <3 min

---

### DISC-020: Exit-Intent Survey on Landing Page (DISCOVERED) ⭐ Priority #3

**Source**: Growth Discovery Agent (2025-12-03)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Qualitative conversion data - know WHY visitors leave without signing up

**Problem**: Landing page has traffic but conversion rate is unknown. Visitors leave without signing up and we don't know WHY. Are they confused? Not contractors? Price sensitive? Don't believe it works?

**Evidence**:
- PostHog analytics tracks clicks but not WHY people leave
- Demo→signup baseline unknown (DISC-006 added modal but no data yet)
- 6 days to iterate - need fast feedback loops

**Proposed Work**:
1. Exit-intent popup when mouse moves toward close/back button
2. Single question: "What's holding you back from trying Quoted?"
3. Options: "Not sure it works for my trade", "Pricing seems high", "Don't have time", "Need real examples", "Other"
4. Submit → Thank you + "Join waitlist for updates?" (email capture)
5. Analytics: exit_survey_shown, exit_survey_completed, exit_reason_selected
6. Daily report: Top 3 objections → rapid iteration

**Success Metric**: 100+ survey responses; identify top objection; +10-15% landing→signup after fix

---

### DISC-021: Email Signature Referral Hack (DISCOVERED)

**Source**: Growth Discovery Agent (2025-12-03)
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Sprint Alignment**: Boosts viral coefficient - every quote email becomes referral opportunity

**Problem**: Referral visibility is delayed until first quote celebration. Most contractors send 5-20 emails/day with quotes - 25-100 free impressions per user per week going to waste.

**Evidence**:
- "Powered by Quoted" branding exists (GROWTH-005) but only on PDF
- No email signature suggestion in onboarding or account settings
- Viral coefficient needs to hit 1.3x (30 users → 40 referred users)

**Proposed Work**:
1. Account Settings: Add "Boost Your Referrals" card with pre-written email signature
2. Pre-written: "PS: I use Quoted for instant voice quotes - [referral link]"
3. Copy button for easy paste into Gmail/Outlook
4. Show projected earnings: "If 1 in 10 clients tries Quoted, you earn $X/month in credits"
5. After first quote modal: Optional email signature copy with one-click

**Success Metric**: 40% of users copy email signature; referral coefficient 1.0 → 1.2+

---

### DISC-022: Customer Memory (Autocomplete) (DISCOVERED)

**Source**: Product Discovery Agent (2025-12-03)
**Impact**: MEDIUM | **Effort**: S | **Score**: 2.0
**Sprint Alignment**: UX improvement - reduces friction for repeat customers

**Problem**: Contractors often quote the same customer multiple times (different jobs, change orders). Currently, every quote requires re-entering customer name/phone/email. Tedious and error-prone.

**Evidence**:
- Database has customer fields on Quote but no separate Customer table
- No autocomplete or customer search in quote generation flow
- API has `PUT /api/quotes/{id}/customer` but no `/api/customers` endpoints

**Proposed Work**:
1. Backend: Extract unique customers from quote history (no new table needed)
2. API endpoint: `GET /api/customers` returns list of {name, phone, email} from past quotes
3. Frontend: Autocomplete dropdown on customer name field
4. When user types, show matching past customers
5. Click to autofill all customer fields
6. Track saves vs. manual entry in analytics

**Success Metric**: 30%+ of quotes use saved customer info (for users with 5+ quotes)

---

### DISC-023: Contractor Community Outreach Plan (DISCOVERED) 🚀 FOUNDER ACTION

**Source**: Growth Discovery Agent (2025-12-03)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Distribution strategy - 100-user goal requires reaching contractors who don't know Quoted exists

**Problem**: Product is built, analytics tracking, but no distribution strategy. 5 users (all founder network). 6 days remaining, need 95 more users. Zero community outreach documented.

**Evidence**:
- BETA_SPRINT assumes 300 demo views but no plan to get them
- DISC-013 identified this gap but no action plan
- No social media posts, Reddit threads, or community outreach

**Proposed Work (FOUNDER REQUIRED)**:
1. **Reddit (Day 1-2)**: Post in r/contractors, r/Construction, r/smallbusiness
   - Title: "Built a voice-to-quote tool for contractors - 60 second demo, no signup"
   - Include demo link + "First 100 beta users get lifetime discount" (scarcity)
2. **Facebook Groups (Day 1-2)**: Post in 5 contractor groups (request permission first)
3. **Blog/SEO (Day 2-3)**: Create /blog/how-to-quote-construction-jobs-faster landing page
4. UTM tracking on all links for channel attribution

**Success Metric**: 200+ demo page views; 20+ signups from community posts

---

### DISC-024: Viral Footer Enhancement on Shared Quotes (DISCOVERED)

**Source**: Growth Discovery Agent (2025-12-03)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: B2C expansion - every shared quote becomes marketing opportunity

**Problem**: "Powered by Quoted" branding exists but is passive - just text. No CTA. Customers who receive quotes see branding but don't know they can GET Quoted themselves.

**Evidence**:
- GROWTH-003: Share quote deployed
- GROWTH-005: "Powered by Quoted" branding exists
- Current branding has no call to action
- No tracking of shared_quote_viewed → signup (B2C funnel)

**Proposed Work**:
1. Enhanced footer: "Powered by Quoted - Get quotes like this in 60 seconds [Try Demo]"
2. Track: shared_quote_cta_clicked
3. Customer landing page `/for-customers`: "Your contractor uses Quoted. You can too."
4. Full funnel: shared_quote_view → cta_click → demo_view → signup

**Success Metric**: 5-10% of shared quote viewers click "Try Demo"; 3-5 B2C signups

---

### DISC-025: Landing Page Segment A/B Test (DISCOVERED) 🧪 STRATEGIC

**Source**: Strategy Discovery Agent (2025-12-03)
**Impact**: MEDIUM | **Effort**: M | **Score**: 1.0
**Sprint Alignment**: GTM clarity - which segment converts better?

**Problem**: CGO analysis shows Segment B (ballpark-only contractors) beats Segment A (qualification-focused) on EVERY metric. Yet messaging serves neither well. No data on which segment actually signs up.

**Evidence**:
- Segment B: 2x better LTV:CAC, 3-5x faster activation, higher viral coefficient
- CMO decision: "Lead with qualification" then "Defer ballpark-only"
- Current landing page has mixed messaging

**Proposed Work**:
1. Create TWO landing pages: /qualify (Segment A) and /ballpark (Segment B)
2. Split initial 100 users: 80% Segment B, 20% Segment A (per CGO recommendation)
3. Measure activation, retention, referral by segment separately
4. Pick ONE segment by January 2026 based on data

**Success Metric**: Clear winner on (Viral Coefficient × Retention × LTV) / CAC

---

### DISC-026: Pricing A/B Test ($19 vs $49) (DISCOVERED) 🧪 STRATEGIC

**Source**: Strategy Discovery Agent (2025-12-03)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Value hypothesis validation - is impulse pricing the right strategy?

**Problem**: Recent pricing drop from $29→$19 signals leadership doesn't trust value perception. At 90%+ gross margin, pricing is NOT unit economics - it's positioning. "Impulse buy" for a tool that creates business moats suggests misaligned GTM.

**Evidence**:
- CFO/CMO/CGO voted for $19 as "impulse buy" and "no-brainer"
- Original positioning: "Moat: After 50+ quotes, system knows YOUR pricing deeply"
- Cheaper than a single wasted trip to quote tire-kicker job
- Learning system is crown jewel but pricing doesn't reflect switching cost value

**Proposed Work**:
1. A/B test value-based pricing ($49 Starter) vs current impulse pricing ($19)
2. High-price cohort messaging: "Your pricing brain - learns what works, predicts what wins"
3. Track which cohort has higher LTV, lower churn, better referrals
4. Consider "outcome pricing" tier later (% of won contract value)

**Success Metric**: LTV:CAC comparison after 90 days; referral quality comparison

---

### DISC-027: LinkedIn Founder Content Blitz (DISCOVERED) 🚀 FOUNDER ACTION

**Source**: Growth Discovery Agent (2025-12-03)
**Impact**: HIGH | **Effort**: M | **Score**: 1.5
**Sprint Alignment**: Leverages founder network for 15-20 users in 6 days

**Problem**: Founder network = 30 users (per BETA_SPRINT) but no ACTIVE outreach. LinkedIn is where contractors AND vendors hang out. One viral post can reach thousands.

**Proposed Work (FOUNDER REQUIRED)**:
**Daily LinkedIn Posts (6 posts over 6 days)**:
1. Day 1: "I'm giving away quotes." (curiosity hook) + demo video
2. Day 2: Customer success story - "Contractor lost $50K job because he quoted too slow"
3. Day 3: Behind-the-scenes - "Why I built this"
4. Day 4: Testimonial (from beta users or placeholder)
5. Day 5: Urgency - "72 spots left in beta"
6. Day 6: Final push - "Last call: 28 spots left"

**Engagement**: Tag 10 contractor connections in each post; comment on competitor posts

**Success Metric**: 5,000+ impressions; 50+ landing page visits; 15-20 signups from LinkedIn

---

## Technical Debt

| Item | Priority | Effort | Notes |
|------|----------|--------|-------|
| ~~Issues API uses in-memory storage~~ | ~~LOW~~ | ~~2h~~ | RESOLVED - Migrated to SQLite (7d50e73) |
| ~~CORS allows all origins~~ | ~~LOW~~ | ~~1h~~ | RESOLVED - Restricted to quoted.it.com (7d50e73) |
| ~~No rate limiting~~ | ~~MEDIUM~~ | ~~3h~~ | RESOLVED - Added slowapi limits (7d50e73) |
| No error tracking (Sentry) | MEDIUM | 2h | Add before scaling |
| No automated tests | MEDIUM | 4h | Add unit tests for core flows |

---

## Recent Deployments

| Date | Commit | Description | Status |
|------|--------|-------------|--------|
| 2025-12-03 | 94ba6dc | Add Custom logo upload for PDF quotes (DISC-016) | **PENDING PUSH** |
| 2025-12-03 | 8c88de2 | Add Trial abuse prevention - email normalization (DISC-017) | **PENDING PUSH** |
| 2025-12-03 | 5c1ebc3 | Add Referral visibility at first quote celebration (DISC-002) | **DEPLOYED** |
| 2025-12-03 | 9607ccf | Add Analytics funnel events for full conversion tracking (DISC-004) | **DEPLOYED** |
| 2025-12-03 | 412f5da | Add Single-click trial upgrade with urgency messaging (DISC-005) | **DEPLOYED** |
| 2025-12-03 | 8628869 | Add First quote activation modal for post-onboarding (DISC-001) | **DEPLOYED** |
| 2025-12-03 | 3d8f8fa | Add Beta spots counter for social proof scarcity (DISC-015) | **DEPLOYED** |
| 2025-12-03 | fd82e2f | Update Landing page CTA hierarchy - demo as primary (DISC-003) | **DEPLOYED** |
| 2025-12-02 | 69ecdc3 | Fix Demo page JS error + disclaimer (BUG-004) | **DEPLOYED** |
| 2025-12-02 | 1fc11fe | Fix Ensure onboarding path consistency (ONBOARD-008) | **DEPLOYED** |
| 2025-12-02 | 2c7244e | Add Product demo animation on landing page (UX-004) | **DEPLOYED** |
| 2025-12-02 | 66b25b9 | Update Improve landing page headline (UX-003) | **DEPLOYED** |
| 2025-12-02 | 03993dd | Fix Quick Setup form fields match industry pricing (ONBOARD-007 + ONBOARD-006) | **DEPLOYED** |
| 2025-12-02 | e0cb0e5 | Fix Help button navigation (BUG-001) | **DEPLOYED** |
| 2025-12-02 | 8a6770f | Add Demo page frontend for try-before-signup (BUG-003) | **DEPLOYED** |
| 2025-12-02 | 709111d | Fix Share quote email sending (BUG-002) | **DEPLOYED** |
| 2025-12-02 | 2460980 | Update Reframe onboarding to recommend interview (UX-002) | **DEPLOYED** |
| 2025-12-02 | a1e6e66 | Add Guided quick setup with industry templates (ONBOARD-002) | **DEPLOYED** |
| 2025-12-02 | c6b266a | Fix Mobile responsiveness across all pages (INFRA-002) | **DEPLOYED** |
| 2025-12-02 | a7b12c2 | Add Pricing Brain global settings editor (FEAT-003) | **DEPLOYED** |
| 2025-12-02 | 5219509 | Add Interview Type C coaching with industry guidance (ONBOARD-004) | **DEPLOYED** |
| 2025-12-02 | 9eba403 | Fix Route ordering - templates before session_id parameter | **DEPLOYED** |
| 2025-12-02 | 18284c6 | Add Industry pricing template library (ONBOARD-003) | **DEPLOYED** |
| 2025-12-02 | 7d4c86e | Add FAQ/Help section (INFRA-003) | **DEPLOYED** |
| 2025-12-02 | d9b7a36 | Add Dormancy re-engagement email templates (RETAIN-002) | **DEPLOYED** |
| 2025-12-02 | 19e304f | Add Industry selection UI for onboarding (ONBOARD-001) | **DEPLOYED** |
| 2025-12-02 | 5d0e693 | Add Industry selection API for onboarding (ONBOARD-001) | **DEPLOYED** |
| 2025-12-02 | 732c643 | Add Engagement email series templates (RETAIN-001) | **DEPLOYED** |
| 2025-12-02 | 5610036 | Add Improved quote input placeholder text (UX-001) | **DEPLOYED** |
| 2025-12-02 | 408586f | Add Share Quote API and UI (GROWTH-003) | **DEPLOYED** |
| 2025-12-02 | 48cb784 | Add Expand trade defaults to 20+ industries (ONBOARD-005) | **DEPLOYED** |
| 2025-12-02 | 8f7b635 | Add Enhanced empty states for quotes and pricing brain (CONVERT-002) | **DEPLOYED** |
| 2025-12-02 | 6c7c94a | Add Pricing Brain Management UI (FEAT-001 Frontend) | **DEPLOYED** |
| 2025-12-02 | 28a98f9 | Add Customer edit endpoint for quotes (FEAT-002 Backend) | **DEPLOYED** |
| 2025-12-02 | fa0f7a4 | Add Edit customer info on existing quotes (FEAT-002 Frontend) | **DEPLOYED** |
| 2025-12-02 | 1361539 | Add Pricing Brain Management API (FEAT-001 Backend) | **DEPLOYED** |
| 2025-12-02 | 59883ef | Fix Randomize landing page slot animation (FIX-001) | **DEPLOYED** |
| 2025-12-02 | b06b712 | Fix category matching - register categories on quote generation | **DEPLOYED** |
| 2025-12-02 | 5a84de5 | Add billing column migrations for existing Postgres databases | **DEPLOYED** |
| 2025-12-02 | 6aedad1 | Add annual billing interval support | **DEPLOYED** |
| 2025-12-02 | f871c12 | Fix pricing card field mapping (API response → frontend) | **DEPLOYED** |
| 2025-12-02 | b4e9fdc | Add Billing UI with pricing, usage tracking, upgrade modal | **DEPLOYED** |
| 2025-12-02 | 33fa641 | Add Resend email service for transactional emails | **DEPLOYED** |
| 2025-12-02 | cb1e311 | Add Stripe payment infrastructure for subscription billing | **DEPLOYED** |
| 2025-12-02 | 325fb25 | Add Terms of Service and Privacy Policy pages | **DEPLOYED** |
| 2025-12-02 | 7d50e73 | Security hardening: SQLite issues, rate limiting, CORS, HTTPS | SUCCESS |
| 2025-12-02 | eb290f0 | Add autonomous operations infrastructure | SUCCESS |
| 2025-12-01 | 43af5c6 | Add quote history UI with editable line items | SUCCESS |

---

## Architecture Notes

### Stack
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL (Railway) - Production; SQLite (dev fallback)
- **AI**: Claude Sonnet 4 (quotes) + Claude Haiku (category detection)
- **Transcription**: OpenAI Whisper
- **PDF**: ReportLab
- **Hosting**: Railway (web service + Postgres)

### Key Files
- `backend/main.py` - FastAPI app entry
- `backend/services/quote_generator.py` - Core quote generation
- `backend/services/learning.py` - Correction processing
- `backend/services/billing.py` - Stripe subscription handling
- `backend/services/email.py` - Resend transactional emails
- `backend/services/pricing_brain.py` - Pricing Brain business logic (NEW)
- `backend/api/pricing_brain.py` - Pricing Brain REST API (NEW)
- `backend/prompts/quote_generation.py` - Prompt construction (learning injection)
- `frontend/index.html` - Main app (includes Pricing Brain UI)
- `frontend/landing.html` - Landing page (with randomized slot animation)
- `frontend/terms.html` - Terms of Service
- `frontend/privacy.html` - Privacy Policy

### API Endpoints
```
/api/auth/*           - Authentication
/api/quotes/*         - Quote CRUD, generation, PDF, customer edit
/api/billing/*        - Stripe subscriptions, checkout, portal
/api/pricing-brain/*  - Category management, AI analysis (NEW)
/api/contractors/*    - Contractor profile
/api/onboarding/*     - Setup interview
/api/issues/*         - Issue reporting (autonomous processing)
/terms                - Terms of Service page
/privacy              - Privacy Policy page
```

---

## On-Call

**Primary**: Autonomous AI Engineering
**Escalation**: Eddie (Founder) for Type 3-4 decisions

---

## Incidents

| Date | Severity | Issue | Resolution | Post-mortem |
|------|----------|-------|------------|-------------|
| 2025-12-02 | MEDIUM | Missing billing columns in Postgres (500 errors on /api/quotes) | Added auto-migrations for billing columns (5a84de5) | SQLAlchemy create_all doesn't add columns to existing tables; need explicit ALTER migrations |

---

## Known Issues

| Issue | Severity | Workaround | Fix ETA |
|-------|----------|------------|---------|
| ~~Issues reset on Railway restart~~ | ~~LOW~~ | ~~None~~ | RESOLVED (SQLite) |
| No issues currently | - | - | - |

---

## Environment Variables

Required in Railway:
```
# Existing (already set)
ANTHROPIC_API_KEY     - Claude API key
OPENAI_API_KEY        - Whisper transcription
SESSION_SECRET        - Auth session signing
ENVIRONMENT           - "production"

# PAYMENT - Add before deployment
STRIPE_SECRET_KEY=sk_test_51SZugaKF9pNNNH32WtiBokn1imZ0IFRdRr38mht4mpebsaZWaH5YM2RhfF2pbxpju2Yo9Z2f67pVTYPdVnLqwBMM000CI0hXIl
STRIPE_PUBLISHABLE_KEY=pk_test_51SZugaKF9pNNNH32PsjrEPHK1ynwZ1vTnHRHlQKqdS5u6r2ivaMcLTpvpK5H1VehWBLyx4hTn5rsZXTza8oVM9qM00K5n28vOe
STRIPE_STARTER_PRODUCT_ID=prod_TWyp6aH4vMY7A8
STRIPE_PRO_PRODUCT_ID=prod_TWyzygs71MWNeQ
STRIPE_TEAM_PRODUCT_ID=prod_TWz0uN0EAbgPKI
STRIPE_WEBHOOK_SECRET=whsec_...  # Generate in Stripe dashboard after deployment

# EMAIL - Add before deployment
RESEND_API_KEY=re_igyXR4D5_6VcjoKhx6SUjPAWZ9UsLwWx6
```

**Post-Deployment Steps**:
1. Add all env vars above to Railway
2. Deploy (auto on push to main)
3. Configure Stripe webhook: `https://quoted.it.com/api/billing/webhook`
4. Get webhook secret from Stripe, add `STRIPE_WEBHOOK_SECRET` to Railway
5. Test checkout flow end-to-end

---

## Testing

| Type | Coverage | Status |
|------|----------|--------|
| Unit Tests | 0% | NOT IMPLEMENTED |
| Integration Tests | 0% | NOT IMPLEMENTED |
| Manual Testing | 100% | Ongoing |

**Note**: MVP shipped without automated tests. Add before scaling.
