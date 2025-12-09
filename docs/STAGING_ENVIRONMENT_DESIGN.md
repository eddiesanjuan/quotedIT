# Staging Environment & Safe Deployment Pipeline

**DISC-073 Design Document**
**Status**: READY FOR IMPLEMENTATION
**Created**: 2025-12-08
**Executive Council**: CTO, CFO, CPO, CGO consensus

---

## Executive Summary

After evaluating three options for deployment safety, the recommendation is a **hybrid approach**: Railway Preview Environments (Option A) for pre-merge testing, combined with PostHog Feature Flags (Option C) for gradual rollout and instant rollback.

**Investment**: 2-3 hours setup, $0/month ongoing
**Benefit**: Zero user-impacting incidents from deployments

---

## The Problem

With 5 active beta users generating real quotes and more incoming via Reddit/LinkedIn acquisition:
- Pushing directly to production is risky
- Recent incidents (DISC-066 PDF failure, DISC-056 badge clipping) were caught by users
- Upcoming features (DISC-071 invoicing, DISC-072 PDF polish) touch core systems
- Bad deploy → negative word-of-mouth → 410K contractors on Reddit see "Quoted broke my quotes"

---

## Options Evaluated

### Option A: Railway Preview Environments (RECOMMENDED)
- **What**: PR-based preview deployments with isolated database
- **Cost**: $0 (included in Railway)
- **Setup**: ~2 hours
- **Pros**: Railway-native, zero maintenance, auto-deploy on PR
- **Cons**: Preview DBs are ephemeral, not for multi-day testing

### Option B: Separate Staging Branch + Environment (DEFERRED)
- **What**: Persistent staging.quoted.it.com with dedicated database
- **Cost**: ~$15-25/month
- **Setup**: ~8 hours
- **Pros**: Persistent environment, production-like data, clear mental model
- **Cons**: Fixed cost, database sync complexity, operational overhead
- **Defer Until**: 50+ paying users, $2K+ MRR

### Option C: Feature Flags + Gradual Rollout (RECOMMENDED)
- **What**: Ship behind PostHog feature flags, enable gradually
- **Cost**: $0 (PostHog free tier)
- **Setup**: ~1 hour
- **Pros**: Instant rollback, real production testing, zero infrastructure
- **Cons**: Requires discipline on flag cleanup, code complexity

---

## CEO Decision: Hybrid A + C

Implement both Railway Preview Environments AND Feature Flags. They solve different problems:

| Scenario | Solution |
|----------|----------|
| Pre-merge testing (does it work?) | Railway Preview |
| Gradual rollout (does it scale?) | Feature Flags |
| Instant rollback (oh no, disable it) | Feature Flags |
| Schema migration testing | Railway Preview |
| Real production data testing | Feature Flags |

---

## Implementation Plan

### Phase 1: Railway Preview Environments (1-2 hours)

**Step 1: Enable in Railway Dashboard**
1. Go to Railway project settings
2. Enable "Preview Deployments" toggle
3. Configure preview domain pattern: `pr-{number}-quoted.up.railway.app`

**Step 2: Update CORS Configuration**

In `backend/main.py`, update allowed origins to include Railway preview domains:

```python
# Add to CORS middleware origins list
origins = [
    "https://quoted.it.com",
    "https://www.quoted.it.com",
    "http://localhost:3000",
    "http://localhost:8000",
]

# Add Railway preview domains
if settings.environment != "production":
    origins.append("https://*.up.railway.app")  # Covers all preview environments
```

**Step 3: Test First Preview**
1. Create test PR with minor change
2. Verify preview auto-deploys
3. Test preview URL works
4. Merge and verify preview is cleaned up

**Step 4: Document Workflow**
Add to CLAUDE.md:
```
## Deployment Workflow

1. Create feature branch
2. Push → PR → Railway auto-deploys preview
3. Test on preview URL (10 min smoke test)
4. Merge to main → auto-deploy to production
5. Monitor PostHog/Sentry for 5 min
```

### Phase 2: Feature Flags Foundation (1 hour)

**Step 1: Create Flag Helper in Frontend**

Add to `frontend/index.html` (in the `<script>` section):

```javascript
// Feature flag helper
function isFeatureEnabled(flagKey, defaultValue = false) {
    if (!window.posthog) return defaultValue;
    return posthog.isFeatureEnabled(flagKey) ?? defaultValue;
}

// Wrapper for gradual rollout
function showFeature(flagKey, showCallback, hideCallback = () => {}) {
    if (isFeatureEnabled(flagKey)) {
        showCallback();
    } else {
        hideCallback();
    }
}
```

**Step 2: Create Standard Flag Names**

| Flag Key | Feature | Default |
|----------|---------|---------|
| `invoicing_enabled` | DISC-071 quote-to-invoice | false |
| `new_pdf_templates` | DISC-072 PDF polish | false |
| `voice_template_customization` | DISC-070 voice PDF | false |

**Step 3: Backend Feature Flag Check**

Add to `backend/services/feature_flags.py`:

```python
import posthog

def is_feature_enabled(flag_key: str, user_id: str = None, default: bool = False) -> bool:
    """Check if feature flag is enabled for user."""
    if not settings.posthog_api_key:
        return default

    try:
        return posthog.feature_enabled(flag_key, user_id or "anonymous") or default
    except Exception:
        return default
```

**Step 4: Establish Flag Discipline**

Add to CLAUDE.md:
```
## Feature Flag Discipline

1. New features ship behind flags (default: false)
2. Enable for Eddie first (48 hours)
3. Enable for all users after validation
4. Remove flag after 2 weeks in production
5. Never ship broken code "behind a flag" - code must work

Flag naming: `{feature}_enabled` (e.g., `invoicing_enabled`)
```

### Phase 3: Rollback Procedure (30 min)

**Step 1: Document Rollback Options**

| Situation | Action | Time |
|-----------|--------|------|
| Feature bug | Disable feature flag in PostHog | 30 seconds |
| Code regression | Revert commit, push to main | 5 minutes |
| Database corruption | Restore from Railway backup | 30 minutes |

**Step 2: Create Emergency Runbook**

Add `docs/EMERGENCY_RUNBOOK.md`:
```markdown
# Emergency Runbook

## P1: Production Down
1. Check Railway dashboard for deployment status
2. If recent deploy: revert commit, push
3. If database issue: check Sentry logs, restore backup
4. Notify Eddie via text

## P2: Feature Broken
1. Disable feature flag in PostHog dashboard
2. Investigate in non-production hours
3. Fix, test in preview, re-enable

## P3: Minor Issue
1. Create ticket (DISC-XXX)
2. Fix in normal workflow
3. No emergency action needed
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| User-impacting incidents | 0 per month | Sentry P1 alerts |
| Rollback time (feature flag) | < 1 minute | Manual timing |
| Rollback time (code revert) | < 10 minutes | Git + Railway deploy |
| Preview environment usage | 100% of PRs | Railway dashboard |

---

## Cost Analysis

| Item | Monthly Cost |
|------|--------------|
| Railway Preview Environments | $0 (included) |
| PostHog Feature Flags | $0 (free tier) |
| **Total** | **$0** |

**Comparison to Option B (separate staging)**: Saves $15-25/month

---

## Timeline

| Day | Task | Owner |
|-----|------|-------|
| Day 1 | Enable Railway Preview Environments | Engineering |
| Day 1 | Update CORS configuration | Engineering |
| Day 1 | Add feature flag helper to frontend | Engineering |
| Day 1 | Document workflow in CLAUDE.md | Engineering |
| Day 2 | Test first feature behind flag | Engineering |
| Day 2 | Create emergency runbook | Engineering |

**Total**: 2-3 hours over 1-2 days

---

## Future: Option B (Separate Staging)

**Trigger**: 50+ paying users OR first revenue milestone ($2K MRR)

**Scope**:
- Create `staging` branch
- Deploy second Railway service: staging.quoted.it.com
- Configure daily database clone from production
- Add staging-specific environment variables

**Estimated Effort**: 8-12 hours
**Monthly Cost**: $15-25/month

**Why Defer**: At 5 users, preview environments + feature flags provide sufficient safety. The operational overhead of maintaining a separate staging environment is not justified until scale demands it.

---

## Appendix: Executive Council Recommendations

### CTO Recommendation
- **Vote**: Option A (Railway Preview)
- **Rationale**: Minimal setup, zero maintenance, Railway-native
- **Concern**: Preview DBs ephemeral, not for multi-day testing

### CFO Recommendation
- **Vote**: Option C (Feature Flags) + Defer B
- **Rationale**: At 5 users, staging ROI is negative
- **Concern**: Feature flags require discipline on cleanup

### CPO Recommendation
- **Vote**: Option B (Separate Staging)
- **Rationale**: Persistent environment for debugging
- **Concern**: Deferred for now, implement at 50+ users

### CGO Recommendation
- **Vote**: Option A (Railway Preview)
- **Rationale**: First-impression protection critical for growth
- **Concern**: Implement BEFORE DISC-071/072
