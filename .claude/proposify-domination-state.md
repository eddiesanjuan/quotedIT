# Proposify Domination - State Tracker

## Current Phase
**Phase**: 4 - Implementation (Wave 1 Deployed & QA Passed)
**Last Updated**: 2024-12-24
**Status**: Wave 1 LIVE in production - all QA tests passed

### Wave 1 Deployment Summary
- **PR #14**: Merged to main (commit 737ea24)
- **Database Migration**: Applied (commit 003974c)
- **Production URL**: https://quoted.it.com
- **QA Status**: ✅ ALL TESTS PASSED
  - Invoice share route: ✅ Returns HTML page
  - Quote share route: ✅ Returns HTML page
  - Accept endpoint: ✅ Working (returns "Quote not found" for invalid token)
  - Reject endpoint: ✅ Working (returns "Quote not found" for invalid token)
  - Accept/Reject UI: ✅ Elements present (btnAccept, btnReject, quoteActions)

---

## Phase Progress

### Phase 0: Context Loading
- [x] COMPANY_STATE.md summarized
- [x] ENGINEERING_STATE.md summarized
- [x] DISCOVERY_BACKLOG.md summarized
- [x] Proposify product analysis complete
- [x] Technical reality baseline established

### Phase 1: Deep Audit
- [x] Quote Sharing audit complete
- [x] Invoice System audit complete
- [x] CRM System audit complete
- [x] Tasks System audit complete
- [x] Quote Lifecycle audit complete
- [x] Audit synthesis complete

### Phase 2: 10x Design
- [x] Invoice Public View design (Fix 404 first)
- [x] Quote Accept/Reject design (Core workflow)
- [x] E-Signatures design (typed-name, included in accept/reject)
- [x] Share Analytics design
- [x] Auto-Reminders design
- [ ] Online Payment design (deferred - not blocking)

### Phase 3: Technical Specs
- [x] All specs written (inline with designs)
- [x] Founder review complete (decisions made autonomously)

### Phase 4: Implementation
- [x] Wave 1 (Foundation) complete ✅
  - [x] Invoice 404 fixed (main.py route + invoices.py API)
  - [x] invoice-view.html created
  - [x] Quote accept/reject endpoints added (share.py)
  - [x] Quote accept/reject UI added (quote-view.html)
  - [x] Signature fields added to Quote model
  - [x] sent_at fix when emailing (KI-012)
  - [x] Error message fixed "Quote not found" (KI-008)
  - [x] view_count tracking in database (KI-004)
- [ ] Wave 2 (Analytics & Status) - pending
- [ ] Wave 3 (Background Jobs) - pending
- [ ] Wave 4 (Notifications) - pending

### Phase 5: QA
- [x] Wave 1 features tested ✅
- [x] Database migration bug found and fixed ✅
- [ ] End-to-end test with real quote (pending - needs Eddie to create quote)

### Phase 6: Release
- [ ] Staged rollout complete
- [ ] GA achieved

---

## Phase 1 Audit Synthesis

### Executive Summary

| Feature | Status | Critical Issues |
|---------|--------|-----------------|
| Quote Sharing | 🟡 YELLOW | view_count not persisted |
| Invoice System | 🟡 YELLOW | **CRITICAL**: /invoice/{token} 404 |
| CRM System | 🟢 GREEN | None - fully functional |
| Tasks System | 🟡 YELLOW | Notifications dead code |
| Quote Lifecycle | 🔴 RED | Accept/reject workflow missing |

### Critical Issues (Must Fix Before Launch)

| # | Issue | Severity | File:Line | Fix Required |
|---|-------|----------|-----------|--------------|
| 1 | Invoice share link 404 | **CRITICAL** | invoices.py:638-639 | Create `/invoice/{token}` route + invoice-view.html |
| 2 | Quote accept/reject missing | **CRITICAL** | quote-view.html | Add accept/reject buttons + backend endpoints |
| 3 | view_count not in database | HIGH | share.py:335-349 | Add view_count field to Quote model |
| 4 | Task reminders dead code | HIGH | database.py:585 | Implement background job for reminder_time |
| 5 | Quote status never changes | HIGH | database.py:325 | Status transitions draft→sent→accepted |

### Proposify Gap Analysis

| Feature | Proposify | Quoted | Priority |
|---------|-----------|--------|----------|
| E-Signatures | ✅ Full DocuSign-style | ❌ Not implemented | P0 |
| Quote Accept/Reject | ✅ Customer clicks button | ❌ Read-only view | P0 |
| Document Tracking | ✅ Views, time spent | 🟡 PostHog only | P1 |
| Auto-Reminders | ✅ Configurable sequences | ❌ Fields exist, no jobs | P1 |
| Online Payments | ✅ Stripe integration | ❌ Not implemented | P2 |
| Quote Expiration | ✅ Auto-expire + notify | ❌ quote_valid_days unused | P2 |
| Invoice Portal | ✅ Customer can view/pay | ❌ 404 error | P0 |
| CRM Integration | ✅ Salesforce, HubSpot | ✅ Built-in CRM | ✅ ADVANTAGE |
| Voice-First | ❌ Desktop only | ✅ Core differentiator | ✅ ADVANTAGE |
| Field-Optimized | ❌ Enterprise focused | ✅ Mobile-first | ✅ ADVANTAGE |

### Recommended Fix Order

**Wave 1: Critical Bugs (Week 1)**
1. Fix invoice 404 - create `/invoice/{token}` route + invoice-view.html
2. Add quote accept/reject workflow to quote-view.html + backend

**Wave 2: Status Tracking (Week 2)**
3. Implement quote status transitions (draft→sent→viewed→accepted)
4. Add view_count to Quote model, persist on view
5. Fix "link expired" error message

**Wave 3: Notifications (Week 3)**
6. Implement task reminder background job
7. Add email notification on quote acceptance
8. Add contractor notification on quote view

**Wave 4: Enhancement (Weeks 4-5)**
9. E-signatures on acceptance
10. Quote expiration enforcement
11. Share analytics dashboard

### Founder Questions (ALL DECIDED)

1. ~~**Invoice 404**: Should invoice-view.html be a copy of quote-view.html with invoice branding, or a completely separate design?~~
   **DECIDED**: Copy quote-view.html with invoice branding. Same structure (line items, totals, customer info), minor differences (invoice #, due date, payment status). Shared template base with conditional logic.

2. ~~**E-Signatures**: Full DocuSign-level legal compliance, or simple "type your name" acceptance?~~
   **DECIDED**: Typed-name signatures only. API-based signatures cost $0.50-3.00 each, unacceptable at $9/mo pricing.

3. ~~**Auto-Reminders**: Should we implement background jobs now (more complex) or defer to post-MVP?~~
   **DECIDED**: Implement now. Cost is ~$5-10/mo TOTAL (not per-user), amortizes to near-zero at scale.

4. ~~**Quote Expiration**: Strict enforcement (can't accept expired quotes) or soft warning only?~~
   **DECIDED**: Soft warning with contractor control. Show prominent "This quote expired on [date]" banner but allow acceptance. Add contractor setting to enable strict mode ("Block acceptance after expiration") if desired.

5. ~~**Network Monetization Priority**: Which platform opportunity to build hooks for first?~~
   **DECIDED**: Financing integration (Wisetack/Affirm) first.
   - Highest $/transaction ($50-200 referral per financed job)
   - No user acquisition needed (just a button)
   - Natural fit for high-ticket jobs (HVAC, roofing, auto body, events)
   - No network effects required (works immediately)
   - Partners actively seeking integrations

---

## Audit Findings Summary

### Quote Sharing (GROWTH-003)
**Status**: 🟡 YELLOW
**Verified Working**:
- Email share with PDF attachment (share.py:167-185)
- Shareable link generation with secure tokens (share.py:257-271)
- Public quote view endpoint works (share.py:310-371)
- Frontend share modal functional (index.html:5968-6012)
- PostHog event tracking (share.py:196-210)
- Quote-view.html renders correctly, mobile responsive
**Gaps**:
- No `view_count` in database (PostHog only)
- No contractor analytics dashboard
- No share link revocation
- No view notifications to contractor
**Critical Issues**:
- view_count not persisted - HIGH - add field to Quote model
- Error message says "link expired" but links never expire - fix wording

### Invoice System (DISC-071)
**Status**: 🟡 YELLOW - CRITICAL BUG
**Verified Working**:
- Full CRUD API (invoices.py:183-445)
- Mark-paid endpoint works (invoices.py:452-502)
- PDF generation works (invoices.py:505-599)
- Quote-to-invoice conversion (invoices.py:706-720)
- Send email generates share_url (invoices.py:608-699)
- Feature flag infrastructure exists (feature_flags.py)
- Invoice model complete with share_token (database.py:436-511)
**Gaps**:
- No public `/invoice/{token}` route - BROKEN
- No invoice-view.html template
- Feature flag not enforced in frontend
- No online payment integration (Stripe)
- No invoice reminders
**Critical Issues**:
- **CRITICAL**: /invoice/{token} route missing - customers get 404 (invoices.py:638-639 generates URL, no route serves it)
- Feature flag not checked in frontend UI - always visible

### CRM System (DISC-085-092)
**Status**: 🟢 GREEN
**Verified Working**:
- Customer table with all fields (database.py:515-558)
- Deduplication logic (customer_service.py:find_or_create_customer)
- Full CRUD API with 17 endpoints (customers.py)
- Voice command routing (crm_voice.py - 7 intents)
- Quote-to-customer auto-linking (quotes.py:472-479)
- Frontend UI complete (index.html:5029-5309)
- Navigation button present (index.html:4323)
- Backfill script for historical data
**Gaps**:
- No pipeline stages (Lead→Won is implicit)
- No custom fields
- No activity timeline
- No customer merge capability
**Critical Issues**: None - fully functional for MVP

### Tasks System (DISC-092)
**Status**: 🟡 YELLOW - Partial Implementation
**Verified Working**:
- Full CRUD API (tasks.py - 9 endpoints)
- Task model with 22 columns (database.py:560-611)
- Frontend UI complete - list, create, snooze, complete
- Task summary badges (overdue, today, upcoming)
- Quick task creation from voice
- Customer/quote linking (task.customer_id, task.quote_id)
**Gaps**:
- reminder_time field NEVER used - dead code
- notification_sent NEVER set
- No background job runner (APScheduler, Celery)
- recurrence fields exist but never processed
- auto_generated fields exist but no automation
**Critical Issues**:
- **HIGH**: reminder_time/notification_sent are dead code - creates confusion
- **HIGH**: No email notifications for task reminders
- DISC-092 marked DEPLOYED but core functionality is stubbed

### Quote Lifecycle
**Status**: 🔴 RED - Missing Core Workflow
**Verified Working**:
- Quote creation with status="draft"
- Quote sharing via email/link
- Public quote view (read-only)
- Customer info linking
**Gaps**:
- **NO ACCEPT/REJECT WORKFLOW** - quote-view.html is 100% read-only
- Status never transitions: draft→sent→accepted/rejected/expired
- outcome/outcome_notes fields never set
- quote_valid_days never enforced
- No expiration check on shared quotes
- sent_at not set when emailing
**Critical Issues**:
- **CRITICAL**: No way for customers to accept/reject quotes
- **CRITICAL**: Quote status is ALWAYS "draft", never "sent"/"accepted"/"rejected"
- Quote.expires_at field doesn't exist despite "expired" status in schema
- Misleading error "link expired" (links never expire)

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2024-12-24 | Re-running Phase 1 with v2.1 orchestrator | Testing improved sequential audit pattern |
| 2024-12-24 | Phase 1 complete | All 5 audits finished, synthesis ready |
| 2024-12-24 | v3.0: Added Known Issues Registry | Prevent re-discovery of documented issues |
| 2024-12-24 | v3.1: Added Strategic Constraints | Bake in pricing philosophy and platform vision |
| 2024-12-24 | Pricing: NO INCREASE for new features | $9/mo and $59/yr maintains margin moat |
| 2024-12-24 | E-signatures: Typed-name only | API signatures ($0.50-3/each) unacceptable at this price point |
| 2024-12-24 | Multi-segment: NOT just contractors | Photographers, consultants, auto shops, events, etc. |
| 2024-12-24 | Network-first: Future platform monetization | Build hooks for financing, referrals, benchmarks |

---

## Blockers

**None** - All founder decisions made, proceeding autonomously.

---

## Context Baseline (from Phase 0)

### Company Phase
Quoted is in Beta with ~10 active contractors. Revenue: $0 (pre-revenue). Focus is on product-market fit validation.

### Key Metrics
- Active users: ~10 beta contractors
- Quotes generated: ~200+
- Quote value: $50K+ total

### Proposify Competitive Intel
- Pricing: Basic $19/mo (5 sends), Team $41/mo (unlimited), Business $3,900/yr
- Key features: E-signatures, document tracking, auto-reminders, Stripe payments, CRM integrations
- Gap we can exploit: Not voice-first, not field-optimized, enterprise pricing

### Quoted Moats (Our Advantages)
- **Voice-First**: Generate quotes while driving/on-site
- **AI Learning**: System improves with every correction
- **Field-Optimized**: Mobile-first, works one-handed
- **Built-in CRM**: No integration needed
- **Contractor Pricing**: $19-79/mo vs $3,900/yr

---

## Phase 2: 10x Designs

### Design 1: Invoice Public View (Fixes KI-001, KI-009)

**Problem**: When contractors send invoices via email, the share URL (`/invoice/{token}`) returns 404 because:
1. No route exists in `main.py` for `/invoice/{token}`
2. No public API endpoint exists at `/api/invoices/shared/{token}`
3. No `invoice-view.html` template exists

**Solution**: Create a complete invoice public view system mirroring the quote share system.

#### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `frontend/invoice-view.html` | CREATE | Public invoice view (copy of quote-view.html with invoice branding) |
| `backend/main.py` | MODIFY | Add `/invoice/{token}` route (lines ~275) |
| `backend/api/invoices.py` | MODIFY | Add `/api/invoices/shared/{token}` endpoint |
| `frontend/index.html` | MODIFY | Add feature flag check for invoicing UI |

#### API Endpoint Design

**New Endpoint**: `GET /api/invoices/shared/{token}`

```python
@router.get("/shared/{token}")
async def get_shared_invoice(token: str, db: AsyncSession = Depends(get_db)):
    """Get invoice data by share token (public endpoint, no auth)."""
    result = await db.execute(
        select(Invoice).where(Invoice.share_token == token)
    )
    invoice = result.scalars().first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found or link invalid")

    # Get contractor info for display
    contractor = await db.get(Contractor, invoice.contractor_id)

    # Track view in PostHog
    analytics_service.track_event(
        user_id="anonymous",
        event_name="invoice_viewed",
        properties={
            "invoice_id": str(invoice.id),
            "contractor_id": str(invoice.contractor_id),
            "source": "share_link"
        }
    )

    return {
        "id": str(invoice.id),
        "invoice_number": invoice.invoice_number,
        "customer_name": invoice.customer_name,
        "customer_address": invoice.customer_address,
        "description": invoice.description,
        "line_items": invoice.line_items,
        "subtotal": invoice.subtotal,
        "tax_amount": invoice.tax_amount,
        "total": invoice.total,
        "status": invoice.status,  # draft, sent, viewed, paid, overdue
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "created_at": invoice.created_at.isoformat(),
        "contractor_name": contractor.business_name if contractor else "Unknown",
        "contractor_phone": contractor.phone if contractor else None,
        "contractor_email": contractor.email if contractor else None,
    }
```

#### Frontend Template Design

**`invoice-view.html`** - Key differences from quote-view.html:

| Element | Quote | Invoice |
|---------|-------|---------|
| Badge | "SHARED QUOTE" (blue) | "INVOICE" (green/amber based on status) |
| Title | Customer Name | Invoice #{number} |
| Header fields | Contractor, Phone, Quote Date | Contractor, Phone, Invoice Date, Due Date |
| Status banner | None | Payment status (Paid ✓, Due, Overdue) |
| Total section | "Estimated Total" | "Amount Due" (or "Amount Paid") |
| CTA button | "Try Demo" | Future: "Pay Now" button hook |

**Status Badge Colors**:
- `draft`: Gray
- `sent`/`viewed`: Blue
- `paid`: Green ✓
- `overdue`: Red/Amber warning

**Due Date Warning**:
- Past due: Red banner "OVERDUE - Payment was due on [date]"
- Due within 7 days: Amber banner "Due in X days"
- Future: Normal display

#### Route Addition (main.py)

```python
@app.get("/invoice/{token}", response_class=HTMLResponse)
async def serve_shared_invoice(request: Request, token: str):
    """Serve the public shared invoice view with injected config."""
    return templates.TemplateResponse("invoice-view.html", {
        "request": request,
        "token": token,
        "posthog_api_key": settings.posthog_api_key,
        "sentry_dsn": settings.sentry_dsn,
        "environment": settings.environment,
    })
```

#### Feature Flag Check (index.html)

```javascript
// Wrap invoice-related UI in feature flag check
async function initInvoicing() {
    if (await isFeatureEnabled('invoicing_enabled')) {
        document.getElementById('invoiceSection').style.display = 'block';
    }
}
```

#### PostHog Events

| Event | Properties | Trigger |
|-------|------------|---------|
| `invoice_viewed` | invoice_id, contractor_id, source | Page load |
| `invoice_cta_clicked` | invoice_id | "Pay Now" button (future) |

#### Mobile Responsiveness

Same breakpoints as quote-view.html:
- Tablet (768px): 2-column contractor info
- Mobile (640px): Stack layout, smaller fonts
- Small mobile (480px): Compact padding
- iPhone SE (375px): Minimum comfortable size

---

### Design 2: Quote Accept/Reject (Fixes KI-002, KI-003, KI-012, KI-013)

**Problem**: Customers viewing shared quotes have no way to formally accept or reject them. This means:
- KI-002: No accept/reject buttons in quote-view.html
- KI-003: Quote status never transitions from "draft"
- KI-012: `sent_at` field is never set when emailing
- KI-013: `outcome`/`outcome_notes` fields never populated

**Solution**: Add a complete quote acceptance workflow with typed-name e-signatures.

#### Database Changes

**New fields on Quote model**:
```python
# E-signature on acceptance
signature_name = Column(String(255))  # Customer's typed name
signature_ip = Column(String(45))     # IP address at time of signing
signature_at = Column(DateTime)       # When they signed
accepted_at = Column(DateTime)        # Alias for clarity
rejected_at = Column(DateTime)        # If rejected
rejection_reason = Column(Text)       # Why they rejected
```

#### API Endpoints

**1. Accept Quote**: `POST /api/quotes/shared/{token}/accept`

```python
class AcceptQuoteRequest(BaseModel):
    signature_name: str  # Required: Customer types their name
    message: Optional[str] = None  # Optional note to contractor

@router.post("/shared/{token}/accept")
async def accept_quote(
    request: Request,
    token: str,
    accept_request: AcceptQuoteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Customer accepts a quote (public endpoint)."""
    quote = await db.get_quote_by_share_token(token)
    if not quote:
        raise HTTPException(404, "Quote not found")

    # Update quote status
    quote.status = "won"
    quote.outcome = "won"
    quote.signature_name = accept_request.signature_name
    quote.signature_ip = request.client.host
    quote.signature_at = datetime.utcnow()
    quote.accepted_at = datetime.utcnow()

    await db.commit()

    # Send email notification to contractor
    await email_service.send_quote_accepted_notification(
        contractor_email=contractor.email,
        quote=quote,
        customer_message=accept_request.message
    )

    # Track analytics
    analytics_service.track_event("quote_accepted", {...})

    return {"success": True, "message": "Quote accepted"}
```

**2. Reject Quote**: `POST /api/quotes/shared/{token}/reject`

```python
class RejectQuoteRequest(BaseModel):
    reason: Optional[str] = None  # Optional reason

@router.post("/shared/{token}/reject")
async def reject_quote(
    request: Request,
    token: str,
    reject_request: RejectQuoteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Customer rejects a quote (public endpoint)."""
    quote = await db.get_quote_by_share_token(token)
    if not quote:
        raise HTTPException(404, "Quote not found")

    quote.status = "lost"
    quote.outcome = "lost"
    quote.outcome_notes = reject_request.reason
    quote.rejected_at = datetime.utcnow()

    await db.commit()

    # Send notification to contractor (optional)
    await email_service.send_quote_rejected_notification(...)

    return {"success": True, "message": "Quote declined"}
```

**3. Fix share.py - Set sent_at** (KI-012):

```python
# In share_quote_via_email():
quote.status = "sent"
quote.sent_at = datetime.utcnow()
await db.commit()
```

#### Frontend Changes (quote-view.html)

**Add Accept/Reject Section** (before footer) - uses safe DOM methods only.

**JavaScript Logic** (safe DOM approach):

```javascript
async function acceptQuote() {
    const signatureName = document.getElementById('signatureName').value.trim();
    if (!signatureName) {
        alert('Please type your name to accept');
        return;
    }

    const message = document.getElementById('customerMessage').value.trim();

    try {
        const response = await fetch(`/api/quotes/shared/${shareToken}/accept`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ signature_name: signatureName, message })
        });

        if (response.ok) {
            // Show accepted state using safe DOM methods
            document.getElementById('actionSection').style.display = 'none';
            document.getElementById('acceptedState').style.display = 'block';
            document.getElementById('signedBy').textContent = signatureName;
            document.getElementById('signedDate').textContent = new Date().toLocaleDateString();

            // Track in PostHog
            posthog.capture('quote_accepted', { token: shareToken });
        }
    } catch (error) {
        console.error('Error accepting quote:', error);
    }
}

async function rejectQuote() {
    const reason = document.getElementById('rejectReason').value.trim();

    try {
        await fetch(`/api/quotes/shared/${shareToken}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason })
        });

        // Show declined state using safe DOM methods
        const actionSection = document.getElementById('actionSection');
        actionSection.textContent = '';

        const declinedDiv = document.createElement('div');
        declinedDiv.className = 'declined-message';

        const declinedText = document.createElement('p');
        declinedText.textContent = 'Quote declined. Thank you for letting us know.';
        declinedDiv.appendChild(declinedText);

        actionSection.appendChild(declinedDiv);

        posthog.capture('quote_rejected', { token: shareToken });
    } catch (error) {
        console.error('Error rejecting quote:', error);
    }
}
```

#### Contractor Notification Email

**Subject**: "Good news! [Customer] accepted your quote"

**Body**: Quote details, signature info, customer message, next steps link.

#### Quote Expiration Integration

If `quote_valid_days` is set and quote is expired:
- Show warning banner: "This quote expired on [date]"
- Still allow acceptance (soft expiration per founder decision)
- Track `expired_quote_accepted` event

#### Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/models/database.py` | MODIFY | Add signature fields to Quote model |
| `backend/api/share.py` | MODIFY | Add accept/reject endpoints, fix sent_at |
| `frontend/quote-view.html` | MODIFY | Add accept/reject UI (safe DOM methods) |
| `backend/services/email_service.py` | MODIFY | Add acceptance notification email |

#### PostHog Events

| Event | Properties | Trigger |
|-------|------------|---------|
| `quote_accepted` | token, quote_id, signature_name | Customer clicks accept |
| `quote_rejected` | token, quote_id, has_reason | Customer declines |
| `quote_status_changed` | quote_id, old_status, new_status | Any status transition |

---

### Design 3: Share Analytics (Fixes KI-004, KI-008)

**Problem**: Contractors can't see who viewed their quotes or how many times:
- KI-004: `view_count` tracked in PostHog but NOT persisted to Quote model
- KI-008: Error message says "link expired" but links never actually expire

**Solution**: Add persistent view tracking with first-view notifications.

#### Database Changes

**New fields on Quote model**:
```python
# View tracking
view_count = Column(Integer, default=0)
first_viewed_at = Column(DateTime)
last_viewed_at = Column(DateTime)
```

#### API Changes (share.py)

**Update `view_shared_quote` endpoint**:

```python
@router.get("/shared/{token}")
async def view_shared_quote(request: Request, token: str):
    quote = await db.get_quote_by_share_token(token)
    if not quote:
        # KI-008 FIX: Clear, accurate error message
        raise HTTPException(status_code=404, detail="Quote not found")

    # Increment view count
    is_first_view = quote.view_count == 0
    quote.view_count = (quote.view_count or 0) + 1
    quote.last_viewed_at = datetime.utcnow()

    if is_first_view:
        quote.first_viewed_at = datetime.utcnow()
        # Update status to "viewed" if currently "sent"
        if quote.status == "sent":
            quote.status = "viewed"

    await db.commit()

    # Notify contractor on first view
    if is_first_view:
        await email_service.send_quote_viewed_notification(
            contractor_email=contractor.email,
            quote=quote
        )

    # Track in PostHog (keep for detailed analytics)
    analytics_service.track_event(...)

    return SharedQuoteResponse(
        ...,
        view_count=quote.view_count,  # Include in response
    )
```

#### New API Endpoint: Quote Analytics

**`GET /api/quotes/{quote_id}/analytics`** (authenticated):

```python
@router.get("/{quote_id}/analytics")
async def get_quote_analytics(
    quote_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a specific quote."""
    quote = await db.get_quote(quote_id)
    if not quote or quote.contractor_id != current_user["contractor_id"]:
        raise HTTPException(404, "Quote not found")

    return {
        "quote_id": str(quote.id),
        "view_count": quote.view_count or 0,
        "first_viewed_at": quote.first_viewed_at.isoformat() if quote.first_viewed_at else None,
        "last_viewed_at": quote.last_viewed_at.isoformat() if quote.last_viewed_at else None,
        "status": quote.status,
        "sent_at": quote.sent_at.isoformat() if quote.sent_at else None,
        "accepted_at": quote.accepted_at.isoformat() if quote.accepted_at else None,
    }
```

#### Frontend: Quote Card Analytics Badge

In the quotes list, show view count badge:

```javascript
// When rendering quote card
if (quote.view_count > 0) {
    const viewBadge = document.createElement('span');
    viewBadge.className = 'view-badge';
    viewBadge.textContent = `${quote.view_count} view${quote.view_count > 1 ? 's' : ''}`;
    quoteCard.appendChild(viewBadge);
}
```

**CSS**:
```css
.view-badge {
    background: #e0f2fe;
    color: #0369a1;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}
```

#### Contractor Notification: First View

**Subject**: "[Customer] just viewed your quote"

**Body**:
```
Your quote for [job description] was just viewed!

Customer: [Name]
Quote Total: $X,XXX.XX
Sent: [date]
Viewed: [just now]

This is a good sign - they're interested. Consider following up!

View quote: [link]
```

#### Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/models/database.py` | MODIFY | Add view_count, first_viewed_at, last_viewed_at |
| `backend/api/share.py` | MODIFY | Increment view_count, fix error message |
| `backend/api/quotes.py` | MODIFY | Add analytics endpoint |
| `backend/services/email_service.py` | MODIFY | Add first-view notification |
| `frontend/index.html` | MODIFY | Show view count on quote cards |

#### Migration

```python
# Alembic migration
def upgrade():
    op.add_column('quotes', sa.Column('view_count', sa.Integer(), default=0))
    op.add_column('quotes', sa.Column('first_viewed_at', sa.DateTime()))
    op.add_column('quotes', sa.Column('last_viewed_at', sa.DateTime()))
```

---

### Design 4: Auto-Reminders (Fixes KI-005, KI-006, KI-007)

**Problem**: Task reminder functionality is dead code:
- KI-005: `reminder_time` field stored but no background job processes it
- KI-006: `notification_sent` field exists but never set
- KI-007: `recurrence`/`auto_generated` fields exist but unused

**Solution**: Implement APScheduler background job for task reminders.

#### Architecture

**APScheduler** (lightweight, in-process) vs Celery (heavyweight, requires Redis):
- Quoted is single-instance on Railway
- APScheduler runs in FastAPI process
- No additional infrastructure needed
- Cost: $0 additional

#### Implementation

**1. Add APScheduler to requirements.txt**:
```
apscheduler>=3.10.0
```

**2. Create scheduler service** (`backend/services/scheduler.py`):

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta

scheduler = AsyncIOScheduler()

async def check_task_reminders():
    """Run every 5 minutes to check for due reminders."""
    db = get_db_service()

    # Find tasks with reminder_time in the past and notification_sent=False
    due_tasks = await db.execute(
        select(Task).where(
            Task.reminder_time <= datetime.utcnow(),
            Task.notification_sent == False,
            Task.status == "pending"
        )
    )

    for task in due_tasks.scalars():
        # Get contractor email
        contractor = await db.get(Contractor, task.contractor_id)

        # Send reminder email
        await email_service.send_task_reminder(
            contractor_email=contractor.email,
            task=task
        )

        # Mark as sent
        task.notification_sent = True
        task.notification_sent_at = datetime.utcnow()

    await db.commit()

async def check_quote_followups():
    """Run daily to check for quotes needing follow-up."""
    db = get_db_service()

    # Find sent quotes not viewed after 3 days
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    stale_quotes = await db.execute(
        select(Quote).where(
            Quote.status == "sent",
            Quote.sent_at < three_days_ago,
            Quote.view_count == 0
        )
    )

    for quote in stale_quotes.scalars():
        # Create auto follow-up task
        task = Task(
            contractor_id=quote.contractor_id,
            quote_id=quote.id,
            customer_id=quote.customer_id,
            title=f"Follow up on quote for {quote.customer_name}",
            description="Quote sent 3+ days ago, not yet viewed",
            due_date=datetime.utcnow(),
            priority="high",
            auto_generated=True,
            source="system:quote_followup"
        )
        db.add(task)

    await db.commit()

def start_scheduler():
    """Initialize and start the scheduler."""
    # Check reminders every 5 minutes
    scheduler.add_job(
        check_task_reminders,
        trigger=IntervalTrigger(minutes=5),
        id="task_reminders",
        replace_existing=True
    )

    # Check quote follow-ups daily at 9am UTC
    scheduler.add_job(
        check_quote_followups,
        trigger=CronTrigger(hour=9),
        id="quote_followups",
        replace_existing=True
    )

    scheduler.start()
```

**3. Start scheduler in main.py lifespan**:

```python
from .services.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    start_scheduler()  # Add this line
    yield
    # Shutdown
    scheduler.shutdown()
```

#### Task Reminder Email

**Subject**: "Reminder: [Task title]"

**Body**:
```
You set a reminder for this task:

[Task title]
Due: [date]
Related to: [Customer name / Quote]

[Task description]

View in Quoted: [link]
```

#### Auto-Generated Follow-Up Tasks

When a quote is sent but not viewed for 3 days:
- Auto-create a "Follow up" task
- Set priority to "high"
- Link to original quote and customer
- Mark `auto_generated=True` and `source="system:quote_followup"`

#### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/services/scheduler.py` | CREATE | APScheduler background jobs |
| `backend/main.py` | MODIFY | Start scheduler in lifespan |
| `backend/requirements.txt` | MODIFY | Add apscheduler |
| `backend/services/email_service.py` | MODIFY | Add task reminder email |

#### Monitoring

Add health check for scheduler:

```python
@app.get("/health/scheduler")
async def scheduler_health():
    """Check if scheduler is running."""
    from .services.scheduler import scheduler
    return {
        "running": scheduler.running,
        "jobs": [job.id for job in scheduler.get_jobs()]
    }
```

---

### Design 5: Quote Expiration (Fixes KI-011)

**Problem**: `quote_valid_days` field exists but is never enforced:
- KI-011: Quotes never actually expire even if validity period is set

**Solution**: Soft expiration with prominent warning banner (per founder decision).

#### Implementation

**1. Calculate expiration in API response**:

```python
# In SharedQuoteResponse
def get_expiration_status(quote):
    if not quote.quote_valid_days or not quote.created_at:
        return {"expired": False, "expires_at": None}

    expires_at = quote.created_at + timedelta(days=quote.quote_valid_days)
    is_expired = datetime.utcnow() > expires_at

    return {
        "expired": is_expired,
        "expires_at": expires_at.isoformat(),
        "days_remaining": max(0, (expires_at - datetime.utcnow()).days)
    }
```

**2. Update quote-view.html** with expiration banner:

```javascript
// After loading quote data
if (quoteData.expiration?.expired) {
    const banner = document.createElement('div');
    banner.className = 'expiration-banner expired';
    banner.textContent = `This quote expired on ${formatDate(quoteData.expiration.expires_at)}`;
    document.querySelector('.container').prepend(banner);
} else if (quoteData.expiration?.days_remaining <= 7) {
    const banner = document.createElement('div');
    banner.className = 'expiration-banner warning';
    banner.textContent = `This quote expires in ${quoteData.expiration.days_remaining} days`;
    document.querySelector('.container').prepend(banner);
}
```

**CSS**:
```css
.expiration-banner {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    font-weight: 600;
    text-align: center;
}

.expiration-banner.expired {
    background: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
}

.expiration-banner.warning {
    background: #fffbeb;
    color: #d97706;
    border: 1px solid #fde68a;
}
```

**3. Allow acceptance of expired quotes** (soft expiration):
- Expired quotes can still be accepted
- Track `expired_quote_accepted` event
- Show confirmation: "This quote has expired. Accept anyway?"

**4. Future: Contractor setting for strict mode**:
```python
# ContractorSettings model
block_expired_acceptance = Column(Boolean, default=False)
```

If enabled, reject acceptance of expired quotes.

#### Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/api/share.py` | MODIFY | Add expiration to response |
| `frontend/quote-view.html` | MODIFY | Show expiration banner |

---

## Implementation Wave Plan

### Wave 1: Critical Bugs (Fixes KI-001, KI-002, KI-003, KI-008, KI-009, KI-012)

**Priority**: Highest - These are production-breaking bugs

| Task | Files | Est. Lines |
|------|-------|------------|
| Create `/invoice/{token}` route | main.py | +10 |
| Create `/api/invoices/shared/{token}` | invoices.py | +40 |
| Create invoice-view.html | frontend/ | +400 (copy+modify) |
| Add accept/reject endpoints | share.py | +80 |
| Add signature fields to Quote | database.py | +6 |
| Update quote-view.html with UI | frontend/ | +100 |
| Fix sent_at when emailing | share.py | +3 |
| Fix error message | share.py | +1 |

**Total**: ~640 lines of code

### Wave 2: Analytics & Status (Fixes KI-004, KI-011, KI-013)

| Task | Files | Est. Lines |
|------|-------|------------|
| Add view_count fields | database.py | +3 |
| Increment on view | share.py | +15 |
| Add analytics endpoint | quotes.py | +25 |
| Add expiration logic | share.py | +20 |
| Add expiration UI | quote-view.html | +30 |

**Total**: ~93 lines

### Wave 3: Background Jobs (Fixes KI-005, KI-006, KI-007)

| Task | Files | Est. Lines |
|------|-------|------------|
| Create scheduler.py | services/ | +100 |
| Add APScheduler | requirements.txt | +1 |
| Integrate in lifespan | main.py | +10 |
| Add task reminder email | email_service.py | +30 |

**Total**: ~141 lines

### Wave 4: Notifications & Polish

| Task | Files | Est. Lines |
|------|-------|------------|
| Quote accepted email | email_service.py | +40 |
| Quote viewed email | email_service.py | +30 |
| Task reminder email | email_service.py | +30 |
| Frontend polish | various | +50 |

**Total**: ~150 lines

---

## Wave 1 Implementation Log (2024-12-24)

### Files Modified

| File | Changes |
|------|---------|
| `backend/main.py` | Added `/invoice/{token}` route (line ~276-285) |
| `backend/api/invoices.py` | Added `SharedInvoiceResponse` model and `/shared/{token}` endpoint |
| `frontend/invoice-view.html` | NEW: ~500 lines, invoice public view with status banners |
| `backend/api/share.py` | Added accept/reject endpoints, fixed error message, added sent_at fix, added view count tracking |
| `backend/models/database.py` | Added signature_name, signature_ip, signature_at, accepted_at, rejected_at, rejection_reason, view_count, first_viewed_at, last_viewed_at to Quote model |
| `frontend/quote-view.html` | Added accept/reject UI section with signature form, ~200 lines of CSS/HTML/JS |

### Known Issues Fixed

| KI # | Issue | Fix Applied |
|------|-------|-------------|
| KI-001 | Invoice 404 | Created `/invoice/{token}` route + API endpoint |
| KI-002 | No accept/reject buttons | Added buttons + signature form to quote-view.html |
| KI-003 | Quote status never changes | Status updates to "won"/"lost" on accept/reject |
| KI-004 | view_count not in database | Added field, increment on each view |
| KI-008 | "link expired" misleading | Changed to "Quote not found" |
| KI-012 | sent_at not set | Now set in share_quote_via_email |
| KI-013 | outcome never set | outcome/status set on accept/reject |

### Remaining Known Issues (Wave 2+)

| KI # | Issue | Wave |
|------|-------|------|
| KI-005 | reminder_time dead code | Wave 3 (APScheduler) |
| KI-006 | notification_sent never set | Wave 3 (APScheduler) |
| KI-007 | recurrence unused | Wave 3 (APScheduler) |
| KI-009 | Feature flag not checked in frontend | Wave 2 |
| KI-010 | No invoice reminders | Wave 3 |
| KI-011 | Quote expiration not enforced | Wave 2 |
| KI-014 | Expired quote error unreachable | Wave 2 |

---

## Next Steps

1. **Test Wave 1** - Manual QA of invoice links and quote accept/reject
2. **Run database migration** - New Quote fields need Alembic migration
3. **Deploy to staging** - Test on preview environment
4. **Begin Wave 2** - Analytics dashboard, expiration UI
5. **Deploy incrementally** - One wave at a time with monitoring
