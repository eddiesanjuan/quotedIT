# Implement Learning Excellence - Full Stack Orchestrator

---
name: implement-learning-excellence
description: Full stack implementation of Learning Excellence designs with testing and deployment
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, TodoWrite, TaskOutput, mcp__claude-in-chrome__*, LSP
---

## Purpose

This orchestrator transforms the Learning Excellence design documents into production code. It operates as a coordinated engineering team:

- **Tech Lead**: Coordinates implementation order, manages dependencies
- **Backend Engineers**: Implement Python services and APIs
- **Database Engineer**: Schema migrations and data backfill
- **Test Engineers**: Unit tests, integration tests
- **QA Automation**: Browser-based testing via Chrome extension
- **DevOps**: Git operations, Railway deployment, production verification

## Execution Model

```
PHASE 1: Context & Planning
    └── Read all design docs, plan implementation order

PHASE 2: Infrastructure (Sequential - dependencies)
    ├── Create feature branch: feature/learning-excellence
    ├── Schema migrations
    ├── New service files (stubs)
    └── Feature flags setup

PHASE 3: Core Implementation (Parallel where safe)
    ├── Agent: Quality Scoring Service
    ├── Agent: Relevance Algorithm Service
    ├── Agent: Acceptance Learning Integration
    └── Agent: Voice Signal Extractor

PHASE 4: Advanced Implementation (Sequential - builds on Phase 3)
    ├── Agent: Contractor DNA Service
    ├── Agent: Confidence System
    └── Agent: Explanation Generator

PHASE 5: Integration (Sequential)
    ├── Wire services into quote_generation.py
    ├── Wire acceptance into share.py
    └── Add API endpoints

PHASE 6: Testing - Unit & Integration (Parallel)
    ├── Agent: Unit Test Writer (>80% coverage required)
    ├── Agent: Integration Test Writer
    ├── Run pytest --cov (MUST PASS)
    └── ⛔ GATE: All tests green before proceeding

PHASE 7: PR Creation & Railway Preview
    ├── Push feature branch to origin
    ├── Create PR with detailed description
    ├── Railway auto-deploys PR preview environment
    ├── Wait for preview URL
    └── ⛔ GATE: Preview deployment successful

PHASE 8: Browser QA on Preview (NOT production)
    ├── Login to PREVIEW environment
    ├── Test all 5 scenarios on preview
    ├── Screenshot evidence collection
    ├── Verify no console errors
    └── ⛔ GATE: All QA scenarios pass on preview

PHASE 9: Code Review
    ├── Agent: Senior Code Reviewer
    ├── Security audit (no injection, XSS)
    ├── Performance review (no N+1 queries)
    ├── Pattern compliance check
    └── ⛔ GATE: Review approved

PHASE 10: Founder Approval
    ├── Present test results summary
    ├── Present QA screenshots
    ├── Present code review findings
    └── ⛔ GATE: Explicit founder "LGTM" required

PHASE 11: Merge & Production Deploy
    ├── Squash merge to main
    ├── Monitor Railway production deploy
    ├── Run database migrations
    └── Enable feature flags for Eddie ONLY

PHASE 12: Production Verification
    ├── Browser test on production (quoted.it.com)
    ├── Verify all features behind flags
    ├── Check production logs for errors
    └── 48-hour monitoring period before wider rollout
```

## Critical Safety Rules

1. **NEVER commit directly to main** - All work on feature branch
2. **NEVER merge without passing tests** - pytest must be green
3. **NEVER skip preview testing** - Railway preview before production
4. **NEVER deploy without founder approval** - Explicit LGTM required
5. **NEVER enable flags for all users initially** - Eddie-only first

## State Management

State file: `.claude/learning-excellence-impl-state.md`

## Pre-Flight Checks

Before starting, verify:
1. Design documents exist in `.claude/learning-excellence-outputs/`
2. Git working tree is clean (or changes are stashed)
3. Railway CLI is authenticated (`railway status`)
4. GitHub CLI is authenticated (`gh auth status`)
5. Chrome extension MCP is available

## Phase Definitions

### Phase 1: Context & Planning

**Agent**: Planning Architect

**Tasks**:
1. Read all 13 design documents from `.claude/learning-excellence-outputs/`
2. Read current implementation files:
   - `backend/services/learning.py`
   - `backend/prompts/quote_generation.py`
   - `backend/api/share.py`
   - `backend/api/quotes.py`
   - `backend/models/database.py`
3. Identify exact integration points
4. Create implementation plan with dependencies
5. Estimate effort per component
6. Output: `.claude/learning-excellence-impl-state.md` with full plan

**Completion Criteria**: Implementation plan created with clear task breakdown

---

### Phase 2: Infrastructure

**Agent**: Database Engineer + DevOps

**Tasks**:
1. Create Alembic migration for schema changes:
   - `category_confidence` JSON field on `pricing_models`
   - `voice_signals` JSON field on `quotes`
   - `outcome_source`, `outcome_date`, `accept_quote_token` on `quotes`
   - `pricing_breakdown` JSON field on `quotes` (for explanations)
2. Create new service file stubs:
   - `backend/services/learning_quality.py`
   - `backend/services/learning_relevance.py`
   - `backend/services/voice_signal_extractor.py`
   - `backend/services/contractor_dna.py`
   - `backend/services/pricing_confidence.py`
   - `backend/services/pricing_explanation.py`
3. Add feature flags to PostHog config:
   - `learning_quality_scoring_enabled`
   - `learning_relevance_enabled`
   - `acceptance_learning_enabled`
   - `contractor_dna_enabled`
   - `confidence_system_enabled`
   - `pricing_explanations_enabled`

**Completion Criteria**:
- Migration file created and tested locally
- All service stubs created with proper imports
- Feature flags documented

---

### Phase 3: Core Implementation

**Parallel Agents** (no dependencies between these):

#### Agent 3A: Quality Scoring Engineer
- Implement `LearningQualityScorer` class from phase2-quality-scoring.md
- 4-dimension scoring algorithm
- Anti-pattern detection
- Retry logic with feedback
- Unit tests for all 12 test cases

#### Agent 3B: Relevance Algorithm Engineer
- Implement `LearningRelevanceSelector` class from phase3-relevance.md
- 4-dimension relevance scoring
- Dynamic 3-7 selection based on complexity
- Conflict detection
- Unit tests for selection scenarios

#### Agent 3C: Acceptance Learning Engineer
- Implement `process_acceptance_learning()` from phase4-acceptance.md
- Confidence boost logic (+0.05)
- Calibration ceiling (accuracy + 0.15)
- Integration hooks for share.py
- Unit tests for 7 scenarios

#### Agent 3D: Voice Signal Engineer
- Implement `VoiceSignalExtractor` class from phase3-voice.md
- Pattern database for 5 signal categories
- Adjustment calculation
- Prompt injection formatting
- Unit tests for extraction

**Completion Criteria**: All 4 services implemented with passing unit tests

---

### Phase 4: Advanced Implementation

**Sequential Agents** (builds on Phase 3):

#### Agent 4A: Contractor DNA Engineer
- Implement `ContractorDNAService` from phase5-contractor-dna.md
- Three-tier pattern classification
- Pattern merging and deduplication
- Related category detection
- Cold start bootstrapping
- Unit tests for 7 scenarios

#### Agent 4B: Confidence System Engineer
- Implement `PricingConfidenceCalculator` from phase6-confidence.md
- 4-dimension confidence scoring
- Recency decay (30-day half-life)
- Coverage entropy calculation
- Confidence labels and behavior adaptation
- Unit tests for 8 edge cases

#### Agent 4C: Explanation Generator Engineer
- Implement `PricingExplanationService` from phase6-explanation.md
- Component tracing
- Uncertainty detection
- DNA transfer attribution
- Pre-computation for quote storage
- Unit tests for 6 scenarios

**Completion Criteria**: All 3 advanced services implemented with passing tests

---

### Phase 5: Integration

**Agent**: Integration Engineer

**Tasks**:
1. Modify `backend/prompts/quote_generation.py`:
   - Replace line 82 `[-7:]` with `LearningRelevanceSelector.select()`
   - Add voice signal injection
   - Add confidence-aware generation hints
   - Add explanation pre-computation

2. Modify `backend/api/share.py`:
   - Line 213: Call `process_acceptance_learning()` after quote sent
   - Line 511: Call `process_acceptance_learning()` after customer accepts
   - Add feature flag checks

3. Modify `backend/services/learning.py`:
   - Integrate quality scoring before storage
   - Integrate Contractor DNA pattern extraction
   - Add confidence updates after learning

4. Modify `backend/api/quotes.py`:
   - Add explanation endpoint
   - Add confidence endpoint
   - Modify correction flow for explanation-aware feedback

5. Add new API endpoints:
   - `GET /api/contractors/{id}/confidence` - Category confidence scores
   - `GET /api/quotes/{id}/explanation` - Pricing explanation
   - `GET /api/contractors/{id}/dna` - Contractor DNA summary

**Completion Criteria**: All integrations complete, imports resolve, no syntax errors

---

### Phase 6: Testing

**Parallel Agents**:

#### Agent 6A: Unit Test Completion
- Ensure all services have >80% coverage
- Run `pytest backend/tests/`
- Fix any failing tests
- Add missing edge case tests

#### Agent 6B: Integration Test Writer
- Test full quote generation flow with new learning
- Test correction → learning → next quote improvement
- Test acceptance signal processing
- Test Contractor DNA transfer to new category
- Test explanation accuracy

**Completion Criteria**: All tests pass, coverage >80%

---

### Phase 7: PR Creation & Railway Preview

**Agent**: DevOps Engineer

**Tasks**:

1. Create feature branch (if not already): `git checkout -b feature/learning-excellence`
2. Stage and commit all changes with descriptive message
3. Push to origin: `git push -u origin feature/learning-excellence`
4. Create PR via GitHub CLI with detailed description
5. Wait for Railway to auto-deploy PR preview environment
6. Verify preview URL is accessible

**PR Description Must Include**:
- Summary of all 6 new services
- List of modified files
- Testing status (pending at this point)
- Rollout plan with feature flags

**Completion Criteria**:
- PR created with detailed description
- Preview environment deployed and accessible
- Preview URL available for QA testing

**GATE**: Do NOT proceed until preview deployment is successful

---

### Phase 8: Browser QA on Preview

**Agent**: QA Automation Engineer (uses Chrome extension)

**CRITICAL**: All testing happens on PREVIEW environment, NOT production!

**Preview URL Pattern**: `https://quoted-it-pr-{number}.up.railway.app`

**Test Scenarios**:

1. **New Category Quote**
   - Login to PREVIEW as test contractor
   - Create quote in new category
   - Verify "Learning" confidence displayed
   - Verify explanation shows "No prior data"
   - Screenshot: `learning-qa/01-new-category.png`

2. **Correction Learning Flow**
   - Create quote, make correction
   - Verify quality scoring accepted the learning
   - Create second quote in same category
   - Verify learned pricing applied
   - Screenshot: `learning-qa/02-correction-flow.png`

3. **Acceptance Signal Flow**
   - Create quote, send without edit
   - Verify acceptance recorded
   - Check confidence increased
   - Screenshot: `learning-qa/03-acceptance.png`

4. **DNA Transfer Flow**
   - Create quotes in Category A, build confidence
   - Create first quote in related Category B
   - Verify DNA patterns transferred
   - Verify explanation shows transfer source
   - Screenshot: `learning-qa/04-dna-transfer.png`

5. **Explanation UI**
   - Create quote with high confidence
   - Verify explanation breakdown visible
   - Check all components have sources
   - Screenshot: `learning-qa/05-explanation.png`

**Evidence Collection**:
- Save all screenshots to `.playwright-mcp/learning-qa/`
- Document any failures in state file
- Verify no console errors

**Completion Criteria**:
- All 5 scenarios pass on preview
- No console errors
- Screenshots collected

**GATE**: Do NOT proceed to code review if any scenario fails

---

### Phase 9: Code Review

**Agent**: Senior Code Reviewer

**Review Checklist**:
- [ ] No security vulnerabilities (injection, XSS)
- [ ] All feature flags properly checked
- [ ] Database migrations are reversible
- [ ] No breaking changes to existing API
- [ ] Error handling comprehensive
- [ ] Logging adequate for debugging
- [ ] Performance: no N+1 queries
- [ ] Code follows existing patterns
- [ ] All new code has docstrings
- [ ] No hardcoded values (use config)

**Security Audit**:
- Check for innerHTML usage (should be none)
- Check for unsafe evaluations (should be none)
- Verify all user input is sanitized

**Performance Audit**:
- Verify no N+1 queries in new services
- Check that relevance scoring is O(n) not O(n squared)
- Verify explanation pre-computation happens at quote creation

**Review Output**:
- Create `.claude/learning-excellence-impl-outputs/code-review.md`
- List all findings (CRITICAL/MAJOR/MINOR)
- CRITICAL issues block merge
- MAJOR issues should be fixed
- MINOR issues can be follow-up tickets

**Completion Criteria**: Review complete, no CRITICAL issues

**GATE**: CRITICAL issues block proceeding to merge

---

### Phase 10: Founder Approval

**Agent**: Orchestrator (presents to founder)

**Present to Founder**:

1. **Test Results Summary**
   - Unit test coverage percentage
   - Integration test pass/fail count
   - Any skipped tests with justification

2. **QA Screenshots**
   - Show all 5 scenario screenshots
   - Highlight any visual issues

3. **Code Review Findings**
   - Summary of review
   - Any MAJOR issues and how addressed
   - Any MINOR issues deferred

4. **Risk Assessment**
   - Database migration risks
   - Rollback plan
   - Feature flag safety

5. **Rollout Plan Confirmation**
   - All flags OFF at deploy
   - Eddie-only for 48 hours
   - Full rollout after validation

**Wait for Response**:
- "LGTM" or "Approved" = Proceed to merge
- "Changes needed" = Return to implementation
- "Defer" = Pause orchestration

**GATE**: Explicit founder approval required before merge

---

### Phase 11: Merge & Production Deploy

**Agent**: DevOps Engineer

**Pre-Merge Checklist**:
- [ ] All tests passing (verify again)
- [ ] Preview QA complete
- [ ] Code review approved
- [ ] Founder LGTM received

**Merge to Main**:
- Squash merge via `gh pr merge --squash --delete-branch`
- Verify merge on main branch

**Monitor Production Deployment**:
- Watch Railway logs during deploy
- Wait for successful deploy (look for "Uvicorn running")

**Run Database Migration**:
- Only after deploy is successful
- Run via `railway run alembic upgrade head`
- Verify with `railway run alembic current`

**Enable Feature Flags for Eddie ONLY**:
- PostHog Dashboard: Feature Flags
- Enable each flag for Eddie's user_id only
- All other users remain on old behavior

**Completion Criteria**:
- Merged to main
- Production deployment successful
- Migrations complete
- Flags enabled for Eddie only

---

### Phase 12: Production Verification

**Agent**: QA Automation Engineer + DevOps

**Production Browser Test** (quoted.it.com):
1. Login as Eddie
2. Create test quote
3. Verify new learning features active
4. Check confidence displays
5. Screenshot evidence: `.playwright-mcp/learning-qa/prod-verification.png`

**Log Verification**:
- Check for any errors via `railway logs -n 500 --filter "@level:error"`
- Check learning-specific logs
- Check for performance issues (slow/timeout)

**48-Hour Monitoring**:
- Day 1: Check logs 3x (morning, afternoon, evening)
- Day 2: Check logs 2x (morning, evening)
- Watch for: Errors, performance degradation, unexpected behavior

**Wider Rollout Decision** (after 48 hours):
- If no issues: Enable flags for all users
- If minor issues: Fix first, then rollout
- If major issues: Disable flags, investigate

**Completion Criteria**:
- Production test passed
- No errors in logs
- 48-hour monitoring complete
- Ready for wider rollout

---

## Error Handling

### If tests fail:
1. Agent reports specific failures
2. Fix agent spawned to address issues
3. Re-run tests
4. Repeat until green

### If deployment fails:
1. Check Railway logs for error
2. If migration issue: `railway run alembic downgrade -1`
3. Fix and redeploy
4. If critical: Disable feature flags immediately

### If production issues:
1. Disable all feature flags (instant rollback)
2. Investigate via logs
3. Fix in new branch
4. Re-deploy

---

## Orchestrator Commands

```bash
# Check status and continue from where left off
/implement-learning-excellence

# Run specific phase (1-12)
/implement-learning-excellence --phase=3

# Status only (no execution)
/implement-learning-excellence --status

# Skip to phase (use with caution - may break dependencies)
/implement-learning-excellence --skip-to=7

# Rollback (disable all feature flags immediately)
/implement-learning-excellence --rollback

# Abort current PR (delete branch, close PR)
/implement-learning-excellence --abort
```

**Phase Reference**:
| Phase | Name | Requires |
|-------|------|----------|
| 1 | Context & Planning | Design docs |
| 2 | Infrastructure | Phase 1 |
| 3 | Core Implementation | Phase 2 |
| 4 | Advanced Implementation | Phase 3 |
| 5 | Integration | Phase 4 |
| 6 | Testing | Phase 5 |
| 7 | PR & Preview | Phase 6 (tests passing) |
| 8 | Browser QA on Preview | Phase 7 (preview deployed) |
| 9 | Code Review | Phase 8 (QA passed) |
| 10 | Founder Approval | Phase 9 (review complete) |
| 11 | Merge & Deploy | Phase 10 (LGTM received) |
| 12 | Production Verify | Phase 11 (deployed) |

---

## Success Metrics

After full deployment:
- [ ] Quality scoring rejecting <40 score statements
- [ ] Relevance algorithm selecting contextually (not just recent)
- [ ] Acceptance signals being recorded
- [ ] Confidence scores visible per category
- [ ] Explanations generated for quotes
- [ ] DNA transfer working for new categories
- [ ] Edit rate baseline established
- [ ] No production errors in logs

---

## Founder Checkpoints

**After Phase 2** (Infrastructure): Confirm schema changes acceptable
**After Phase 6** (Testing): Review test coverage before PR creation
**After Phase 9** (Code Review): Review findings before approval gate
**Phase 10** (Approval): MANDATORY - Explicit "LGTM" required to proceed
**After Phase 12** (Production): Validate behavior before wider rollout

---

## Estimated Timeline

| Phase | Effort | Parallel Factor | Elapsed |
|-------|--------|-----------------|---------|
| 1. Planning | 30 min | 1x | 30 min |
| 2. Infrastructure | 1 hour | 1x | 1.5 hours |
| 3. Core Implementation | 4 hours | 4x parallel | 2.5 hours |
| 4. Advanced Implementation | 3 hours | 1x sequential | 5.5 hours |
| 5. Integration | 2 hours | 1x | 7.5 hours |
| 6. Testing | 2 hours | 2x parallel | 8.5 hours |
| 7. PR & Preview Deploy | 15 min | 1x | 8.75 hours |
| 8. Browser QA on Preview | 1 hour | 1x | 9.75 hours |
| 9. Code Review | 30 min | 1x | 10.25 hours |
| 10. Founder Approval | WAIT | - | (pause) |
| 11. Merge & Deploy | 15 min | 1x | 10.5 hours |
| 12. Production Verify | 30 min | 1x | 11 hours |

**Total: ~11 hours of orchestrator time** (with parallelization)
**Plus**: 48-hour monitoring period before wider rollout

Without parallelization: ~15 hours

**Human Checkpoints**:
- Phase 10 requires explicit founder "LGTM" before proceeding
- Phase 12 includes 48-hour monitoring before full rollout
