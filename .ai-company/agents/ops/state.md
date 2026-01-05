# Ops Agent State

Last Run: 2026-01-05T15:29:22Z
Status: MONITORING (YELLOW - non-critical alert active)

## System Health

| Component | Status | Last Check |
|-----------|--------|------------|
| Overall | GREEN | 2026-01-05T15:29:22Z |
| API | GREEN | 2026-01-05T15:29:22Z |
| Database | GREEN (166ms latency) | 2026-01-05T15:29:22Z |
| Cache (Redis) | GREEN (2.9ms, 1.03M used) | 2026-01-05T15:29:22Z |
| Railway | GREEN | 2026-01-05T15:29:22Z |

## Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Error Rate | 0% | <1% | GREEN |
| DB Response Time | 166ms | <500ms | GREEN |
| Cache Response Time | 2.9ms | <50ms | GREEN |
| Uptime | 100% (since 15:24 UTC) | 99.9% | GREEN |

## Active Alerts

### YELLOW - Missing Database Column (Non-Critical)

**Issue**: `column contractors.feedback_email_sent does not exist`

**Impact**: The `run_feedback_drip` scheduled job fails every run. This is a background feature for sending feedback emails to new users - it does NOT affect core quote generation, authentication, or user-facing functionality.

**Frequency**: 4 errors logged at 14:00 UTC (daily cron job)

**Root Cause**: Code references `feedback_email_sent` column that was never migrated to production database.

**Recommended Fix**: Run database migration to add the missing column, or disable the feedback_drip job until migration is applied.

## Pending Fixes

- [ ] DISC-147: Add `feedback_email_sent` column to contractors table (for feedback drip feature)
  - Migration file created: `backend/alembic/add_feedback_email_sent_column.sql`
  - Requires manual execution: `ALTER TABLE contractors ADD COLUMN IF NOT EXISTS feedback_email_sent INTEGER;`
  - Non-critical: Only affects feedback drip emails (day 3, day 7)

## Recent Incidents

*No critical incidents - system operational*

## Notes

### Health Check Summary (2026-01-05 15:29 UTC)

**Production Status**: Fully operational

**Container Restart**: 15:24 UTC today (clean startup)

**Verified Working**:
- Landing page loads correctly (https://quoted.it.com)
- Health endpoint returns healthy: `{"status":"healthy"}`
- Database connected and responsive (166ms latency)
- Cache (Redis) operational (2.9ms latency, 1.03M memory used)
- All scheduled jobs registered and running (task reminders, smart followups, etc.)
- No ERROR-level logs since container restart
- Railway deployment stable (web service in production)

**Non-Critical Issues**:
1. **Sentry DSN not configured** - Error tracking disabled (INFO level, not a blocker)
2. **JWT_SECRET_KEY warning** - Key is shorter than 32 chars (security warning, not blocking)
3. **feedback_email_sent column missing** - Background drip feature broken, needs DB migration
   - *Note*: Since container restarted at 15:24 UTC (after 14:00 UTC run time), this error will not recur until tomorrow's 14:00 UTC run

**Overall Assessment**: GREEN - Core functionality fully operational. The missing column affects only the feedback drip feature which is a non-critical background task. All user-facing features (quote generation, authentication, CRM, PDF export) are unaffected.
