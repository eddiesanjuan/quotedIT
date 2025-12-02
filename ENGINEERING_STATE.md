# Engineering State

**Last Updated**: 2025-12-02 21:15 PST
**Updated By**: CEO (AI)

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
| BUG-001 | Help Button Navigation Broken | Frontend | **READY** | None |
| ONBOARD-006 | Expand Industries Beyond Construction | Frontend + Backend | **READY** | None |
| ONBOARD-007 | Quick Setup Form/Tips Mismatch | Frontend + Backend | **READY** | None |
| ONBOARD-008 | Ensure Onboarding Path Consistency | Backend | **READY** | None |
| UX-003 | Improve Landing Page Headline | Frontend | **READY** | None |
| UX-004 | Add Product Demo Animation to Landing Page | Frontend | **READY** | None |

---

## BUG-001: Help Button Navigation Broken (READY)

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
| 2025-12-02 | 8a6770f | Add Demo page frontend for try-before-signup (BUG-003) | **PENDING PUSH** |
| 2025-12-02 | 709111d | Fix Share quote email sending (BUG-002) | **PENDING PUSH** |
| 2025-12-02 | 2460980 | Update Reframe onboarding to recommend interview (UX-002) | **PENDING PUSH** |
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
