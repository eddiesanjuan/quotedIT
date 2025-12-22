# Regression Gate Protocol

**DISC-108**: Quality checkpoint before commits in autonomous operations

---

## Overview

Failures compound across autonomous cycles. A broken commit poisons subsequent work. This protocol prevents broken code from reaching the repository.

## The Gate

**Before ANY commit, this check must pass:**

```bash
# Run regression tests
cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant/quoted/backend
pytest -x --tb=short 2>/dev/null || echo "NO_TESTS_CONFIGURED"
```

## Decision Tree

```
Run pytest
    ↓
Tests pass? ─── YES → Proceed with commit
    ↓ NO
    ↓
Log failure to HANDOFF.md "Failed & Fixed" section
    ↓
Attempt fix (max 2 attempts)
    ↓
Fixed? ─── YES → Proceed with commit
    ↓ NO
    ↓
Escalate to founder via DECISION_QUEUE.md
DO NOT COMMIT
```

## Integration in /quoted-run

Insert as Phase 3.5 (after implementation, before commit):

```
Phase 3: Execution
├── Step 3.3: Implementation complete
├── [NEW] Step 3.5: Regression Gate
│   ├── Run pytest -x --tb=short
│   ├── Pass → Continue to Step 3.6
│   └── Fail → Fix or escalate (DO NOT COMMIT)
└── Step 3.6: Commit to branch
```

## Test Status

**Current State**: Minimal test coverage

| Area | Tests Exist | Coverage |
|------|-------------|----------|
| Backend API | Partial | ~20% |
| Claude Service | No | 0% |
| PDF Service | No | 0% |
| Billing | No | 0% |

**Fallback When No Tests**: If pytest returns "no tests" or "not configured":
1. Log this to QUOTED_RUN_LIVE.md
2. Proceed with commit (can't block on missing tests)
3. Add "improve test coverage" as a DISCOVERED ticket

## Logging

All gate results logged to `QUOTED_RUN_LIVE.md`:

```
[HH:MM:SS]   🚦 Regression Gate:
   Result: PASS (3 tests, 0.2s)
   Proceeding to commit...

[HH:MM:SS]   🚦 Regression Gate:
   Result: FAIL
   test_auth.py::test_magic_link - AssertionError
   Attempting fix...

[HH:MM:SS]   🚦 Regression Gate:
   Result: NO_TESTS
   Note: No pytest configuration found. Proceeding with commit.
   Ticket created: DISC-XXX (add regression tests)
```

## Failure Logging to HANDOFF.md

When tests fail and are fixed, add to HANDOFF.md:

```markdown
## Failed & Fixed
| Date | What Failed | How Fixed | Lesson |
|------|-------------|-----------|--------|
| 2025-12-21 | test_auth.py - magic link validation | Fixed token expiry check | Always verify token expiry before validation |
```

## Escape Hatches

1. **Critical Hotfix**: Can bypass with explicit logging: "Bypassing gate for critical fix: [reason]"
2. **No Tests Available**: Proceed but log the gap
3. **Flaky Tests**: Mark test as flaky, proceed, create ticket to fix

## Implementation Checklist

- [ ] pytest installed and configured in backend/
- [ ] Basic smoke tests for critical paths
- [ ] Gate check added to /quoted-run Phase 3.5
- [ ] Failure logging to HANDOFF.md implemented
- [ ] DECISION_QUEUE.md escalation path tested

## Future Enhancements

1. **Pre-commit Hook**: Add git pre-commit hook for local development
2. **Coverage Threshold**: Require minimum coverage % for new code
3. **Integration Tests**: Add Railway preview environment tests
4. **Performance Tests**: Track response time regression

---

*Created: 2025-12-21 | DISC-108*
