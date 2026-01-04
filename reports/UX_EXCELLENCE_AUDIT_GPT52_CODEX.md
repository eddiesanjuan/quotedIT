# UX Excellence Audit Report (Real Browser via Playwright)

**Product**: Quoted (`https://quoted.it.com`)  
**Date**: 2025-12-27  
**Auditors (simulated team)**: UX Research Lead · Conversion Auditor · Mobile Specialist · Accessibility Auditor · Performance Auditor · Content/Copy Auditor  
**Tooling**: Playwright `@playwright/test` (Chromium)  
**Primary Artifact Run**: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/`

---

## 0) What I Actually Did (and What “Real Browser” Means Here)

This audit was executed with an automated **Playwright-run browser engine** (Chromium) against production URLs, capturing:
- Full-page screenshots (desktop + mobile)
- Navigation timings (DCL/load + transfer sizes)
- Quote-generation elapsed time
- Mobile tap-target measurements (44×44 guideline)
- Mobile horizontal overflow detection + offender element hints

No test accounts or real credentials were used; authenticated, data-bearing areas were **not** exercised beyond the `/app` entry/login screen.

### Execution log (audit ops)
1. Reviewed the existing Claude command at `.claude/commands/orchestrate-ux-excellence.md`.
2. Authored a Codex/Playwright version at `.claude/commands/orchestrate-ux-excellence-playwright.md`.
3. Implemented `scripts/ux_audit_playwright/ux-excellence.spec.js`.
4. Ran the suite multiple times; final run is `2025-12-27-gpt52-codex-v4`.

---

## 1) Executive Summary

### Overall UX Scorecard (public experience only)
| Dimension | Score | Summary |
|---|---:|---|
| First-impression clarity | 9/10 | The hero headline communicates value fast. |
| Demo time-to-value | 9/10 | Real quote generation + excellent results UI. |
| Conversion readiness | 7/10 | Strong demo, but **social proof** is still thin above the fold. |
| Mobile usability | 7/10 | Core flows work, but **tap targets** and **horizontal overflow** need fixing. |
| Accessibility fundamentals | 6.5/10 | Contrast mostly good; **target sizes** + some “muted” text likely fail AA. |
| Performance (public pages) | 8.5/10 | Landing and demo are fast; `/app` payload is comparatively heavy. |

### “What’s great already” (keep and amplify)
- The landing story is direct: “Talk, don’t type. Quote in seconds.” is elite messaging.
- The demo (`/try`) is a **legit product experience**, not a fake animation: line items, totals, clarifying questions, and a “what’s next” CTA.
- Help & FAQ and customer-facing landing pages are polished and consistent with the brand aesthetic.

### “What’s holding growth back right now” (top 5)
1. **P0 — Mobile tap targets below 44×44** on primary nav links and a key hero link.
2. **P0 — Horizontal overflow on mobile** landing and use-cases pages (subtle sideways scroll).
3. **P1 — Social proof gap** on the main landing experience (above the fold + early scroll).
4. **P1 — /app is heavy** vs other public pages; could slow cold-start “try the app” intent.
5. **P2 — Demo share is not a shareable quote** (shares the demo URL, not the generated quote output).

---

## 2) Evidence Pack (Artifacts You Can Open)

All artifacts are in: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/`

Key files:
- Run metadata: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/run-meta.json`
- Session summaries:  
  - Desktop: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/session-summary.json`  
  - Mobile: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/session-summary.json`
- Mobile tap targets (landing): `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/landing-target-size-summary.json`
- Mobile overflow offenders:  
  - Landing: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/landing-overflow.json`  
  - Use cases: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/use-cases-overflow.json`

Screenshots (high-signal):
- Landing (desktop): `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/landing.png`
- Landing (mobile): `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/landing.png`
- Demo results (desktop): `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-results.png`
- Demo results (mobile): `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/try-results.png`
- Demo progress moments:  
  - `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-generating-0.5s.png`  
  - `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-generating-3s.png`

---

## 3) Persona Walkthroughs (First-Time User Experience)

### Persona A: Desktop contractor evaluating quoting software
| Time | Action | Expectation | Reality | Confusion (1-5) |
|---:|---|---|---|---:|
| 0s | Land on `/` | Understand what it is immediately | Clear headline + two CTAs | 1 |
| 10s | Scan hero + subtext | “What’s the fastest proof?” | “Try It Now — No Signup” is perfect | 1 |
| 20s | Click “Try It Now — No Signup” | See an actual demo | `/try` loads fast | 1 |
| 35s | Switch to Text, paste job | Expect guidance | Good placeholder + example chips | 1 |
| 40s | Click “Generate Quote” | Expect wait/progress | Progress state + “Usually takes ~10–15s” | 1 |
| ~53s | Quote appears | Expect usable output | Line items + total + notes + questions | 1 |
| 60s | Look for “what next” | Next step should be obvious | Tour modal + CTA “Start Free Trial” | 2 |

Net: The public flow is unusually strong. The “fresh user” path feels intentional, fast, and satisfying.

### Persona B: Mobile contractor on a job site (one-handed)
| Action | Thumb Zone (Y/N) | Readable | Works | Notes |
|---|---|---|---|---|
| Landing hero CTAs | Partial | Yes | Yes | CTAs are large; nav links are small. |
| Tap top nav links | No | Yes | Yes | Links are visually small; below 44px target size. |
| Open demo and generate quote | Yes | Yes | Yes | Text path works; results are readable. |
| Share from demo | Yes | Yes | Mostly | Shares demo URL; not the generated quote. |

Net: Mobile is good where it matters (demo + results), but needs quick accessibility/overflow fixes.

---

## 4) Findings (Prioritized, Ticket-Ready)

### P0 — Mobile tap targets below 44×44 (WCAG 2.5.5 / usability)
**Evidence**: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/landing-target-size-summary.json`  
Worst offenders include:
- Nav links “Use Cases” and “Blog” at ~23px height
- Hero link “See how it works for your industry” at ~22px height

**Why it matters**: This directly impacts mobile conversion and creates mis-taps; also an avoidable accessibility violation.

**Fix direction** (low effort):
- Wrap nav links in larger tap areas (padding + `min-height: 44px; display: inline-flex; align-items: center`).
- Convert the hero secondary link into a small button-style component on mobile (padding + border), or place it inside a 44px row.

---

### P0 — Horizontal overflow on mobile landing and use-cases (sideways scroll)
**Evidence**:
- Landing overflow: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/landing-overflow.json`  
  - Top offenders include `nav`, `.container`, and `#heroLogo` / `.logo-spinner` elements.
- Use-cases overflow: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/use-cases-overflow.json`  
  - Offenders include `nav` and `.industry-chip` cards.

**What the user experiences**: subtle sideways scroll / layout jitter; feels “not quite native” on mobile.

**Fix direction** (low effort):
- Ensure mobile nav collapses (hide extra links, reduce padding/gap, or add hamburger) on `frontend/landing.html` similarly to `frontend/use-cases.html`.
- Add `max-width: 100%` and safe overflow containment for large hero/logo animation elements; avoid `white-space: nowrap` on mobile for the animated hero-logo or constrain it.
- On use-cases, ensure chips/cards wrap or are in an intentional horizontal scroller with `overflow-x: auto;` and `scroll-snap` (so overflow is *intentional*, not “page is wider than viewport”).

---

### P1 — Social proof gap on landing (trust / conversion)
**Evidence**: landing screenshots show clear messaging and CTAs, but no prominent proof block near the hero: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/landing.png`

**Impact**: This is likely the biggest lever for “cold visitor → signup” once demo works this well.

**Fix direction**:
- Add a compact “proof bar” under CTAs: usage count, time-saved claim, 1–2 real quotes screenshots, a mini testimonial.
- If you can’t claim numbers yet, use “micro-proof”: founder credibility, “built for contractors”, “no credit card”, “PDFs look professional”.

---

### P1 — `/app` initial payload is large vs other pages
**Evidence**: Transfer size ~746KB (Playwright nav entry): `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/sessions.json`

**Impact**: This is where “Start Quoting” intent goes; any extra seconds cost conversions.

**Fix direction**:
- Defer non-critical JS/CSS on the unauth entry screen.
- Consider a smaller unauth shell that progressively loads the full app after login.

---

### P2 — Demo sharing doesn’t share the generated quote output
**Evidence**: `/try` share code uses a static URL `https://quoted.it.com/try?utm_source=demo_share...` (see `frontend/try.html`).

**Impact**: Sharing is a natural viral loop; right now it shares the *demo*, not the *quote you just made* (the emotional peak).

**Fix direction**:
- For demo users: create a temporary share token for the generated quote (even if it’s marked “DEMO”) and share `/shared/<token>` so the recipient sees “their quote”.

---

## 5) What’s Working Exceptionally Well (Keep / Double Down)

### Demo generation UX is a highlight
Screenshots show:
- Clear expectation setting (“Usually takes about 10–15 seconds”).
- Progressive status steps (“Analyzing your job description…”, “Identifying line items…”).

Evidence:
- `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-generating-0.5s.png`
- `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-generating-3s.png`

Actual measured generation time:
- Desktop: ~12.8s
- Mobile: ~12.0s  
(`generationMs` in session summaries)

This alignment between **system reality** and **user expectation** is rare and very good.

### Public support surfaces are clean and credible
- Help & FAQ looks consistent and well-structured: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/help.png`
- Customer landing page is strong (viral ready): `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/for-customers.png`

---

## 5) Page-by-Page UX Audit (Public Surfaces)

### 5.1 Landing (`/`)

**What the user sees (first 5 seconds)**:
- Brand + headline: “Talk, don’t type. Quote in seconds.”
- Clear, parallel CTAs: “Try It Now — No Signup” and “Start Free Trial”
- Subtext promise: “Generate a real quote in 30 seconds • Free trial includes 75 quotes”

**What’s excellent**:
- The headline is short, concrete, and benefit-led.
- “No Signup” is doing real work: it reduces perceived risk and makes the promise testable.
- The aesthetic feels premium without being sterile.

**Where it breaks down (conversion + mobile)**:
- **Mobile nav is overpacked** (logo + multiple links + CTA): leads to tap-target failures and horizontal overflow.
- Social proof is not strongly present at the “decision moment” (hero / early scroll).

**Specific improvements**:
1. **Mobile nav collapse** (low effort):
   - Hide “Use Cases” + “Blog” behind a hamburger under ~900px, or move them below the fold into a sticky bottom nav.
   - Expand link hit areas to 44px min (see P0 finding).
2. **Add a proof bar under CTAs** (medium effort, high ROI):
   - One-liner founder credibility (real contractor), one stat (time saved / quotes created), one tiny testimonial.
3. **Reduce “silent skepticism”**:
   - Add a 1-line “What you get” row: “PDF quote + line items + client-ready view + edit/regenerate”.

**Evidence**:
- Desktop hero: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/landing.png`
- Mobile hero: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/landing.png`

---

### 5.2 Demo / Try (`/try`)

**What the user sees**:
- Clear “DEMO MODE” badge and the promise: “Generate a Real Quote”.
- Two input modes (Voice/Text) with a big, confident voice affordance.
- “Demo uses industry-standard pricing” disclaimer (important expectation-setting).

**What’s excellent**:
- The progress UI is unusually good: it sets expectations and narrates steps.
- Output is high-value: line items, total, notes, clarifying questions.
- The post-result CTAs are coherent: download/share/try again + upsell panel.

**Friction / opportunities**:
1. **Share doesn’t share the quote** (it shares the demo URL). You’re missing the emotional peak.
2. **PDF download is powerful** but needs a demo watermark (so users don’t accidentally send “industry standard” pricing to real customers).
3. **Voice permissions**: voice-first products often fail at the permission moment; a micro-hint reduces abandonment.

**Specific improvements**:
- Create a temporary share token for the generated quote and share `/shared/<token>` (with “DEMO” watermark).
- Add a short 1-liner under the mic button on first interaction: “Your browser will ask for mic access.”
- Add “Edit & regenerate” callouts *before* the user sees the quote, so they understand they’re in control.

**Evidence**:
- Results (desktop): `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-results.png`
- Generating states:  
  - `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-generating-0.5s.png`  
  - `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-generating-3s.png`

---

### 5.3 App Entry (`/app`)

**What the user sees**:
- A clean auth box with “Sign In” / “Create Account”
- A safety valve: “Try a Demo Quote Free”
- A help affordance (“?”)

**What’s excellent**:
- The demo escape hatch is correctly placed and reduces fear of commitment.
- The UI is minimal; easy to understand.

**Friction / opportunities**:
- `/app` is where intent lands (“Start Quoting”), but it has a much larger initial transfer size than public pages.
- The entry screen doesn’t proactively answer “what happens after I sign up?” (especially if passwordless/magic links are used elsewhere or planned).

**Specific improvements**:
- Defer heavy app assets until after successful auth (or load a smaller unauth shell).
- Add a 1–2 line “what you get after signup” under the primary button (reduces uncertainty).

**Evidence**:
- Desktop: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/app-entry.png`
- Mobile: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/app-entry.png`

---

### 5.4 Use Cases (`/use-cases`)

**What the user sees**:
- A strong framing headline (“Stop Fighting With Templates. Start Talking.”)
- An industry grid that helps users self-identify

**What’s excellent**:
- “Works for me?” is a major objection; this page addresses it.
- The page is skimmable and “benefit dense”.

**Friction / opportunities**:
- Mobile horizontal overflow (industry chips/cards) creates sideways scroll.
- This page should be a conversion weapon, but it currently feels like a brochure: it doesn’t always connect directly to “try my industry now”.

**Specific improvements**:
- Make the industry grid drive into `/try` with prefilled prompts (and label them “Example”).
- Make overflow *intentional* (wrap chips, or horizontal scroller with scroll-snap) so it feels native.

**Evidence**:
- Desktop: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/use-cases.png`
- Mobile: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/use-cases.png`
- Overflow offenders: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/use-cases-overflow.json`

---

### 5.5 Blog (`/blog`)

**What the user sees**:
- A clean “Quoting Guide” index with categories and cards.

**What’s excellent**:
- Fast load, skimmable layout, and credible structure (for SEO + trust).

**Friction / opportunities**:
- The blog is an acquisition channel; it should also be a conversion channel.
- Add cross-links between guides (“Related Guides”) and stronger mid-article conversion modules.

**Evidence**:
- Desktop: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/blog-index.png`
- Mobile: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/blog-index.png`

---

### 5.6 Help & FAQ (`/help`)

**What the user sees**:
- Well-grouped accordion sections (Getting Started, Pricing, Using Quoted, Troubleshooting)
- A “Talk to Eddie” contact card that feels personal

**What’s excellent**:
- Clean IA, minimal distraction, and the “Talk to Eddie” module is credibility.

**Friction / opportunities**:
- Ensure accordions are fully accessible (aria-expanded/controls) and keyboard-navigable.
- Add a “Quick start” section that links directly to `/try` and “how to record voice”.

**Evidence**:
- Desktop: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/help.png`
- Mobile: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/help.png`

---

### 5.7 Customer Landing (`/for-customers`)

**What the user sees**:
- “Your contractor uses Quoted. You can too.”
- A strong green CTA to the demo
- A trust badge: “Join 100+ contractors using Quoted”

**What’s excellent**:
- This page can become a viral loop when tied to shared quotes/invoices.
- The CTA and feature cards are clear and mobile-friendly.

**Friction / opportunities**:
- Ensure all claims (“100+ contractors”) are accurate or safely phrased (“Contractors are using Quoted” without a specific number).
- This page should be directly reachable from shared quote views (“Made with Quoted”).

**Evidence**:
- Desktop: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/for-customers.png`
- Mobile: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/mobile-375/for-customers.png`

---

### 5.8 Legal (`/terms`, `/privacy`)

**What the user sees**:
- Long-form legal pages in the same brand aesthetic.

**What’s excellent**:
- Presence of these links reduces risk perception (“this is a real company”).

**Opportunity**:
- Add a short “plain-English summary” section at the top (especially for privacy) to reduce anxiety.

Evidence:
- `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/terms.png`
- `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/privacy.png`

---

## 6) What’s Working Exceptionally Well (Keep / Double Down)

### Demo generation UX is a highlight
Screenshots show:
- Clear expectation setting (“Usually takes about 10–15 seconds”).
- Progressive status steps (“Analyzing your job description…”, “Identifying line items…”).

Evidence:
- `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-generating-0.5s.png`
- `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/try-generating-3s.png`

Actual measured generation time:
- Desktop: ~12.8s
- Mobile: ~12.0s  
(`generationMs` in session summaries)

This alignment between **system reality** and **user expectation** is rare and very good.

### Public support surfaces are clean and credible
- Help & FAQ looks consistent and well-structured: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/help.png`
- Customer landing page is strong (viral ready): `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/desktop-1440/for-customers.png`

---

## 7) Performance Snapshot (From Playwright Navigation Timing)

These are “best effort” timings from `performance.getEntriesByType('navigation')` captured by Playwright.

| Page | Desktop DCL | Mobile DCL | Transfer Size |
|---|---:|---:|---:|
| `/` | ~365ms | ~279ms | ~91KB |
| `/try` | ~60ms | ~54ms | ~90KB |
| `/app` | ~715ms | ~400ms | ~747KB |
| `/blog` | ~54ms | ~64ms | ~25KB |
| `/use-cases` | ~67ms | ~52ms | ~95KB |

Source: `reports/ux-excellence-playwright/2025-12-27-gpt52-codex-v4/sessions.json`

---

## 8) Innovation Opportunities (10x, Not Just Fixes)

### 1) “Share the Quote” Viral Loop (Demo + Product)
When a user generates a quote, the peak emotion is “holy crap, it did it”. That’s when sharing is most likely.
- Generate a **public demo quote link** (`/shared/demo_<token>`) with a tasteful “DEMO” watermark.
- Add “Send to customer” as a guided step (explain it’s a demo; in product it becomes branded + your pricing brain).

### 2) The Pricing Brain “Moat Visualization”
The demo explains “we learn YOUR pricing”, but the public site doesn’t show the *felt* benefit.
- Add a “Pricing Brain” visualization: 3–5 “learned rules” cards and a confidence meter.
- After each correction in-product, show a “+1 learning captured” micro-celebration.

### 3) One-Screen Mobile Conversion Pattern
Given the product is mobile-friendly, consider a sticky mobile CTA:
- Persistent “Try It Now” bottom bar on landing on mobile.
- After scroll depth > X, turn it into “Generate a quote →” with a small context hint.

### 4) Industry-specific demo presets
Use-cases is strong; connect it to demo:
- “Try electrician example” deep links that prefill the demo prompt (and label it as such).

---

## 9) 14-Day Roadmap (Focused)

### Days 1–3 (P0 fixes)
1. Fix mobile tap targets on landing navigation + hero secondary link.
2. Fix mobile horizontal overflow (landing + use-cases) with targeted CSS changes and re-run Playwright audit.

### Days 4–7 (Conversion lift)
3. Add social proof block near hero (even if it’s founder credibility + early beta metrics).
4. Add a “demo quote share link” that shares the generated quote output (DEMO token).

### Days 8–14 (Moat storytelling)
5. Add a lightweight “Pricing Brain” explainer + visuals (public) and a progress indicator (product).

---

## Appendix A) Current Limitations of This Audit

- Authenticated flows (dashboard/CRM/invoicing/learning UI) were not audited end-to-end because no test account credentials were used.
- Voice recording UX was not executed (microphone permissions are hard to automate reliably in this setup without explicit config).
