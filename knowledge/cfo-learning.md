# CFO Learning

**Last Updated**: 2025-12-02
**Purpose**: Financial learnings, unit economics, and pricing strategy for Quoted

---

## Current Pricing Structure

| Tier | Monthly | Annual | Quotes/mo | Overage | Target Segment |
|------|---------|--------|-----------|---------|----------------|
| Starter | $29 | $290 | 75 | $0.50 | Solo contractors |
| Pro | $49 | $490 | 200 | $0.35 | Growing businesses |
| Team | $79 | $790 | 500 | $0.25 | Small firms |

**Trial**: 7 days, 75 quotes
**Referral**: +7 days both parties

---

## Unit Economics

### Cost Structure
| Item | Current | 3x Stress |
|------|---------|-----------|
| Cost per quote | $0.02-0.03 | $0.06-0.09 |
| Whisper | ~$0.006/min | |
| Claude Sonnet | ~$0.015-0.02 | |

### Margin by Tier
| Tier | Current Margin | 3x Stress Margin |
|------|---------------|------------------|
| Starter (75 quotes) | 92-95% | 77% |
| Pro (200 quotes) | 88-92% | 63% |
| Team (500 quotes) | 81-88% | 43% |

**Key insight**: Even at 3x API pricing, all tiers remain profitable.

---

## Segment Economics (From Audit)

### Segment A (Qualification-focused)
| Metric | Estimate |
|--------|----------|
| Quotes/month | 15-40 |
| Likely tier | Starter |
| Cap utilization | 20-53% |
| Overage rate | <10% |
| Monthly margin | $27-28 |
| 12-month LTV | $332-344 |
| LTV:CAC | **9.5x** |

### Segment B (Ballpark-only)
| Metric | Estimate |
|--------|----------|
| Quotes/month | 80-250 |
| Likely tier | Pro/Team |
| Cap utilization | 75-125%+ |
| Overage rate | 40-60% |
| Monthly margin | $44-60 |
| 12-month LTV | $534-726 |
| LTV:CAC | **17.8x** |

**Key insight**: Segment B is nearly 2x more profitable due to higher volume driving overage revenue.

---

## Financial Risks Identified

| Risk | Severity | Mitigation |
|------|----------|------------|
| Segment B cap friction → churn | HIGH | Proactive upgrade prompts at 50 quotes |
| Segment A underutilization → low perceived value | MEDIUM | Emphasize time savings, not quote volume |
| Heavy users hitting caps | LOW | Overage pricing protects margins |
| API price increases | LOW | Stress-tested to 3x, still profitable |

---

## Opportunities Identified

| Opportunity | Revenue Impact | Timing |
|-------------|----------------|--------|
| Volume tier ($149, 1500 quotes) | +89% per heavy user | Post-beta if demand |
| Segment B natural upgrades | Higher LTV | Built-in |
| Overage revenue from Segment B | +$120-420/yr per user | Automatic |
| Segment-specific pricing | Risk: complexity | Test in beta |

---

## Metrics to Track

### Core Economics (Weekly)
| Metric | Segment A Target | Segment B Target |
|--------|------------------|------------------|
| Avg quotes/month | 20-40 | 100-200 |
| Tier distribution | 80% Starter | 50% Pro, 20% Team |
| Overage rate | <10% | 40-60% |
| Avg revenue/user | $29-35 | $55-85 |
| Gross margin | >92% | >85% |

### Retention & Growth (Monthly)
| Metric | Segment A | Segment B |
|--------|-----------|-----------|
| 30-day retention | 60-70% | 75-85% |
| Tier upgrade rate | 5-10% | 30-40% |
| LTV:CAC | >5x | >10x |

---

## Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-02 | Keep current pricing structure | Works for both segments |
| 2025-12-02 | Keep usage caps | Protects margins, overages = profit |
| 2025-12-02 | Add upgrade prompts at 50 quotes | Prevent surprise overages (churn) |
| 2025-12-02 | Target 50/50 beta split | Validate economics for both |

---

## Pending Validation

- [ ] Actual quote volume by segment in beta
- [ ] Overage revenue as % of total
- [ ] Churn rate by segment at 30/60/90 days
- [ ] Upgrade rate from Starter → Pro
- [ ] CAC by acquisition channel
