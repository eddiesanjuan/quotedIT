# Starting a Session with Quoted, Inc.

**Purpose**: This guide explains how to resume working with the AI company after a session ends (Cursor crash, terminal closes, etc.)

---

## Quick Start

When you start a new Claude Code session and want to work on Quoted:

1. **Navigate to the project directory**:
   ```bash
   cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant/quoted
   ```

2. **Say one of these to activate the company**:
   - "Start the company"
   - "What's the status?"
   - "Run the company"

3. **Claude will automatically**:
   - Read all state files (COMPANY_STATE.md, ENGINEERING_STATE.md, etc.)
   - Check `/api/issues/new` for pending user issues
   - Summarize status and recommend priorities
   - Ask what you want to focus on

---

## State Files (Company Memory)

The company maintains context through these files:

| File | Purpose | Claude Reads On Start |
|------|---------|----------------------|
| `COMPANY_STATE.md` | Overall status, org structure, strategic priorities | Yes |
| `ENGINEERING_STATE.md` | Sprint tracking, deployments, tech debt | Yes |
| `SUPPORT_QUEUE.md` | User issues, tickets, SLAs | Yes |
| `PRODUCT_STATE.md` | Roadmap, feature backlog, user research | Yes |
| `METRICS_DASHBOARD.md` | KPIs, metrics, alerts | Yes |
| `AUTONOMOUS_OPERATIONS.md` | How the company runs itself | Reference |

---

## Production Deployment

**Live URLs**:
- **Custom Domain**: https://quoted.it.com (once SSL provisions)
- **Railway Direct**: https://web-production-0550.up.railway.app

**Railway Dashboard**: https://railway.app/dashboard

---

## Environment Variable Required

**IMPORTANT**: Set this in Railway for security features to work:

1. Go to Railway Dashboard → Your Quoted project
2. Click on the web service
3. Go to **Variables**
4. Add: `ENVIRONMENT=production`

This enables:
- HTTPS redirects
- CORS restrictions (only quoted.it.com allowed)
- Rate limiting is active

---

## SSL Certificate (Security Warning Fix)

If you see a security warning at quoted.it.com:

1. **Wait 5-10 minutes** - Railway auto-provisions SSL via Let's Encrypt
2. **Check Railway dashboard** - Look for green checkmark on custom domain
3. **Force refresh** - Clear browser cache and retry with https://

If SSL still doesn't work after 30 minutes:
- Check DNS is pointing correctly (CNAME to Railway URL)
- Contact Railway support

---

## Deploying Changes

The company deploys automatically on git push to main:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

Railway will auto-deploy within 2-3 minutes.

---

## If Something Breaks

1. **Check Railway dashboard** for deployment status
2. **Check Railway logs** for errors
3. **Rollback if needed**: `git revert HEAD && git push`
4. **Create an issue**: The company will fix it next session

---

## Decision Authority (What Claude Can Do)

| Type | Examples | Claude's Authority |
|------|----------|-------------------|
| **Type 1** | Bug fixes, documentation | Just does it |
| **Type 2** | Backlog features, refactoring | Does it, reports after |
| **Type 3** | Architecture changes, new integrations | Proposes first, waits for approval |
| **Type 4** | Pricing, external commitments | Always asks you |

---

## Example Session Starts

**Scenario 1: Daily check-in**
```
You: "Status?"
Claude: [Reads state files, checks issues, summarizes]
"Quoted, Inc. is BETA-READY. No pending issues.
DNS configured, SSL pending.
Recommend: Test the full user flow today."
```

**Scenario 2: You have a specific task**
```
You: "Add a feature to save favorite quotes"
Claude: [Assesses as Type 2, implements directly]
```

**Scenario 3: Strategic question**
```
You: "Should we integrate with QuickBooks?"
Claude: [Type 3 - proposes approach first]
"I'd recommend this architecture... Want me to proceed?"
```

---

## Key Contacts

- **Founder**: Eddie (you) - Type 4 decisions, spending, credentials
- **AI Company**: Claude - Everything else within authority

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Claude doesn't know context | Say "Read the state files" or start with "Status?" |
| Changes not deploying | Check Railway dashboard, verify git push succeeded |
| API errors | Check Railway logs, run `curl https://quoted.it.com/health` |
| SSL warning persists | Wait longer, or check DNS configuration |

---

**Last Updated**: 2025-12-01
