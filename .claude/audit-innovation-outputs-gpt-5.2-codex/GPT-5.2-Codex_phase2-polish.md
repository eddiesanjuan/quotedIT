# Phase 2: UX & Polish Audit (GPT-5.2-Codex)

**Date**: 2025-12-25  
**Scope**: Frontend UI/UX (index + customer views), interaction design, accessibility, perceived performance

---

## Executive summary

Quoted already has strong “voice-first” scaffolding and a cohesive aesthetic. The biggest polish opportunities are:
- **Consistency** (replace `alert()`/`confirm()` with the existing toast + modal patterns)
- **Accessibility** (add ARIA semantics, focus management, keyboard support)
- **Resilience** (timeouts, retries, and unified error parsing)
- **Perceived performance** (reduce “hanging” loading states, add progress messaging)

---

## HIGH priority polish items

### UX-01: Replace browser alerts/confirms with first-class UI components
- **Evidence**: `frontend/index.html:8725`, `frontend/index.html:11240`, `frontend/index.html:14510` and many more
- **Why it matters**: alerts feel unpolished on mobile, interrupt flow, and are hard to style/accessibly manage
- **Recommendation**:
  - Use toast for information/success
  - Use a custom confirmation modal for destructive actions
  - Standardize error messaging (“what happened” + “what to do next”)

### UX-02: Add accessibility primitives (ARIA + focus management)
- **Evidence**: no `aria-*` or `role="dialog"` usage detected in `frontend/index.html` (search for `aria-` returns none)
- **Why it matters**: keyboard users and screen readers will struggle with modal-heavy UI
- **Recommendation**:
  - Dialog modals: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, focus trap, Escape-to-close
  - Buttons: ensure all clickable divs are actual `<button>` or have `role="button"` + key handlers
  - Inputs: ensure labels/`aria-describedby` exist for helper text and errors

### UX-03: Add request timeouts + “retry” UX for long operations
- **Evidence**: many `fetch()` calls, no AbortController timeouts; `authenticatedFetch()` exists but doesn’t apply timeouts (`frontend/index.html:7066`)
- **Recommendation**:
  - Introduce `apiRequest()` wrapper: timeout, consistent JSON parsing, user-friendly errors, retry for idempotent GETs
  - For transcription/quote generation: show “this may take ~X seconds” + cancel button

### UX-04: Defense-in-depth for DOM insertion
- **Evidence**: `frontend/index.html:12077` uses `innerHTML` with API values for template cards
- **Recommendation**:
  - Render with DOM nodes + `textContent`
  - Adopt a “no innerHTML with external strings” rule

---

## MEDIUM priority polish items

### UX-05: Unify auth refresh behavior across features
- **Evidence**: wrapper exists (`frontend/index.html:7066`) but many calls use raw `fetch`
- **Recommendation**: enforce one wrapper for all API calls, including settings, invoices, CRM, and onboarding.

### UX-06: Mobile ergonomics improvements (tap targets, spacing)
- **Evidence**: demo UI uses small fonts (e.g., `frontend/demo.html:463` uses 11px)
- **Recommendation**: ensure 44px minimum tap target, 12–14px minimum text for body, avoid tiny badges.

### UX-07: Reduce “single file” frontend risk
- **Evidence**: `frontend/index.html` is ~652KB and mixes CSS/JS/HTML
- **Recommendation**: split assets for caching, faster iteration, and safer diffs.

---

## What’s already strong (keep it)
- Voice support detection and fallback concept (`frontend/index.html:7665` onward)
- Safe DOM rendering approach in customer quote view (`frontend/quote-view.html:819` onward uses `textContent`)
- Toast system exists (use it everywhere)

