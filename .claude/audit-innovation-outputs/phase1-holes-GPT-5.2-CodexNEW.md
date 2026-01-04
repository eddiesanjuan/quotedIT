# Phase 1: Technical Audit Findings - GPT-5.2-CodexNEW

## Critical (Fix Before Launch)
- CRIT-001 Billing bypass on /api/quotes/generate-with-clarifications. This endpoint skips BillingService checks and usage increments, so trial-expired users can generate unlimited quotes and incur LLM costs. Evidence: backend/api/quotes.py:645. Fix: mirror the /quotes/generate billing check + increment logic, including grace-quote handling.
- CRIT-002 Onboarding session data is publicly readable and writable. The continue/get/messages endpoints are unauthenticated and only require a session_id, enabling IDOR data leaks or tampering. Evidence: backend/api/onboarding.py:161, backend/api/onboarding.py:549, backend/api/onboarding.py:561. Fix: require get_current_contractor and verify session ownership; add rate limits.
- CRIT-003 Refresh token validation is O(n) with bcrypt checks over all non-expired tokens. This makes auth refresh CPU/DB-exhaustive and a DoS vector as tokens accumulate. Evidence: backend/services/auth.py:216. Fix: store a lookup hash (SHA-256/HMAC), query by hash, then verify; schedule cleanup; index lookup column.
- CRIT-004 Audio upload endpoints read entire files into memory without size/duration limits. This enables memory/disk DoS and runaway transcription spend. Evidence: backend/api/quotes.py:781, backend/api/quotes.py:821, backend/api/demo.py:141. Fix: enforce max upload size and duration before read; validate content-type.

## High (Fix Within 1 Week)
- HIGH-001 Undefined auth_db usage in generate-with-clarifications breaks CRM linking with NameError. Evidence: backend/api/quotes.py:753. Fix: pass auth_db in signature and use it consistently (or use db service session).
- HIGH-002 Logo fetch always fails because DatabaseService has no get_contractor method. Evidence: backend/api/contractors.py:541. Fix: call get_contractor_by_id or get_contractor_by_user_id.
- HIGH-003 Accept/reject notifications silently fail: EmailService.send_email does not exist, and settings.app_url is undefined. Evidence: backend/api/share.py:543, backend/api/share.py:639, backend/config.py:21. Fix: add EmailService.send_email or use existing send_* methods; add app_url to settings or use frontend_url.
- HIGH-004 Invoice numbers are generated from counts, causing duplicates under concurrent creates. Evidence: backend/api/invoices.py:161. Fix: use a DB sequence, unique constraint + retry, or atomic increment per contractor.
- HIGH-005 Share-by-email PDFs are written to local ./data/pdfs and paths stored in DB. This breaks in multi-worker or ephemeral storage setups and bypasses the storage abstraction. Evidence: backend/api/share.py:128, backend/services/pdf_generator.py:452. Fix: route through StorageService and store stable URLs.
- HIGH-006 Public demo contractor endpoints are mutable and unauthenticated, enabling memory growth and confusion vs real data. Evidence: backend/api/contractors.py:183, backend/api/contractors.py:219. Fix: remove, gate behind admin auth, or feature-flag.
- HIGH-007 Expired quotes can still be accepted because accept/reject endpoints do not enforce expiration. Evidence: backend/api/share.py:479-520. Fix: enforce terms.quote_valid_days server-side and block acceptance past expiry.

## Medium (Fix Within 1 Month)
- MED-001 Feedback stats pull all quote IDs and feedback rows into memory, which will degrade on large accounts. Evidence: backend/services/database.py:1247. Fix: compute aggregates via SQL (COUNT, AVG, GROUP BY) without full materialization.
- MED-002 customer sort_by is not allowlisted; invalid values can trigger 500s and unexpected ordering. Evidence: backend/services/customer_service.py:295. Fix: validate sort_by against a small allowed set.
- MED-003 Shared invoice view has no rate limiting; public token endpoints are scrapeable. Evidence: backend/api/invoices.py:727. Fix: add limiter or request throttling.
- MED-004 Template metadata is injected via innerHTML without escaping; if template data ever becomes user-supplied, this is XSS (tokens are in localStorage). Evidence: frontend/index.html:12023, frontend/index.html:12077. Fix: use textContent or sanitize fields.
- MED-005 Raw exception strings are returned to clients, leaking internal errors. Evidence: backend/api/quotes.py:766, backend/api/quotes.py:818. Fix: return generic messages, log details server-side.

## Low (Backlog)
- LOW-001 EmailService uses synchronous Resend calls inside async functions, blocking the event loop. Evidence: backend/services/email.py:224. Fix: run in executor consistently or switch to async client.
- LOW-002 Quote share tokens are permanent with no revoke/rotate path. Evidence: backend/api/share.py:272. Fix: add revoke/regenerate endpoints and optional expiry.
- LOW-003 Auth tokens stored in localStorage are vulnerable to XSS-based session theft. Evidence: frontend/index.html:7013. Fix: consider HttpOnly cookies or CSP hardening.

## User Journey Friction Points

### Journey 1: Brand New User
- Pricing help text conflicts with the new single-tier model, creating immediate trust friction ("Starter plan 30 quotes/month"). Evidence: frontend/help.html:560.
- "Email Direct coming soon" contradicts the shipping share-by-email feature, reducing perceived product maturity. Evidence: frontend/help.html:621, backend/api/share.py:101.
- Onboarding session cannot be resumed after refresh because session_id is kept only in memory. Evidence: frontend/index.html:8942.
- No visible password reset flow in the auth UI; users who forget passwords have no self-serve recovery (auth UI has no reset controls). Evidence: frontend/index.html:4365.

### Journey 2: Active User Creating a Quote
- Clarification flow can generate a quote even when billing is blocked, leading to later surprises when saving/sending is restricted. Evidence: backend/api/quotes.py:645.
- If CRM linking fails in clarifications (auth_db NameError), the quote appears created but customer history is silently missing. Evidence: backend/api/quotes.py:753.
- Local PDF path usage means sharing from a different worker can fail even though the UI looks successful. Evidence: backend/api/share.py:128.

### Journey 3: Customer Receiving Quote
- Expired quotes still accept signatures server-side, which can create pricing disputes and support churn. Evidence: backend/api/share.py:479.
- Contractor may never receive acceptance/rejection notifications due to missing EmailService.send_email, so follow-up relies on manual checking. Evidence: backend/api/share.py:543.
- Shared quote error state lacks a recovery action (no contact/help CTA). Evidence: frontend/quote-view.html:928.

### Journey 4: Learning and Improvement
- Learning outcomes are mostly invisible after edits; there is no immediate feedback loop to show what changed or how accuracy improved (only aggregate progress exists). Evidence: frontend/index.html:14664.
- Feedback stats are heavy to compute and can slow down learning insights as data grows. Evidence: backend/services/database.py:1247.
