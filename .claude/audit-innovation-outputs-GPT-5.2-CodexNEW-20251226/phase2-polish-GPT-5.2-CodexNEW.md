# Phase 2: UX & Polish Audit (GPT-5.2-CodexNEW)

## Mobile Experience
- Mobile bottom nav omits Tasks and Invoices, making key features hard to discover on small screens (`frontend/index.html:6464`, `frontend/index.html:5872`).
- Industry selection is a long, static grid with no search or quick filter; on mobile this creates high friction early in onboarding (`frontend/index.html:5159`).

## Copy & Messaging
- Help page still says "Email Direct (coming soon)" even though direct email sharing is live; update to avoid trust erosion (`frontend/help.html:623`, `backend/api/share.py:108`).
- Mixed domain usage (quoted.it vs quoted.it.com) across config and emails undermines brand consistency and can confuse users (`backend/config.py:26`, `backend/services/email.py:33`).

## Loading, Error, Empty States
- Customer backfill shows a generic "Syncing" state but provides limited progress or error detail if long-running (`frontend/index.html:14482`).
- Invoice share view shows a minimal error card with no recovery path or support link (`frontend/invoice-view.html:649`).

## Interaction & Accessibility
- Quote sharing and invoice flows rely on toasts only; critical errors could be missed by screen readers without ARIA live regions (`frontend/index.html:13496`).
- Several onboarding and quote creation steps depend on long scrolling; consider persistent step indicators for orientation (`frontend/index.html:5159`).
