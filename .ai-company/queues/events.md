# Event Queue

Last Updated: 2025-12-29
Pending Events: 0

---

## Unprocessed Events

*No events pending*

---

## Recently Processed

*No events processed yet*

---

## Event Format Reference

Events from the Railway Event Gateway follow this format:

```markdown
### EVT-YYYY-NNNN
- **Source**: stripe | resend | posthog | app
- **Type**: charge.succeeded | email.delivered | etc.
- **Urgency**: critical | high | normal | low
- **Received**: ISO timestamp
- **Status**: pending | processing | processed | failed

**Payload Summary**:
Key information from the webhook payload.

**Routing**:
- Assigned to: Support | Ops | Growth | Finance
- Processing started: timestamp or -
- Processing completed: timestamp or -

**Outcome**:
What happened when this event was processed.
```

---

## Event Statistics

| Source | Today | This Week | This Month |
|--------|-------|-----------|------------|
| Stripe | 0 | 0 | 0 |
| Resend | 0 | 0 | 0 |
| PostHog | 0 | 0 | 0 |
| App | 0 | 0 | 0 |
| **Total** | 0 | 0 | 0 |

## Urgency Distribution

| Urgency | Count | % |
|---------|-------|---|
| Critical | 0 | 0% |
| High | 0 | 0% |
| Normal | 0 | 0% |
| Low | 0 | 0% |
