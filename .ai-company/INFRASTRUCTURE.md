# AI Company Infrastructure Briefing

**All agents MUST read this before taking any action.**

---

## Production Stability is Priority #1

Quoted is LIVE at https://quoted.it.com with real paying customers. Every action must preserve production stability. When in doubt, err on the side of safety.

---

## Deployment Workflow

```
Feature Branch → PR → Railway Preview → Verification → Merge → Production
       ↑                      ↑              ↑            ↑
   Your work              Automatic     8-point       Code Agent
                                        checklist     autonomous
```

### How Railway Works

1. **PR Created** → Railway automatically creates a PREVIEW environment
   - Preview URL format: `quoted-pr-{number}.railway.app`
   - Use this for testing BEFORE merge

2. **Verification Protocol** → Code Agent runs 8-point checklist
   - Tests pass, preview healthy, no console errors
   - Feature works, mobile works, no regressions
   - All pass → Merge autonomously
   - Any fail → Escalate to founder

3. **PR Merged** → Railway automatically deploys to PRODUCTION
   - Code Agent can merge verified PRs (Constitution v2.0)
   - Sensitive files (auth, billing) still require human approval

4. **Push to main** → Triggers production deploy
   - This is why we NEVER push directly to main (always use PR workflow)

### Critical Rules

- **NEVER push to main** - Always use feature branches + PRs
- **Code Agent CAN merge** - After passing verification checklist
- **Sensitive files require approval** - auth.py, billing.py, config.py
- **ALWAYS test on preview** - Railway gives you a free staging environment
- **Post-merge monitoring** - Verify production health after deploy

---

## Tool Access

All agents have access to these tools when spawned as subagents:

### GitHub CLI (`gh`)

```bash
# Create PR
gh pr create --title "Title" --body "Description"

# Check PR status
gh pr list
gh pr view {number}

# Check PR checks (CI status)
gh pr checks {number}

# View workflow runs
gh run list
gh workflow run {workflow}.yml

# Create issues
gh issue create --title "Title" --body "Description"
```

**Use for**: Creating PRs, checking CI status, triggering workflows, creating issues.

### Railway CLI (`railway`)

```bash
# View production logs (real-time)
railway logs

# View last N lines
railway logs -n 100

# Filter for errors
railway logs -n 100 --filter "@level:error"

# Check environment variables (read-only)
railway variables

# Check deployment status
railway status

# Open Railway dashboard
railway open
```

**Use for**: Debugging production issues, checking deployment status, viewing logs.

### Playwright Browser Control

Full browser automation via MCP tools:

```
mcp__plugin_playwright_playwright__browser_navigate   # Go to URL
mcp__plugin_playwright_playwright__browser_snapshot   # Get accessibility tree
mcp__plugin_playwright_playwright__browser_click      # Click elements
mcp__plugin_playwright_playwright__browser_type       # Type text
mcp__plugin_playwright_playwright__browser_take_screenshot  # Visual screenshot
mcp__plugin_playwright_playwright__browser_console_messages  # Check for JS errors
mcp__plugin_playwright_playwright__browser_network_requests  # Check API calls
```

**Use for**: E2E testing on Railway preview URLs, visual verification, API testing.

---

## Testing Protocol

### Before Creating Any PR

1. **Run backend tests**: `pytest backend/tests/ -x --tb=short`
2. **Manual smoke test** via Playwright if UI changes
3. **Check for linting errors**

### After PR Created

1. **Wait for Railway preview** (~2-3 minutes)
2. **Test on preview URL** using Playwright
3. **Verify no console errors**
4. **Test mobile viewport** (375px width)
5. **Check API responses** via network requests

### Verification Checklist

```bash
# 1. Check PR preview is deployed
railway status

# 2. Navigate to preview
mcp__plugin_playwright_playwright__browser_navigate(url="https://quoted-pr-{N}.railway.app")

# 3. Get accessibility snapshot
mcp__plugin_playwright_playwright__browser_snapshot()

# 4. Check console for errors
mcp__plugin_playwright_playwright__browser_console_messages(level="error")

# 5. Take evidence screenshot
mcp__plugin_playwright_playwright__browser_take_screenshot()
```

---

## Production Debugging

When investigating production issues:

```bash
# 1. Check current health
railway status

# 2. View recent errors
railway logs -n 200 --filter "@level:error"

# 3. Check specific endpoint
railway logs -n 200 --filter "/api/quotes"

# 4. Check environment
railway variables | grep DATABASE

# 5. Test production directly
mcp__plugin_playwright_playwright__browser_navigate(url="https://quoted.it.com")
mcp__plugin_playwright_playwright__browser_snapshot()
```

---

## Emergency Procedures

### If Production Is Down

1. Check Railway status: `railway status`
2. Check recent deploys: `gh run list`
3. If recent merge caused it: Escalate to founder for rollback
4. Create incident ticket in `.ai-company/incidents/`

### If Tests Are Failing

1. **DO NOT create PR with failing tests**
2. Fix the test or document why it's expected to fail
3. If unfixable: Escalate to founder

### If Stuck

1. Update state file with what's blocked
2. Create escalation in DECISION_QUEUE.md
3. Output partial progress (don't lose work)
4. DO NOT output completion promise

---

## Agent-Specific Access

| Agent | Primary Tools | Secondary Tools |
|-------|---------------|-----------------|
| **Code** | gh (PRs), pytest, Playwright | railway (verify) |
| **Ops** | railway (logs, status), Playwright | gh (issues) |
| **Support** | Playwright (test flows), gh (issues) | railway (logs) |
| **Discovery** | Read/Grep/Glob (codebase analysis) | - |
| **Growth** | Web tools, PostHog | Playwright (verify) |
| **Finance** | Read (metrics), Stripe | - |
| **Meta** | All read tools | - |

---

## Key URLs

| Environment | URL |
|-------------|-----|
| **Production** | https://quoted.it.com |
| **Railway Dashboard** | https://railway.app/project/quoted |
| **GitHub Repo** | https://github.com/{org}/quoted |
| **PostHog** | https://app.posthog.com |
| **Stripe** | https://dashboard.stripe.com |

---

## Remember

1. **Production stability > Feature velocity**
2. **PRs are the path to production** - Railway handles the rest
3. **Test before requesting merge** - Use preview environments
4. **When in doubt, ask** - Escalate to founder
5. **Tools are available** - Use gh, railway, Playwright
