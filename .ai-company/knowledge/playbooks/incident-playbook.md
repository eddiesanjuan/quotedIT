# Incident Response Playbook

## Severity Definitions

| Level | Definition | Response Time | Notification |
|-------|------------|---------------|--------------|
| **P1 (CRITICAL)** | Complete outage, data loss risk, security breach | 5 min | SMS + immediate escalation |
| **P2 (HIGH)** | Major feature broken, payment issues, significant errors | 30 min | Email + Slack |
| **P3 (MEDIUM)** | Degraded performance, minor feature broken | 4 hours | Email |
| **P4 (LOW)** | Cosmetic issues, warnings | 24 hours | Log only |

## Incident Response Flow

```
Incident Detected
    │
    ├─> Classify severity (P1-P4)
    │
    ├─> P1 CRITICAL:
    │       1. Immediate SMS to Eddie
    │       2. Create incident record
    │       3. Gather diagnostics
    │       4. Prepare rollback if recent deployment
    │       5. Draft status update for users
    │
    ├─> P2 HIGH:
    │       1. Create incident record
    │       2. Email notification
    │       3. Gather diagnostics
    │       4. Prepare fix PR (don't merge)
    │       5. Queue for approval
    │
    ├─> P3 MEDIUM:
    │       1. Create ticket
    │       2. Gather diagnostics
    │       3. Schedule fix for next work session
    │
    └─> P4 LOW:
            1. Log in weekly review
            2. No immediate action
```

## Common Incidents

### 1. API Down / 500 Errors

**Detection**: Error rate > 5%, multiple 500s in logs

**Immediate Steps**:
1. Check Railway deployment status
2. Check recent commits
3. Check database connection
4. Check external service status (Stripe, Resend, Claude)

**Diagnostic Commands**:
```bash
# Check Railway logs
railway logs -n 500 --filter "@level:error"

# Check deployment
railway status

# Check database
railway logs -n 100 --filter "database OR postgres"
```

**Likely Causes**:
- Recent deployment introduced bug
- Database connection pool exhausted
- External API down
- Environment variable missing/changed

**Resolution**:
- If recent deploy: Prepare rollback PR
- If database: Check connection limits
- If external API: Wait for recovery, notify users

---

### 2. Quote Generation Failing

**Detection**: Multiple failed quote generations, Claude API errors

**Immediate Steps**:
1. Check Claude API status
2. Check for rate limiting
3. Check prompt length (might exceed limits)

**Diagnostic Commands**:
```bash
railway logs -n 200 --filter "claude OR anthropic OR quote"
```

**Likely Causes**:
- Claude API rate limited
- Claude API down
- Prompt exceeded token limit
- API key expired/invalid

**Resolution**:
- If rate limited: Wait, consider caching
- If API down: Show user-friendly error
- If prompt issue: Check for abnormal input

---

### 3. Payment Processing Issues

**Detection**: Stripe webhook errors, failed payments

**Immediate Steps**:
1. Check Stripe dashboard
2. Check webhook delivery
3. Check for code changes to billing

**Diagnostic Commands**:
```bash
railway logs -n 200 --filter "stripe OR payment OR billing"
```

**Likely Causes**:
- Webhook signature validation failing
- Stripe API version mismatch
- Subscription handling bug
- Webhook endpoint down

**Resolution**:
- Verify webhook secret matches
- Check Stripe API version
- Review recent billing code changes

---

### 4. Email Delivery Failures

**Detection**: Bounce rate spike, delivery failures

**Immediate Steps**:
1. Check Resend dashboard
2. Check DNS/SPF/DKIM records
3. Check for spam reports

**Diagnostic Commands**:
```bash
railway logs -n 200 --filter "email OR resend OR send"
```

**Likely Causes**:
- DNS misconfiguration
- Sending to invalid addresses
- Rate limited
- Spam reports

**Resolution**:
- Verify DNS records
- Clean email list
- Contact Resend if rate limited

---

### 5. Authentication Issues

**Detection**: Users can't log in, JWT errors

**Immediate Steps**:
1. Check JWT_SECRET_KEY is set
2. Check for recent auth code changes
3. Check magic link email delivery

**Diagnostic Commands**:
```bash
railway logs -n 200 --filter "auth OR jwt OR token OR login"
railway variables | grep JWT
```

**Likely Causes**:
- JWT secret changed
- Token expiration issue
- Cookie settings wrong
- Magic link emails not sending

**Resolution**:
- Verify JWT secret
- Check token expiration settings
- Test magic link flow

---

### 6. Slow Performance

**Detection**: Response times > 1s, user complaints

**Immediate Steps**:
1. Check database query times
2. Check external API latency
3. Check memory/CPU usage

**Diagnostic Commands**:
```bash
railway logs -n 200 --filter "slow OR timeout OR performance"
```

**Likely Causes**:
- N+1 database queries
- Large PDF generation
- Claude API latency
- Database connection exhaustion

**Resolution**:
- Add database indexes
- Optimize queries
- Implement caching
- Increase connection pool

## Rollback Procedure

**Only with Eddie's approval**

```bash
# 1. Identify last good commit
git log --oneline -10

# 2. Create rollback PR
git checkout main
git checkout -b rollback/[incident-id]
git revert [bad-commit]
git push origin rollback/[incident-id]

# 3. Queue for approval
# 4. After approval, merge and Railway auto-deploys
```

## Post-Incident Process

After resolution:

1. **Update incident record** with timeline, root cause, resolution
2. **Create prevention ticket** in DISCOVERY_BACKLOG.md
3. **Update playbook** if new scenario
4. **Send update to affected users** (if appropriate)

## Communication Templates

### User-Facing Status Update
```
Hi,

We're aware of an issue affecting [description]. Our team is actively working on a fix.

Current status: [Investigating / Identified / Fixing / Monitoring]

We'll update you when resolved. Apologies for any inconvenience!

The Quoted Team
```

### Resolution Notification
```
Hi,

The issue affecting [description] has been resolved.

What happened: [Brief non-technical explanation]
Duration: [X] minutes/hours
What we did: [Brief fix description]

Thank you for your patience!

The Quoted Team
```

## Emergency Contacts

| Role | Contact | Method |
|------|---------|--------|
| Eddie (Founder) | [configured in Twilio] | SMS for P1, Email for P2 |
| Railway Support | support@railway.app | Email for platform issues |
| Stripe Support | stripe.com/support | Dashboard + Email |
| Resend Support | support@resend.com | Email |
