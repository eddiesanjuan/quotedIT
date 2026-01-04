# Phase 2: UX & Polish Audit (GPT-5.2-Codex)

**Generated**: 2025-12-26  
**Repo revision**: `97803ee`  
**Evidence**: UI screenshots in `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/ui/`

---

## What’s already working (so you keep it)

- The visual system is cohesive: dark premium styling, strong hierarchy, minimal clutter (see `ui/landing-1440.png` and `ui/try-1440.png`).
- The demo experience is compelling and reduces signup friction (see `ui/try-iphone11.png`).

## Mobile experience (375px)

### High impact issues
- Bottom navigation omits Tasks and Invoices, reducing discoverability of core “CRM/workflow” features: `frontend/index.html:6464`.
- Several settings flows fail silently (console errors only) if backend endpoints return errors (logo and quote defaults): `frontend/index.html:12885`.

### Recommendations
- Add nav items (or a “More” menu) for Tasks and Invoices, or surface them prominently on the Home dashboard.
- Convert “console-only” failures into user-visible error toasts with recovery actions.

---

## Copy & messaging

### Trust/consistency issues
- Help copy still claims “Email Direct (coming soon)” while email sharing exists: `frontend/help.html:623`, `backend/api/share.py:108`.
- Domain mismatch across app shell / config / email templates increases confusion and can break deep links:
  - `backend/config.py:19`
  - `backend/services/email.py:30`
  - `frontend/help.html:486`

### Recommendations
- Choose one canonical public domain and enforce it everywhere (frontend templates, email templates, config).
- Audit help/FAQ for “coming soon” statements and align with shipped behavior.

---

## Loading, feedback, and error states

### Gaps
- Some operations change button text but don’t provide durable confirmation/error recovery (e.g., invoice send button): `frontend/index.html:13496`.
- Shared invoice error state is minimalist and offers no support link or retry path: `frontend/invoice-view.html:649`.

### Recommendations
- Standardize async UX patterns:
  - consistent loading indicators
  - success confirmation
  - actionable error messages (“Retry”, “Contact support”, “Copy error details”)
- Add accessible announcements (ARIA live regions) for critical toast notifications.

---

## Onboarding and first-time UX

- Trade/industry selection can become a scroll trap on mobile; add search, “top trades”, or “recently used” to reduce friction (the selection UI lives in `frontend/index.html` onboarding section).
- Surface “Demo mode uses industry-standard pricing” messaging consistently (landing + try + demo results) to avoid users assuming it learned their business before signup (see `ui/try-1440.png`).

---

## Accessibility (a11y) checklist (high leverage)

Recommended improvements (mostly mechanical, high ROI):
- Ensure every icon-only button has an accessible label.
- Add focus styles for keyboard navigation.
- Ensure toast system uses `aria-live="polite"` for non-critical and `assertive` for blocking errors.
- Validate color contrast for secondary text on dark backgrounds (especially on mobile).

---

## Polish opportunities (quick wins)

- Reduce `confirm()` usage in favor of consistent in-app modals/toasts: `frontend/index.html:9228`.
- Replace `innerHTML` template renders for remote strings with `textContent` rendering to reduce XSS blast radius: `frontend/index.html:13037`.
- Ensure Shepherd tour fallback waits for script load (avoid race when primary CDN fails): `frontend/index.html:4423`.
