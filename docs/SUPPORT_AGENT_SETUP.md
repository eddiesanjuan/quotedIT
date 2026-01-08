# Support Agent Infrastructure Setup

**DISC-160**: File-based support queue for automated customer communication handling.

## Overview

The Support Agent receives incoming customer emails via Resend webhooks, classifies them using Claude, and queues them for processing. This document describes how to configure the infrastructure.

## Architecture

```
Customer → Email → Resend → Webhook → FastAPI → Classification → inbox.md
                                              ↓
                                          Support Agent
                                              ↓
                                      (Future: Auto-responses)
```

## Components

### 1. Webhook Endpoint

**Location**: `backend/api/webhooks.py`

**Route**: `POST /api/webhooks/resend`

**Handles**:
- `email.received` - Incoming customer emails (queued to inbox.md)
- `email.delivered` - Outbound email tracking
- `email.bounced` - Bounce notifications
- `email.complained` - Spam complaints

### 2. Support Service

**Location**: `backend/services/support.py`

**Functions**:
- `classify_email()` - Uses Claude to analyze sentiment, urgency, type
- `should_escalate()` - Determines if founder review is needed
- `update_inbox_with_classification()` - Updates inbox.md with AI analysis

### 3. File-Based Queue

**Location**: `.ai-company/agents/support/inbox.md`

**Structure**:
```markdown
# Support Agent Inbox

## Queue Status
- Unprocessed: N
- Processing: N
- Escalated: N

---

## Email Received: 2026-01-07 19:00 UTC

**From**: Customer Name <customer@example.com>
**Subject**: Help with quote generation
**Message ID**: msg-abc123
**Status**: UNPROCESSED

**Body**:
```
I need help creating a quote for a bathroom remodel.
```

**Agent Notes**:
- Classification: question
- Urgency: normal
- Sentiment: 0.2
- Summary: Customer needs help with bathroom remodel quote
- Confidence: 0.85
- Escalate: False
```

## Setup Instructions

### Step 1: Configure Resend Webhook

1. **Log in to Resend Dashboard**: https://resend.com/domains

2. **Navigate to Webhooks**:
   - Go to Settings → Webhooks
   - Click "Add Webhook"

3. **Configure Webhook**:
   - **Endpoint URL**: `https://quoted.it.com/api/webhooks/resend`
   - **Events to subscribe**:
     - ✅ `email.received` (CRITICAL - this is the incoming email event)
     - ✅ `email.delivered`
     - ✅ `email.bounced`
     - ✅ `email.complained`
   - Click "Create Webhook"

4. **Copy Webhook Secret** (optional but recommended):
   - Resend will show a webhook signing secret
   - Copy this secret
   - Add to Railway environment variables:
     ```
     RESEND_WEBHOOK_SECRET=<your-secret>
     ```
   - This enables signature verification for security

### Step 2: Configure Email Forwarding

To receive incoming customer emails:

1. **Set up email forwarding** in your email provider:
   - Forward `support@quoted.it.com` → Resend inbound address
   - Resend will provide an inbound email address (format: `xxx@inbound.resend.dev`)

2. **Or configure Resend domains**:
   - Add `quoted.it.com` as a verified domain in Resend
   - Configure MX records to receive email directly via Resend
   - See: https://resend.com/docs/dashboard/domains/introduction

### Step 3: Verify Setup

1. **Send a test email** to `support@quoted.it.com`

2. **Check inbox.md** was created:
   ```bash
   cat .ai-company/agents/support/inbox.md
   ```

3. **Verify classification** ran:
   - inbox.md should show Agent Notes with classification
   - Check Railway logs: `railway logs -n 100 | grep "support"`

4. **Test webhook endpoint** directly (optional):
   ```bash
   curl -X POST https://quoted.it.com/api/webhooks/resend \
     -H "Content-Type: application/json" \
     -d '{
       "type": "email.received",
       "data": {
         "from": {"email": "test@example.com", "name": "Test"},
         "to": [{"email": "support@quoted.it.com"}],
         "subject": "Test",
         "text": "Test body",
         "message_id": "test-123",
         "created_at": "2026-01-07T12:00:00Z"
       }
     }'
   ```

## Classification Rules

The Support Service classifies emails into:

### Type
- **question** - Customer asking how to do something
- **bug_report** - Something isn't working correctly
- **feedback** - General feedback or feature request
- **complaint** - Customer is upset or dissatisfied
- **refund** - Requesting a refund or cancellation
- **other** - Doesn't fit other categories

### Urgency
- **critical** - Service down, data loss, urgent business need
- **high** - Blocking work, time-sensitive issue
- **normal** - Standard inquiry or issue
- **low** - Nice-to-have, general question

### Sentiment Scale (-1.0 to 1.0)
- `1.0` - Very positive, happy customer
- `0.5` - Somewhat positive
- `0.0` - Neutral
- `-0.3` - Slightly frustrated
- `-0.5` - Upset or disappointed
- `-1.0` - Very angry or hostile

## Escalation Rules

Emails automatically escalate to founder review if:

| Condition | Threshold | Reason |
|-----------|-----------|--------|
| Very negative sentiment | ≤ -0.5 | Immediate founder notification |
| Negative sentiment | < -0.3 | Requires human review |
| Refund request | Any | Always escalate |
| Critical urgency | Any | Immediate attention needed |
| Low confidence | < 0.7 | Human review recommended |

## Agent Autonomy Boundaries

**Can Do Autonomously** (future features):
- Send acknowledgment emails
- Answer questions matching FAQ >90% confidence
- Create internal tickets for reported issues
- Classify and prioritize requests
- Update customer context notes

**Must Queue for Approval**:
- Any substantive response to customer
- Responses to upset customers
- Refund requests
- Discount or pricing discussions
- Feature commitments or timelines

**Never**:
- Make promises about features
- Share other customers' information
- Provide legal advice
- Process refunds without approval

## Security

### Webhook Signature Verification

If `RESEND_WEBHOOK_SECRET` is configured, the endpoint verifies the `svix-signature` header to ensure requests come from Resend.

**Without signature verification**: Webhook is still functional but less secure (dev mode).

**With signature verification**: Unauthorized requests are rejected with 401.

### Rate Limiting

Rate limiting should be configured at the infrastructure level (Railway, Cloudflare, etc.) to prevent webhook abuse.

Recommended: 100 requests/minute per IP.

## Monitoring

### Logs to Watch

```bash
# View webhook activity
railway logs --filter "Received Resend webhook"

# View classification activity
railway logs --filter "Classified email"

# View escalations
railway logs --filter "requires escalation"

# View errors
railway logs --filter "@level:error" --filter "webhook"
```

### Metrics to Track (future)

- Emails received per day
- Classification confidence average
- Escalation rate
- Response time (when auto-response is implemented)

## Troubleshooting

### Emails not appearing in inbox.md

**Possible causes**:
1. Resend webhook not configured correctly
   - Check webhook is enabled in Resend dashboard
   - Verify endpoint URL is correct
2. Email forwarding not set up
   - Test by checking Resend inbound logs
3. File permissions issue
   - Check `.ai-company/agents/support/` directory exists and is writable

**Diagnostic**:
```bash
# Check Railway logs for webhook calls
railway logs --filter "resend_webhook" -n 100

# Check if inbox.md exists
ls -la .ai-company/agents/support/inbox.md

# Check file contents
cat .ai-company/agents/support/inbox.md
```

### Classification failing

**Possible causes**:
1. `ANTHROPIC_API_KEY` not configured
   - Check Railway environment variables
2. Claude API rate limit reached
   - Check logs for 429 errors
3. Invalid JSON response from Claude
   - This should fall back to default classification

**Fallback behavior**: If classification fails, email is still added to inbox with default values (type: other, urgency: normal, sentiment: 0.0).

### Webhook signature verification failing

**Possible causes**:
1. `RESEND_WEBHOOK_SECRET` is incorrect
   - Re-copy from Resend dashboard
   - Update Railway env var
2. Resend not sending signature header
   - Signature is optional; remove `RESEND_WEBHOOK_SECRET` to disable verification

## Future Enhancements

**Phase 2** (not yet implemented):
- Auto-responses for high-confidence FAQ matches
- Sentiment trend tracking
- Customer thread management
- Integration with Support Agent autonomous processing

See `.ai-company/agents/support/AGENT.md` for full agent specification.

## Testing

Run the test suite:

```bash
cd /path/to/quoted
python3 -m pytest backend/tests/test_support_webhook.py -v
```

Tests cover:
- Webhook payload validation
- Inbox.md file creation
- Classification logic
- Escalation rules
- Error handling

## References

- **Agent Spec**: `.ai-company/agents/support/AGENT.md`
- **Resend Webhook Docs**: https://resend.com/docs/api-reference/webhooks
- **Railway Docs**: https://docs.railway.app
