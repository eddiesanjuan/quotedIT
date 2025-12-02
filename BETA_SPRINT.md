# Beta Sprint: 100 Users in 2 Weeks

**Created**: 2025-12-02
**Goal**: 100 active beta testers by 2025-12-16
**Sprint Duration**: December 2 - December 16, 2025

---

## The Problem

The product is technically functional but missing critical infrastructure for growth:

| Category | Status | Impact on 100-User Goal |
|----------|--------|------------------------|
| **Error Tracking** | MISSING | Can't detect/fix issues before users report |
| **Analytics** | MISSING | Can't measure conversion or identify dropoff |
| **Demo Mode** | MISSING | Friction: must signup before trying product |
| **Referral System** | MISSING | No viral growth mechanism |
| **Share Quotes** | MISSING | Can't easily send quotes to customers |
| **Mobile UX** | PARTIAL | Contractors use phones on job sites |
| **Empty States** | BASIC | No guidance when user has no data |
| **Help/FAQ** | MISSING | Users stuck with no self-service support |
| **Engagement Emails** | MISSING | No re-engagement for inactive users |

---

## Success Metrics

| Metric | Current | Target | Tracking |
|--------|---------|--------|----------|
| Registered Users | ~5 | 100 | Database count |
| Activation Rate (first quote) | Unknown | 60% | Analytics (after INFRA-002) |
| 7-Day Retention | Unknown | 40% | Analytics (after INFRA-002) |
| Referral Rate | 0% | 15% | Referral tracking (after GROWTH-002) |
| Error Detection Time | Manual | < 5 min | Sentry alerts (after INFRA-001) |

---

## Task Tiers (Priority Order)

### Tier 1: Launch Blockers
*Must complete before inviting users. Without these, we're flying blind.*

| Ticket | Description | Scope | Why Critical |
|--------|-------------|-------|--------------|
| **INFRA-001** | Sentry Error Tracking | 2h | Can't fix what we can't see |
| **INFRA-002** | Basic Analytics (PostHog) | 4h | Can't optimize without data |
| **GROWTH-001** | Demo Mode (Try Before Signup) | 6h | Removes biggest conversion barrier |
| **UX-001** | Mobile Responsiveness Audit | 4h | Contractors use phones on job sites |

### Tier 2: Growth Levers
*Enable user acquisition and viral growth.*

| Ticket | Description | Scope | Why Important |
|--------|-------------|-------|---------------|
| **GROWTH-002** | Referral System | 6h | Viral coefficient for free growth |
| **GROWTH-003** | Share Quote (Email/SMS) | 4h | Completes the contractor workflow |
| **CONTENT-001** | FAQ/Help Section | 3h | Self-service reduces support load |
| **UX-002** | Enhanced Empty States | 2h | Guide new users to first action |

### Tier 3: Retention
*Keep users coming back.*

| Ticket | Description | Scope | Why Important |
|--------|-------------|-------|---------------|
| **ENG-001** | Engagement Email Series | 4h | Tips, milestones, education |
| **ENG-002** | Dormancy Re-engagement | 2h | Win back inactive users |
| **UX-003** | First Quote Celebration | 1h | Positive reinforcement |
| **FEEDBACK-001** | Contextual Feedback Triggers | 2h | Capture insights at right moment |

### Tier 4: Polish
*Nice to have, do if time permits.*

| Ticket | Description | Scope | Why Nice |
|--------|-------------|-------|----------|
| **UX-004** | Loading States & Skeletons | 2h | Perceived performance |
| **UX-005** | Tablet Breakpoints | 2h | iPad users |
| **CONTENT-002** | Video Walkthrough Embed | 2h | Visual learners |
| **TRUST-001** | Testimonial Collection | 3h | Social proof for landing |

---

## Detailed Ticket Specifications

### INFRA-001: Sentry Error Tracking

**Priority**: CRITICAL (Tier 1)
**Scope**: Backend + Frontend (2h)
**Dependencies**: None

**Problem**: No visibility into production errors. Users encounter issues silently.

**Implementation**:
1. Add `sentry-sdk[fastapi]` to requirements.txt
2. Initialize Sentry in `backend/main.py`:
   ```python
   import sentry_sdk
   sentry_sdk.init(
       dsn="$SENTRY_DSN",
       environment=os.getenv("ENVIRONMENT", "development"),
       traces_sample_rate=0.1,
   )
   ```
3. Add Sentry JS to `frontend/index.html`:
   ```html
   <script src="https://browser.sentry-cdn.com/7.x/bundle.min.js"></script>
   <script>Sentry.init({ dsn: "..." });</script>
   ```
4. Configure Sentry project alerts (email on error)
5. Add SENTRY_DSN to Railway environment

**Acceptance Criteria**:
- [ ] Backend errors captured in Sentry dashboard
- [ ] Frontend errors captured with stack traces
- [ ] Alert configured for P1 errors

---

### INFRA-002: Basic Analytics (PostHog)

**Priority**: CRITICAL (Tier 1)
**Scope**: Backend + Frontend (4h)
**Dependencies**: None

**Problem**: No visibility into user behavior, conversion funnels, or feature adoption.

**Events to Track**:
```
# Acquisition
page_view (landing)
signup_started
signup_completed

# Activation
onboarding_started
onboarding_interview_completed
onboarding_quick_setup_completed
first_quote_generated

# Engagement
quote_generated
quote_edited
quote_pdf_downloaded
pricing_correction_submitted

# Conversion
trial_started
upgrade_modal_opened
checkout_started
subscription_activated

# Retention
session_started
feature_used (feature_name)
```

**Implementation**:
1. Create PostHog account (free tier: 1M events/month)
2. Add PostHog JS to frontend:
   ```javascript
   posthog.init('phc_...', {api_host: 'https://app.posthog.com'})
   ```
3. Track events at key touchpoints in frontend
4. Add PostHog Python SDK for backend events:
   ```python
   posthog.capture(user_id, 'quote_generated', {'category': category})
   ```
5. Create conversion funnel: Landing → Signup → Onboarding → First Quote

**Acceptance Criteria**:
- [ ] All events listed above firing correctly
- [ ] Conversion funnel visible in PostHog dashboard
- [ ] Can segment by user properties

---

### GROWTH-001: Demo Mode (Try Before Signup)

**Priority**: CRITICAL (Tier 1)
**Scope**: Frontend + Backend (6h)
**Dependencies**: None

**Problem**: Users must create account and complete 5-15 min onboarding before seeing if product works. High friction = low conversion.

**Solution**: 2-minute demo that generates a real quote without signup.

**Demo Flow**:
1. Landing page: "Try it now - no signup required" button
2. Demo page shows:
   - Pre-filled contractor type: "General Contractor"
   - Pre-configured pricing: Standard rates
   - Voice recorder OR sample text input
3. User records/enters job description
4. System generates real quote (no auth required)
5. Show quote with watermark: "DEMO - Sign up to save"
6. CTA: "Create free account to save this quote"

**Implementation**:
1. Add `/demo` route in frontend
2. Create `POST /api/demo/quote` endpoint (no auth):
   - Uses generic contractor profile
   - Returns quote without saving to database
   - Rate limited: 3/hour per IP
3. Demo quote display with limitations:
   - Watermarked PDF
   - Can't save or edit
   - Customer info disabled
4. Prominent signup CTA after quote generation

**Acceptance Criteria**:
- [ ] Demo accessible without signup
- [ ] Quote generated in < 30 seconds
- [ ] Clear path from demo → signup
- [ ] Rate limiting prevents abuse

---

### GROWTH-002: Referral System

**Priority**: HIGH (Tier 2)
**Scope**: Backend + Frontend (6h)
**Dependencies**: INFRA-002 (for tracking)

**Problem**: No viral growth mechanism. Users have no incentive to share.

**Referral Program**:
- Referrer gets: 1 free month when referral subscribes
- Referee gets: Extended trial (14 days instead of 7)
- Tracking: Unique referral codes per user

**Implementation**:
1. Add to User model:
   ```python
   referral_code = Column(String, unique=True)  # e.g., "JOHN-A3X9"
   referred_by = Column(String, nullable=True)
   referral_count = Column(Integer, default=0)
   ```
2. Generate referral code on registration
3. Add referral endpoints:
   ```
   GET /api/referral/code - Get user's referral code
   GET /api/referral/stats - Referral count, rewards earned
   POST /api/referral/apply - Apply referral code during signup
   ```
4. Frontend: Referral section in Account showing:
   - Personal referral link
   - Share buttons (copy, email, SMS)
   - Referral stats
5. Stripe integration: Apply credit on successful referral

**Acceptance Criteria**:
- [ ] Unique referral codes generated for each user
- [ ] Referral link applies extended trial
- [ ] Referrer credited when referee subscribes
- [ ] Tracking visible in user dashboard

---

### GROWTH-003: Share Quote to Email/SMS

**Priority**: HIGH (Tier 2)
**Scope**: Backend + Frontend (4h)
**Dependencies**: None

**Problem**: After generating a quote, contractors must manually export PDF and email it. Friction in core workflow.

**Solution**: One-click share to customer via email or SMS.

**Implementation**:
1. Add "Share" button to quote detail view
2. Share modal with options:
   - Email: Enter customer email, optional message
   - SMS: Enter customer phone, sends link
   - Copy Link: Shareable URL (read-only quote view)
3. Backend endpoints:
   ```
   POST /api/quotes/{id}/share/email - Send quote via email
   POST /api/quotes/{id}/share/sms - Send quote via SMS (Twilio)
   GET /api/quotes/shared/{token} - Public quote view (read-only)
   ```
4. Email template: Professional quote email with PDF attachment
5. Public quote view: Branded, read-only, with contractor contact info

**Acceptance Criteria**:
- [ ] Quotes can be emailed with one click
- [ ] Public quote link works without login
- [ ] Contractor branding on shared quotes
- [ ] Track shares in analytics

---

### UX-001: Mobile Responsiveness Audit

**Priority**: CRITICAL (Tier 1)
**Scope**: Frontend (4h)
**Dependencies**: None

**Problem**: Only one mobile breakpoint (640px). Contractors use phones on job sites. Current UI may be cramped or unusable.

**Audit Checklist**:
1. [ ] Voice recording works on mobile browsers
2. [ ] Touch targets are minimum 44x44px
3. [ ] Modals fit on small screens without scrolling issues
4. [ ] Navigation is thumb-friendly
5. [ ] Quote editing is usable on phone
6. [ ] Text is readable without zooming

**Implementation**:
1. Test on real devices: iPhone SE (small), iPhone 14 (medium), iPad (tablet)
2. Add tablet breakpoint: `@media (max-width: 900px)`
3. Fix identified issues:
   - Increase touch targets on buttons
   - Stack navigation on mobile
   - Simplify modals for small screens
4. Test voice recording on iOS Safari, Android Chrome

**Acceptance Criteria**:
- [ ] All core flows work on iPhone SE
- [ ] No horizontal scrolling on any screen
- [ ] Voice recording tested on iOS + Android
- [ ] Touch targets meet accessibility guidelines

---

### UX-002: Enhanced Empty States

**Priority**: MEDIUM (Tier 2)
**Scope**: Frontend (2h)
**Dependencies**: None

**Problem**: Empty states are minimal. New users see blank screens with no guidance.

**Empty States to Enhance**:
1. **My Quotes (no quotes)**:
   - Illustration + "Create your first quote in 2 minutes"
   - Big CTA: "Generate Quote"
   - Tip: "Try the voice recorder - just describe the job"

2. **Quote History (no history)**:
   - "Your quote history will appear here"
   - Explain value: "Track all your quotes and see patterns"

3. **Pricing Brain (no learned data)**:
   - "The AI hasn't learned your pricing yet"
   - "Generate a few quotes and it will start adapting"

**Implementation**:
1. Create SVG illustrations or use simple icons
2. Write encouraging, action-oriented copy
3. Add prominent CTAs that lead to next action
4. Style consistently with brand

**Acceptance Criteria**:
- [ ] All empty states have illustration + copy + CTA
- [ ] Copy is encouraging and action-oriented
- [ ] CTAs lead to logical next step

---

### CONTENT-001: FAQ/Help Section

**Priority**: MEDIUM (Tier 2)
**Scope**: Frontend (3h)
**Dependencies**: None

**Problem**: No self-service support. Users with questions have only email support.

**FAQ Topics**:
1. **Getting Started**
   - How does voice-to-quote work?
   - What if the AI gets my pricing wrong?
   - How do I set up my pricing model?

2. **Pricing & Billing**
   - What's included in each plan?
   - How does the quote limit work?
   - What happens after my trial?

3. **Using Quoted**
   - How do I edit a quote?
   - Can I add my logo?
   - How do I share quotes with customers?

4. **Troubleshooting**
   - Voice recording not working?
   - Quote seems inaccurate?
   - How do I report an issue?

**Implementation**:
1. Add `/help` route to frontend
2. Create FAQ page with accordion-style questions
3. Link to help from:
   - Main navigation
   - Footer
   - Contextual locations (e.g., "Having trouble?" links)
4. Include contact email for issues not covered

**Acceptance Criteria**:
- [ ] FAQ covers top 10 expected questions
- [ ] Accessible from multiple locations
- [ ] Search-friendly (plain HTML, not JS-rendered)

---

### ENG-001: Engagement Email Series

**Priority**: MEDIUM (Tier 3)
**Scope**: Backend (4h)
**Dependencies**: PAY-004 (email service - COMPLETE)

**Problem**: After welcome email, no further engagement. Users forget about product.

**Email Series**:
1. **Day 1 (post-first-quote)**: "Your first quote is ready!" + tips
2. **Day 3**: "Pro tip: How to handle rush job pricing"
3. **Day 5**: "Did you know? You can edit quotes anytime"
4. **Day 7 (trial ending)**: Already implemented
5. **Day 14**: "You've generated X quotes this week" (if active)
6. **Day 14**: "We miss you!" (if inactive)

**Implementation**:
1. Add email templates to `backend/services/email.py`
2. Create background job system (or use Railway cron)
3. Track email sent status to prevent duplicates
4. Add unsubscribe handling (required for CAN-SPAM)

**Acceptance Criteria**:
- [ ] Emails trigger at correct intervals
- [ ] Personalized with user's quote data
- [ ] Unsubscribe link in all emails
- [ ] No duplicate sends

---

### ENG-002: Dormancy Re-engagement

**Priority**: MEDIUM (Tier 3)
**Scope**: Backend (2h)
**Dependencies**: ENG-001, INFRA-002

**Problem**: Users who stop using product are lost forever.

**Re-engagement Triggers**:
- 7 days inactive: "Quick check-in" email
- 14 days inactive: "We've made improvements" email
- 30 days inactive: "Special offer to come back" email

**Implementation**:
1. Track last_active_at on User model
2. Daily cron job checks for inactive users
3. Send appropriate re-engagement email
4. Track opens/clicks to measure effectiveness

**Acceptance Criteria**:
- [ ] Inactive users receive re-engagement emails
- [ ] Emails are spaced appropriately (not spammy)
- [ ] Can track re-engagement success rate

---

## Execution Plan

**Week 1 (Dec 2-8): Foundation**
- INFRA-001: Sentry (Day 1-2)
- INFRA-002: Analytics (Day 2-3)
- UX-001: Mobile audit (Day 3-4)
- GROWTH-001: Demo mode (Day 4-6)

**Week 2 (Dec 9-16): Growth**
- GROWTH-002: Referrals (Day 1-2)
- GROWTH-003: Share quotes (Day 2-3)
- UX-002: Empty states (Day 3)
- CONTENT-001: FAQ (Day 3-4)
- ENG-001: Email series (Day 4-5)
- Polish remaining items (Day 5-7)

---

## User Acquisition Strategy

**With the above infrastructure, here's how we get to 100:**

1. **Founder Network (30 users)**
   - Eddie's contractor contacts
   - EF San Juan network
   - Direct outreach with demo link

2. **Referral Viral Loop (40 users)**
   - Each user refers 1.3 users on average
   - 30 initial × 1.3 referral rate = ~40 additional

3. **Demo Conversion (30 users)**
   - Share demo link on social/forums
   - Contractor subreddits, Facebook groups
   - 300 demo tries × 10% conversion = 30 users

**Total**: 30 + 40 + 30 = 100 users

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Voice recording fails on mobile | HIGH | UX-001 includes device testing |
| Demo abuse (spam) | MEDIUM | Rate limiting in GROWTH-001 |
| Users don't refer | MEDIUM | Make referral reward compelling |
| Analytics overwhelm | LOW | Start with key events only |
| Email deliverability | MEDIUM | Use Resend (already configured) |

---

## Definition of Done

Sprint is complete when:
- [ ] INFRA-001, INFRA-002, GROWTH-001, UX-001 deployed (Tier 1)
- [ ] GROWTH-002, GROWTH-003, UX-002, CONTENT-001 deployed (Tier 2)
- [ ] Conversion funnel visible in analytics
- [ ] 0 unhandled errors in Sentry for 24h
- [ ] Demo mode tested and live
- [ ] Referral system generating codes

---

## Autonomous Team Instructions

The autonomous engineering team should:

1. **Pick up Tier 1 tickets first** - These block user acquisition
2. **Work in parallel where possible** - INFRA-001 + UX-001 have no dependencies
3. **Deploy incrementally** - Each ticket is independently valuable
4. **Track progress in ENGINEERING_STATE.md** - Update status after each deployment
5. **Escalate blockers immediately** - Don't wait for daily check-ins

**Decision Authority**:
- Type 1 (autonomous): Implementation details, copy, styling
- Type 2 (async approval): API design, third-party service selection
- Type 3 (sync required): Pricing changes, feature scope changes
