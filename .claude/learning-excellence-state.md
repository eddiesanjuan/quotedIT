# Learning Excellence State Ledger

## Meta
- version: 3.0
- last_updated: 2025-12-24T21:45:00Z
- current_phase: 6
- status: COMPLETE

---

## Phases

### phase_0
- status: COMPLETE
- started_at: 2025-12-24T19:00:00Z
- completed_at: 2025-12-24T19:15:00Z
- agents:
  - arch-analyst: COMPLETE → .claude/learning-excellence-outputs/phase0-architecture.md
  - comp-intel: COMPLETE → .claude/learning-excellence-outputs/phase0-competitive.md
- findings:
  - CRITICAL: Injection bug at line 82 takes most recent 7, not most relevant
  - CRITICAL: Max 20 limit purges oldest rules without quality assessment
  - Three quality degradation pathways: recency spiral, dilution, contamination
  - Acceptance signals fully available (sent_at, was_edited, accepted_at, status)
  - No competitor has personalized pricing learning - category-defining opportunity
  - Voice = unique moat (no competitor can replicate)

### phase_1
- status: COMPLETE
- started_at: 2025-12-24T19:15:00Z
- completed_at: 2025-12-24T19:45:00Z
- agents:
  - db-auditor: COMPLETE → .claude/learning-excellence-outputs/phase1-database.md
  - effectiveness-analyst: COMPLETE → .claude/learning-excellence-outputs/phase1-effectiveness.md
  - acceptance-analyst: COMPLETE → .claude/learning-excellence-outputs/phase1-acceptance.md
- findings:
  - BLOCKER: Railway DB access blocked, need admin endpoint for audit
  - CRITICAL: "Confidence inflation" risk - system confidently wrong
  - Rich effectiveness data exists but no reporting layer
  - All acceptance signal fields exist (sent_at, was_edited, accepted_at)
  - Acceptance learning implementation: 9-12 hours, low risk
  - Edit rate + adjustment magnitude tracking available
  - No time-series effectiveness measurement
  - Created audit script: scripts/audit_learning_data.py

### phase_2
- status: COMPLETE
- started_at: 2025-12-24T19:45:00Z
- completed_at: 2025-12-24T20:00:00Z
- agents:
  - quality-designer: COMPLETE → .claude/learning-excellence-outputs/phase2-quality-scoring.md
  - prompt-engineer: COMPLETE → .claude/learning-excellence-outputs/phase2-enhanced-prompt.md
- findings:
  - Quality scoring algorithm: 4 dimensions (Specificity 35pts, Actionability 25pts, Clarity 20pts, Anti-patterns -25)
  - Thresholds: Accept 60+, Reject <40, Retry limit 2
  - 12 test cases covering full quality spectrum
  - Enhanced prompt with explicit examples and self-critique
  - Expected improvement: generic statements 30% → <10%, $ amounts 40% → >70%
  - Rejection feedback templates for Claude re-extraction
  - Full production-ready implementations delivered

### phase_3
- status: COMPLETE
- started_at: 2025-12-24T20:00:00Z
- completed_at: 2025-12-24T20:30:00Z
- agents:
  - relevance-designer: COMPLETE → .claude/learning-excellence-outputs/phase3-relevance.md
  - voice-extractor: COMPLETE → .claude/learning-excellence-outputs/phase3-voice.md
- findings:
  - Relevance algorithm: 4-dimension scoring (Keyword 40%, Recency 30%, Specificity 20%, Foundational 10%)
  - Dynamic selection: 3-7 learnings based on job complexity
  - Conflict detection for contradictory pricing rules
  - Voice signal extraction: 5 categories (difficulty, relationship, timeline, quality, corrections)
  - Signal adjustments stack: difficulty +15%, rush +20%, premium +15%, repeat -5%
  - No schema changes required for relevance (works with existing data)
  - New file: backend/services/learning_relevance.py
  - New file: backend/services/voice_signal_extractor.py
  - Integration point: Replace line 82 of quote_generation.py

### phase_4
- status: COMPLETE
- started_at: 2025-12-24T20:30:00Z
- completed_at: 2025-12-24T21:00:00Z
- agents:
  - acceptance-impl: COMPLETE → .claude/learning-excellence-outputs/phase4-acceptance.md
  - outcome-designer: COMPLETE → .claude/learning-excellence-outputs/phase4-outcomes.md
- findings:
  - Acceptance learning = opposite of correction learning (boost confidence, NO new statements)
  - Two trigger points: share.py:213 (quote sent) and share.py:511 (customer accepts)
  - Confidence boost +0.05 for acceptance vs +0.02 for corrections
  - Confidence calibration: ceiling = actual_accuracy + 0.15 prevents inflation
  - Outcome collection: customer acceptance (primary), 7-day follow-ups (secondary)
  - Win rate queries by edit status, category, pricing direction
  - Learning decay: deprecate patterns appearing in 70%+ lost quotes
  - Dashboard scorecard design with AI vs edited comparison

### phase_5
- status: COMPLETE
- started_at: 2025-12-24T21:00:00Z
- completed_at: 2025-12-24T21:15:00Z
- agents:
  - contractor-dna: COMPLETE → .claude/learning-excellence-outputs/phase5-contractor-dna.md
- findings:
  - Three-tier pattern classification (universal 60%, partial 40%, specific 0% inheritance)
  - TransferablePattern and ContractorDNA TypedDicts designed
  - Cold start acceleration: new categories bootstrap at 40-60% confidence
  - Pattern merging with deduplication and conflict detection
  - Integration points: learning.py line 117, quote_generation.py line 59
  - Related category detection (deck → fence transfers well, deck → painting less so)
  - 7 test scenarios covering basic transfer, override, accumulation
  - Migration plan: backfill script from existing learnings
  - Expected impact: 3x faster to 80% confidence, +15pp first quote accuracy

### phase_6
- status: COMPLETE
- started_at: 2025-12-24T21:15:00Z
- completed_at: 2025-12-24T21:45:00Z
- agents:
  - confidence-designer: COMPLETE → .claude/learning-excellence-outputs/phase6-confidence.md
  - explanation-generator: COMPLETE → .claude/learning-excellence-outputs/phase6-explanation.md
- findings:
  - Multi-dimensional confidence: 4 dimensions (Data 20%, Accuracy 40%, Recency 25%, Coverage 15%)
  - Calibration principle: "80% confidence = 80% acceptance rate"
  - Volume vs accuracy: 10 accurate quotes beats 100 mediocre quotes
  - AI behavior adaptation: High/Medium/Low/Learning modes with different generation strategies
  - Recency decay: 30-day half-life prevents stale data overconfidence
  - Coverage tracking: Shannon entropy detects "all simple jobs" gaps
  - 8 edge cases handled: new category, high volume low accuracy, long gaps, contradictory corrections
  - Schema change: category_confidence JSON field on pricing_models table
  - Integration: 6 files updated, confidence dashboard endpoint created
  - Migration: 10-15 hour estimated effort with backfill script
  - PricingExplanationService with component tracing (source, calculation, confidence)
  - 3-level progressive disclosure UI (summary → details → advanced)
  - Explanation-aware correction flow with diff highlighting
  - 6 test scenarios covering learning stages (new, experienced, multi-category, DNA, corrections)
  - Pre-computed explanations stored in quote.pricing_breakdown (no latency impact)

### phase_7
- status: NOT_STARTED
- started_at: null
- completed_at: null
- note: Design only, no implementation until scale achieved
- agents: []
- findings: []

---

## Prior Session Knowledge

### From Previous Session (2025-12-24)

The following was discovered in a prior session and should be considered validated knowledge:

#### Architecture (CONFIRMED)
- Three-layer learning system:
  1. `learned_adjustments[]` - Updated every correction, top 7 most recent injected
  2. `tailored_prompt` - Updated ~10% of corrections
  3. `pricing_philosophy` - Updated ~2% of corrections
- Injection bug: Line 82 in quote_generation.py takes `[-7:]` (most RECENT, not most RELEVANT)
- Dynamic learning rate (DISC-054): +0.04 early → +0.02 mid → +0.01 late → cap at 0.95
- Max 20 learnings per category (oldest deleted when exceeded)

#### Acceptance Signal (CONFIRMED)
- `sent_at` field EXISTS (set on email share, NOT on link generation)
- `was_edited` field EXISTS
- Detection query POSSIBLE: `sent_at IS NOT NULL AND was_edited = FALSE`
- Implementation effort: ~2-4 hours

#### Competitive Landscape (CONFIRMED)
- ServiceTitan: Regional benchmarks, not personalized
- Jobber: No pricing learning
- Proposify: Engagement analytics only
- HoneyBook: Lead prioritization, not pricing
- GAP: No competitor has contractor-specific pricing optimization

#### Known Weaknesses (CONFIRMED)
| ID | Issue | Severity |
|----|-------|----------|
| LW-001 | Only 7 learnings injected (most recent, not relevant) | HIGH |
| LW-002 | No learning quality validation | MEDIUM |
| LW-003 | No outcome tracking | HIGH |
| LW-007 | No acceptance learning | HIGH |
| LW-008 | sent_at only on email, not link | MEDIUM |
| LW-009 | Max 20 truncates oldest | MEDIUM |
| LW-010 | Confidence plateau at 0.95 | MEDIUM |

#### Key Code Locations
| File | Purpose | Key Lines |
|------|---------|-----------|
| backend/services/learning.py | Learning processing | 581 total |
| backend/prompts/quote_generation.py | Injection (THE BUG) | Line 82 |
| backend/services/database.py | Learning storage | 213-392 |
| backend/api/quotes.py | Correction flow | 1280-1418 |
| backend/api/share.py | Sent tracking | 208-211, 286 |

---

## Blockers
- BLOCK-001: Railway database uses internal hostname (postgres.railway.internal), cannot access from local dev
  - Since: 2025-12-24
  - Resolution options:
    - A: Add admin API endpoint for learning stats (RECOMMENDED)
    - B: Upgrade to Railway Pro for database proxy
    - C: Proceed with code-analysis findings only

---

## Decisions

### Pending
(none)

### Resolved
- DEC-001: Tone/hesitation analysis → REJECTED (too fragile, over-engineered)
- DEC-002: Learn from unsent quotes → REJECTED (ambiguous signal, only learn from SENT quotes)

---

## Constraints (Founder-Mandated)

These constraints MUST be followed in all designs:

1. **NO tone/hesitation analysis** - Learn from WORDS only, not voice patterns
2. **Only learn from SENT quotes** - Unsent quotes are ambiguous, do not learn from them
3. **Acceptance = sent without edit** - This is the positive signal to learn from

---

## Metrics

| Metric | Baseline | Current | Target | Notes |
|--------|----------|---------|--------|-------|
| Edit rate | ? | ? | <15% | Lower = better AI accuracy |
| Adjustment magnitude | ? | ? | <5% | Lower = closer to contractor price |
| Statement quality (high %) | ~40-50% (est) | ? | 70%+ | Phase 2 will measure |
| "Sent as-is" rate | ? | ? | Track | Acceptance signal baseline |
| Quote win rate | ? | ? | Track | Need outcome loop first |

---

## Session Log

| Date | Session | Phase | Actions | Outcome |
|------|---------|-------|---------|---------|
| 2025-12-24 | Prior | 0-1 | Architecture + competitive intel + code audit | Partial complete, DB blocked |
| 2025-12-24 | Prior | N/A | Redesigned orchestrator to v3.0 | Ready for fresh execution |
| 2025-12-24 | Current | 0-6 | Full orchestration: 13 agents across 7 phases | ALL PHASES COMPLETE |
