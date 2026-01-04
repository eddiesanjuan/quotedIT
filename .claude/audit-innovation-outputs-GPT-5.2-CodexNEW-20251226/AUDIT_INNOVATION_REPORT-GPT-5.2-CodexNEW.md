# Quoted Audit + Innovation Report (GPT-5.2-CodexNEW)

Generated: 2025-12-26 UTC
Scope: Full stack audit (backend, frontend, UX, reliability, security, product flows)

## Executive Summary
- Findings: 1 critical, 8 high, 8 medium, 2 low.
- The single most urgent issue is the clarifications quote path bypassing billing and sanity checks, enabling unlimited, unmetered quote generation.
- Reliability is the second largest risk cluster: follow-up flows and acceptance emails fail due to missing config and missing email method.
- UX polish opportunities focus on mobile discoverability and domain consistency across app, emails, and marketing pages.

## Fix-Now Priorities (Order of Operations)
1) Close billing and sanity-check bypass on `/api/quotes/generate-with-clarifications` and ensure usage increment. (`backend/api/quotes.py:733`)
2) Lock down onboarding session read/continue endpoints with auth or scoped session tokens. (`backend/api/onboarding.py:162`)
3) Add upload size limits + content type validation for all audio uploads. (`backend/api/quotes.py:871`, `backend/api/demo.py:143`)
4) Fix broken follow-up and acceptance flows by adding contractor_id to auth context and implementing `EmailService.send_email` or replacing calls with existing methods. (`backend/services/auth.py:519`, `backend/api/share.py:618`)
5) Replace invoice number generation with atomic sequence or DB-side increment. (`backend/api/invoices.py:161`)

## Key Risks by Category
- Security/Entitlements: Billing bypass, unauthenticated onboarding sessions, public contractor endpoints, unapproved testimonials exposure.
- Reliability: Follow-up endpoints fail due to missing contractor_id; acceptance/rejection emails and deposit flow broken by missing config/methods.
- Data Integrity: Invoice number race conditions; task creation accepts foreign customer/quote IDs.
- Performance: Refresh token validation is O(n) with bcrypt; synchronous email sends in async flows.

## UX & Product Polish Highlights
- Mobile nav hides Tasks/Invoices, reducing discoverability on phones.
- Mixed domains (quoted.it vs quoted.it.com) across emails/config/marketing pages can erode trust and break expected routing.
- Help copy is out of date on direct email sharing.

## Innovation Roadmap (Top Picks)
- Adaptive Quote Bundles: auto-pack winning line-item groups based on history; strongest revenue/close-rate lever.
- Confidence-Guided Clarifications: show low-confidence items and ask targeted questions before send.
- One-Tap Deposit + Schedule: convert acceptance into paid, scheduled jobs; aligns with contractor workflows.

## Recommended Next Steps
- Patch the top 5 fixes in sequence and add regression tests for billing/quote generation and share acceptance.
- Align domain configuration across frontend, backend config, and email templates.
- Add explicit rate limits for public share endpoints and tighten testimonial access.

## Appendix
- Phase 1 findings: `.claude/audit-innovation-outputs-GPT-5.2-CodexNEW-20251226/phase1-holes-GPT-5.2-CodexNEW.md`
- Phase 2 findings: `.claude/audit-innovation-outputs-GPT-5.2-CodexNEW-20251226/phase2-polish-GPT-5.2-CodexNEW.md`
- Phase 3 ideas: `.claude/audit-innovation-outputs-GPT-5.2-CodexNEW-20251226/phase3-innovations-GPT-5.2-CodexNEW.md`
