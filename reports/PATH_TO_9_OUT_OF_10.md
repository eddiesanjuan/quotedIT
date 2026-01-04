# Path to 9/10: Quoted UX Excellence Roadmap

**Generated**: December 27, 2025
**Baseline**: UX Excellence Audit (14 agents, 50+ files analyzed)

---

## Current Scores → Target

| Area | Current | Gap | Priority |
|------|---------|-----|----------|
| Desktop First Impression | 9.0 | - | DONE |
| Landing Page | 8.2 | +0.8 | Medium |
| Quote Sharing | 8.2 | +0.8 | Medium |
| Settings | 7.8 | +1.2 | Medium |
| Dashboard | 7.5 | +1.5 | High |
| Invoicing | 7.5 | +1.5 | High |
| Blog/SEO | 7.2 | +1.8 | Medium |
| Tasks | 6.8 | +2.2 | High |
| CRM | 6.5 | +2.5 | High |
| Mobile Experience | 6.5 | +2.5 | **Critical** |
| Auth Flow | 6.5 | +2.5 | **Critical** |
| Demo Flow | 6.5 | +2.5 | **Critical** |
| Learning System | 6.5 | +2.5 | **Critical** |

---

## Critical Priority (6.5 → 9.0)

### 1. Mobile Experience (+2.5 points needed)

**Current**: Touch targets fail WCAG 2.5.5 (78% below 44px minimum)

| Fix | Impact |
|-----|--------|
| Add 44px minimum touch targets to nav links | +0.8 |
| Add 375px breakpoint to all pages | +0.6 |
| Convert nav to hamburger menu on mobile | +0.4 |
| Fix example chips (currently 0x0px) | +0.4 |
| Add proper mobile form styling | +0.3 |

**Deliverable**: Single PR with mobile CSS overhaul

---

### 2. Auth Flow (+2.5 points needed)

**Current**: Two different signup paths with inconsistent legal exposure

| Fix | Impact |
|-----|--------|
| Add Terms/Privacy links to `/start` signup form | +1.0 |
| Unify signup flow (remove duplicate paths) | +0.6 |
| Add password strength indicator | +0.3 |
| Add "remember me" option | +0.3 |
| Add social login (Google OAuth) | +0.3 |

**Deliverable**: Merge `/start` and `/app` into single unified auth flow

---

### 3. Demo Flow (+2.5 points needed)

**Current**: Demo page was animation-only (now deleted). Real demo exists via `/try` but needs polish.

| Fix | Impact |
|-----|--------|
| Connect demo to real backend API (already done) | +0.8 |
| Add voice recording support to demo | +0.6 |
| Add PDF download with DEMO watermark | +0.4 |
| Add edit quote capability in demo | +0.4 |
| Add "What happens next" CTA after demo | +0.3 |

**Deliverable**: `/try` page is full product demo with real AI

---

### 4. Learning System (+2.5 points needed)

**Current**: Quality scoring exists but wasn't persisted (now fixed). Outcome learning not implemented.

| Fix | Impact |
|-----|--------|
| Persist quality scores with learnings (DONE) | +0.6 |
| Add outcome learning (win/loss tracking) | +0.8 |
| Add learning transparency UI ("Why this price?") | +0.5 |
| Add cross-category pattern transfer | +0.3 |
| Add learning quality dashboard for user | +0.3 |

**Deliverable**: Learning system becomes visible, explainable moat

---

## High Priority (6.8-7.5 → 9.0)

### 5. Tasks System (6.8 → 9.0)

| Fix | Impact |
|-----|--------|
| Wire up reminder_time UI (currently dead code) | +0.8 |
| Add task completion tracking | +0.4 |
| Add recurring tasks | +0.4 |
| Add task templates | +0.3 |
| Add task-to-quote linking | +0.3 |

---

### 6. CRM System (6.5 → 9.0)

| Fix | Impact |
|-----|--------|
| Display loyalty tier badges on customer cards | +0.6 |
| Add customer activity timeline | +0.5 |
| Add quote history per customer | +0.4 |
| Add customer notes/tags | +0.4 |
| Add dormant customer reactivation prompts | +0.3 |
| Add customer merge (deduplication UI) | +0.3 |

---

### 7. Dashboard (7.5 → 9.0)

| Fix | Impact |
|-----|--------|
| Add outstanding invoices widget | +0.5 |
| Add quote win rate metrics | +0.4 |
| Add learning accuracy trending | +0.3 |
| Add quick actions (new quote, new customer) | +0.2 |
| Add recent activity feed | +0.1 |

---

### 8. Invoicing (7.5 → 9.0)

| Fix | Impact |
|-----|--------|
| Fix invoice share link 404 (CRITICAL) | +0.6 |
| Add outstanding invoices dashboard | +0.4 |
| Add payment reminder automation | +0.3 |
| Add partial payment support | +0.2 |

---

## Medium Priority (7.2-8.2 → 9.0)

### 9. Landing Page (8.2 → 9.0)

| Fix | Impact |
|-----|--------|
| Add testimonials + customer logos to hero | +0.4 |
| Fix video loading issue | +0.2 |
| Add pricing comparison table | +0.2 |

---

### 10. Quote Sharing (8.2 → 9.0)

| Fix | Impact |
|-----|--------|
| Add share link expiration option | +0.3 |
| Send rejection notification regardless of reason | +0.3 |
| Add viewed/opened tracking | +0.2 |

---

### 11. Settings (7.8 → 9.0)

| Fix | Impact |
|-----|--------|
| Add quote defaults preview | +0.4 |
| Expand Pricing Brain to show 4+ rules per category | +0.3 |
| Add "export my data" option | +0.2 |
| Add notification preferences | +0.3 |

---

### 12. Blog/SEO (7.2 → 9.0)

| Fix | Impact |
|-----|--------|
| Add og:image tags (1200x630) to all articles | +0.5 |
| Add internal cross-links (3-5 per article) | +0.4 |
| Wire up category filters (currently non-functional) | +0.3 |
| Add article read time | +0.2 |
| Add related articles sidebar | +0.4 |

---

## Summary: Effort to Reach 9/10 Everywhere

| Tier | Areas | Est. Effort |
|------|-------|-------------|
| **Critical** | Mobile, Auth, Demo, Learning | 2-3 weeks |
| **High** | Tasks, CRM, Dashboard, Invoicing | 2 weeks |
| **Medium** | Landing, Sharing, Settings, Blog | 1 week |

**Total Estimated Effort**: 5-6 weeks of focused development

**Recommended Order**:
1. Week 1-2: Mobile + Auth (legal risk, accessibility lawsuit risk)
2. Week 2-3: Learning + Demo (competitive moat, conversion)
3. Week 3-4: CRM + Tasks + Dashboard (user retention)
4. Week 4-5: Invoicing + Sharing (revenue)
5. Week 5-6: Landing + Settings + Blog (growth)

---

## Quick Wins (Can ship in 1 day each)

1. Add Terms/Privacy to `/start` form
2. Add loyalty tier badges to CRM cards
3. Add outstanding invoices widget
4. Send rejection emails regardless of reason
5. Add og:image tags to blog articles

---

## Already Fixed in This Session

1. ~~Demo animation artifact~~ → **DELETED** (frontend/demo.html removed)
2. ~~Learning quality not persisted~~ → **FIXED** (metadata now stored with quality scores)
