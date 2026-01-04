# Quoted Audit and Innovation Report - GPT-5.2-CodexNEW
Generated: 2025-12-25T21:52:59Z

## Executive Summary
This GPT-5.2-CodexNEW audit found four launch-blocking risks: a billing bypass in the clarifications quote flow, unauthenticated onboarding session endpoints (IDOR), refresh token validation that scales poorly and can be abused for DoS, and unbounded audio uploads that can exhaust memory and transcription budgets. Several high-impact reliability issues also exist (missing auth_db in clarifications, broken logo retrieval, failed acceptance notifications, invoice number races, and local-only PDF storage for share-by-email).

UX and messaging are strong overall but have critical mismatches in the help center around legacy plans and an outdated "Email Direct" status, plus inconsistent error feedback (alerts vs toasts) and thin empty/error states. The innovation runway is rich: immediate wins include follow-up automation, interactive quote options, and visible learning diffs; medium-term bets focus on integrated acceptance + payment and customer portal consolidation; long-term moonshots include photo-to-quote and AR visualization.

## Part 1: Critical Fixes (Before More Users)
1. Billing bypass on /api/quotes/generate-with-clarifications (backend/api/quotes.py:645).
2. Unauthenticated onboarding session endpoints (backend/api/onboarding.py:161, backend/api/onboarding.py:549).
3. Refresh token validation O(n) with bcrypt scans (backend/services/auth.py:216).
4. No file size limits on audio upload endpoints (backend/api/quotes.py:781, backend/api/demo.py:141).
5. Clarification flow crashes due to auth_db undefined (backend/api/quotes.py:753).
6. Logo retrieval always fails due to missing db.get_contractor (backend/api/contractors.py:541).
7. Acceptance/rejection notifications fail due to missing send_email and app_url (backend/api/share.py:543, backend/config.py:21).
8. Invoice number race condition under concurrent creates (backend/api/invoices.py:161).
9. Local-only PDF storage breaks share-by-email in multi-worker deployments (backend/api/share.py:128).
10. Expired quotes can still be accepted server-side (backend/api/share.py:479).

## Part 2: Polish and UX Improvements
1. Update pricing FAQ to match unlimited plan model (frontend/help.html:560).
2. Remove "Email Direct coming soon" copy now that email share ships (frontend/help.html:621).
3. Align all email links to canonical domain quoted.it.com (backend/services/email.py:205).
4. Replace alert() usage with in-app toasts (frontend/index.html:14467).
5. Provide user-visible errors for share-link generation failures (frontend/index.html:14421).
6. Add CTA to empty customer quotes state (frontend/index.html:12857).
7. Add recovery action to shared quote not found screen (frontend/quote-view.html:928).
8. Expose Help and Sign Out in mobile nav (frontend/index.html:5813).
9. Add visual affordance to horizontal account tabs on mobile (frontend/index.html:2615).
10. Add onboarding industry search/filter (frontend/index.html:8942).

## Part 3: Innovation Roadmap

### Immediate (This Month)
- Interactive quote options (QPR-01). User story: customers toggle Good/Better/Best packages. Approach: add option sets to quote schema and render toggles in quote-view. Effort: M. Success: higher accept rate, longer time on page. Dependencies: quote schema update, UI changes.
- Smart follow-up sequences (AUT-01). User story: contractors get automatic follow-up tasks and emails based on view status. Approach: extend scheduler rules + templates. Effort: M. Success: reduced stale quotes. Dependencies: scheduler, email templates.
- Correction diff view (LRN-04). User story: show before/after and what the AI learned. Approach: store diff metadata and render in quote detail. Effort: S. Success: increased trust and edits. Dependencies: edit_details usage.
- Voice QA checklist (VOX-10). User story: short checklist after recording reduces misses. Approach: add post-transcription prompts driven by heuristics. Effort: S. Success: fewer clarifications, higher accuracy. Dependencies: UI prompts.
- Win/loss reason capture (BI-01). User story: reasons logged on reject. Approach: extend reject flow to include structured reasons. Effort: S. Success: actionable loss insights. Dependencies: reject UI and analytics.

### Next Quarter
- One-click acceptance + deposit (QPR-02). Story: customer accepts and pays in one step. Approach: Stripe payment intent linked to quote. Effort: M. Success: higher conversion, faster cash. Dependencies: Stripe integration, security review.
- Customer portal for quotes and invoices (QPR-09). Story: single link for all documents. Approach: shared portal endpoint with auth token. Effort: M. Success: improved customer engagement. Dependencies: portal UI, auth model.
- Voice command editing (VOX-02). Story: edit quote by voice. Approach: intent parsing for line item operations. Effort: M. Success: faster edits. Dependencies: NLP intents, UI feedback.
- Seasonal and regional multipliers (LRN-05). Story: auto adjustments by season/region. Approach: time-series factors in pricing model. Effort: M. Success: improved pricing accuracy. Dependencies: data logging.
- Integrations marketplace (AUT-06). Story: sync with QuickBooks and Jobber. Approach: OAuth connectors. Effort: L. Success: retention lift. Dependencies: partner APIs.

### Future Vision
- Photo-to-quote intake (AUT-04). Story: generate scope from site photos. Approach: CV pipeline + LLM summarization. Effort: L. Success: differentiated capture flow. Dependencies: CV model, storage.
- AR/3D project previews (QPR-10). Story: visualize work before signing. Approach: model templates + WebAR. Effort: L. Success: premium conversion lift. Dependencies: 3D assets.
- Market benchmarks (LRN-09). Story: compare pricing vs peers. Approach: opt-in anonymized aggregation. Effort: L. Success: pricing confidence. Dependencies: privacy/legal.
- Capacity planning (BI-08). Story: forecast crew bandwidth. Approach: schedule + job duration models. Effort: L. Success: operational planning. Dependencies: calendar integration.
- Price uplift simulator (BI-10). Story: simulate acceptance vs price changes. Approach: logistic model trained on outcomes. Effort: L. Success: margin gains. Dependencies: win/loss data.

## Part 4: Recommended Next Steps
- Patch Critical items CRIT-001 through CRIT-004 and HIGH-001 through HIGH-003 first; re-run regression tests around onboarding and quote generation.
- Align product messaging across help, landing, and email templates to the unlimited plan narrative.
- Add storage abstraction to PDF generation and share flows before scaling workers.
- Scope a small "Immediate" innovation batch (2-3 items) for next sprint.

## Appendix: Full Findings
- Phase 1: .claude/audit-innovation-outputs/phase1-holes-GPT-5.2-CodexNEW.md
- Phase 2: .claude/audit-innovation-outputs/phase2-polish-GPT-5.2-CodexNEW.md
- Phase 3: .claude/audit-innovation-outputs/phase3-innovations-GPT-5.2-CodexNEW.md
