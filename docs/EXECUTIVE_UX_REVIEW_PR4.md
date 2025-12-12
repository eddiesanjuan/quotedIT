# Quoted PR‑4 Executive UX & Company Review
**Date:** 2025‑12‑12  
**Reviewer:** Codex (GPT‑5.2)  
**Scope:** Live PR site walkthrough + product/ops lens for executive review.

---

## Blunt Executive Summary
Quoted is already a credible, premium-feeling product with a sharp wedge: **instant budgetary quotes from voice/text at the job site**. The core experience (Describe job → Generate quote → Edit → Learns → PDF) is clean, fast, and trustworthy. Adjacent features (Customers CRM, Tasks, Invoices) are coherently integrated and don’t break the quoting loop.

The main risk is **adoption speed and early trust**, not core capability. The app still feels like a full “suite” before users have felt first value, and the learning moat isn’t yet *visibly rewarding* enough to drive the correction volume that compounds your advantage.

### The 3 Changes That Most Improve Outcomes
1. **Exploit and tighten the try‑first demo funnel:** The live landing now offers **“Try It Now — No Signup”** at `/demo` (voice + text, industry‑standard pricing). Make this the dominant first‑touch, ensure demo output mirrors the app, and instrument demo→signup conversion.  
2. **Progressive disclosure of suite features:** Hide/soft‑gate CRM/Tasks/Invoices until after first quote(s). Keep the mental model “quoting app that learns,” not “new CRM to manage.”  
3. **Make learning tangible after edits:** After any edit, show what Quoted learned and let users accept/tweak. This will drive corrections and accelerate the moat.

---

## What We Evaluated
Live PR walkthrough included:
- Login → New Quote → Generate quote from text  
- Navigation into My Quotes, Customers, Tasks, Invoices, Account  
- Review of empty‑state flows and suite mental model  
- Review of quote output hierarchy and actions
- Live landing + demo flow on `quoted.it.com` (`/demo`, `/use-cases`) to validate top‑of‑funnel.

---

## What’s Strong (Keep)
### Product / Wedge
- **Category is clear and defensible:** “Instant voice quote from job site” is unclaimed and intuitive.
- **Budgetary framing is explicit:** The UI reinforces “ballpark estimate, not takeoff.”
- **Learning system is a real moat:** Three‑layer learning (global philosophy → category tailored prompt → specific adjustments) is simple, transparent, and compounding.

### UX / Execution
- **Premium aesthetic builds trust.** Looks like a serious tool, not a hobby SaaS.
- **New Quote page is extremely clear.** One card, one action, voice + text fallback.
- **Transcription review is a practical trust booster.**
- **Quote output reads professional and send‑ready.**
- **Empty states are strong.** Every one routes back to creating a quote with crisp copy.
- **Suite coherence is good.** CRM/Tasks/Invoices feel like natural extensions, not bolt‑ons.
- **Live landing is doing the right job:** crisp hero (“Talk, don’t type. Quote in seconds.”), strong proof sections, and a functional demo CTA that reduces trust friction.

### Company Readiness
- **Billing, analytics, referrals, feature flags, and error tracking are already in place.**
- You’re not flying blind; you can measure activation, retention, edit rate, and payback.

---

## Primary Weaknesses / Risks
1. **Demo→signup conversion still needs proof.** The live site now solves the trust gap with a real `/demo` quote flow; the remaining risk is making that path convert and ensuring post‑signup onboarding stays lightweight. In PR‑4 the post‑signup path is mostly progressive, but the industry‑selection step is a noticeable extra screen and the “Try a Quote Now” list row looked tappable yet didn’t reliably advance unless the primary button was used.  
2. **Too much surface area too early.** The app feels like an all‑in‑one suite before the user has completed the core loop.  
3. **Learning loop visibility is low.** The moat requires edits; the product doesn’t yet make “edit → it gets smarter” obvious and motivating.  
4. **Mobile voice UX is existential.** Contractors live on phones. If iOS recording or quote actions feel flaky/buried, adoption stalls.
5. **Plan/packaging consistency risk.** Pricing and usage‑cap messaging must stay consistent across landing, in‑app billing, and docs to avoid trust erosion.

---

## Detailed UX Findings & Recommendations

### 1) Entry / Login
**Observed:** `/app` opens to sign‑in/create account inside the app shell, while the live landing now routes skeptics to a functional `/demo` first.  
**Issue:** The PR app doesn’t surface that demo path; first‑time users can still hit auth/onboarding friction before value.

**Recommendations**
- **Keep `/demo` as the primary first‑touch and mirror it in‑app:** add “Try a demo quote” CTA on the auth screen and during onboarding deferral.  
- **Tighten demo→signup handoff:** clear watermark/limits, then a single CTA: “Save and teach your pricing (free trial).”
- **Align auth model in messaging.** UI is password‑based here; docs previously referenced magic links. Pick one and keep it consistent.

### 2) Onboarding
**Observed:** After signup, users pick a trade/industry, then see a 3‑option start screen: **Try a Quote Now (industry defaults)**, Quick Chat Setup, or Manual Setup. This is the right progressive onboarding pattern and matches the landing `/demo` promise.

**Issues**
- **Industry selection is heavy for first value.** The grid is large (many non‑contractor roles), so it adds friction before a user gets their first quote.  
- **Try‑first row click reliability.** The “Try a Quote Now” *list row* looks tappable but didn’t reliably proceed unless the large primary button was clicked → risk of stuck users.

**Recommendations**
- Keep the 3‑option progressive start, but **reduce friction**:  
  - Auto‑suggest/top‑filter the trade based on landing “use cases,” and allow a “skip/decide later” path for unsure users.  
  - Make the entire “Try a Quote Now” row reliably trigger the same behavior as the button.  
- After try‑first activation, show a one‑sentence reassurance: “Using industry defaults now; edits teach your real pricing.”  
- Add a short post‑interview recap (plain English) to cement trust and reduce “what did it learn?” anxiety.

### 3) New Quote (Voice/Text)
**Observed:** Clean, minimal, correct hierarchy.  
**Recommendation upgrades**
- Add **recording timer + “tap again to stop” microcopy** for field clarity.  
- **Sticky actions on quote result** (Download / Edit / New Quote) so mobile users don’t scroll hunt.  
- Consider **optional skip‑review** after trust is established (e.g., after 5 successful quotes).

### 4) Quote Result + Editing
**Observed:** Professional output; total is clear. Badge shows “Limited data or corrections.”

**Issues**
- Badge language can sound like user error or unreliability.
- Actions can get buried on long quotes (especially mobile).

**Recommendations**
- Replace badge text with job‑specific, reassuring language:
  - “Still learning your pricing for decks”
  - “High confidence for your fencing jobs”
- Add a **one‑sentence explainer under badge:**  
  “Edit any line item and Quoted will learn your real pricing for next time.”
- **If clarifying questions exist:** offer “Answer now” vs “Create follow‑up task.”

**Observed in edit detail view:** Line items are editable via name/qty/unit/unit‑cost, and an edit‑mode banner + change summary appear once you modify something. However, the **Save Changes panel (including correction notes) sits below the fold** on long quotes; it’s easy to miss unless the user scrolls.

**Editing UX recommendations**
- Make **Save Changes sticky/docked** whenever unsaved changes exist.  
- Surface correction notes at save time (modal or near top), not hidden at bottom.  
- After saving, show a clear “Learned adjustment saved” toast and **reflect the first correction immediately** in Pricing Brain. In PR‑4, Pricing Brain remained empty after a first correction, which undercuts the reward loop.

### 5) My Quotes
**Observed:** Great empty state and CTA.  
**Future‑state recommendation**
- Keep history UX lightweight; contractors mostly need recency and search.
- Add **“duplicate quote”** once usage grows (high leverage for repeat jobs).

### 6) Customers CRM
**Observed:** Even empty, UI shows filters/actions/stats.

**Issue**
- Before any customers exist, this reads like “another CRM to manage.”

**Recommendations**
- **Progressive disclosure:** before first customer, show only the auto‑creation narrative + CTA. Hide filters behind “Manage customers.”  
- Add **1‑tap link from quote → customer detail** (“View customer history”).
- Surface CRM voice commands contextually right after quotes.

### 7) Tasks & Reminders
**Observed:** Full task manager layout even when empty.

**Issue**
- Same suite‑early risk as CRM; can feel like overhead.

**Recommendations**
- **Gate Tasks behind first 2–3 quotes** unless beta pull proves otherwise.  
- Add **voice‑first task capture from anywhere:**  
  “Remind me to follow up with John Friday.”
- Auto‑suggest follow‑up tasks after quote generation, accept/decline.

### 8) Invoices
**Observed:** Simple empty state, CTA back to quotes.  
**Recommendation**
- Keep beta scope narrow: “Convert to invoice” from a quote + minimal fields.  
- Avoid AR/accounting expansion until PMF is proven.

### 9) Account & Billing
**Observed:** Clean billing tab with plan grid.

**Risk**
- **Pricing/usage messaging must be consistent** everywhere (avoid “unlimited” drift if caps are strategic). Inconsistency kills trust.

**Recommendations**
- Show remaining quotes / overage rate **in app header** as well as billing.
- Trigger referral CTA at success moments (first PDF).

### 10) Mobile/PWA
**Strategic reality:** This surface decides PMF.

**Recommendations**
- Ship **PWA manifest + add‑to‑home‑screen** immediately (fast win).  
- Run an iOS voice regression pass (permissions, MIME types, backgrounding, slow networks).  
- Reduce vertical density in CRM/tasks on small screens.

---

## Mental Model Tightening
Right now Quoted feels close to “all‑in‑one quoting + CRM suite.” That’s fine later, but too early for beta.

**Ideal early mental model:**
1. Describe job  
2. Get a good ballpark quote fast  
3. Edit once, it learns forever  
4. Everything else appears as a natural extension after that loop is felt

---

## Beta / PMF Recommendations

### Focused ICP + Positioning
- Keep beta tightly on contractors/trades.
- Don’t lead with CRM/Tasks/Invoices in messaging yet.
- Lead with **speed, budgetary honesty, and learning moat**.

### Acquisition Play
- Product is ready; distribution is bottleneck.
- Start with 1–2 trades, 10–20 users, tight feedback loops.
- Use referral system immediately after first‑quote success.

### What to Measure in Beta
- Activation (first quote generated)
- Voice vs text usage in real field conditions
- Edit rate over time (moat KPI)
- Time‑to‑quote p50/p95
- Weekly retention by trade + onboarding path

### 4–6 Week Sequencing
1. Optimize demo funnel + progressive onboarding alignment (measure demo→signup, reduce post‑signup friction)  
2. Mobile/PWA voice hardening + sticky actions  
3. Post‑edit learning recap + correction nudges  
4. Expand CRM/Tasks/Invoices only based on observed pull

---

## Quick Wins (Low Effort / High ROI)
- Rename/clarify confidence badge text.
- Hide CRM/Tasks/Invoices tabs until after first quote (or move them under “More”).
- Sticky action bar on quote results for mobile.
- Post‑edit “Here’s what I learned” toast + link to Pricing Brain.
- Add “Try a demo quote” CTA on `/app` auth for first‑timers to match landing.
- Fix “Try a Quote Now” list‑row click so it always advances.  
- Make Save Changes sticky and bring correction notes into view on long quotes.

---

## Closing Take
Quoted is past “cool AI demo” and into “real product with a moat.” The next wins aren’t more features — they’re **faster first value, ruthless mobile voice reliability, and visibly rewarding edits to compound learning.**
