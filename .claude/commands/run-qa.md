# Quoted QA Fleet - Autonomous Quality Assurance

You are initiating a **QA cycle** for Quoted, Inc. - the quality gate that prevents regressions from reaching production.

## Purpose

Run automated tests across the entire product to verify everything works correctly. This command should be run:
- **Before** autonomous execution cycles (`/quoted-run`)
- **After** autonomous execution cycles (regression check)
- When deploying to production
- On-demand when something seems broken

## Profile Requirement

**CRITICAL**: This command requires the `browser` MCP profile for Playwright testing.

If you don't have Playwright MCP available, check your profile:
```bash
# Switch to browser profile (from personal assistant root)
cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant
./.claude-mcp-profiles/switch-profile.sh browser
# Then restart Claude Code
```

If Playwright MCP is unavailable, the command will fall back to API-only testing (partial coverage).

## Test Suites

| Suite | Duration | Coverage | When to Use |
|-------|----------|----------|-------------|
| `smoke` | 30 seconds | Critical paths only | Quick sanity check |
| `full` | 5-10 minutes | All user flows | Before production deploys |
| `api` | 1 minute | Backend endpoints | After backend changes |
| `visual` | 3 minutes | Screenshots + mobile | After CSS/layout changes |

## Test Environment

**Target**: Production (`https://quoted.it.com`)

**Test Credentials**: Use demo mode for unauthenticated tests, or create test session for authenticated flows.

---

## Phase 0: Pre-Flight Check

1. **Verify MCP Profile**:
   - Check if `mcp__playwright__*` tools are available
   - If not, warn user and offer API-only testing

2. **Read State Files**:
   - `ENGINEERING_STATE.md` - Recent deployments, known issues
   - `BETA_SPRINT.md` - Current priorities
   - Check for any `BUG-XXX` tickets that should be verified as fixed

3. **Determine Test Suite**:
   - If user specified a suite, use that
   - Default to `smoke` for quick checks
   - Suggest `full` if recent deployments detected

---

## Phase 1: QA Agent Fleet (Parallel)

Spawn 6 QA agents in parallel using the Task tool. Each agent tests a specific domain.

### Agent 1: Landing Page QA

**Tests**:
- [ ] Landing page loads at `https://quoted.it.com`
- [ ] All images load (no broken images)
- [ ] "Try Demo" button navigates to demo page
- [ ] "Start Free Trial" button shows auth modal
- [ ] Mobile menu works at 640px viewport
- [ ] Hero section renders correctly on mobile
- [ ] Testimonials section displays
- [ ] FAQ accordion expands/collapses
- [ ] Footer links work

**Return Format**:
```
LANDING_PAGE_RESULTS:
- passed: [count]
- failed: [count]
- failures: [list of failed tests with details]
- screenshots: [list of screenshot paths]
```

### Agent 2: Authentication QA

**Tests**:
- [ ] Auth modal opens when clicking "Sign Up"
- [ ] Magic link form accepts email input
- [ ] Invalid email shows validation error
- [ ] Terms and Privacy links work in modal
- [ ] Modal closes when clicking outside
- [ ] Login link switches to login mode

**Return Format**:
```
AUTH_RESULTS:
- passed: [count]
- failed: [count]
- failures: [list of failed tests with details]
```

### Agent 3: Demo Page QA

**Tests**:
- [ ] Demo page loads at `/demo`
- [ ] Text input mode works
- [ ] Voice input mode initiates (if permissions granted)
- [ ] Demo quote generates without errors
- [ ] Demo quote displays correctly
- [ ] "Sign Up" CTA appears after quote
- [ ] No JavaScript console errors
- [ ] Mobile layout works

**Return Format**:
```
DEMO_RESULTS:
- passed: [count]
- failed: [count]
- failures: [list of failed tests with details]
```

### Agent 4: API Health QA

**Tests** (use direct fetch, no browser needed):
- [ ] `GET /health` returns 200
- [ ] `GET /api/billing/plans` returns valid JSON with 3 plans
- [ ] `POST /api/auth/magic-link` with invalid email returns 422
- [ ] `GET /api/testimonials/?approved_only=true` returns array
- [ ] Rate limiting works (429 after too many requests)
- [ ] CORS headers present for quoted.it.com origin

**Return Format**:
```
API_RESULTS:
- passed: [count]
- failed: [count]
- failures: [list of failed tests with details]
- response_times: [p50, p95, p99]
```

### Agent 5: Billing QA

**Tests**:
- [ ] `/api/billing/plans` returns Starter, Pro, Team plans
- [ ] Plan prices match expected ($29, $49, $99)
- [ ] Trial configuration is correct (7 days, 75 quotes)
- [ ] Stripe checkout URLs are valid (don't actually purchase)
- [ ] All three plan buttons initiate checkout (verify URLs generated)

**Return Format**:
```
BILLING_RESULTS:
- passed: [count]
- failed: [count]
- failures: [list of failed tests with details]
```

### Agent 6: Mobile/Visual QA

**Tests** (take screenshots at each breakpoint):
- [ ] 1440px (desktop) - all elements visible
- [ ] 1024px (tablet landscape) - layout adapts
- [ ] 768px (tablet portrait) - mobile menu appears
- [ ] 640px (mobile) - no horizontal scroll
- [ ] 480px (small mobile) - text readable
- [ ] 375px (iPhone SE) - buttons not overlapping
- [ ] No z-index issues (nav above content)
- [ ] No text cutoff in containers

**Return Format**:
```
VISUAL_RESULTS:
- passed: [count]
- failed: [count]
- failures: [list of failed tests with details]
- screenshots: [paths to viewport screenshots]
```

---

## Phase 2: Authenticated Flow Tests (Full Suite Only)

If running `full` suite, also test authenticated flows:

### Create Test Session
1. Use a test account or create temporary session
2. If no test account, skip authenticated tests with warning

### Authenticated Tests:
- [ ] App dashboard loads after auth
- [ ] Onboarding flow initiates for new user
- [ ] Quick Setup form submits successfully
- [ ] New Quote section accepts text input
- [ ] Quote generation completes (may take 10-15s)
- [ ] Generated quote displays correctly
- [ ] Quote editing works (change a line item)
- [ ] Quote PDF downloads
- [ ] Quote sharing modal opens
- [ ] Account/Billing page loads
- [ ] Pricing Brain tab shows learning progress
- [ ] Mobile bottom nav works in app

---

## Phase 3: Results Aggregation

After all agents return, compile results:

```
QA_REPORT:

## Summary
| Area | Passed | Failed | Coverage |
|------|--------|--------|----------|
| Landing Page | X/Y | A | Z% |
| Authentication | X/Y | A | Z% |
| Demo | X/Y | A | Z% |
| API | X/Y | A | Z% |
| Billing | X/Y | A | Z% |
| Visual/Mobile | X/Y | A | Z% |
| **TOTAL** | **X/Y** | **A** | **Z%** |

## Status: [PASS / FAIL / PARTIAL]

## Failures (if any)
| Test | Area | Error | Severity |
|------|------|-------|----------|
| [test name] | [area] | [error message] | CRITICAL/HIGH/MEDIUM |

## Screenshots
[List of captured screenshots for review]

## Recommendations
1. [If failures] Create BUG-XXX tickets for failures
2. [If pass] Safe to proceed with deployment
3. [If partial] Review failures before proceeding
```

---

## Phase 4: Auto-Ticketing (on Failures)

If tests fail, automatically create tickets in `ENGINEERING_STATE.md`:

```markdown
### BUG-XXX: [Test Name] Failure (QA-DETECTED)

**Detected**: [timestamp]
**Source**: QA Fleet - [Agent Name]
**Severity**: [CRITICAL/HIGH/MEDIUM]

**Test**: [Test description]
**Expected**: [What should happen]
**Actual**: [What happened]
**Screenshot**: [If available]

**Recommended Fix**: [If obvious from error]
```

**Severity Rules**:
- CRITICAL: Core functionality broken (can't generate quotes, can't sign up)
- HIGH: Major feature broken (billing, sharing, PDF)
- MEDIUM: Minor issue (visual glitch, non-blocking error)

---

## Phase 5: Final Report

Output summary to founder:

```
QA_CYCLE_COMPLETE:

## Result: [PASS ✅ / FAIL ❌ / WARNING ⚠️]

## Test Coverage
- Suite: [smoke/full/api/visual]
- Total Tests: [X]
- Passed: [Y]
- Failed: [Z]
- Pass Rate: [%]

## Critical Issues
[List any CRITICAL or HIGH severity failures]

## Tickets Created
[List of BUG-XXX tickets created]

## Next Steps
- [PASS] Safe to proceed with deployment/execution
- [FAIL] Fix critical issues before proceeding
- [WARNING] Review warnings, proceed with caution

## Run Details
- Started: [timestamp]
- Completed: [timestamp]
- Duration: [X minutes]
- Profile: [browser/minimal]
```

---

## Test URLs Reference

| Page | URL | Auth Required |
|------|-----|---------------|
| Landing | `https://quoted.it.com` | No |
| Demo | `https://quoted.it.com/demo` | No |
| Help | `https://quoted.it.com/help.html` | No |
| Terms | `https://quoted.it.com/terms.html` | No |
| Privacy | `https://quoted.it.com/privacy.html` | No |
| App | `https://quoted.it.com/app` | Yes |

## API Endpoints Reference

| Endpoint | Method | Auth | Expected |
|----------|--------|------|----------|
| `/health` | GET | No | 200 OK |
| `/api/billing/plans` | GET | No | JSON with plans |
| `/api/testimonials/` | GET | No | JSON array |
| `/api/auth/magic-link` | POST | No | 200 or 422 |

---

## Key Principles

1. **Non-destructive** - Tests should not create real data or charge cards
2. **Fast feedback** - Smoke tests complete in under 1 minute
3. **Actionable results** - Failures create tickets automatically
4. **Visual evidence** - Screenshots captured for review
5. **Profile-aware** - Falls back gracefully without Playwright

## When to Run

- `/run-qa` - Default smoke tests
- `/run-qa smoke` - Quick critical path check
- `/run-qa full` - Comprehensive before production
- `/run-qa api` - Backend-only testing
- `/run-qa visual` - Screenshots and mobile testing

## Integration with Autonomous Cycles

The QA Fleet should be run:
1. **Pre-execution**: Before `/quoted-run` to establish baseline
2. **Post-execution**: After `/quoted-run` to catch regressions
3. **Pre-deploy**: Before any production deployment

If QA fails post-execution, the autonomous cycle should be flagged for human review.
