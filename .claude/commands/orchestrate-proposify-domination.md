# Proposify Feature Domination Orchestrator (v3.1 - Strategy-Aware)

---

## ⚠️ THIN ORCHESTRATOR PATTERN (MANDATORY)

**This orchestrator MUST NOT perform substantive work directly. ALL work is done by spawned Task agents.**

### Orchestrator ONLY:
- ✅ Read/update state file (`.claude/proposify-domination-state.md`)
- ✅ Spawn Task agents with detailed prompts
- ✅ Collect TaskOutput and synthesize
- ✅ Decide phase transitions

### Orchestrator MUST NOT:
- ❌ Write code directly (spawn agent)
- ❌ Run tests directly (spawn agent)
- ❌ Make browser interactions directly (spawn agent)
- ❌ Analyze code directly (spawn agent)

### Browser Automation for Subagents:
```
✅ mcp__claude-in-chrome__tabs_context_mcp  # Get tabs FIRST
✅ mcp__claude-in-chrome__computer          # Screenshots (action: "screenshot")
✅ mcp__claude-in-chrome__navigate          # Navigate with tabId
✅ mcp__claude-in-chrome__read_page         # Read accessibility tree
❌ mcp__claude-in-chrome__browser_snapshot  # NOT available to subagents
❌ mcp__plugin_playwright_playwright__*     # Conflicts with Chrome
```

---

## Architecture

**Problem**: v2.1 ran full audits that re-discovered the same known issues repeatedly.

**Solution**: This orchestrator maintains a **Known Issues Registry** and **Verified Working Baseline** so that:
1. Audits look for NEW issues beyond documented ones
2. Phase 2 designs automatically incorporate known critical issues
3. Fresh sessions inherit full context from state file
4. End-to-end runs are efficient and non-redundant

---

## Strategic Constraints (MUST READ)

**These constraints override all design and implementation decisions.**

### Pricing Philosophy
```
Current: $9/month OR $59/year unlimited
Strategy: DO NOT RAISE PRICES for new features
Goal: Margin moat - price so low competition is unprofitable
```

### Cost Constraints
| Constraint | Rationale |
|------------|-----------|
| **$0 marginal cost per feature** | Maintain 70-85% blended margins |
| **Typed-name e-signatures ONLY** | API signatures cost $0.50-3.00 each - unacceptable |
| **No per-user infrastructure** | Background jobs must scale to thousands without linear cost |
| **Stripe fees on customer** | Online payments = $0 cost to Quoted |

### Multi-Segment Awareness
**Quoted is NOT just for contractors.** All designs must work for:
- Trades (HVAC, plumbing, electrical, roofing)
- Home services (cleaning, landscaping, pest control)
- Auto (body shops, mechanics, detailing)
- Events (photographers, caterers, DJs, florists)
- Creative (freelance designers, videographers)
- Professional services (consultants, coaches)

**Language rules:**
- ❌ "contractor" in UI → ✅ "business" or segment-neutral
- ❌ "job site" assumptions → ✅ "service location" or omit
- ❌ Construction-specific terms → ✅ Universal terms

### Network-First Design
**Every feature should consider future platform monetization:**

| Feature | Network Opportunity |
|---------|---------------------|
| Invoice + Payments | Financing partner integration (Wisetack, Affirm) |
| Customer data | Cross-referral network (photographer → caterer) |
| Quote analytics | Pricing benchmarks by industry/region |
| Accept/Reject | Lead marketplace (homeowner submits, pros bid) |
| Share tracking | Engagement data for conversion optimization |

**Design principle**: Build hooks for future partnerships even if not implementing now.

### Infrastructure Efficiency
```
Target: < $0.02/user/month additional infrastructure
Reality check:
- Background jobs (Railway): ~$5-10/month TOTAL (not per-user)
- At 100 users: $0.05-0.10/user
- At 1000 users: $0.005-0.01/user
- At 10000 users: $0.0005-0.001/user
```

**Decision**: Invest in background job infrastructure NOW. Costs amortize to near-zero at scale.

---

## Quick Start

```bash
# Full end-to-end (reads state, continues from where left off)
/orchestrate-proposify-domination

# Run specific phase
/orchestrate-proposify-domination --phase=2

# Status only (no action)
/orchestrate-proposify-domination --status

# Force re-audit (ignore known issues baseline)
/orchestrate-proposify-domination --phase=1 --fresh
```

---

## Known Issues Registry (Baseline: 2024-12-24)

**CRITICAL**: These issues are ALREADY DOCUMENTED. Audits should:
- Verify they still exist (haven't been fixed)
- Look for ADDITIONAL issues NOT in this list
- NOT re-report these as new findings

### Critical Issues (P0)

| ID | Issue | Location | Status |
|----|-------|----------|--------|
| KI-001 | Invoice share link returns 404 | invoices.py:638-639 | OPEN |
| KI-002 | Quote accept/reject workflow missing | quote-view.html | OPEN |
| KI-003 | Quote status never transitions from "draft" | database.py:325 | OPEN |

### High Priority Issues (P1)

| ID | Issue | Location | Status |
|----|-------|----------|--------|
| KI-004 | view_count not persisted in database | share.py:335-349 | OPEN |
| KI-005 | Task reminder_time is dead code | database.py:585 | OPEN |
| KI-006 | notification_sent field never set | tasks.py | OPEN |
| KI-007 | recurrence/auto_generated fields unused | database.py:592-598 | OPEN |
| KI-008 | "link expired" error message misleading | share.py:328 | OPEN |
| KI-009 | Feature flag not checked in frontend | index.html (invoicing) | OPEN |

### Medium Priority Issues (P2)

| ID | Issue | Location | Status |
|----|-------|----------|--------|
| KI-010 | No share link revocation | share.py | OPEN |
| KI-011 | quote_valid_days never enforced | database.py:209 | OPEN |
| KI-012 | sent_at not set when emailing quote | share.py:188-194 | OPEN |
| KI-013 | outcome/outcome_notes fields never set | quotes.py | OPEN |
| KI-014 | No customer merge capability | customer_service.py | OPEN |

---

## Verified Working Baseline (2024-12-24)

**These systems are CONFIRMED WORKING**. Audits should:
- Verify they STILL work (regression check)
- NOT report these as findings unless they regressed

### Quote Sharing (YELLOW - Working with Gaps)
- Email share with PDF attachment (share.py:167-185)
- Shareable link generation with secure tokens (share.py:257-271)
- Public quote view endpoint (share.py:310-371)
- Quote-view.html renders correctly, mobile responsive
- PostHog event tracking (share.py:196-210)

### Invoice System (YELLOW - Working with Critical Bug)
- Full CRUD API (invoices.py:183-445)
- Mark-paid endpoint (invoices.py:452-502)
- PDF generation (invoices.py:505-599)
- Quote-to-invoice conversion (invoices.py:706-720)
- Invoice model with share_token (database.py:436-511)

### CRM System (GREEN - Fully Functional)
- Customer table with all fields (database.py:515-558)
- Deduplication logic (customer_service.py)
- Full CRUD API - 17 endpoints (customers.py)
- Voice command routing - 7 intents (crm_voice.py)
- Quote-to-customer auto-linking (quotes.py:472-479)
- Frontend UI complete (index.html:5029-5309)
- Backfill script (backfill_customers.py)

### Tasks System (YELLOW - UI Works, Notifications Stubbed)
- Full CRUD API - 9 endpoints (tasks.py)
- Task model with 22 columns (database.py:560-611)
- Frontend UI - list, create, snooze, complete
- Task summary badges
- Quick task creation from voice

### Quote Lifecycle (RED - Missing Core Workflow)
- Quote creation with status="draft"
- Quote sharing via email/link
- Public quote view (read-only)
- Customer info linking

---

## State File

**Location**: `.claude/proposify-domination-state.md`

**ALWAYS READ THIS FIRST** before taking any action.

The state file contains:
- Phase progress checkboxes
- Audit findings summaries
- Critical issues list (may have updates since this command was written)
- Design decisions
- PR numbers and preview URLs
- Founder decisions

---

## Execution Protocol

### Step 1: Read State File
```
Read .claude/proposify-domination-state.md
Compare state file issues with Known Issues Registry above
Identify: current phase, what's complete, what's next
```

### Step 2: Determine Next Action
```
If --status flag → Report state and stop
If --fresh flag → Ignore baseline, run full audit
If Phase 0 incomplete → Run Phase 0
If Phase 1 incomplete → Run delta audits (look for NEW issues only)
If Phase 1 complete but not reviewed → Pause for founder review
If Phase 2 incomplete → Run next design (incorporating known issues)
...and so on
```

### Step 3: Execute ONE Subagent at a Time
Use Task tool with the specific prompt for current step.
Wait for completion before continuing.

### Step 4: Update State File
After subagent completes:
1. Extract key findings (500 words max)
2. Update state file with summary
3. Check relevant checkbox
4. Add any NEW issues to Critical Issues table

### Step 5: Report & Continue or Pause
- If more work in current phase → Continue to next item
- If phase complete → Report synthesis and pause for review
- If context getting full → Save state and recommend fresh session

---

## Phase 0: Context Loading

**Goal**: Build baseline understanding. Skip if state file shows complete.

### Subagent Prompt (Context Summary)
```xml
<mission>
  <objective>Create concise baseline summary for Proposify Domination</objective>
  <files>
    - COMPANY_STATE.md
    - ENGINEERING_STATE.md
    - DISCOVERY_BACKLOG.md
  </files>
  <extract>
    - Current company phase and key metrics
    - Active engineering work and recent deploys
    - Relevant DISC tickets (CRM, invoicing, sharing)
    - Strategic priorities
  </extract>
  <output-format>
    ## Quoted Baseline (500 words max)

    ### Company Phase
    [2 sentences]

    ### Key Metrics
    - Metric: Value

    ### Active Work
    - Ticket: Status

    ### Relevant Features
    - DISC-XXX: Status

    ### Strategic Context
    [How Proposify features fit strategy]
  </output-format>
</mission>
```

### Competitive Intel (Separate Subagent)
```xml
<mission>
  <objective>Analyze Proposify's product offering</objective>
  <urls>
    - https://www.proposify.com/product-overview
    - https://www.proposify.com/pricing
  </urls>
  <extract>
    - Core features list
    - Pricing tiers
    - Key differentiators
    - Gaps we can exploit
  </extract>
  <output>300 words max summary</output>
</mission>
```

---

## Phase 1: Delta Audit (Context-Aware)

**Goal**: Find NEW issues not in the Known Issues Registry.

**CRITICAL**:
- Run ONE audit at a time
- Each audit receives the Known Issues baseline
- Report only NEWLY DISCOVERED issues
- Verify baseline still accurate (regression check)

### Delta Audit Output Format
```markdown
## {Feature} Delta Audit

### Baseline Verification
- [x] KI-XXX still exists / [ ] KI-XXX has been FIXED
- [verified working item] still works / REGRESSED

### NEW Issues Found (not in baseline)
- [new issue]: [severity] - [file:line] - [fix required]

### Updated Proposify Gap
- [any new competitive gaps discovered]

### Recommendation
[No new issues / New issues require attention / Baseline needs update]
```

### Delta Audit 1: Quote Sharing
```xml
<delta-audit>
  <feature>Quote Sharing (GROWTH-003)</feature>

  <known-issues>
    - KI-004: view_count not persisted in database (share.py:335-349)
    - KI-008: "link expired" error message misleading (share.py:328)
    - KI-010: No share link revocation
  </known-issues>

  <verified-working>
    - Email share with PDF attachment (share.py:167-185)
    - Shareable link generation (share.py:257-271)
    - Public quote view endpoint (share.py:310-371)
    - Quote-view.html renders correctly
    - PostHog event tracking (share.py:196-210)
  </verified-working>

  <files>
    - backend/api/share.py (MUST READ FULLY)
    - frontend/quote-view.html (MUST READ FULLY)
    - backend/models/database.py (Quote model section)
  </files>

  <instructions>
    1. VERIFY known issues still exist (or mark as FIXED)
    2. VERIFY baseline items still work (or mark as REGRESSED)
    3. SEARCH for NEW issues NOT in the known-issues list
    4. Report ONLY new findings
  </instructions>

  <output>[Use Delta Audit Output Format above]</output>
</delta-audit>
```

### Delta Audit 2: Invoice System
```xml
<delta-audit>
  <feature>Invoice System (DISC-071)</feature>

  <known-issues>
    - KI-001: Invoice share link returns 404 (invoices.py:638-639)
    - KI-009: Feature flag not checked in frontend
  </known-issues>

  <verified-working>
    - Full CRUD API (invoices.py:183-445)
    - Mark-paid endpoint (invoices.py:452-502)
    - PDF generation (invoices.py:505-599)
    - Quote-to-invoice conversion (invoices.py:706-720)
    - Invoice model with share_token (database.py:436-511)
  </verified-working>

  <files>
    - backend/api/invoices.py (MUST READ FULLY)
    - backend/main.py (check for /invoice/{token} route)
    - frontend/index.html (search for invoice UI sections)
  </files>

  <instructions>
    1. VERIFY KI-001 still exists (no /invoice/{token} route)
    2. VERIFY KI-009 still exists (frontend doesn't check flag)
    3. VERIFY baseline items still work
    4. SEARCH for NEW issues NOT in the known-issues list
    5. Report ONLY new findings
  </instructions>

  <output>[Use Delta Audit Output Format above]</output>
</delta-audit>
```

### Delta Audit 3: CRM System
```xml
<delta-audit>
  <feature>CRM System (DISC-085-092)</feature>

  <known-issues>
    - KI-014: No customer merge capability
  </known-issues>

  <verified-working>
    - Customer table with all fields (database.py:515-558)
    - Deduplication logic (customer_service.py)
    - Full CRUD API - 17 endpoints (customers.py)
    - Voice command routing - 7 intents (crm_voice.py)
    - Quote-to-customer auto-linking (quotes.py:472-479)
    - Frontend UI complete (index.html:5029-5309)
    - Backfill script (backfill_customers.py)
  </verified-working>

  <files>
    - backend/api/customers.py
    - backend/services/customer_service.py
    - backend/services/crm_voice.py
    - frontend/index.html (customer sections)
  </files>

  <instructions>
    1. VERIFY KI-014 still exists
    2. VERIFY all baseline items still work (this system was GREEN)
    3. SEARCH for NEW issues or regressions
    4. Report ONLY new findings
  </instructions>

  <output>[Use Delta Audit Output Format above]</output>
</delta-audit>
```

### Delta Audit 4: Tasks System
```xml
<delta-audit>
  <feature>Tasks/Reminders (DISC-092)</feature>

  <known-issues>
    - KI-005: Task reminder_time is dead code (database.py:585)
    - KI-006: notification_sent field never set
    - KI-007: recurrence/auto_generated fields unused (database.py:592-598)
  </known-issues>

  <verified-working>
    - Full CRUD API - 9 endpoints (tasks.py)
    - Task model with 22 columns (database.py:560-611)
    - Frontend UI - list, create, snooze, complete
    - Task summary badges
    - Quick task creation from voice
  </verified-working>

  <files>
    - backend/api/tasks.py (MUST READ FULLY)
    - backend/models/database.py (Task model section)
    - frontend/index.html (task sections)
  </files>

  <instructions>
    1. VERIFY KI-005, KI-006, KI-007 still exist
    2. VERIFY baseline items still work
    3. Look for background job attempts (APScheduler, Celery, cron)
    4. SEARCH for NEW issues NOT in the known-issues list
    5. Report ONLY new findings
  </instructions>

  <output>[Use Delta Audit Output Format above]</output>
</delta-audit>
```

### Delta Audit 5: Quote Lifecycle
```xml
<delta-audit>
  <feature>Quote Status & Acceptance</feature>

  <known-issues>
    - KI-002: Quote accept/reject workflow missing (quote-view.html)
    - KI-003: Quote status never transitions from "draft" (database.py:325)
    - KI-011: quote_valid_days never enforced (database.py:209)
    - KI-012: sent_at not set when emailing quote (share.py:188-194)
    - KI-013: outcome/outcome_notes fields never set (quotes.py)
  </known-issues>

  <verified-working>
    - Quote creation with status="draft"
    - Quote sharing via email/link
    - Public quote view (read-only)
    - Customer info linking
  </verified-working>

  <files>
    - backend/api/quotes.py (search for status changes)
    - backend/models/database.py (Quote model)
    - frontend/quote-view.html (search for accept/reject)
  </files>

  <instructions>
    1. VERIFY all known issues still exist
    2. VERIFY baseline items still work
    3. Check if any accept/reject endpoints were added
    4. Check if status transitions were implemented
    5. SEARCH for NEW issues NOT in the known-issues list
    6. Report ONLY new findings
  </instructions>

  <output>[Use Delta Audit Output Format above]</output>
</delta-audit>
```

### Audit Synthesis (After All 5 Complete)

```markdown
## Phase 1 Delta Audit Synthesis

### Baseline Status
| Known Issue | Still Exists? | Notes |
|-------------|---------------|-------|

### NEW Issues Discovered
| ID | Issue | Severity | Location | Fix Required |

### Regressions Detected
| Verified Working Item | Status | Notes |

### Updated Recommendations
[Based on new findings and baseline verification]
```

---

## Phase 2: 10x Design (Issue-Aware)

**Prerequisites**: Phase 1 complete, founder reviewed and approved direction.

**CRITICAL**: Each design MUST address relevant known issues from the registry.

### Design Principles
```
CORE UX:
1. VOICE-FIRST: Every action possible via voice command
2. AI-ENHANCED: System gets smarter with each use
3. FIELD-READY: Works on mobile, poor connectivity, one-handed
4. ZERO-FRICTION: Fewer clicks than Proposify for any action
5. FIX-FORWARD: Address known issues, don't work around them

STRATEGIC (from Strategic Constraints section):
6. SEGMENT-NEUTRAL: Works for photographer AND plumber AND consultant
7. ZERO-COST FEATURES: No per-use API costs (typed signatures, not DocuSign)
8. NETWORK-AWARE: Build hooks for future platform monetization
9. SCALE-FRIENDLY: Infrastructure costs amortize, not multiply
10. MARGIN-PROTECTED: Never design features that erode unit economics
```

### Issue-Aware Design Template
```xml
<design-mission>
  <feature>{FEATURE_NAME}</feature>

  <known-issues-to-address>
    [List KI-XXX issues this design MUST fix]
  </known-issues-to-address>

  <audit-findings>
    [Paste from state file]
  </audit-findings>

  <proposify-approach>
    [What Proposify does]
  </proposify-approach>

  <deliverable>
    ## {Feature} 10x Design

    ### Known Issues Addressed
    | Issue ID | How This Design Fixes It |
    |----------|-------------------------|

    ### Current State
    [Summary from audit]

    ### Proposify Approach
    [What they do]

    ### Why That's Not Good Enough
    [Critique from contractor POV]

    ### Quoted's 10x Approach
    [Our superior design that ALSO fixes known issues]

    ### Voice Commands
    - "{command}" -> {result}

    ### AI Learning
    - Data: [what we collect]
    - Pattern: [what we learn]
    - Improvement: [how it gets better]

    ### Mobile UX
    - Primary: [one-tap action]
    - Offline: [what happens]

    ### Implementation Scope
    - MVP: [week 1] - Must fix: [KI-XXX]
    - Enhanced: [week 2]
    - 10x: [week 3+]

    ### Strategic Validation
    | Constraint | Compliant? | Notes |
    |------------|------------|-------|
    | Zero marginal cost | ✅/❌ | [explain] |
    | Segment-neutral language | ✅/❌ | [explain] |
    | Network hooks identified | ✅/❌ | [future monetization angle] |
    | Scale-friendly infrastructure | ✅/❌ | [cost at 10K users] |
  </deliverable>
</design-mission>
```

### Features to Design (In Order with Issue Mapping)

1. **Invoice Public View**
   - Must fix: KI-001 (404), KI-009 (feature flag)

2. **Quote Accept/Reject**
   - Must fix: KI-002 (missing workflow), KI-003 (status transitions), KI-012 (sent_at), KI-013 (outcome fields)

3. **E-Signatures**
   - Enhancement on top of Accept/Reject

4. **Share Analytics**
   - Must fix: KI-004 (view_count), KI-008 (error message)

5. **Auto-Reminders**
   - Must fix: KI-005 (reminder_time), KI-006 (notification_sent), KI-007 (recurrence)

6. **Online Payment**
   - New feature, no known issues

7. **Quote Expiration**
   - Must fix: KI-011 (quote_valid_days)

---

## Phase 3: Technical Specs

Run ONE spec at a time after corresponding design is approved.

### Spec Template
```xml
<spec-mission>
  <feature>{FEATURE}</feature>
  <design>{PASTE 10X DESIGN}</design>
  <issues-to-fix>{KI-XXX list}</issues-to-fix>

  <deliverable>
    ## {Feature} Technical Spec

    ### Issues Fixed by This Spec
    | Issue ID | Implementation |
    |----------|---------------|

    ### Database Changes
    [Migration SQL or "None"]

    ### API Endpoints
    | Method | Path | Request | Response |

    ### Frontend Changes
    - Files: [list]
    - Components: [list]

    ### Voice Integration
    - Pattern: "{command}"
    - Handler: [function]

    ### Feature Flag
    - Key: {flag_name}
    - Default: false

    ### Test Cases
    1. [test that verifies KI-XXX is fixed]

    ### Rollout
    - Eddie (48h) -> 10% -> 50% -> GA
  </deliverable>
</spec-mission>
```

---

## Phase 4: Implementation

### CLI Tools Available

**GitHub CLI (`gh`)** - Installed and authenticated
```bash
gh pr create          # Create pull request
gh pr view            # View PR details
gh pr merge           # Merge PR
gh pr list            # List open PRs
gh api                # Raw GitHub API access
gh issue create       # Create issues
```

**Railway CLI** - Available for deployment management
```bash
railway status        # Check deployment status
railway logs          # View application logs
railway variables     # View/set environment variables
```

**Preview URLs**: PRs auto-deploy to `https://web-quotedit-pr-{NUMBER}.up.railway.app/`

### PR Protocol
```bash
# 1. Create branch (include issue IDs being fixed)
git checkout -b feat/PROP-XXX-feature-name-fixes-KI-001

# 2. Implement per spec

# 3. Create PR
gh pr create \
  --title "PROP-XXX: Feature Description" \
  --body "## Summary
- Point 1
- Point 2

## Issues Fixed
- KI-001: [how]
- KI-002: [how]

## Preview
https://web-quotedit-pr-{NUMBER}.up.railway.app/

## Test Instructions
1. Verify KI-001 no longer reproduces
2. Test happy path
3. Test error cases"

# 4. Get preview URL
gh pr view --json number -q '.number'

# 5. After QA passes
gh pr merge --squash --delete-branch
```

### Implementation Waves
```
Wave 1: Database migrations + feature flags
Wave 2: Backend services + API endpoints (fix KI-001, KI-002, KI-003)
Wave 3: Frontend components + UI (fix KI-004, KI-008, KI-009)
Wave 4: Voice integration
Wave 5: Background jobs (fix KI-005, KI-006, KI-007)
Wave 6: Polish + edge cases (fix KI-010, KI-011, KI-012, KI-013, KI-014)
```

---

## Phase 5: QA (Issue Verification)

### QA Protocol (Per Feature)
```xml
<qa-mission>
  <feature>{FEATURE}</feature>
  <preview-url>https://web-quotedit-pr-{NUMBER}.up.railway.app/</preview-url>
  <issues-that-should-be-fixed>{KI-XXX list}</issues-that-should-be-fixed>

  <tests>
    1. VERIFY each KI-XXX is fixed (regression test)
    2. Happy path end-to-end
    3. Error cases (invalid input, network failure)
    4. Mobile responsive (375px viewport)
    5. Voice commands (if applicable)
    6. Feature flag toggle (on/off behavior)
  </tests>

  <output>
    ## QA Report: {Feature}

    ### Issue Verification
    | Issue ID | Fixed? | Evidence |
    |----------|--------|----------|

    ### Functional Tests
    | Test | Pass/Fail | Notes |
    |------|-----------|-------|

    ### New Bugs Found
    - [bug]

    ### Recommendation
    [Ready to merge / Needs fixes / Issues not fully resolved]
  </output>
</qa-mission>
```

---

## Phase 6: Release & Issue Closure

### Rollout Protocol
```
1. Enable feature flag for Eddie (48 hours validation)
2. Verify all targeted KI-XXX issues are fixed in production
3. Enable for 10% of users (monitor PostHog)
4. Enable for 50% of users (monitor errors)
5. GA - 100% enabled
6. Update Known Issues Registry: Mark KI-XXX as CLOSED
7. Remove feature flag after 2 weeks stable
```

### Issue Closure
After successful GA release:
1. Update this command file - change issue status from OPEN to CLOSED
2. Update state file - move issues to "Resolved Issues" section
3. Document resolution date and PR number

---

## Founder Checkpoints

**PAUSE and report after:**
- Phase 1 complete (delta audit synthesis)
- Phase 2 complete (all designs with issue mappings)
- Before each Wave merge in Phase 4 (show which KI-XXX will be fixed)
- Before GA release in Phase 6

---

## Context Management

### If Context Getting Full (>100K tokens)

1. **STOP** current work immediately
2. **UPDATE** state file with all progress
3. **UPDATE** Known Issues Registry if new issues found
4. **REPORT**: "Context at ~X%. Recommend fresh session."
5. User starts new session and runs `/orchestrate-proposify-domination`
6. New session reads state file AND this command's baseline

### State File Preserves Everything
- Phase progress checkboxes
- Audit findings summaries (delta from baseline)
- Critical issues list (NEW issues only)
- Design decisions
- PR numbers and preview URLs
- Founder decisions
- Issue closure status

---

## Maintaining This Command

### When to Update Known Issues Registry

1. **After initial audit**: Add all discovered issues with IDs
2. **After delta audit finds new issues**: Add new KI-XXX entries
3. **After PR merges**: Mark issues as CLOSED with date
4. **After regression detected**: Re-open or add new issue

### Issue ID Convention
```
KI-001 through KI-099: Phase 1 audit findings
KI-100 through KI-199: Phase 2 design issues
KI-200 through KI-299: Phase 4 implementation bugs
KI-300+: Production issues found post-release
```

---

## Emergency: Reset

If state becomes corrupted or needs full reset:
```bash
# 1. Reset state file to initial
# (manually edit .claude/proposify-domination-state.md)
# Set all checkboxes to unchecked
# Clear findings sections

# 2. Run fresh audit (ignores baseline)
/orchestrate-proposify-domination --phase=1 --fresh
```

If Known Issues Registry needs update:
```bash
# Edit this file directly
# Update issue statuses
# Add/remove issues as needed
# Increment version number in title
```
