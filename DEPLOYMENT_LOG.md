# Deployment Log

**Last Updated**: 2025-12-03
**Auto-Updated**: On each deployment

---

## Recent Deployments (Last 30)

| Date | Commit | Description | Status |
|------|--------|-------------|--------|
| 2025-12-04 | 7488616 | Fix mobile quote disappearing after generation (BUG-006) | **DEPLOYED** |
| 2025-12-03 | 6bdc08e | Fix Stripe product IDs to production values | **DEPLOYED** |
| 2025-12-03 | e3c8786 | Add Customer memory autocomplete (DISC-022) | **DEPLOYED** |
| 2025-12-03 | 1c3d0d3 | Add Viral footer enhancement on shared quotes (DISC-024) | **DEPLOYED** |
| 2025-12-03 | 8672a3e | Add Email signature referral hack (DISC-021) | **DEPLOYED** |
| 2025-12-03 | 136d244 | Add Trial grace period with soft warnings (DISC-018) | **DEPLOYED** |
| 2025-12-03 | 0ade9e9 | Add "Try It First" fast activation path (DISC-019) | **DEPLOYED** |
| 2025-12-03 | 048d173 | Add Exit-intent survey on landing page (DISC-020) | **DEPLOYED** |
| 2025-12-03 | 94ba6dc | Add Custom logo upload for PDF quotes (DISC-016) | **DEPLOYED** |
| 2025-12-03 | 8c88de2 | Add Trial abuse prevention - email normalization (DISC-017) | **DEPLOYED** |
| 2025-12-03 | 5c1ebc3 | Add Referral visibility at first quote celebration (DISC-002) | **DEPLOYED** |
| 2025-12-03 | 9607ccf | Add Analytics funnel events for full conversion tracking (DISC-004) | **DEPLOYED** |
| 2025-12-03 | 412f5da | Add Single-click trial upgrade with urgency messaging (DISC-005) | **DEPLOYED** |
| 2025-12-03 | 8628869 | Add First quote activation modal for post-onboarding (DISC-001) | **DEPLOYED** |
| 2025-12-03 | 3d8f8fa | Add Beta spots counter for social proof scarcity (DISC-015) | **DEPLOYED** |
| 2025-12-03 | fd82e2f | Update Landing page CTA hierarchy - demo as primary (DISC-003) | **DEPLOYED** |
| 2025-12-02 | 69ecdc3 | Fix Demo page JS error + disclaimer (BUG-004) | **DEPLOYED** |
| 2025-12-02 | 1fc11fe | Fix Ensure onboarding path consistency (ONBOARD-008) | **DEPLOYED** |
| 2025-12-02 | 2c7244e | Add Product demo animation on landing page (UX-004) | **DEPLOYED** |
| 2025-12-02 | 66b25b9 | Update Improve landing page headline (UX-003) | **DEPLOYED** |
| 2025-12-02 | 03993dd | Fix Quick Setup form fields match industry pricing | **DEPLOYED** |
| 2025-12-02 | e0cb0e5 | Fix Help button navigation (BUG-001) | **DEPLOYED** |
| 2025-12-02 | 8a6770f | Add Demo page frontend for try-before-signup (BUG-003) | **DEPLOYED** |
| 2025-12-02 | 709111d | Fix Share quote email sending (BUG-002) | **DEPLOYED** |
| 2025-12-02 | 2460980 | Update Reframe onboarding to recommend interview (UX-002) | **DEPLOYED** |
| 2025-12-02 | a1e6e66 | Add Guided quick setup with industry templates (ONBOARD-002) | **DEPLOYED** |
| 2025-12-02 | c6b266a | Fix Mobile responsiveness across all pages (INFRA-002) | **DEPLOYED** |
| 2025-12-02 | a7b12c2 | Add Pricing Brain global settings editor (FEAT-003) | **DEPLOYED** |
| 2025-12-02 | 5219509 | Add Interview Type C coaching with industry guidance | **DEPLOYED** |
| 2025-12-02 | 18284c6 | Add Industry pricing template library (ONBOARD-003) | **DEPLOYED** |
| 2025-12-02 | 7d4c86e | Add FAQ/Help section (INFRA-003) | **DEPLOYED** |

---

## Deployment Stats

| Period | Deployments | Success Rate |
|--------|-------------|--------------|
| 2025-12-03 | 15+ | 100% |
| 2025-12-02 | 30+ | 100% |
| 2025-12-01 | 5 | 100% |

---

## Incidents

| Date | Severity | Issue | Resolution | Post-mortem |
|------|----------|-------|------------|-------------|
| 2025-12-02 | MEDIUM | Missing billing columns in Postgres | Added auto-migrations (5a84de5) | SQLAlchemy create_all doesn't add columns to existing tables |

---

## Rollback Procedure

If a deployment breaks production:

1. **Immediate**: `git revert HEAD && git push` (auto-deploys fix)
2. **Railway Dashboard**: Use "Rollback" button in deployment history
3. **Notify**: Update `ENGINEERING_STATE.md` with incident
