# Metrics Dashboard

**Last Updated**: 2025-12-01 22:45 PST
**Updated By**: COO (AI)

---

## North Star Metric

**Quotes Generated Per Active User Per Week**: -
*No users yet*

---

## Acquisition

| Metric | This Week | Last Week | Trend | Target |
|--------|-----------|-----------|-------|--------|
| Website Visitors | 0 | - | - | 100 |
| Signups | 0 | - | - | 20 |
| Activation Rate | - | - | - | 60% |
| Source: Organic | - | - | - | - |
| Source: Referral | - | - | - | - |
| Source: Direct | - | - | - | - |

*Activation = Completed onboarding + generated first quote*

---

## Engagement

| Metric | This Week | Last Week | Trend | Target |
|--------|-----------|-----------|-------|--------|
| Daily Active Users | 0 | - | - | 5 |
| Weekly Active Users | 0 | - | - | 15 |
| Quotes Generated | 0 | - | - | 50 |
| Quotes per User | - | - | - | 5 |
| Voice vs Text Ratio | - | - | - | 80/20 |
| PDFs Generated | 0 | - | - | 20 |

---

## Quality

| Metric | This Week | Last Week | Trend | Target |
|--------|-----------|-----------|-------|--------|
| Quote Edit Rate | - | - | - | <30% |
| Avg Edit Amount | - | - | - | <15% |
| Confidence Distribution | - | - | - | 70% HIGH |
| Learning Corrections | 0 | - | - | 10+ |
| NPS | - | - | - | 40 |

---

## Operational

| Metric | This Week | Last Week | Trend | Target |
|--------|-----------|-----------|-------|--------|
| Uptime | 100% | - | - | 99.9% |
| Avg Response Time | <500ms | - | - | <300ms |
| Error Rate | 0% | - | - | <1% |
| Support Tickets | 0 | - | - | <5 |
| Avg Resolution Time | - | - | - | <24h |

---

## Revenue (Post-Launch)

| Metric | This Month | Last Month | Trend | Target |
|--------|------------|------------|-------|--------|
| MRR | $0 | - | - | - |
| New Customers | 0 | - | - | - |
| Churn Rate | - | - | - | <5% |
| ARPU | - | - | - | $79 |
| LTV | - | - | - | - |

---

## Funnel Analysis

```
Landing Page Visitors:    0
         ↓ (--%)
Started Onboarding:       0
         ↓ (--%)
Completed Onboarding:     0
         ↓ (--%)
Generated First Quote:    0
         ↓ (--%)
Generated 5+ Quotes:      0
         ↓ (--%)
Paid Conversion:          0
```

---

## Cohort Analysis

| Cohort | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|--------|--------|--------|--------|
| - | - | - | - | - |

*No cohorts yet - awaiting users*

---

## Key Insights

1. **No users yet** - Primary focus: beta recruitment
2. **Product is ready** - All Phase 1 features shipped
3. **DNS pending** - Blocking branded URL access

---

## Alerts

| Alert | Threshold | Current | Status |
|-------|-----------|---------|--------|
| Error Rate High | >5% | 0% | OK |
| Uptime Low | <99% | 100% | OK |
| Support Queue Long | >10 tickets | 0 | OK |

---

## Data Sources

- **User data**: SQLite database (`./data/quoted.db`)
- **Quote data**: SQLite database
- **Error tracking**: Not configured (Sentry planned)
- **Analytics**: Not configured (consider Plausible/Mixpanel)

---

## Metric Definitions

| Metric | Definition |
|--------|------------|
| **Activation** | User completed onboarding AND generated at least 1 quote |
| **Active User** | Generated at least 1 quote in the past 7 days |
| **Edit Rate** | % of quotes that were edited after generation |
| **Confidence** | AI-reported confidence level (HIGH/MEDIUM/LOW) |
| **NPS** | "How likely to recommend?" (0-10), % Promoters - % Detractors |
