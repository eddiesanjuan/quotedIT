# Discovery Agent State

Last Run: 2026-01-05
Status: COMPLETE

## Run Summary

| Metric | Value |
|--------|-------|
| New Discoveries | 5 |
| Duplicates Avoided | 8 |
| Questions Raised | 1 |

## Discovery Sources

| Source | Count | Top Finding |
|--------|-------|-------------|
| Product | 2 | invoice.payment_failed webhook is a TODO - users not notified of failed payments |
| Growth | 2 | Referral credits earned but no mechanism to redeem them |
| Strategy | 1 | Payment failure email notification gap is revenue risk |

## Backlog Status

| Status | Count |
|--------|-------|
| DISCOVERED | 15 |
| READY | 18 |
| COMPLETE | 9 |
| **Active Total** | **42** |
| Archived (DEPLOYED) | 66+ |

*Counts from DISCOVERY_BACKLOG.md as of 2026-01-05*

## New Discoveries (For Founder Review)

### DISC-149: Payment Failure Email Notifications - MEDIUM/S (Score: 2.0)

**Source**: Code analysis - billing.py line 264 has `# TODO: Send email notification to user`
**Impact**: MEDIUM | **Effort**: S

**Problem**: When a user's payment fails (invoice.payment_failed webhook), the system logs the event but does NOT notify the user. This means:
- User doesn't know their card failed
- Subscription may lapse unexpectedly
- Founder has no visibility into churn risk from payment failures

**Proposed Work**:
1. Implement `send_payment_failed_notification()` in email service
2. Send to user: "Your payment failed - please update your card"
3. Send to founder: Alert about potential churn
4. Track in analytics for churn prediction

**Success Metric**: 100% of payment failures trigger user notification; reduced involuntary churn

---

### DISC-150: Referral Credit Redemption Mechanism - HIGH/M (Score: 1.5)

**Source**: Code analysis - referral.py awards credits but no redemption path
**Impact**: HIGH | **Effort**: M

**Problem**: The referral system awards `referral_credits` (1 month credit) when a referee subscribes, but there's no mechanism to REDEEM these credits against their subscription. This means:
- Users refer friends expecting rewards
- Credits accumulate but provide no value
- Referral incentive is effectively broken

**Current State**: `credit_referrer()` increments `referral_credits` counter, but billing system never checks/applies them.

**Proposed Work**:
1. Add credit redemption check in Stripe checkout/renewal
2. UI in Account Settings showing available credits
3. Auto-apply one credit per billing cycle
4. Notification when credit is applied

**Success Metric**: Referral credits redeemable; referral rate increases

---

### DISC-151: Demo Generation Database Tracking - MEDIUM/S (Score: 2.0)

**Source**: Code analysis - marketing_analytics.py line 98 has `# TODO: Track demo generations in database (DISC-142)`
**Impact**: MEDIUM | **Effort**: S

**Problem**: Demo quote generations are tracked in PostHog but NOT in the database. This makes it impossible to:
- Query demo volume via API
- Include demo counts in daily marketing reports
- Compare demo-to-signup conversion accurately

**Current State**: `demos_generated = 0` is hardcoded in marketing report because no DB tracking exists.

**Proposed Work**:
1. Create `demo_generations` table (ip_address, transcription_hash, total, created_at)
2. Insert record on each demo.py quote generation
3. Update marketing_analytics.py to query actual count
4. Add to daily report

**Success Metric**: Demo volume trackable via API; accurate marketing reports

---

### DISC-152: Win Factors Tracking for Quotes - MEDIUM/M (Score: 1.0)

**Source**: Code analysis - quotes.py line 3004 has `top_win_factors=[],  # TODO: Track win factors`
**Impact**: MEDIUM | **Effort**: M

**Problem**: The quote analytics endpoint returns empty `top_win_factors`. This data could help contractors understand WHY quotes are accepted or rejected, enabling better pricing strategy.

**Proposed Work**:
1. Capture win/loss reasons from customer feedback
2. Analyze patterns (price sensitivity, timeline, scope clarity)
3. Display insights: "Your bathroom remodel quotes win 80% when under $5,000"
4. Feed into learning system

**Success Metric**: Win factor analysis available; actionable pricing insights

---

### DISC-153: Contractor Performance Dashboard Placeholder - LOW/M (Score: 0.5)

**Source**: Code analysis - contractors.py line 431 has `# TODO: Calculate from actual quote history`
**Impact**: LOW | **Effort**: M

**Problem**: The contractor stats endpoint has placeholder logic instead of calculating real metrics from quote history (total_revenue, average_quote, win_rate).

**Current State**: Returns hardcoded/estimated values instead of actual data.

**Proposed Work**:
1. Implement proper aggregation from quotes table
2. Calculate: total quotes, win rate, avg quote value, total revenue
3. Cache for performance
4. Expose in dashboard

**Success Metric**: Accurate contractor performance metrics; contractor can track business growth

---

## Duplicates Avoided

The following ideas were considered but already exist in the backlog:

1. **Google Ads conversion tracking** - Already covered by DISC-138, DISC-141, DISC-143
2. **Social login (Google/Apple)** - Already DISC-134 (READY)
3. **Landing page messaging evolution** - Already DISC-144 (READY)
4. **Blog content refresh** - Already DISC-145 (READY)
5. **Testimonial collection** - Mentioned in BETA_SPRINT.md (TRUST-001)
6. **Mobile PWA** - Covered by MOBILE-001 strategic initiative
7. **Exit survey reporting** - Already DISC-137 (READY)
8. **Autonomous monitoring agent** - Already DISC-140 (READY)

## Anti-Discoveries

1. **DO NOT add Sentry** - Already implemented (see landing.html lines 34-43)
2. **DO NOT add PostHog** - Already implemented comprehensively
3. **DO NOT build demo mode** - Animation demo exists, functional demo NOT needed per BETA_SPRINT.md

## Questions for Founder

1. **Referral Credit Priority**: The referral credit redemption gap (DISC-150) seems like a broken promise to users. Should this be elevated to HIGH priority given potential trust impact?

## Notes

Discovery cycle complete. Focused on TODOs in codebase and functional gaps.

Key observation: The product is feature-complete for MVP. Most remaining opportunities are polish, analytics depth, and operationalizing existing features (like referral credits).

The 80 Google Ads clicks / 0 conversions problem is well-covered by existing tickets (DISC-136, 138, 141, 143). No additional discovery needed there.
