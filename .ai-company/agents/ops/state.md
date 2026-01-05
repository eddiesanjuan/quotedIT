# Ops Agent State

Last Run: 2026-01-05T14:45:00Z
Status: MONITORING (YELLOW - non-critical alert active)

## System Health

| Component | Status | Last Check |
|-----------|--------|------------|
| Overall | GREEN | 2026-01-05T14:15:00Z |
| API | GREEN | 2026-01-05T14:15:00Z |
| Database | GREEN (147ms latency) | 2026-01-05T14:15:00Z |
| Cache (Redis) | GREEN (2.9ms, 1.03M used) | 2026-01-05T14:15:00Z |
| Railway | GREEN | 2026-01-05T14:15:00Z |

## Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Error Rate | <1% | <1% | GREEN |
| DB Response Time | 147ms | <500ms | GREEN |
| Cache Response Time | 2.9ms | <50ms | GREEN |
| Uptime | 100% (since 13:55 UTC) | 99.9% | GREEN |

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

### Health Check Summary (2026-01-05)

**Production Status**: Fully operational

**Verified Working**:
- Landing page loads correctly (https://quoted.it.com)
- Health endpoint returns healthy: `{"status":"healthy"}`
- Database connected and responsive (147ms latency)
- Cache (Redis) operational (2.9ms latency, 1.03M memory used)
- All scheduled jobs running (task reminders, smart followups, etc.)
- No console errors on frontend
- Railway deployment stable (web service in production)

**Non-Critical Issues**:
1. **Sentry DSN not configured** - Error tracking disabled (INFO level, not a blocker)
2. **feedback_email_sent column missing** - Background drip feature broken, needs DB migration

**Overall Assessment**: GREEN - Core functionality fully operational. The missing column affects only the feedback drip feature which is a non-critical background task. All user-facing features (quote generation, authentication, CRM, PDF export) are unaffected.
