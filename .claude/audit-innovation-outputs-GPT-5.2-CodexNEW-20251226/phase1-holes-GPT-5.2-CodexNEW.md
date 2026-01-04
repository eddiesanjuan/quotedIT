# Phase 1: Technical Audit Findings (GPT-5.2-CodexNEW)

## Critical (Fix Before Launch)
- Billing and safety bypass in clarifications flow: `/api/quotes/generate-with-clarifications` skips BillingService checks, usage increment, and sanity bounds, enabling unlimited quote generation outside guardrails (`backend/api/quotes.py:733`, `backend/api/quotes.py:818`, `backend/api/quotes.py:840`).

## High (Fix Within 1 Week)
- Onboarding sessions are readable and mutable without auth; any party with a session_id can continue/read pricing interviews and learn contractor details (`backend/api/onboarding.py:162`, `backend/api/onboarding.py:550`, `backend/api/onboarding.py:562`).
- Refresh token validation scans every non-expired token and bcrypt-checks each; O(n) per refresh enables DoS as token count grows (`backend/services/auth.py:216`).
- Audio uploads have no size limits in production paths; a single oversized file can exhaust memory/disk and trigger costly transcription calls (`backend/api/quotes.py:871`, `backend/api/quotes.py:912`, `backend/api/demo.py:143`).
- Public contractor endpoints are unauthenticated and allow creating/listing contractor data (even if demo-only, these are deployed routes) (`backend/api/contractors.py:184`, `backend/api/contractors.py:219`, `backend/api/contractors.py:468`).
- Invoice numbers are generated via count, leading to race collisions and duplicate invoice IDs under concurrent creation (`backend/api/invoices.py:161`).
- Testimonials endpoint exposes unapproved testimonials when `approved_only=false` without any auth check (`backend/api/testimonials.py:88`).
- Follow-up endpoints rely on `user["contractor_id"]`, but `get_current_user` does not return it; follow-up creation/resume fails at runtime (`backend/api/followup.py:76`, `backend/services/auth.py:519`).
- Quote accept/reject notifications rely on `EmailService.send_email` (missing) and `settings.app_url` (undefined), so acceptance/rejection and deposit flows silently fail in production (`backend/api/share.py:618`, `backend/api/share.py:713`, `backend/api/share.py:826`).

## Medium (Fix Within 1 Month)
- Task creation accepts arbitrary `customer_id`/`quote_id` without verifying ownership, allowing cross-tenant linkage if IDs are known (`backend/api/tasks.py:383`).
- Logo fetch uses `db.get_contractor` which does not exist, causing 500s on logo retrieval (`backend/api/contractors.py:546`).
- Deposit checkout uses `db.get_contractor` (missing), breaking deposit flow before Stripe checkout (`backend/api/share.py:781`).
- Shared invoice endpoint lacks any rate limiting, enabling token brute-force attempts (`backend/api/invoices.py:942`).
- Quote expiration is calculated for view-only, but accept/reject does not enforce expiration, so expired quotes can still be accepted (`backend/api/share.py:531`).
- Raw exception text is returned to clients across multiple quote endpoints, leaking internal error details (`backend/api/quotes.py:652`).
- Customer list sorting uses direct attribute access from user input; no allowlist for `sort_by` increases risk of unexpected query behavior (`backend/services/customer_service.py:296`).
- Email sending uses synchronous Resend calls inside async handlers, blocking the event loop and risking latency spikes (`backend/services/email.py:513`).

## Low (Backlog)
- Share tokens are permanent and never expire, increasing long-term exposure if leaked (`backend/api/share.py:272`).
- Auth tokens are stored in `localStorage`, increasing blast radius of any XSS in the app shell (`frontend/index.html:7712`).

## User Journey Friction Points
Journey 1: Brand New User
- Industry selection is a long grid without search or filtering; mobile users must scroll extensively to find their trade (`frontend/index.html:5159`).
- Domain inconsistency across app, emails, and config (quoted.it vs quoted.it.com) erodes trust and can break cross-domain link expectations (`backend/config.py:26`, `backend/services/email.py:33`).

Journey 2: Active User Creating Quote
- Clarifications flow bypasses billing warnings and usage tracking, so users can generate quotes that later appear "missing" from billing metrics (`backend/api/quotes.py:733`).
- Large audio uploads can fail without a clear size limit or user feedback; failures surface as generic errors (`backend/api/quotes.py:871`).

Journey 3: Customer Receiving Quote
- Accept/reject notifications fail to send (missing `send_email` and `app_url`), so contractors never hear back even when customers act (`backend/api/share.py:618`).
- Deposit checkout fails before Stripe due to missing `get_contractor` and undefined `app_url`, causing dead-end acceptance attempts (`backend/api/share.py:781`).

Journey 4: Learning & Improvement
- Customer backfill and CRM learning require manual trigger and provide limited feedback on progress; errors are easy to miss (`frontend/index.html:14482`).
