# Support Agent Inbox

Last Updated: 2025-12-29

## Pending Items

*No items in inbox*

---

## Item Format Reference

```markdown
### SUP-YYYY-NNNN
- **Received**: ISO timestamp
- **Source**: email | ticket | feedback | review
- **Priority**: critical | high | normal | low
- **Sentiment**: X.X (-1.0 to 1.0)

**From**: Customer name <email>
**Subject**: [subject or topic]

**Content**:
[Full message or summary]

**Customer Context**:
- Subscription: plan, tenure
- Usage: quotes created, last activity
- History: previous tickets, sentiment trend

**Classification**:
- Type: question | bug_report | feedback | complaint | refund | other
- FAQ Match: yes/no (confidence X%)
- Suggested Playbook: [link]

**Status**: pending | processing | drafted | escalated
```
