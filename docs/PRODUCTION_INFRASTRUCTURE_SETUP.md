# Production Infrastructure Setup Guide

This guide covers the new production infrastructure services added in the prod-ready PRs.

## Quick Start

**Minimum required:** Nothing new! All services have graceful fallbacks. The app works without any new environment variables - it just won't have caching, S3 storage, or enhanced monitoring.

**Recommended:** Add Redis for caching and Sentry DSN for error tracking.

## Environment Variables

### Already Configured (verify these exist)

```bash
# Core (required)
JWT_SECRET_KEY=...          # For authentication
DATABASE_URL=...            # PostgreSQL connection

# Payments (required for billing)
STRIPE_SECRET_KEY=...
STRIPE_PUBLISHABLE_KEY=...
STRIPE_WEBHOOK_SECRET=...

# Email (required for magic links)
RESEND_API_KEY=...

# AI (required for quotes)
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...

# Analytics (optional but recommended)
POSTHOG_API_KEY=...
SENTRY_DSN=...              # Now used by alerts service too
```

### New Variables (all optional)

#### Redis Caching (PR3: INFRA-004)

```bash
REDIS_URL=redis://...       # Railway Redis add-on URL
CACHE_TTL_DEFAULT=300       # Default cache TTL (5 min)
CACHE_TTL_CONTRACTOR=600    # Contractor profile TTL (10 min)
CACHE_TTL_PRICING=1800      # Pricing categories TTL (30 min)
```

**If not set:** App works normally, just no caching. Slightly slower repeated requests.

**To add on Railway:**
1. Go to your Railway project
2. Click "New" → "Database" → "Redis"
3. Copy the `REDIS_URL` from the Redis service
4. Add to your web service environment variables

#### S3 Storage (PR3: INFRA-001)

```bash
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=quoted-production
AWS_REGION=us-east-1
```

**If not set:** Files stored locally in `./data/` directory. Works fine for Railway (ephemeral but regenerated).

**To add:**
1. Create S3 bucket in AWS Console
2. Create IAM user with S3 access
3. Add credentials to Railway environment

#### Rate Limiting (PR5: SEC-004)

No new variables needed. Uses in-memory storage by default.

For distributed rate limiting across multiple instances:
```bash
REDIS_URL=redis://...       # Same Redis as caching
```

#### Key Rotation (PR5: SEC-006)

No new variables needed. Uses existing `JWT_SECRET_KEY` as the initial key.

## What Each Service Does

### Cache Service (`backend/services/cache.py`)

Caches frequently accessed data:
- Contractor profiles (10 min TTL)
- Pricing categories (30 min TTL)
- Quote templates (5 min TTL)

**Fallback:** Returns `None` on cache miss, app fetches from database.

### Storage Service (`backend/services/storage.py`)

Unified file storage for:
- Generated PDFs
- Uploaded logos
- Voice recordings

**Fallback:** Uses local filesystem (`./data/pdfs/`, `./data/uploads/`, `./data/logos/`).

### Resilience Service (`backend/services/resilience.py`)

Circuit breakers prevent cascading failures:
- **OpenAI:** 5 failures → open for 60s
- **Anthropic:** 3 failures → open for 30s
- **Stripe:** 3 failures → open for 30s
- **Resend:** 5 failures → open for 60s

Retry logic with exponential backoff for transient failures.

### Health Service (`backend/services/health.py`)

Two endpoints:
- `GET /health` - Quick check for load balancers (DB only)
- `GET /health/full` - Full check including external services

### Alerts Service (`backend/services/alerts.py`)

Sends alerts to Sentry for:
- Circuit breaker events
- Payment failures
- Security events
- External service errors

**Fallback:** Logs to console if Sentry not configured.

### Rate Limiting (`backend/services/rate_limiting.py`)

Tiered limits:
- Auth: 5 login attempts/minute
- Demo: 5 quotes/hour
- API reads: 120/minute
- API writes: 60/minute

### Key Rotation (`backend/services/key_rotation.py`)

Supports multiple active JWT keys for zero-downtime rotation.
Old tokens remain valid during rotation period (default 7 days).

## Testing After Deploy

### 1. Basic Health Check

```bash
curl https://quoted.it.com/health
# Should return: {"status": "healthy", "database": "ok"}
```

### 2. Full Health Check

```bash
curl https://quoted.it.com/health/full
# Returns status of all services including external
```

### 3. Rate Limiting Test

```bash
# This should work
curl https://quoted.it.com/api/info

# Hitting the same endpoint 200+ times quickly should trigger rate limit
for i in {1..200}; do curl -s https://quoted.it.com/api/info > /dev/null; done
curl https://quoted.it.com/api/info
# Should return 429 Too Many Requests with Retry-After header
```

### 4. Cache Test (if Redis configured)

Check health endpoint includes cache status:
```bash
curl https://quoted.it.com/health/full | jq .cache
# Should show: {"available": true, "latency_ms": ...}
```

## Monitoring

### Sentry Dashboard

After deploy, check Sentry for:
- No new errors
- Circuit breaker events (should be empty unless services failing)
- Performance metrics

### PostHog

Existing tracking continues to work. No changes needed.

## Rollback

If issues occur after merging:

1. **Quick rollback:** Revert the merge commit on `main`
2. **Selective disable:** Set feature flags in PostHog (if applicable)
3. **Service isolation:** Individual services fail gracefully

All new services are designed to not break existing functionality if they fail.

## Merge Order

```
1. prod-ready/foundation-security  (HTTPS, headers, validation)
2. prod-ready/auth-hardening       (JWT refresh security)
3. prod-ready/data-layer           (Redis, S3)
4. prod-ready/resilience           (circuit breakers, health)
5. prod-ready/governance           (rate limiting, key rotation, tests)
```

Each can be merged independently, but this order is recommended for cleanest git history.
