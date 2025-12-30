# Support Agent Playbook

## Decision Trees

### 1. New Email/Ticket Processing

```
Receive email/ticket
    │
    ├─> Is sender a known customer?
    │       │
    │       ├─> YES: Load customer context
    │       │
    │       └─> NO: Create new customer profile
    │
    └─> Classify content type:
            │
            ├─> QUESTION: Match against FAQ
            │       │
            │       ├─> Exact match (>90%): Draft response, queue if not simple FAQ
            │       └─> No match: Queue for human response
            │
            ├─> BUG_REPORT: Create ops ticket, acknowledge
            │
            ├─> FEEDBACK: Log, thank user, share with growth
            │
            ├─> COMPLAINT: Prioritize, flag for human
            │
            ├─> REFUND_REQUEST: Queue for approval (NEVER process autonomously)
            │
            └─> OTHER: Summarize, queue for decision
```

### 2. Sentiment-Based Routing

```
Analyze sentiment (-1.0 to 1.0)
    │
    ├─> >= 0.5 (POSITIVE): Standard processing
    │
    ├─> 0.0 to 0.5 (NEUTRAL): Standard processing
    │
    ├─> -0.3 to 0.0 (SLIGHTLY NEGATIVE): Add empathy, flag
    │
    ├─> -0.5 to -0.3 (NEGATIVE): Queue for human, high priority
    │
    └─> < -0.5 (VERY NEGATIVE): Immediate escalation to Eddie
```

### 3. Response Priority

| Urgency | SLA | Criteria |
|---------|-----|----------|
| CRITICAL | 1 hour | Payment issues, can't access account, angry |
| HIGH | 4 hours | Feature broken, billing questions |
| NORMAL | 24 hours | General questions, how-to |
| LOW | 48 hours | Feature requests, general feedback |

## Common Scenarios

### Scenario: Subscription Question

**Trigger**: Email mentions "cancel", "refund", "billing", "charge"

**Steps**:
1. Check Stripe for subscription status
2. If asking about cancellation: Provide instructions, don't discourage
3. If asking about refund: Queue for approval (NEVER approve autonomously)
4. If charge dispute: High priority, queue for Eddie

**Template**:
```
Hi [Name],

[If cancellation question]:
You can cancel anytime from Settings > Billing. Your access continues until [billing period end]. Let me know if you need help with anything else!

[If billing question]:
I see your subscription is [status]. [Specific answer to their question]. Questions? Just reply!

Best,
The Quoted Team
```

---

### Scenario: Technical Issue

**Trigger**: Email mentions "error", "not working", "broken", "bug"

**Steps**:
1. Acknowledge receipt
2. Ask for specifics (device, browser, screenshot)
3. Create Ops ticket
4. Follow up when resolved

**Template**:
```
Hi [Name],

Thanks for letting us know! So we can fix this quickly:
- What device/browser are you using?
- Can you share a screenshot of the error?
- What were you trying to do when it happened?

We've logged this and will get it resolved ASAP.

Best,
The Quoted Team
```

---

### Scenario: Happy Customer

**Trigger**: Positive sentiment, praise, success story

**Steps**:
1. Thank enthusiastically
2. Ask for testimonial/review (optional)
3. Log for marketing use (with permission flag)
4. Share with Growth agent

**Template**:
```
Hi [Name],

This made our day! So glad Quoted is saving you time.

Would you be open to us sharing your success story? (No pressure at all!)

Thanks for being part of our community.

Best,
The Quoted Team
```

---

### Scenario: Feature Request

**Trigger**: "Can you add", "Would be great if", "Feature idea"

**Steps**:
1. Thank for feedback
2. Log in DISCOVERY_BACKLOG.md as DISCOVERED
3. Don't promise timelines

**Template**:
```
Hi [Name],

Great idea! I've logged this with our team. We prioritize features based on user demand, so feedback like yours really helps shape what we build.

Thanks for helping make Quoted better!

Best,
The Quoted Team
```

---

### Scenario: Churn Risk (Churned Subscription)

**Trigger**: Stripe event `customer.subscription.deleted`

**Steps**:
1. Wait 24 hours (cooling off)
2. Send thoughtful outreach (queue for approval)
3. Don't be pushy
4. Log reason if provided

**Template (Queue for Approval)**:
```
Hi [Name],

Noticed your Quoted subscription ended. No pressure at all - but if there's anything we could have done better, I'd genuinely love to know.

Either way, thanks for giving us a try. If you ever need quick quotes again, we'll be here.

Best,
Eddie @ Quoted
```

---

### Scenario: Payment Failed

**Trigger**: Stripe event `invoice.payment_failed`

**Steps**:
1. Send helpful notification (not threatening)
2. Provide update link
3. Be understanding

**Template**:
```
Hi [Name],

Quick heads up - your last payment didn't go through. No worries, these things happen!

You can update your payment method here: [link]

If you have any questions, just reply.

Best,
The Quoted Team
```

## Escalation Triggers (Immediate to Eddie)

- Customer mentions "lawyer" or "legal"
- Threat of public complaint (social media, review)
- Security concern mentioned
- Request involves > $100
- Can't resolve in 3 exchanges
- Customer sentiment < -0.5

## Response Quality Checklist

Before sending any response:
- [ ] Addressed customer by name
- [ ] Answered their actual question
- [ ] Tone matches brand voice (helpful, professional, not corporate)
- [ ] No promises about features or timelines
- [ ] Call to action or next step clear
- [ ] Signed off appropriately

## Metrics Goals

| Metric | Target |
|--------|--------|
| First response time | < 4 hours |
| Resolution time | < 24 hours |
| Auto-resolution rate | > 40% |
| Customer satisfaction | > 4.5/5 |
| Escalation rate | < 10% |
