# Production Readiness Orchestration Plan

**Created**: 2025-12-23
**Purpose**: Autonomous implementation of 18 infrastructure/security tickets
**Target**: 5 PRs, fully tested, production-ready

---

## Executive Summary

This plan enables a fresh Claude Code instance to act as an **Orchestrator Agent** that:
1. Implements 18 production readiness tickets in 5 optimally-batched PRs
2. Spawns parallel sub-agents for independent work streams
3. Maintains context across all work via state files
4. Tests continuously and rolls back on failure
5. Deploys incrementally with validation gates

**Estimated Total Effort**: 35-40 hours of AI agent time
**Expected Duration**: 4-6 hours wall clock (with parallelization)

---

## Ticket Inventory (18 tickets)

### P0 Critical (7 tickets) - Must complete first
| ID | Title | Effort | Dependencies |
|----|-------|--------|--------------|
| INFRA-002 | Database Connection Pooling | XS (30m) | None |
| INFRA-003 | Multi-Worker Uvicorn | XS (5m) | None |
| SEC-001 | Fix XSS in Customer Autocomplete | S (1h) | None |
| SEC-002 | Fix Unauthenticated Contractor Endpoint | S (30m) | None |
| SEC-003 | Reduce JWT Token Expiry + Refresh | S (2-3h) | None |
| SEC-005 | Tighten CORS Regex | XS (30m) | None |
| PAY-001 | Fix Stripe Webhook Error Handling | S (30m) | None |

### P1 Reliability (6 tickets)
| ID | Title | Effort | Dependencies |
|----|-------|--------|--------------|
| INFRA-001 | Persistent File Storage (S3) | M (4-6h) | None |
| INFRA-004 | Redis Caching Layer | M (4h) | None |
| INFRA-005 | Database Indexes | S (2h) | INFRA-002 |
| INFRA-006 | Claude API Retry Logic | S (2h) | None |
| INFRA-007 | Comprehensive Health Check | XS (1h) | INFRA-004 |
| INFRA-008 | Structured Logging | S (3h) | None |

### P2/P3 Scale (5 tickets)
| ID | Title | Effort | Dependencies |
|----|-------|--------|--------------|
| INFRA-009 | Circuit Breakers for External APIs | M (4h) | INFRA-006 |
| INFRA-010 | Alerting (PagerDuty/OpsGenie) | S (2h) | INFRA-008 |
| SEC-004 | Per-User Rate Limiting | M (4h) | INFRA-004 |
| SEC-006 | Key Rotation Process | S (2h) | None |
| QA-002 | Basic Test Suite | L (8h) | All above |

---

## PR Batching Strategy

### PR 1: Foundation & Critical Security
**Branch**: `prod-ready/foundation-security`
**Tickets**: INFRA-002, INFRA-003, SEC-001, SEC-002, SEC-005, PAY-001
**Parallelizable**: YES (all independent)
**Effort**: ~4 hours

**Rationale**: These are quick wins with no dependencies. Deploy first to immediately improve security posture.

### PR 2: Authentication Hardening
**Branch**: `prod-ready/auth-hardening`
**Tickets**: SEC-003 (JWT + Refresh Tokens)
**Parallelizable**: NO (single complex feature)
**Effort**: ~3 hours

**Rationale**: Refresh token flow requires careful implementation and testing. Separate PR for focused review.

### PR 3: Data Layer & Storage
**Branch**: `prod-ready/data-layer`
**Tickets**: INFRA-001, INFRA-004, INFRA-005, INFRA-008
**Parallelizable**: PARTIALLY (INFRA-001/004/008 parallel, INFRA-005 after 002 merged)
**Effort**: ~12 hours

**Rationale**: Storage (S3), caching (Redis), indexes, and logging form the data infrastructure layer.

### PR 4: Resilience & Observability
**Branch**: `prod-ready/resilience`
**Tickets**: INFRA-006, INFRA-007, INFRA-009, INFRA-010
**Parallelizable**: PARTIALLY (006/010 parallel, 007/009 depend on 004/006)
**Effort**: ~9 hours

**Rationale**: Retry logic, health checks, circuit breakers, and alerting form the resilience layer.

### PR 5: Rate Limiting, Governance & Tests
**Branch**: `prod-ready/governance-tests`
**Tickets**: SEC-004, SEC-006, QA-002
**Parallelizable**: PARTIALLY (004/006 parallel, QA-002 last)
**Effort**: ~14 hours

**Rationale**: Final governance features plus comprehensive test suite to validate everything.

---

## Dependency Graph

```
                    [START]
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼
[PR1: Foundation]  [PR2: Auth]      [PR3: Data Layer]
INFRA-002,003      SEC-003          INFRA-001,004,005,008
SEC-001,002,005
PAY-001
    │                  │                  │
    └──────────────────┼──────────────────┘
                       │
                       ▼
              [PR4: Resilience]
              INFRA-006,007,009,010
                       │
                       ▼
              [PR5: Governance+Tests]
              SEC-004,006, QA-002
                       │
                       ▼
                    [DONE]
```

**Critical Path**: PR1 → PR3 → PR4 → PR5
**Parallel Track**: PR2 can run alongside PR1-PR3

---

## Context Preservation Architecture

### State Files

**1. `ORCHESTRATOR_STATE.md`** - Master state tracker
```markdown
## Current Phase
PR: [1-5]
Status: [planning|in_progress|testing|merging|complete]

## Completed Work
- [x] INFRA-002: Connection pooling (PR #123)
- [x] SEC-001: XSS fix (PR #123)

## In Progress
- [ ] INFRA-001: S3 storage (agent-id: abc123)

## Failed/Blocked
- INFRA-004: Redis - blocked on Railway addon (see DECISION_QUEUE.md)

## Test Results
PR1: 47/47 passed
PR2: pending

## Next Actions
1. Wait for INFRA-004 Railway addon
2. Continue with INFRA-006
```

**2. `AGENT_REGISTRY.md`** - Track spawned agents
```markdown
## Active Agents
| ID | Ticket | Status | Started | Last Update |
|----|--------|--------|---------|-------------|
| agent-001 | INFRA-002 | complete | 10:00 | 10:15 |
| agent-002 | SEC-001 | in_progress | 10:05 | 10:20 |
```

**3. `TEST_RESULTS.md`** - Test output log
```markdown
## PR1 Tests (2025-12-23 10:30)
✅ test_connection_pooling: PASSED
✅ test_xss_sanitization: PASSED
❌ test_cors_rejection: FAILED - regex too permissive
   → Fixed in commit abc123
✅ test_cors_rejection: PASSED (retry)
```

### Context Handoff Protocol

Before spawning any agent:
1. Read `ORCHESTRATOR_STATE.md` for current state
2. Read `AGENT_REGISTRY.md` for active work
3. Update state file with new agent entry
4. Include relevant context in agent prompt

After agent completion:
1. Agent writes results to `TEST_RESULTS.md`
2. Orchestrator updates `ORCHESTRATOR_STATE.md`
3. Orchestrator updates `AGENT_REGISTRY.md`
4. If failed, add to `DECISION_QUEUE.md` for review

---

## Orchestrator Execution Protocol

### Phase 0: Setup (5 minutes)
```
1. Create git worktree for isolation:
   git worktree add ../quoted-prod-ready main

2. Initialize state files:
   - Create ORCHESTRATOR_STATE.md
   - Create AGENT_REGISTRY.md
   - Create TEST_RESULTS.md

3. Verify environment:
   - Check Railway CLI access
   - Verify database connectivity
   - Confirm API keys present
```

### Phase 1: PR1 - Foundation & Critical Security

**Agent Dispatch Strategy**: 6 parallel agents

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                              │
│  Spawns 6 agents simultaneously for PR1 tickets             │
└─────────────────────────────────────────────────────────────┘
       │         │         │         │         │         │
       ▼         ▼         ▼         ▼         ▼         ▼
   [Agent1]  [Agent2]  [Agent3]  [Agent4]  [Agent5]  [Agent6]
   INFRA-002 INFRA-003 SEC-001   SEC-002   SEC-005   PAY-001
   Pool cfg  Workers   XSS fix   Auth fix  CORS fix  Webhook
       │         │         │         │         │         │
       └─────────┴─────────┴─────────┴─────────┴─────────┘
                              │
                              ▼
                    [Orchestrator Merge]
                    - Combine all changes
                    - Run integration tests
                    - Create PR1
```

**Agent 1 Prompt (INFRA-002)**:
```
TASK: Implement database connection pooling for production scale.

CONTEXT:
- File: backend/services/database.py:26
- Current: `engine = create_async_engine(settings.async_database_url, echo=False)`
- Problem: No pool_size, max_overflow, pool_timeout parameters

REQUIREMENTS:
1. Add connection pool parameters:
   - pool_size=20
   - max_overflow=10
   - pool_timeout=30
   - pool_recycle=1800
2. Add pool_pre_ping=True for connection health
3. Test with concurrent requests

SUCCESS CRITERIA:
- Connection pool visible in logs
- No connection exhaustion under load
- Existing tests pass

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent 2 Prompt (INFRA-003)**:
```
TASK: Configure multi-worker uvicorn deployment.

CONTEXT:
- File: railway.json (or Procfile if used)
- Current: Single worker uvicorn
- Problem: One slow request blocks everyone

REQUIREMENTS:
1. Update start command to use --workers 4
2. Consider gunicorn wrapper for production
3. Ensure graceful shutdown works

SUCCESS CRITERIA:
- 4 workers visible in Railway logs
- Concurrent requests handled properly
- No startup errors

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent 3 Prompt (SEC-001)**:
```
TASK: Fix XSS vulnerability in customer autocomplete.

CONTEXT:
- File: frontend/index.html
- Problem: Customer names rendered with innerHTML
- Attack vector: <script>alert('xss')</script> in customer name

REQUIREMENTS:
1. Find all innerHTML usage with user data
2. Replace with textContent or createElement
3. Add Content-Security-Policy header (optional, document if skipped)
4. Test with XSS payload in customer name

SUCCESS CRITERIA:
- XSS payloads render as text, not executed
- Autocomplete still works correctly
- No visual regressions

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent 4 Prompt (SEC-002)**:
```
TASK: Fix unauthenticated contractor endpoint.

CONTEXT:
- File: backend/api/contractors.py
- Problem: Some endpoints missing get_current_contractor dependency
- Risk: Any user can access any contractor's data

REQUIREMENTS:
1. Audit all endpoints in contractors.py
2. Add authentication dependency where missing
3. Add ownership verification (contractor_id == current_user)
4. Return 401 for unauthenticated, 403 for unauthorized

SUCCESS CRITERIA:
- curl without token returns 401
- curl with wrong user token returns 403
- Legitimate requests work normally

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent 5 Prompt (SEC-005)**:
```
TASK: Tighten CORS regex to only allow Quoted's Railway domains.

CONTEXT:
- File: backend/main.py:141
- Current: `allow_origin_regex=r"https://.*\.up\.railway\.app"`
- Problem: Any Railway subdomain allowed (security risk)

REQUIREMENTS:
1. Restrict to Quoted's specific Railway patterns:
   - pr-\d+-quoted.up.railway.app (preview)
   - web-production-*.up.railway.app (production)
2. Document allowed patterns in comments
3. Test rejection of other Railway domains

SUCCESS CRITERIA:
- Quoted domains allowed
- Random Railway domains rejected
- No CORS errors on production

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent 6 Prompt (PAY-001)**:
```
TASK: Fix Stripe webhook error handling.

CONTEXT:
- File: backend/api/billing.py
- Problem: Webhook always returns 200, even on errors
- Impact: Stripe won't retry failed webhooks

REQUIREMENTS:
1. Return 500 on processing errors (Stripe will retry)
2. Return 400 on signature verification failure
3. Add logging for all webhook events
4. Test with Stripe CLI: stripe listen --forward-to localhost:8000/api/billing/webhook

SUCCESS CRITERIA:
- Failed processing returns 500
- Invalid signature returns 400
- Successful processing returns 200
- Logs show webhook details

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

### Phase 2: PR2 - Authentication Hardening

**Agent Dispatch Strategy**: 1 agent (complex, sequential work)

```
TASK: Implement refresh token flow and reduce JWT expiry.

CONTEXT:
- File: backend/config.py:33 - jwt_expire_minutes: int = 60 * 24 * 7
- File: backend/api/auth.py - current auth flow
- Problem: 7-day tokens are high risk if stolen

REQUIREMENTS:
1. Reduce access token expiry to 15 minutes
2. Create refresh token with 7-day expiry
3. Store refresh tokens in database (new table)
4. Add /api/auth/refresh endpoint
5. Update frontend to auto-refresh tokens
6. Add token revocation capability
7. Handle concurrent refresh requests safely

IMPLEMENTATION PLAN:
1. Create RefreshToken model in backend/models/database.py
2. Add refresh token generation to auth flow
3. Create /api/auth/refresh endpoint
4. Update frontend auth.js to handle refresh
5. Add /api/auth/logout to revoke tokens
6. Test full flow: login → expire → refresh → logout

SUCCESS CRITERIA:
- Access tokens expire in 15 minutes
- Refresh flow is seamless (no user interruption)
- Logout invalidates refresh token
- Concurrent refreshes don't create duplicates

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

### Phase 3: PR3 - Data Layer & Storage

**Agent Dispatch Strategy**: 3 parallel agents + 1 sequential

```
[Parallel]
- Agent A: INFRA-001 (S3 storage)
- Agent B: INFRA-004 (Redis caching)
- Agent C: INFRA-008 (Structured logging)

[Sequential - after PR1 merged]
- Agent D: INFRA-005 (Database indexes)
```

**Agent A Prompt (INFRA-001)**:
```
TASK: Implement persistent file storage with S3.

CONTEXT:
- File: backend/config.py:58-63 - storage_type, storage_path
- Files: backend/services/pdf_service.py - PDF generation
- Problem: ./data/ directory lost on Railway redeploy

REQUIREMENTS:
1. Add boto3 to requirements.txt
2. Add S3 config to Settings (s3_bucket, aws_region, aws_access_key, aws_secret_key)
3. Create backend/services/storage_service.py:
   - upload_file(local_path, s3_key) → s3_url
   - download_file(s3_key, local_path)
   - delete_file(s3_key)
   - get_presigned_url(s3_key, expires=3600)
4. Update pdf_service.py to use storage_service
5. Keep local fallback for development
6. Migrate existing ./data/pdfs to S3 (one-time script)

SUCCESS CRITERIA:
- PDFs stored in S3 in production
- Local storage works in development
- Presigned URLs work for PDF access
- Old PDFs migrated successfully

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent B Prompt (INFRA-004)**:
```
TASK: Add Redis caching layer.

CONTEXT:
- No Redis currently configured
- Need: Railway Redis addon or external Redis
- Caching targets: contractor profiles, pricing categories, templates

REQUIREMENTS:
1. Add redis[hiredis] to requirements.txt
2. Add Redis config to Settings (redis_url)
3. Create backend/services/cache_service.py:
   - get(key) → value or None
   - set(key, value, ttl=3600)
   - delete(key)
   - invalidate_pattern(pattern)
4. Add caching to high-frequency endpoints:
   - GET /api/contractors/me (5 min TTL)
   - GET /api/pricing-brain/categories (10 min TTL)
5. Add cache invalidation on updates
6. Graceful degradation if Redis unavailable

SUCCESS CRITERIA:
- Cache hits visible in logs
- Response times improved for cached endpoints
- Cache invalidation works on updates
- App works (slower) without Redis

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent C Prompt (INFRA-008)**:
```
TASK: Replace print() with structured logging.

CONTEXT:
- Files: Multiple backend/*.py files use print()
- Problem: No log levels, no structured format, not searchable

REQUIREMENTS:
1. Add structlog to requirements.txt
2. Configure structlog in backend/config.py or new logging.py:
   - JSON format in production
   - Console format in development
   - Add timestamp, level, module, request_id
3. Replace all print() statements with appropriate log levels:
   - info: Normal operations
   - warning: Recoverable issues
   - error: Failures
   - debug: Detailed tracing
4. Add request_id middleware for tracing
5. Test log output in both formats

SUCCESS CRITERIA:
- No print() statements remain
- JSON logs in production
- Request IDs trace through logs
- Log levels filter correctly

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent D Prompt (INFRA-005)**:
```
TASK: Add database indexes for common queries.

CONTEXT:
- Models: backend/models/database.py
- Slow queries: quotes by contractor, customers by contractor, invoices by quote

REQUIREMENTS:
1. Analyze common query patterns (check API endpoints)
2. Create Alembic migration with indexes:
   - quotes(contractor_id)
   - quotes(created_at)
   - quotes(customer_id) if exists
   - customers(contractor_id)
   - invoices(quote_id)
   - invoices(contractor_id)
3. Add composite indexes where beneficial
4. Test with EXPLAIN ANALYZE before/after

SUCCESS CRITERIA:
- Migration runs without errors
- Query plans show index usage
- 5x+ improvement on listing queries

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

### Phase 4: PR4 - Resilience & Observability

**Agent Dispatch Strategy**: 2 parallel + 2 sequential

```
[Parallel]
- Agent E: INFRA-006 (Claude API retry)
- Agent F: INFRA-010 (Alerting)

[Sequential - after Phase 3]
- Agent G: INFRA-007 (Health check - needs Redis)
- Agent H: INFRA-009 (Circuit breakers - extends retry logic)
```

**Agent E Prompt (INFRA-006)**:
```
TASK: Implement retry logic for Claude API calls.

CONTEXT:
- File: backend/services/claude_service.py
- Problem: Single API call, no retry on transient failures
- Claude API has occasional 5xx errors, rate limits

REQUIREMENTS:
1. Add tenacity to requirements.txt
2. Add retry decorator to Claude API calls:
   - retry_if_exception_type(APIError)
   - wait_exponential(multiplier=1, min=2, max=30)
   - stop_after_attempt(3)
3. Handle specific error codes:
   - 429: Rate limit - longer backoff
   - 5xx: Server error - normal retry
   - 4xx: Client error - don't retry
4. Log retry attempts with attempt number
5. Surface final error to user gracefully

SUCCESS CRITERIA:
- Transient errors retried automatically
- Rate limits handled with backoff
- Client errors fail fast
- Logs show retry attempts

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent F Prompt (INFRA-010)**:
```
TASK: Set up alerting with webhook integration.

CONTEXT:
- No alerting currently
- Options: PagerDuty, OpsGenie, simple webhook
- For MVP: Start with Slack webhook or email alerts

REQUIREMENTS:
1. Add alerting config to Settings (alert_webhook_url, alert_email)
2. Create backend/services/alerting_service.py:
   - send_alert(severity, title, message, context)
   - Severity: critical, warning, info
3. Integrate with existing error handling:
   - 5xx errors → critical alert
   - High error rate → warning alert
   - Health check failures → critical alert
4. Add rate limiting to prevent alert storms
5. Document escalation policy in code comments

SUCCESS CRITERIA:
- Critical errors trigger alerts
- No duplicate/storm alerts
- Alert contains useful context
- Test alert endpoint works

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent G Prompt (INFRA-007)**:
```
TASK: Implement comprehensive health check.

CONTEXT:
- File: backend/main.py:176-179
- Current: Returns {"status": "healthy"} without checking anything
- Need: Verify database, Redis, external APIs

REQUIREMENTS:
1. Create /health/live (liveness - is app running?)
2. Create /health/ready (readiness - are dependencies up?)
3. Ready check should verify:
   - Database connectivity (simple query)
   - Redis connectivity (PING)
   - Required API keys present
4. Return 503 when dependencies down
5. Include response times in health output
6. Don't expose sensitive info in response

SUCCESS CRITERIA:
- /health/live always returns 200 if app running
- /health/ready returns 503 when DB down
- Response includes dependency status
- Railway uses /health/ready for routing

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent H Prompt (INFRA-009)**:
```
TASK: Implement circuit breakers for external APIs.

CONTEXT:
- External APIs: Claude, OpenAI (Whisper), Stripe, Resend
- Problem: If one goes down, all requests fail
- Need: Graceful degradation

REQUIREMENTS:
1. Add circuitbreaker to requirements.txt
2. Create backend/services/circuit_breaker.py:
   - Configure per-service circuit breakers
   - States: closed (normal), open (failing), half-open (testing)
   - Thresholds: 5 failures opens, 30s reset time
3. Apply to:
   - claude_service.py - quote generation
   - transcription (OpenAI) - voice processing
   - billing.py - Stripe calls
   - email_service.py - Resend calls
4. Add fallback behaviors where possible:
   - Claude down → queue for later, show "processing" state
   - Email down → queue for retry
5. Expose circuit states in health check

SUCCESS CRITERIA:
- Circuit opens after 5 failures
- Half-open tests after 30s
- Fallbacks work gracefully
- Health check shows circuit states

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

### Phase 5: PR5 - Governance & Tests

**Agent Dispatch Strategy**: 2 parallel + 1 sequential

```
[Parallel]
- Agent I: SEC-004 (Per-user rate limiting)
- Agent J: SEC-006 (Key rotation process)

[Sequential - after all above]
- Agent K: QA-002 (Test suite)
```

**Agent I Prompt (SEC-004)**:
```
TASK: Implement per-user rate limiting.

CONTEXT:
- File: backend/main.py:60 - limiter = Limiter(key_func=get_remote_address)
- Problem: IP-based limits block shared IPs (offices, VPNs)
- Need: User-based limits with IP fallback

REQUIREMENTS:
1. Create custom key function:
   - If authenticated: use user_id
   - If unauthenticated: use IP address
2. Store rate limit state in Redis (from INFRA-004)
3. Implement tiered limits:
   - Authenticated: 100 req/min
   - Unauthenticated: 20 req/min
   - Quote generation: 10 req/min (expensive)
4. Add rate limit headers to responses:
   - X-RateLimit-Limit
   - X-RateLimit-Remaining
   - X-RateLimit-Reset
5. Return 429 with helpful message

SUCCESS CRITERIA:
- User limits work across IPs
- IP limits work for unauthenticated
- Headers present in responses
- Redis stores rate limit state

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent J Prompt (SEC-006)**:
```
TASK: Create key rotation process and documentation.

CONTEXT:
- API keys: Anthropic, OpenAI, Stripe, Resend, PostHog
- No rotation process currently
- Risk: Leaked keys have unlimited validity

REQUIREMENTS:
1. Create docs/KEY_ROTATION_RUNBOOK.md:
   - Step-by-step for each service
   - Verification steps
   - Rollback procedure
2. Add key age tracking:
   - Store key creation date in Railway variables
   - Log warning if key > 90 days old
3. Create /api/admin/key-status endpoint (admin only):
   - Show key ages
   - Show last rotation date
4. Document in runbook:
   - How to rotate each key
   - Expected downtime (should be zero)
   - Who to notify

SUCCESS CRITERIA:
- Runbook covers all services
- Key age warnings in logs
- Admin endpoint shows status
- Rotation tested in staging

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

**Agent K Prompt (QA-002)**:
```
TASK: Create comprehensive test suite with CI.

CONTEXT:
- No pytest currently
- Need: Tests for all new infrastructure
- Target: 50% coverage on critical paths

REQUIREMENTS:
1. Set up pytest:
   - Add pytest, pytest-asyncio, pytest-cov to requirements.txt
   - Create pytest.ini with async settings
   - Create tests/ directory structure
2. Create test categories:
   - tests/unit/ - isolated function tests
   - tests/integration/ - API endpoint tests
   - tests/e2e/ - full flow tests
3. Write tests for new features:
   - test_connection_pooling.py
   - test_auth_refresh.py
   - test_storage_service.py
   - test_cache_service.py
   - test_circuit_breakers.py
   - test_rate_limiting.py
   - test_health_check.py
   - test_xss_prevention.py
   - test_webhook_handling.py
4. Create GitHub Actions workflow:
   - Run on PR and push to main
   - Require passing tests to merge
5. Add coverage report

SUCCESS CRITERIA:
- pytest runs successfully
- 50%+ coverage on critical paths
- CI runs on every PR
- Coverage report generated

OUTPUT: Write changes and test results to TEST_RESULTS.md
```

---

## Testing Protocol

### Per-Ticket Tests
Each agent must verify:
1. **Unit test**: Function works in isolation
2. **Integration test**: Feature works with dependencies
3. **Regression test**: Existing features still work

### Per-PR Tests
Before creating PR:
```bash
# Run full test suite
pytest tests/ -v --tb=short

# Run linting
ruff check backend/

# Check for security issues
bandit -r backend/

# Verify app starts
uvicorn backend.main:app --port 8001 &
curl http://localhost:8001/health
kill %1
```

### Pre-Merge Checklist
```markdown
- [ ] All tests pass locally
- [ ] No new lint errors
- [ ] No security warnings
- [ ] App starts successfully
- [ ] Manual smoke test completed
- [ ] PR description accurate
- [ ] ORCHESTRATOR_STATE.md updated
```

---

## Rollback Procedures

### Code Rollback
```bash
# Revert last commit
git revert HEAD --no-commit
git commit -m "Revert: [ticket-id] - reason"

# Revert entire PR
git revert -m 1 <merge-commit-hash>
```

### Railway Rollback
```bash
# List recent deployments
railway logs --last 20

# Rollback to previous deployment
railway up --environment production --rollback
```

### Database Rollback
```bash
# Alembic downgrade
alembic downgrade -1

# Full rollback to specific revision
alembic downgrade <revision>
```

### Feature Flag Rollback
1. Go to PostHog Dashboard
2. Feature Flags → Find flag → Disable
3. Takes effect in ~30 seconds

---

## Execution Commands

### Start Orchestration
```bash
# From quoted/ directory
cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant/quoted

# Initialize state files
touch ORCHESTRATOR_STATE.md AGENT_REGISTRY.md TEST_RESULTS.md

# Create feature branch
git checkout -b prod-ready/foundation-security

# Begin Phase 1
# (Orchestrator spawns agents here)
```

### Monitor Progress
```bash
# Watch state file
watch -n 5 cat ORCHESTRATOR_STATE.md

# Check agent status
cat AGENT_REGISTRY.md

# View test results
cat TEST_RESULTS.md
```

### Complete Phase
```bash
# After all agents complete
git add -A
git commit -m "PR1: Foundation & Critical Security

Implements: INFRA-002, INFRA-003, SEC-001, SEC-002, SEC-005, PAY-001

- Add database connection pooling
- Configure multi-worker uvicorn
- Fix XSS vulnerability in customer autocomplete
- Add authentication to contractor endpoints
- Tighten CORS regex
- Fix Stripe webhook error handling

All tests passing. See TEST_RESULTS.md for details.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Create PR
gh pr create --title "PR1: Foundation & Critical Security" --body "..."
```

---

## Orchestrator Prompt Template

When starting a fresh Claude Code session to orchestrate:

```
You are the Orchestrator Agent for Quoted production readiness.

READ THESE FILES FIRST:
1. /quoted/ORCHESTRATOR_PLAN.md - This plan
2. /quoted/ORCHESTRATOR_STATE.md - Current progress
3. /quoted/AGENT_REGISTRY.md - Active agents
4. /quoted/TEST_RESULTS.md - Test output

YOUR ROLE:
- Track overall progress across all PRs
- Spawn sub-agents for parallel work (use Task tool)
- Merge completed work into PRs
- Run tests after each phase
- Update state files continuously
- Escalate blockers to DECISION_QUEUE.md

CURRENT PHASE: [Read from ORCHESTRATOR_STATE.md]

NEXT ACTION: [Determined by current state]

CONSTRAINTS:
- Never proceed if tests are failing
- Always update state files after agent completion
- Create focused, small PRs
- Test before merging

BEGIN: Read state files and continue from current phase.
```

---

## Success Criteria

### PR1 Complete When:
- [ ] Connection pooling configured and tested
- [ ] Multi-worker uvicorn running
- [ ] XSS vulnerability fixed and tested
- [ ] All contractor endpoints authenticated
- [ ] CORS regex tightened
- [ ] Stripe webhooks return proper status codes
- [ ] All tests passing
- [ ] PR merged to main

### PR2 Complete When:
- [ ] Access tokens expire in 15 minutes
- [ ] Refresh token flow works seamlessly
- [ ] Token revocation works
- [ ] Frontend handles refresh automatically
- [ ] All tests passing
- [ ] PR merged to main

### PR3 Complete When:
- [ ] S3 storage working in production
- [ ] Redis caching reducing response times
- [ ] Database indexes improving query performance
- [ ] Structured logging in JSON format
- [ ] All tests passing
- [ ] PR merged to main

### PR4 Complete When:
- [ ] Claude API retries on transient failures
- [ ] Health check verifies all dependencies
- [ ] Circuit breakers prevent cascade failures
- [ ] Alerts fire on critical errors
- [ ] All tests passing
- [ ] PR merged to main

### PR5 Complete When:
- [ ] Per-user rate limiting working
- [ ] Key rotation runbook documented
- [ ] Test suite with 50%+ coverage
- [ ] CI pipeline running on PRs
- [ ] All tests passing
- [ ] PR merged to main

### Overall Complete When:
- [ ] All 5 PRs merged
- [ ] Production deployment successful
- [ ] No increase in error rate
- [ ] Performance metrics stable
- [ ] ENGINEERING_STATE.md updated
- [ ] DISCOVERY_BACKLOG.md tickets marked DEPLOYED

---

## Estimated Timeline

| Phase | PRs | Effort | Wall Clock (with parallelization) |
|-------|-----|--------|----------------------------------|
| Phase 1 | PR1 | 4h | 1h (6 parallel agents) |
| Phase 2 | PR2 | 3h | 3h (sequential) |
| Phase 3 | PR3 | 12h | 4h (3 parallel + 1 sequential) |
| Phase 4 | PR4 | 9h | 3h (2 parallel + 2 sequential) |
| Phase 5 | PR5 | 14h | 5h (2 parallel + 1 sequential) |
| **Total** | **5 PRs** | **42h** | **~16h** |

With aggressive parallelization and minimal context switching overhead, total wall clock time is approximately **16 hours** of continuous orchestrated execution.

---

## Finalized Decisions (CONFIRMED)

These decisions are **final** - implement exactly as specified:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **File Storage** | AWS S3 | Industry standard, durable, ~$0.02/GB/mo, presigned URLs for secure access |
| **Redis Provider** | Railway Redis addon | Same platform, simple setup, no external credentials |
| **Alerting** | Slack webhook | Immediate visibility, free tier sufficient, low friction setup |
| **JWT Access Token** | 15 minutes | Security best practice; refresh tokens handle UX seamlessly |

**Do not ask for confirmation on these.** Implement as specified.

### Required Environment Variables (Add to Railway)

Before PR3/PR4 can deploy, these must be set in Railway:

```bash
# S3 Storage (INFRA-001)
AWS_ACCESS_KEY_ID=<create IAM user with S3 access>
AWS_SECRET_ACCESS_KEY=<from IAM user>
AWS_S3_BUCKET=quoted-production
AWS_REGION=us-east-1

# Redis (INFRA-004) - Railway auto-sets this when addon enabled
REDIS_URL=<auto-populated by Railway Redis addon>

# Alerting (INFRA-010)
SLACK_WEBHOOK_URL=<create incoming webhook in Slack>
```

**Note**: The orchestrator will implement the code. Eddie must add env vars in Railway before deploying PR3/PR4.

### Risk Mitigations:
- Each PR is independently deployable and revertable
- Feature flags available for gradual rollout
- Tests run before every merge
- Monitoring in place before aggressive changes

### Post-Completion Checklist:
- [ ] Update DISCOVERY_BACKLOG.md (mark all 18 tickets DEPLOYED)
- [ ] Update ENGINEERING_STATE.md (new architecture summary)
- [ ] Create PRODUCTION_READINESS_COMPLETE.md celebration doc
- [ ] Schedule 1-week post-mortem review
