# Orchestrate Codex Remediation

## Command Definition
```yaml
name: orchestrate-codex-remediation
description: Autonomous CI/CD-integrated orchestrator for Codex audit findings with full testing, PR workflow, and production verification
trigger: /orchestrate-codex-remediation
source: .claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/
state: .claude/codex-remediation-state.md
```

## Overview

This orchestrator autonomously remediates all confirmed issues from the GPT-5.2-Codex audit, following a rigorous workflow:

1. **Fix on Branch** - All changes on feature branch, never direct to main
2. **Automated Testing** - Backend tests, API verification, Railway logs
3. **Visual QA** - Chrome MCP browser automation for UI verification
4. **PR Review Gate** - Autonomous merge decision based on test results
5. **Production Verification** - Post-deploy testing with rollback capability
6. **Re-Audit** - Fresh audit to catch any new holes

**Protection**: Production is NEVER touched until all tests pass on PR.

---

## Quick Start

```bash
# Check status and continue
/orchestrate-codex-remediation

# Status only
/orchestrate-codex-remediation --status

# Jump to specific phase
/orchestrate-codex-remediation --phase=N

# Reset and start fresh
/orchestrate-codex-remediation --reset
```

---

## THIN ORCHESTRATOR PATTERN (MANDATORY)

**This orchestrator MUST NOT perform substantive work directly. ALL work is done by spawned Task agents.**

### Orchestrator ONLY:
- Read/update state file (`.claude/codex-remediation-state.md`)
- Spawn Task agents with detailed prompts
- Collect TaskOutput and synthesize
- Decide phase transitions

### Orchestrator MUST NOT:
- Write/modify code directly (spawn agent)
- Run tests directly (spawn agent)
- Create PRs directly (spawn agent)
- Make browser interactions directly (spawn agent)
- Fix bugs directly (spawn agent)
- Deploy or merge directly (spawn agent)

### Correct Execution Pattern:
```
1. Read state file → determine current phase
2. Spawn Task agent(s) with detailed prompt(s)
3. If parallel: spawn multiple agents, use run_in_background: true
4. Wait for TaskOutput (blocking or polling)
5. Update state file with findings/results
6. Repeat for next agent/phase
```

---

## Phase Structure

| Phase | Name | Agents | Focus |
|-------|------|--------|-------|
| 0 | Context & Pre-flight | 1 | Load state, verify tools, create branch |
| 1 | Critical Fixes | 4 | Billing bypass, deposit checkout, scheduler, health endpoint |
| 2 | Backend Testing | 3 | Unit tests, API curl tests, Railway log verification |
| 3 | Browser QA | 2 | Chrome MCP visual testing of critical paths |
| 4 | PR Creation & Review | 1 | Create PR, run CI, generate summary |
| 5 | Merge Decision Gate | 1 | Autonomous pass/fail decision |
| 6 | Production Verification | 3 | Post-deploy testing, log monitoring |
| 7 | Re-Audit | 2 | Fresh security scan, find new holes |
| 8 | Completion | 1 | Final report, cleanup |

**Total**: 18 agents across 9 phases

---

## Tool Arsenal Reference

### GitHub CLI
```bash
# Create branch
git checkout -b fix/codex-audit-remediation

# Create PR
gh pr create --title "..." --body "..."

# Check PR status
gh pr status

# Merge PR
gh pr merge --squash --delete-branch

# View PR checks
gh pr checks
```

### Railway CLI
```bash
# View production logs
railway logs -n 100

# Filter for errors
railway logs -n 200 --filter "@level:error"

# Check deployment status
railway status

# View environment variables
railway variables
```

### Chrome MCP (Browser Automation) - WORKS IN SUBAGENTS

**These tools work when spawned via Task tool:**

```javascript
// Get tab context - ALWAYS CALL FIRST
mcp__claude-in-chrome__tabs_context_mcp({ createIfEmpty: true })

// Navigate
mcp__claude-in-chrome__navigate({ url: "https://quoted.it.com", tabId: X })

// Screenshot (use computer tool, NOT browser_snapshot)
mcp__claude-in-chrome__computer({ action: "screenshot", tabId: X })

// Read page
mcp__claude-in-chrome__read_page({ tabId: X })

// Find elements
mcp__claude-in-chrome__find({ query: "login button", tabId: X })

// Click
mcp__claude-in-chrome__computer({ action: "left_click", coordinate: [X, Y], tabId: X })

// Form input
mcp__claude-in-chrome__form_input({ ref: "ref_X", value: "...", tabId: X })

// Read console errors
mcp__claude-in-chrome__read_console_messages({ tabId: X, onlyErrors: true })

// Read network requests
mcp__claude-in-chrome__read_network_requests({ tabId: X, urlPattern: "/api/" })

// Resize viewport
mcp__claude-in-chrome__resize_window({ width: 375, height: 812, tabId: X })
```

### DO NOT USE in Subagents

```javascript
// browser_snapshot - NOT available to subagents
mcp__claude-in-chrome__browser_snapshot({})  // WILL FAIL

// Playwright tools - conflict with Chrome MCP
mcp__plugin_playwright_playwright__*  // WILL FAIL or cause "instance in use" error
```

### Subagent Browser Setup Pattern

Include this in ALL subagent prompts that need browser access:

```markdown
BROWSER SETUP:
1. Call mcp__claude-in-chrome__tabs_context_mcp to get available tabs
2. Use an existing tab or create new if needed
3. For screenshots, use: mcp__claude-in-chrome__computer with action: "screenshot"
4. DO NOT use browser_snapshot (not available to subagents)
5. DO NOT use Playwright tools (conflicts with Chrome MCP)
6. If browser tools fail, fall back to code inspection using Read/Grep
```

---

## Phase 0: Context & Pre-flight

**Agent Count**: 1 (orchestrator itself)
**Dependencies**: None

### Mandatory First Steps

```
1. READ STATE FILE:
   .claude/codex-remediation-state.md

2. READ SOURCE DOCUMENTS:
   .claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/GPT-5.2-Codex_FINAL_REPORT.md
   .claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/GPT-5.2-Codex_phase1-holes.md

3. VERIFY TOOLS AVAILABLE:
   - Run: gh --version (GitHub CLI)
   - Run: railway --version (Railway CLI)
   - Test: mcp__claude-in-chrome__tabs_context_mcp (Chrome MCP)

4. CHECK GIT STATUS:
   - Ensure clean working tree
   - Identify current branch

5. CREATE FEATURE BRANCH:
   git checkout -b fix/codex-audit-remediation-$(date +%Y%m%d)

6. DETERMINE RESUME POINT:
   - If state file exists: continue from last incomplete phase
   - If fresh start: begin Phase 1
```

### Pre-flight Checklist

```
[ ] State file exists or created
[ ] Source documents readable
[ ] GitHub CLI authenticated (gh auth status)
[ ] Railway CLI linked (railway status)
[ ] Chrome MCP responding
[ ] Feature branch created
[ ] Working tree clean
```

### State File Initialization

If state file doesn't exist, create:

```markdown
# Codex Remediation State

## Status
Phase: 1
Started: [TIMESTAMP]
Last Updated: [TIMESTAMP]
Branch: fix/codex-audit-remediation-[DATE]
PR: None

## Confirmed Issues (from Claude analysis of Codex audit)

### P0 Critical
- [ ] P0-02: Scheduler duplication (4 workers = 4 schedulers)
- [ ] P0-03: Billing bypass on /generate-with-clarifications
- [ ] P0-04: Deposit checkout broken (method names, config, redirect)
- [ ] P0-08: Health/full cost burn (unprotected endpoint)

### P1 High
- [ ] P0-01: SQLite engine args (dev/test only)
- [ ] DB-ENGINES: Multiple DB engines (architectural debt)

## Phase Completion
- [ ] Phase 0: Context & Pre-flight
- [ ] Phase 1: Critical Fixes
- [ ] Phase 2: Backend Testing
- [ ] Phase 3: Browser QA
- [ ] Phase 4: PR Creation
- [ ] Phase 5: Merge Decision
- [ ] Phase 6: Production Verification
- [ ] Phase 7: Re-Audit
- [ ] Phase 8: Completion

## Test Results
(Updated after Phase 2 & 3)

## PR Details
(Updated after Phase 4)

## Commits
(Updated after each fix)

## Blocked Items
(If issues arise)
```

---

## Phase 1: Critical Fixes

**Agent Count**: 4 parallel agents
**Priority**: CRITICAL
**Dependencies**: Phase 0 complete

### Agent 1A: Billing Bypass Fix

**Target**: `backend/api/quotes.py`
**Issue**: P0-03 - `/generate-with-clarifications` bypasses billing

```
TASK: Add billing check to clarifications endpoint matching main quote flow

EVIDENCE:
- Main flow (line ~362): BillingService.check_quote_limit(auth_db, current_user["id"])
- Clarifications flow (line ~733): NO billing check

IMPLEMENTATION:

1. Find the generate_quote_with_clarifications function (~line 733)

2. Add billing check at start of function (after getting current_user):

```python
# Check billing status first (matches main quote generation flow)
billing_check = await BillingService.check_quote_limit(auth_db, current_user["id"])

if not billing_check["can_generate"]:
    if billing_check["reason"] == "trial_expired":
        raise HTTPException(
            status_code=402,
            detail={
                "error": "trial_expired",
                "message": "Your trial has expired. Please upgrade to continue generating quotes.",
                "trial_ends_at": billing_check.get("trial_ends_at"),
            }
        )
    elif billing_check["reason"] == "trial_limit_reached":
        raise HTTPException(
            status_code=402,
            detail={
                "error": "trial_limit_reached",
                "message": f"You've reached your trial limit. Please upgrade to continue.",
            }
        )
    else:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "quota_exceeded",
                "message": "Unable to generate quote. Please check your subscription status.",
            }
        )
```

3. Also add usage increment after successful quote creation (if main flow does this)

VERIFICATION:
- Create test user with expired trial
- Call /api/quotes/generate-with-clarifications
- Expected: 402 error, not successful quote
```

### Agent 1B: Deposit Checkout Fix

**Target**: `backend/api/share.py`
**Issue**: P0-04 - Multiple broken components in deposit checkout

```
TASK: Fix all broken components in deposit checkout endpoint

EVIDENCE (line ~759-850):
1. settings.app_url doesn't exist (only frontend_url)
2. db.get_contractor() doesn't exist (should be get_contractor_by_id)
3. db.get_contractor_terms() doesn't exist (should be get_terms)
4. Redirect URL uses /quote/{token} but route is /shared/{token}

IMPLEMENTATION:

1. Fix config reference (line ~826):
   BEFORE: base_url = settings.app_url.rstrip("/")
   AFTER:  base_url = settings.frontend_url.rstrip("/")

2. Fix method names (line ~781, ~786):
   BEFORE: contractor = await db.get_contractor(str(quote.contractor_id))
   AFTER:  contractor = await db.get_contractor_by_id(str(quote.contractor_id))

   BEFORE: terms = await db.get_contractor_terms(str(contractor.id))
   AFTER:  terms = await db.get_terms(str(contractor.id))

3. Fix redirect path (line ~827-828):
   BEFORE: success_url = f"{base_url}/quote/{token}?payment=success"
   AFTER:  success_url = f"{base_url}/shared/{token}?payment=success"

   BEFORE: cancel_url = f"{base_url}/quote/{token}?payment=cancelled"
   AFTER:  cancel_url = f"{base_url}/shared/{token}?payment=cancelled"

4. Also fix any other occurrences of settings.app_url in share.py (lines 631, 723)

VERIFICATION:
- Code review: No references to app_url, get_contractor(), get_contractor_terms()
- All redirect URLs use /shared/{token}
```

### Agent 1C: Scheduler Duplication Fix

**Target**: `backend/main.py`, `Procfile`
**Issue**: P0-02 - 4 workers each start scheduler = 4x duplicate jobs

```
TASK: Ensure scheduler runs once regardless of worker count

EVIDENCE:
- Procfile: uvicorn ... --workers 4
- main.py:110: start_scheduler() called in lifespan (runs per worker)

IMPLEMENTATION OPTIONS:

OPTION A: Environment variable guard (simplest)

In main.py, modify lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.app_name}")

    # ... existing setup ...

    # Only start scheduler in first worker (use env var)
    import os
    if os.environ.get("SCHEDULER_WORKER", "0") == "0":
        os.environ["SCHEDULER_WORKER"] = "1"  # Claim it
        from .services.scheduler import start_scheduler, stop_scheduler
        start_scheduler()
        scheduler_started = True
    else:
        scheduler_started = False

    yield

    # Shutdown
    if scheduler_started:
        stop_scheduler()
```

OPTION B: Reduce to 1 worker (Railway environment)
- Set in Railway: WEB_CONCURRENCY=1
- Or modify Procfile: --workers 1

OPTION C: Leader election with Redis (if Redis available)
- More complex but production-grade
- Only implement if Option A doesn't work

RECOMMENDED: Start with Option A, fallback to B if issues

VERIFICATION:
- Deploy to Railway
- Check scheduler job logs
- Expected: Jobs execute once, not 4x
```

### Agent 1D: Health Endpoint Protection

**Target**: `backend/main.py`
**Issue**: P0-08 - /health/full is public and triggers external API calls

```
TASK: Protect /health/full from public abuse

EVIDENCE:
- main.py:200 - /health/full is public
- health.py:65+ - Makes real API calls to OpenAI/Anthropic/Stripe

IMPLEMENTATION:

1. Add rate limiting to /health/full:

```python
from .services.rate_limiting import limiter

@app.get("/health/full")
@limiter.limit("2/minute")  # Strict limit
async def health_full(request: Request):
    """Comprehensive health check - rate limited to prevent abuse."""
    from .services.health import check_all_health
    return await check_all_health(include_external=True)
```

2. Optionally add admin secret check:

```python
@app.get("/health/full")
@limiter.limit("2/minute")
async def health_full(
    request: Request,
    x_admin_secret: Optional[str] = Header(None)
):
    """Comprehensive health check - protected endpoint."""
    # Optional: require admin secret for external checks
    if settings.admin_secret and x_admin_secret != settings.admin_secret:
        # Return basic health only if no secret
        from .services.health import check_basic_health
        return await check_basic_health()

    from .services.health import check_all_health
    return await check_all_health(include_external=True)
```

VERIFICATION:
- Call /health/full 5 times rapidly
- Expected: 429 on 3rd+ call
- Alternative: Call without secret, expect limited response
```

### Phase 1 Completion

```
AFTER ALL AGENTS COMPLETE:

1. Verify all changes:
   git diff --stat

2. Run quick syntax check:
   python -c "import backend.main"

3. Commit with descriptive message:
   git add -A
   git commit -m "fix(critical): Codex audit P0 fixes

   - P0-02: Guard scheduler to run once per deployment
   - P0-03: Add billing check to /generate-with-clarifications
   - P0-04: Fix deposit checkout (methods, config, redirect paths)
   - P0-08: Rate limit /health/full endpoint

   🤖 Generated with Claude Code"

4. Update state file:
   - Mark Phase 1 complete
   - Record commit hash
```

---

## Phase 2: Backend Testing

**Agent Count**: 3 parallel agents
**Priority**: REQUIRED
**Dependencies**: Phase 1 complete

### Agent 2A: Unit & Import Tests

```
TASK: Verify code changes don't break imports or existing tests

COMMANDS:

1. Import smoke test:
   python -c "import backend.main; print('Import OK')"

2. Run existing tests (if any):
   cd backend && python -m pytest -q --tb=short

3. Check for syntax errors:
   python -m py_compile backend/api/quotes.py
   python -m py_compile backend/api/share.py
   python -m py_compile backend/main.py

OUTPUT:
| Test | Status | Details |
|------|--------|---------|
| Import smoke | PASS/FAIL | |
| pytest | PASS/FAIL | X tests, Y failures |
| Syntax check | PASS/FAIL | |

IF ANY FAIL: Log to state file, spawn fix agent
```

### Agent 2B: API Endpoint Testing

```
TASK: Test affected endpoints with curl

TESTS:

1. Test billing bypass fix:
   # This should work for valid user
   curl -X POST https://quoted.it.com/api/quotes/generate-with-clarifications \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"transcription": "test", "clarifications": []}'

   Expected: 200 or 402 (if trial expired) - NOT 500

2. Test health endpoint rate limiting:
   for i in {1..5}; do
     curl -s -o /dev/null -w "%{http_code}\n" https://quoted.it.com/health/full
     sleep 0.5
   done

   Expected: 200, 200, 429, 429, 429

3. Test deposit checkout (if possible without real payment):
   # Just verify endpoint doesn't 500 immediately
   curl -X POST https://quoted.it.com/api/share/test-token/deposit-checkout \
     -H "Content-Type: application/json" \
     -d '{}'

   Expected: 404 (token not found) or 400 (validation) - NOT 500

NOTE: These tests run against PRODUCTION unless we have a staging env.
For PR testing, we may need to deploy to Railway preview first.

OUTPUT:
| Endpoint | Expected | Actual | Pass |
|----------|----------|--------|------|
```

### Agent 2C: Railway Log Verification

```
TASK: Check Railway logs for any errors from recent changes

COMMANDS:

1. View recent errors:
   railway logs -n 100 --filter "@level:error"

2. Check for specific issues:
   railway logs -n 200 | grep -i "undefined\|TypeError\|AttributeError"

3. Verify scheduler behavior (after deploy):
   railway logs -n 200 | grep -i "scheduler\|job\|background"

4. Check for billing-related logs:
   railway logs -n 200 | grep -i "billing\|quota\|trial"

OUTPUT:
| Check | Status | Findings |
|-------|--------|----------|
| Error logs | CLEAN/ISSUES | Details |
| Scheduler | SINGLE/DUPLICATE | Details |
| Type errors | CLEAN/ISSUES | Details |

IF ISSUES FOUND: Log to state file
```

### Phase 2 Completion

```
AGGREGATE TEST RESULTS:

All Pass Criteria:
[ ] Import smoke test passes
[ ] No new test failures
[ ] API endpoints return expected status codes
[ ] No new errors in Railway logs
[ ] Scheduler running single instance

IF ANY FAIL:
1. Log issue in state file under "Blocked Items"
2. Spawn fix agent for specific issue
3. Re-run failed tests
4. Max 3 retry attempts before escalating to human

IF ALL PASS:
1. Update state file with test results
2. Proceed to Phase 3
```

---

## Phase 3: Browser QA

**Agent Count**: 2 parallel agents
**Priority**: REQUIRED
**Dependencies**: Phase 2 complete

### Agent 3A: Critical User Journey - Quote Creation

```
TASK: Test quote creation flow with browser automation

TOOLS: Chrome MCP or Playwright

PROCEDURE:

1. Initialize browser:
   mcp__claude-in-chrome__tabs_context_mcp({ createIfEmpty: true })
   # Get tabId from response

2. Navigate to app:
   mcp__claude-in-chrome__navigate({ url: "https://quoted.it.com/app", tabId: X })

3. Take initial screenshot:
   mcp__claude-in-chrome__computer({ action: "screenshot", tabId: X })

4. Check for console errors:
   mcp__claude-in-chrome__read_console_messages({ tabId: X, onlyErrors: true })

5. If logged in, test quote flow:
   a. Find "New Quote" button
   b. Click it
   c. Enter test transcription
   d. Submit
   e. Verify quote generated
   f. Screenshot result

6. Check network for failed requests:
   mcp__claude-in-chrome__read_network_requests({ tabId: X, urlPattern: "/api/" })
   # Look for 4xx/5xx responses

OUTPUT:
| Step | Status | Screenshot | Console Errors | Network Errors |
|------|--------|------------|----------------|----------------|
| Load app | PASS/FAIL | img_1 | | |
| Create quote | PASS/FAIL | img_2 | | |

NOTE: May need authentication. If login required, document steps.
```

### Agent 3B: Critical User Journey - Shared Quote View

```
TASK: Test shared quote view and deposit flow

TOOLS: Chrome MCP or Playwright

PROCEDURE:

1. Get a valid share token from database or create test quote

2. Navigate to shared quote:
   mcp__claude-in-chrome__navigate({
     url: "https://quoted.it.com/shared/{token}",
     tabId: X
   })

3. Screenshot initial load:
   mcp__claude-in-chrome__computer({ action: "screenshot", tabId: X })

4. Check for errors:
   mcp__claude-in-chrome__read_console_messages({ tabId: X, onlyErrors: true })

5. Verify quote renders correctly:
   mcp__claude-in-chrome__read_page({ tabId: X })
   # Check for contractor name, line items, total

6. Test accept button (if exists):
   mcp__claude-in-chrome__find({ query: "accept button", tabId: X })
   # Don't actually click if it triggers payment

7. Test mobile view:
   mcp__claude-in-chrome__resize_window({ width: 375, height: 812, tabId: X })
   mcp__claude-in-chrome__computer({ action: "screenshot", tabId: X })

OUTPUT:
| Step | Status | Screenshot | Notes |
|------|--------|------------|-------|
| Load shared quote | PASS/FAIL | img_1 | |
| Quote renders | PASS/FAIL | | |
| Mobile view | PASS/FAIL | img_2 | |
```

### Phase 3 Completion

```
AGGREGATE BROWSER QA RESULTS:

Pass Criteria:
[ ] App loads without console errors
[ ] Quote creation flow works
[ ] Shared quote view renders correctly
[ ] No network errors on API calls
[ ] Mobile view is usable

IF ISSUES FOUND:
1. Screenshot the issue
2. Capture console/network errors
3. Log to state file
4. Decide: blocking or non-blocking

IF ALL PASS:
1. Update state file with QA results
2. Proceed to Phase 4
```

---

## Phase 4: PR Creation & Review

**Agent Count**: 1
**Priority**: REQUIRED
**Dependencies**: Phase 2 & 3 complete with passing results

### PR Creation Agent

```
TASK: Create PR with comprehensive summary

PRE-REQUISITES:
- All Phase 2 tests passing
- All Phase 3 browser QA passing
- All changes committed on feature branch

PROCEDURE:

1. Push branch to origin:
   git push -u origin fix/codex-audit-remediation-[DATE]

2. Create PR with detailed body:
   gh pr create --title "fix(critical): Codex Audit P0 Remediation" --body "$(cat <<'EOF'
## Summary

Addresses critical issues identified by GPT-5.2-Codex audit.

### Issues Fixed

| ID | Issue | Fix |
|----|-------|-----|
| P0-02 | Scheduler duplication (4x jobs) | Environment guard for single scheduler |
| P0-03 | Billing bypass on clarifications | Added billing check matching main flow |
| P0-04 | Deposit checkout broken | Fixed method names, config key, redirect paths |
| P0-08 | Health endpoint abuse vector | Added rate limiting (2/minute) |

### Test Results

**Backend Tests:**
- Import smoke: ✅ PASS
- Syntax check: ✅ PASS
- API endpoints: ✅ PASS

**Browser QA:**
- App load: ✅ PASS
- Quote creation: ✅ PASS
- Shared quote view: ✅ PASS
- Mobile view: ✅ PASS

### Files Changed
- `backend/api/quotes.py` - Billing check for clarifications
- `backend/api/share.py` - Method names, config, redirects
- `backend/main.py` - Scheduler guard, health rate limit

### Rollback Plan
```bash
git revert [COMMIT_HASH]
git push origin main
# Railway auto-deploys revert
```

### Post-Deploy Verification
- [ ] Check scheduler runs once (Railway logs)
- [ ] Verify billing check works (test with expired trial)
- [ ] Verify deposit checkout doesn't 500
- [ ] Verify health endpoint rate limited

🤖 Generated with Claude Code
EOF
)"

3. Record PR number in state file

4. Check if CI passes (if configured):
   gh pr checks --watch

OUTPUT:
- PR URL: https://github.com/.../pull/XXX
- CI Status: PASS/FAIL
```

---

## Phase 5: Merge Decision Gate

**Agent Count**: 1
**Priority**: CRITICAL DECISION POINT
**Dependencies**: Phase 4 complete, CI passing

### Autonomous Merge Decision

```
TASK: Decide whether to merge based on all test results

DECISION CRITERIA:

MUST ALL BE TRUE TO MERGE:
[ ] Phase 2 backend tests: ALL PASS
[ ] Phase 3 browser QA: ALL PASS (or non-blocking issues only)
[ ] PR CI checks: ALL PASS
[ ] No blocking issues in state file
[ ] No new errors discovered

IF ALL CRITERIA MET:
1. Log decision: "AUTONOMOUS MERGE APPROVED"
2. Execute merge:
   gh pr merge --squash --delete-branch
3. Wait for Railway deploy (check: railway status)
4. Proceed to Phase 6

IF ANY CRITERIA FAIL:
1. Log decision: "MERGE BLOCKED"
2. Document blocking issue
3. Either:
   a. Spawn fix agent for fixable issues
   b. Escalate to human for complex issues
4. Re-run from appropriate phase after fix

MERGE COMMAND:
gh pr merge [PR_NUMBER] --squash --delete-branch --body "Merging after autonomous QA passed"

POST-MERGE:
- Wait 2-3 minutes for Railway deployment
- Verify deployment: railway status
- Check: railway logs -n 20 (no startup errors)
```

---

## Phase 6: Production Verification

**Agent Count**: 3 parallel agents
**Priority**: CRITICAL
**Dependencies**: Phase 5 merge complete, deployment finished

### Agent 6A: Railway Log Monitoring

```
TASK: Monitor production logs for 5 minutes post-deploy

PROCEDURE:

1. Verify deployment complete:
   railway status
   # Should show recent deployment

2. Watch logs for errors (5 minutes):
   railway logs --filter "@level:error"

   # Or check periodically:
   for i in {1..5}; do
     railway logs -n 50 | head -20
     sleep 60
   done

3. Check scheduler is single instance:
   railway logs -n 100 | grep -i "scheduler\|Starting\|background"
   # Should see ONE "Starting scheduler" not four

4. Check for any 500 errors:
   railway logs -n 200 | grep "500\|Internal Server Error"

OUTPUT:
| Check | Status | Details |
|-------|--------|---------|
| Deployment | SUCCESS/FAIL | |
| Error logs | CLEAN/ISSUES | |
| Scheduler | SINGLE/DUPLICATE | |
| 500 errors | NONE/FOUND | |

IF ISSUES: Trigger rollback procedure
```

### Agent 6B: API Smoke Tests on Production

```
TASK: Verify all fixed endpoints work in production

TESTS:

1. Health endpoint rate limiting:
   for i in {1..5}; do
     STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://quoted.it.com/health/full)
     echo "Request $i: $STATUS"
     sleep 0.5
   done
   # Should see 200, 200, 429, 429, 429

2. Basic health (should always work):
   curl -s https://quoted.it.com/health
   # Should return {"status": "healthy"}

3. Auth endpoint (verify app is up):
   curl -s -X POST https://quoted.it.com/api/auth/magic-link \
     -H "Content-Type: application/json" \
     -d '{"email": "test@test.com"}'
   # Should return 200 or 429 (rate limited) - not 500

OUTPUT:
| Endpoint | Expected | Actual | Pass |
|----------|----------|--------|------|
```

### Agent 6C: Browser Production Smoke Test

```
TASK: Quick browser smoke test of production

PROCEDURE:

1. Navigate to production:
   mcp__claude-in-chrome__navigate({ url: "https://quoted.it.com", tabId: X })

2. Screenshot landing:
   mcp__claude-in-chrome__computer({ action: "screenshot", tabId: X })

3. Check console for errors:
   mcp__claude-in-chrome__read_console_messages({ tabId: X, onlyErrors: true })

4. Navigate to app:
   mcp__claude-in-chrome__navigate({ url: "https://quoted.it.com/app", tabId: X })

5. Screenshot app:
   mcp__claude-in-chrome__computer({ action: "screenshot", tabId: X })

6. Check console again:
   mcp__claude-in-chrome__read_console_messages({ tabId: X, onlyErrors: true })

OUTPUT:
| Page | Loads | Console Errors | Screenshot |
|------|-------|----------------|------------|
| Landing | YES/NO | NONE/[list] | img_1 |
| App | YES/NO | NONE/[list] | img_2 |

IF ANY CRITICAL ERRORS: Trigger rollback
```

### Phase 6 Rollback Procedure

```
IF PRODUCTION ISSUES DETECTED:

1. Immediate rollback:
   git revert HEAD
   git push origin main
   # Railway auto-deploys revert

2. Verify rollback:
   railway status
   railway logs -n 20

3. Log in state file:
   - Rollback triggered at: [TIMESTAMP]
   - Reason: [DESCRIPTION]
   - Status: Investigating

4. Spawn investigation agent to determine root cause

5. Fix and retry from Phase 1
```

---

## Phase 7: Re-Audit

**Agent Count**: 2 parallel agents
**Priority**: RECOMMENDED
**Dependencies**: Phase 6 complete with no rollback

### Agent 7A: Security Re-Scan

```
TASK: Verify security issues are actually fixed

TESTS:

1. Rate limiting verification:
   - Hammer /health/full 10 times
   - Expected: Rate limited after 2

2. Billing bypass verification:
   - If possible, test with expired trial user
   - Call /api/quotes/generate-with-clarifications
   - Expected: 402 rejection

3. Scheduler verification:
   - Check Railway logs over 10 minutes
   - Count "scheduler" or "job" messages
   - Expected: Consistent with single scheduler

4. Code review of fixes:
   - Re-read modified files
   - Verify no regressions introduced
   - Check for any new vulnerabilities

OUTPUT:
| Issue | Fixed | Verification Method | Notes |
|-------|-------|---------------------|-------|
| P0-02 Scheduler | YES/NO | Log analysis | |
| P0-03 Billing | YES/NO | API test | |
| P0-04 Deposit | YES/NO | Code review | |
| P0-08 Health | YES/NO | Rate limit test | |
```

### Agent 7B: Fresh Hole Discovery

```
TASK: Look for new issues introduced by fixes

CHECKS:

1. Import/startup check:
   python -c "import backend.main"

2. Search for common issues in changed files:
   - Undefined variables
   - Missing imports
   - Type errors
   - Unhandled exceptions

3. Check for new public endpoints:
   grep -r "@router\." backend/api/ | grep -v "Depends(get_current"

4. Check for hardcoded secrets:
   grep -r "sk_\|pk_\|api_key" backend/ --include="*.py"

5. Review any TODO/FIXME added:
   grep -r "TODO\|FIXME\|HACK" backend/ --include="*.py"

OUTPUT:
| Check | Status | Findings |
|-------|--------|----------|
| New vulnerabilities | CLEAN/FOUND | |
| Undefined vars | CLEAN/FOUND | |
| Hardcoded secrets | CLEAN/FOUND | |
| New TODOs | COUNT | |

IF NEW ISSUES FOUND:
1. Assess severity (P0/P1/P2)
2. If P0: Create new fix branch, start mini-remediation
3. If P1/P2: Log for next sprint
```

---

## Phase 8: Completion

**Agent Count**: 1
**Priority**: FINAL
**Dependencies**: All previous phases complete

### Final Report Generation

```
TASK: Generate completion report and update state

PROCEDURE:

1. Compile all results:
   - Issues fixed: [COUNT]
   - Tests passed: [COUNT]
   - Time elapsed: [DURATION]
   - Commits: [LIST]
   - PR: [URL]

2. Generate final report:

   ## Codex Remediation Complete

   **Duration**: [START] to [END]
   **Branch**: fix/codex-audit-remediation-[DATE]
   **PR**: #[NUMBER]
   **Merged**: [TIMESTAMP]

   ### Issues Addressed
   | ID | Description | Status |
   |----|-------------|--------|
   | P0-02 | Scheduler duplication | ✅ FIXED |
   | P0-03 | Billing bypass | ✅ FIXED |
   | P0-04 | Deposit checkout | ✅ FIXED |
   | P0-08 | Health endpoint | ✅ FIXED |

   ### Test Summary
   - Backend tests: X/X passed
   - Browser QA: X/X passed
   - Production smoke: X/X passed
   - Re-audit: CLEAN

   ### Rollbacks: 0

   ### New Issues Found: [COUNT]
   [List if any]

3. Update state file to COMPLETE

4. Clean up:
   - Delete local feature branch (already deleted on merge)
   - Archive any temporary files

5. Notify success:
   "Codex remediation complete. All P0 issues fixed and verified."
```

---

## Rollback Procedures

### Immediate Rollback (Production Issues)

```bash
# Get the merge commit hash
git log --oneline -3

# Revert the merge
git revert HEAD --no-edit
git push origin main

# Railway auto-deploys
# Monitor: railway logs
```

### Phase-Level Rollback

```bash
# If a phase introduced issues
git log --oneline -5  # Find phase commit

# Revert that commit
git revert [COMMIT_HASH]

# Re-run phase with fixes
```

### Full Reset

```bash
# If everything is broken
git checkout main
git pull
git branch -D fix/codex-audit-remediation-*

# Reset state file
rm .claude/codex-remediation-state.md

# Start fresh
/orchestrate-codex-remediation --reset
```

---

## Resume Procedures

### After Context Reset

```
1. Read: .claude/codex-remediation-state.md
2. Identify current phase
3. Check git status for uncommitted work
4. Continue from next incomplete item
5. Don't repeat completed work
```

### After Partial Phase

```
1. Check state file for completed agents
2. Run only remaining agents in phase
3. If phase commit exists, skip to next phase
```

### After Merge

```
1. If state shows "Phase 5 complete, Phase 6 pending"
2. Skip directly to Phase 6 production verification
3. Don't re-merge
```

---

## Success Metrics

At completion:
- **4 P0 issues fixed**
- **All backend tests passing**
- **All browser QA passing**
- **Production stable for 24+ hours**
- **Re-audit clean**
- **Zero rollbacks**

---

## Execution

```
/orchestrate-codex-remediation
```

The orchestrator will:
1. Load state and determine current phase
2. Execute agents in parallel where possible
3. Run verification before proceeding
4. Create and merge PR autonomously (if tests pass)
5. Verify production after deploy
6. Re-audit for completeness
7. Generate final report

**Estimated execution time**: 1-2 hours
**Human intervention required**: Only on test failures or rollback
