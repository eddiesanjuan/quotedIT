# Finance Agent Playbook

## Revenue Tracking

### Daily Revenue Check

```
1. Query Stripe for yesterday's activity
2. Record:
   - New subscriptions (count + MRR added)
   - Churned subscriptions (count + MRR lost)
   - Failed payments (count + at-risk MRR)
   - Successful renewals
3. Update metrics.md
4. Flag anomalies (>20% variance from average)
```

### Key Metrics Definitions

| Metric | Definition | Calculation |
|--------|------------|-------------|
| **MRR** | Monthly Recurring Revenue | Active subscriptions × price (monthly equiv) |
| **ARR** | Annual Recurring Revenue | MRR × 12 |
| **Churn Rate** | Monthly churn percentage | Churned MRR / Starting MRR |
| **Net Revenue** | After refunds and disputes | Gross - refunds - disputes |
| **LTV** | Lifetime Value | Average revenue / churn rate |
| **CAC** | Customer Acquisition Cost | Marketing spend / new customers |

### Revenue Events to Track

| Event | Source | Action |
|-------|--------|--------|
| `customer.subscription.created` | Stripe | +MRR, celebrate |
| `customer.subscription.deleted` | Stripe | -MRR, log reason |
| `invoice.paid` | Stripe | Record payment |
| `invoice.payment_failed` | Stripe | At-risk MRR, trigger follow-up |
| `charge.refunded` | Stripe | -Revenue, log reason |
| `charge.dispute.created` | Stripe | High priority alert |

## Financial Reporting

### Daily Summary Format

```markdown
# Daily Finance Summary - [Date]

## Revenue
- New MRR: $[X] ([N] subscriptions)
- Churned MRR: $[X] ([N] subscriptions)
- Net MRR Change: $[X]

## Payments
- Successful: [N] totaling $[X]
- Failed: [N] totaling $[X] at-risk

## Current State
- Total MRR: $[X]
- Active Subscriptions: [N]
- Trial Users: [N]

## Flags
[Any anomalies or concerns]
```

### Weekly Summary Format

```markdown
# Weekly Finance Report - Week of [Date]

## Summary
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| MRR | $X | $X | +X% |
| New Subs | X | X | +X% |
| Churn | X | X | -X% |
| Net MRR | $X | $X | +X% |

## Revenue Breakdown
- Monthly subscriptions: [N] @ $9 = $[X]
- Annual subscriptions: [N] @ $59/12 = $[X]

## Churn Analysis
| Reason | Count | MRR Lost |
|--------|-------|----------|

## At-Risk
- Failed payments: [N] accounts, $[X] at-risk MRR
- Inactive users (30+ days): [N]

## Projections
- Month-end MRR (projected): $[X]
- YoY Growth Rate: X%

## Action Items
[Recommendations]
```

### Monthly Summary Format

```markdown
# Monthly Finance Report - [Month Year]

## Executive Summary
[2-3 sentences on overall financial health]

## Key Metrics
| Metric | Actual | Target | Status |
|--------|--------|--------|--------|
| MRR | $X | $X | [On track / Below] |
| Growth Rate | X% | X% | |
| Churn Rate | X% | <X% | |
| LTV | $X | $X | |

## Revenue
- Starting MRR: $[X]
- New MRR: +$[X]
- Churned MRR: -$[X]
- Ending MRR: $[X]
- Net Change: $[X] (X%)

## Customer Metrics
- Starting customers: [N]
- New customers: +[N]
- Churned customers: -[N]
- Ending customers: [N]
- Net change: [N]

## Cohort Analysis
| Cohort | Month 1 | Month 2 | Month 3 | Retention |
|--------|---------|---------|---------|-----------|

## Financial Health
- Runway: [X] months at current burn
- Break-even MRR: $[X]
- Days to break-even: [X] (projected)

## Recommendations
[Strategic financial recommendations]
```

## Refund & Dispute Handling

### Refund Request Flow

```
Refund request received
    │
    └─> NEVER process autonomously
        │
        ├─> Create decision queue item:
        │   - Customer context (tenure, usage, history)
        │   - Request reason
        │   - Amount
        │   - Recommendation (approve/deny)
        │
        └─> Wait for Eddie's decision
```

### Refund Recommendation Framework

| Scenario | Recommendation | Reasoning |
|----------|---------------|-----------|
| < 7 days, barely used | Approve | Good faith, minimal loss |
| < 30 days, technical issues | Approve | Our fault |
| < 30 days, "not what expected" | Consider partial | Case by case |
| > 30 days, regular usage | Deny | Got value |
| Longtime customer, issue | Approve + extra month | Retain relationship |

### Dispute Response

**High Priority Alert Triggers**:
- Any charge dispute
- Fraud flag
- Significant refund (>$50)

**Dispute Response Steps**:
1. Gather evidence (usage logs, communications)
2. Prepare Stripe dispute response
3. Queue for Eddie's review
4. Submit response
5. Track outcome

## Cost Tracking

### Known Costs

| Service | Monthly Cost | Billing Cycle |
|---------|--------------|---------------|
| Railway | ~$X | Monthly |
| Resend | ~$X | Usage-based |
| Claude API | ~$X | Usage-based |
| Stripe Fees | 2.9% + $0.30 | Per transaction |
| Domain | ~$X/12 | Annual |

### Cost Anomaly Detection

Flag if any cost exceeds:
- 50% above average for usage-based services
- Any unexpected charges
- New recurring charges

## Cash Flow Projections

### Projection Model

```
Next Month Revenue = Current MRR × (1 - Churn Rate) + Expected New MRR
Next Month Costs = Fixed Costs + Variable Costs × Scale Factor
Next Month Net = Revenue - Costs
```

### Scenarios to Model

| Scenario | Growth | Churn | Use Case |
|----------|--------|-------|----------|
| Base | Current trend | Current avg | Planning |
| Optimistic | 2× growth | Half churn | Best case |
| Pessimistic | Half growth | 2× churn | Stress test |
| Zero Growth | 0 | Current | Runway check |

## Subscription Optimization

### Pricing Insights to Track

- Monthly vs annual split
- Upgrade rate (monthly → annual)
- Price sensitivity signals
- Feature usage by plan

### Recommendations to Generate

Based on data, suggest:
- Optimal pricing changes (with modeling)
- Annual plan promotion timing
- Upgrade incentive campaigns
- At-risk customer interventions

## Compliance & Records

### What to Maintain

- All Stripe events logged
- Revenue calculations documented
- Refund decisions recorded
- Dispute outcomes tracked

### What NOT to Do

- Never access raw payment details
- Never make financial commitments
- Never modify Stripe data directly
- Never provide tax advice
- Never process refunds without approval

## Alert Thresholds

| Event | Threshold | Alert Level |
|-------|-----------|-------------|
| Failed payments | >3 in one day | Medium |
| Churn spike | >2× average | High |
| Revenue drop | >20% WoW | High |
| Dispute filed | Any | Critical |
| Fraud flag | Any | Critical |
| Cost spike | >50% above average | Medium |
