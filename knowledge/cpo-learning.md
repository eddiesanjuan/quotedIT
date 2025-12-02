# CPO Learning

**Last Updated**: 2025-12-02
**Purpose**: Product-message fit learnings and claim validation for Quoted

---

## Claim Validation Status

| Claim | Status | Reality | Risk |
|-------|--------|---------|------|
| "30-second quotes" | SOFTENED → "under 2 minutes" | Real UX: 1-3 minutes end-to-end | Overpromise risk |
| "Learns automatically" | APPROVED | Corrections auto-update pricing model | Low risk |
| "Gets smarter every time" | SOFTENED → "with every correction" | Improvements visible after 10-20 quotes | Set expectations |
| "Your gut feeling, systematized" | APPROVED | Onboarding + learning captures intuition | Low risk |
| "Close enough to close the deal" | CUT | Not validated, cold-start accuracy unknown | High risk |
| "Only tool you need" | REJECTED | Sounds limited, not validated for final quotes | High risk |

---

## UX Reality Check

### End-to-End Timing

| Step | Time Range | Notes |
|------|------------|-------|
| Record voice note | 20-60 sec | User variable |
| Whisper transcription | 3-8 sec | Depends on audio length |
| Quote generation (single) | 5-10 sec | |
| Quote generation (3-sample) | 15-30 sec | Confidence mode |
| User review + edits | 30-90 sec | Almost always happens |
| **Total realistic** | **1-3 minutes** | Not 30 seconds |

### Learning Curve Reality

| Quote Range | Expected Edit Rate | Learning Status |
|-------------|-------------------|-----------------|
| 1-5 | 35-45% | Cold start |
| 10-20 | 25-35% | Patterns emerging |
| 50+ | 15-25% | Well-calibrated |

**Key insight**: "Gets smarter every time" implies immediate improvement. Reality is gradual. Message accordingly.

---

## Segment Product Fit

### Segment A (Qualification)
- **Fit**: STRONG
- **Why**: Speed matters more than precision, 70-85% accuracy acceptable
- **Missing**: Mobile app (critical), offline mode, quick comparison to past jobs

### Segment B (Ballpark-Only)
- **Fit**: UNPROVEN
- **Why**: Requires 90%+ accuracy for customer-facing, not validated
- **Missing**: Accuracy transparency, templates, premium PDF polish
- **Risk**: Don't position until beta validates

---

## Product Gaps Identified

| Gap | Priority | Impact | Status |
|-----|----------|--------|--------|
| Mobile app | HIGH | Unlocks field usage | BACKLOG |
| Accuracy transparency (show confidence) | HIGH | Builds trust | BACKLOG |
| Learning progress visibility | MEDIUM | Makes "gets smarter" tangible | BACKLOG |
| Cold-start accuracy boost | MEDIUM | Improves first-run experience | BACKLOG |
| Customer-facing PDF polish | LOW | Enables ballpark-only segment | POST-BETA |

---

## Beta Validation Metrics

### Must Measure

| Metric | Target | Why |
|--------|--------|-----|
| End-to-end time | 90% under 2 min | Validates timing claims |
| Edit rate over time | Decreasing trend | Validates learning claims |
| Cold-start accuracy | <50% edit rate | Validates "close enough" |
| Confidence calibration | High conf = <10% edits | Validates ballpark-only viability |
| Quote sent as-is rate | Track % | Validates segment assumptions |

---

## Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-02 | Soften "30-second" to "under 2 minutes" | Honest about real UX |
| 2025-12-02 | Cut "close enough to close the deal" | Unvalidated, high risk |
| 2025-12-02 | Approve learning claims with softer language | Accurate but gradual |
| 2025-12-02 | Reject "only tool you need" | Sounds limited, needs validation |

---

## Pending Validation

- [ ] What's actual average end-to-end time in beta?
- [ ] Edit rate trend over first 50 quotes per user
- [ ] Cold-start accuracy (first quote with zero corrections)
- [ ] What % send quote to customer as-is?
- [ ] Does confidence score predict accuracy?
