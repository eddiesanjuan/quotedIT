# Emergency Runbook

**Last Updated**: 2025-12-08
**Source**: DISC-073 Staging Environment Brainstorm

This runbook documents procedures for handling production incidents. All Quoted team members should be familiar with these procedures.

---

## Incident Classification

| Priority | Definition | Response Time | Examples |
|----------|------------|---------------|----------|
| **P1 (Critical)** | Production down, all users affected | Immediate | Server 500s, database down, app won't load |
| **P2 (High)** | Major feature broken, some users affected | Within 1 hour | PDF generation fails, voice recording broken, login issues |
| **P3 (Medium)** | Minor issue, workaround available | Within 24 hours | Styling bug, non-critical feature glitch, slow performance |

---

## P1: Production Down

### Symptoms
- https://quoted.it.com returns 5xx error
- Users report "app won't load"
- Railway dashboard shows service unhealthy

### Immediate Actions (0-5 minutes)

1. **Check Railway Status**
   - Go to [Railway Dashboard](https://railway.app)
   - Check if deployment is running
   - Check logs for error messages

2. **Recent Deploy?**
   - If yes → Revert immediately:
   ```bash
   git log --oneline -5  # Find last working commit
   git revert HEAD --no-edit  # Revert most recent commit
   git push origin main  # Railway auto-deploys
   ```

3. **Check External Services**
   - Database: Railway Postgres status
   - Stripe: dashboard.stripe.com/status
   - Resend: resend.com/status
   - Claude API: anthropic.com/status

4. **Check Sentry**
   - Go to [Sentry Dashboard](https://sentry.io)
   - Look for new error spikes
   - Identify error type and stack trace

### If Database Issue

1. **Check Railway Postgres**
   - Railway Dashboard → Database → Check metrics
   - If connections maxed: Railway may need service restart

2. **Restore from Backup** (last resort)
   - Railway Dashboard → Database → Backups
   - Click most recent backup → Restore
   - **WARNING**: Restores take 5-30 minutes depending on DB size

### Notification

- Text Eddie: "[P1] quoted.it.com is down. [Brief description]. Working on fix."
- If resolved: "[P1 RESOLVED] Issue: [X]. Root cause: [Y]. Prevention: [Z]"

---

## P2: Feature Broken

### Symptoms
- Specific feature returns errors
- Users report "X doesn't work"
- Sentry shows isolated errors (not site-wide)

### Immediate Actions (0-10 minutes)

1. **Is it behind a feature flag?**
   - Go to [PostHog Dashboard](https://app.posthog.com)
   - Search for relevant feature flag
   - **Disable immediately** if flag exists

2. **Check error patterns**
   - Sentry: Filter by feature/endpoint
   - Identify affected user count
   - Determine if it's new code or existing

3. **If no feature flag exists**
   - Assess severity: Is the workaround acceptable?
   - If critical (PDF, quotes, auth): treat as P1
   - If non-critical: create DISC ticket, fix in normal workflow

### Feature Flag Rollback

```bash
# PostHog Dashboard → Feature Flags → [Flag Name] → Disable
# Takes effect in ~30 seconds for all users
```

### Common P2 Issues

| Feature | Quick Check | Fix |
|---------|-------------|-----|
| PDF Generation | Check pdf_service.py logs | Often type issues, restart usually helps |
| Voice Recording | Browser console errors | Check MediaRecorder API permissions |
| Stripe Billing | Check webhook logs | Verify webhook signatures in settings |
| Magic Link Auth | Check Resend logs | Verify RESEND_API_KEY is set |

---

## P3: Minor Issue

### Symptoms
- Cosmetic bugs
- Non-blocking UX issues
- Performance degradation (not critical)

### Actions

1. **Create Ticket**
   - Add to DISCOVERY_BACKLOG.md as DISCOVERED
   - Include: Problem description, steps to reproduce, severity assessment

2. **No Emergency Action**
   - Do not revert or disable features for P3
   - Fix in normal development workflow

3. **Monitor**
   - Check if issue escalates
   - Watch Sentry for increased error rate

---

## Rollback Procedures

### Option 1: Feature Flag Toggle (Fastest - 30 seconds)

**When**: Feature shipped behind flag, needs to be disabled

```
1. PostHog Dashboard → Feature Flags
2. Search for flag (e.g., "invoicing_enabled")
3. Click flag → Disable
4. Confirm in UI (refresh app to verify)
```

### Option 2: Git Revert (Fast - 5 minutes)

**When**: No feature flag, recent commit caused issue

```bash
# Find bad commit
git log --oneline -10

# Revert it
git revert <commit-hash> --no-edit

# Push (Railway auto-deploys)
git push origin main

# Watch Railway dashboard for green deploy
```

### Option 3: Hard Reset to Known Good State (Last Resort - 10 minutes)

**When**: Multiple commits bad, or unclear which commit

```bash
# Find last known good commit
git log --oneline -20

# Create revert branch
git checkout -b emergency-rollback

# Reset to known good
git reset --hard <good-commit-hash>

# Force push (DANGEROUS - only in emergency)
git push origin main --force

# Railway auto-deploys
```

**⚠️ WARNING**: Force push rewrites history. Only use when no other option.

### Option 4: Railway Backup Restore (Slow - 30+ minutes)

**When**: Database corruption or data loss

```
1. Railway Dashboard → Database service
2. Click "Backups" tab
3. Select most recent backup before incident
4. Click "Restore"
5. Wait for restore to complete
6. Verify data integrity
```

---

## Post-Incident

### Required After Any P1 or P2

1. **Post-Mortem Document**
   - What happened?
   - Timeline of events
   - Root cause analysis
   - Prevention measures

2. **Update ENGINEERING_STATE.md**
   - Add incident to "Recent Incidents" section
   - Note any tech debt created

3. **Create Follow-Up Tickets**
   - Prevention measures as DISC tickets
   - Mark as READY if approved by Eddie

4. **Notify Eddie**
   - Summary of incident
   - Impact (users affected, duration)
   - Prevention plan

---

## Emergency Contacts

| Person | Role | Contact |
|--------|------|---------|
| Eddie | Founder | [Primary phone] |
| Railway Support | Infrastructure | support@railway.app |
| Stripe Support | Billing | stripe.com/support |
| Anthropic | Claude API | support@anthropic.com |

---

## Quick Reference

### Rollback Decision Tree

```
Is there a feature flag?
├── YES → Disable in PostHog (30 sec)
└── NO → Was it the most recent commit?
    ├── YES → git revert HEAD (5 min)
    └── NO → Identify bad commit, git revert <hash>
        └── UNCLEAR → Reset to known good state
```

### Key URLs

- Production: https://quoted.it.com
- Railway: https://railway.app
- PostHog: https://app.posthog.com
- Sentry: https://sentry.io
- Stripe: https://dashboard.stripe.com
