# Learning Excellence Implementation State

## Meta
- version: 1.1
- created: 2025-12-25
- last_updated: 2025-12-25
- current_phase: 1
- status: IN_PROGRESS

---

## Pre-Flight Checklist

- [x] Design documents exist (20 files in `.claude/learning-excellence-outputs/`)
- [x] Git working tree: Has unrelated changes (blog, state files) - OK to proceed
- [x] Railway CLI authenticated: quoted.It production
- [x] GitHub CLI authenticated: eddiesanjuan with repo/workflow scopes
- [x] Chrome extension MCP available: Tab ready

---

## Phases

### phase_1
- name: Context & Planning
- status: COMPLETE
- started_at: 2025-12-25T10:00:00
- completed_at: 2025-12-25T10:30:00
- agents:
  - planning-architect: COMPLETE
- outputs:
  - implementation_plan: See "Implementation Plan" section below
- blockers: []

### phase_2
- name: Infrastructure
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - database-engineer: NOT_STARTED
  - devops-engineer: NOT_STARTED
- outputs:
  - migration_file: null
  - service_stubs: []
  - feature_flags: []
- blockers: []

### phase_3
- name: Core Implementation
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - quality-scoring-engineer: NOT_STARTED
  - relevance-algorithm-engineer: NOT_STARTED
  - acceptance-learning-engineer: NOT_STARTED
  - voice-signal-engineer: NOT_STARTED
- outputs:
  - learning_quality.py: null
  - learning_relevance.py: null
  - acceptance_learning: null
  - voice_signal_extractor.py: null
- test_results:
  - quality_tests: null
  - relevance_tests: null
  - acceptance_tests: null
  - voice_tests: null
- blockers: []

### phase_4
- name: Advanced Implementation
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - contractor-dna-engineer: NOT_STARTED
  - confidence-system-engineer: NOT_STARTED
  - explanation-generator-engineer: NOT_STARTED
- outputs:
  - contractor_dna.py: null
  - pricing_confidence.py: null
  - pricing_explanation.py: null
- test_results:
  - dna_tests: null
  - confidence_tests: null
  - explanation_tests: null
- blockers: []

### phase_5
- name: Integration
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - integration-engineer: NOT_STARTED
- outputs:
  - quote_generation_modified: false
  - share_modified: false
  - learning_modified: false
  - quotes_api_modified: false
  - new_endpoints: []
- blockers: []

### phase_6
- name: Testing
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - unit-test-engineer: NOT_STARTED
  - integration-test-engineer: NOT_STARTED
- outputs:
  - unit_test_coverage: null
  - integration_tests_passed: null
  - all_tests_green: false
- gate: All tests must pass before proceeding
- blockers: []

### phase_7
- name: PR Creation & Railway Preview
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - devops-engineer: NOT_STARTED
- outputs:
  - branch_name: null
  - pr_url: null
  - preview_url: null
  - preview_deployed: false
- gate: Preview must be deployed and accessible
- blockers: []

### phase_8
- name: Browser QA on Preview
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - qa-automation-engineer: NOT_STARTED
- test_scenarios:
  - new_category_quote: NOT_STARTED
  - correction_learning_flow: NOT_STARTED
  - acceptance_signal_flow: NOT_STARTED
  - dna_transfer_flow: NOT_STARTED
  - explanation_ui: NOT_STARTED
- screenshots: []
- console_errors: null
- gate: All 5 scenarios must pass on preview
- blockers: []

### phase_9
- name: Code Review
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - senior-code-reviewer: NOT_STARTED
- outputs:
  - review_file: null
  - critical_issues: 0
  - major_issues: 0
  - minor_issues: 0
  - review_passed: false
- gate: No CRITICAL issues allowed
- blockers: []

### phase_10
- name: Founder Approval
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - orchestrator: NOT_STARTED
- outputs:
  - test_summary_presented: false
  - qa_screenshots_presented: false
  - review_findings_presented: false
  - founder_response: null
- gate: Explicit "LGTM" or "Approved" required
- blockers: []

### phase_11
- name: Merge & Production Deploy
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - devops-engineer: NOT_STARTED
- outputs:
  - merged_to_main: false
  - production_deployed: false
  - migrations_run: false
  - flags_enabled_for_eddie: false
- blockers: []

### phase_12
- name: Production Verification
- status: NOT_STARTED
- started_at: null
- completed_at: null
- agents:
  - qa-automation-engineer: NOT_STARTED
  - devops-engineer: NOT_STARTED
- outputs:
  - production_test_passed: false
  - logs_verified: false
  - monitoring_started: false
- verification:
  - quality_scoring_working: null
  - relevance_selection_working: null
  - acceptance_signals_recording: null
  - confidence_visible: null
  - explanations_generating: null
  - dna_transfer_working: null
- 48_hour_monitoring:
  - day1_morning: null
  - day1_afternoon: null
  - day1_evening: null
  - day2_morning: null
  - day2_evening: null
  - ready_for_wider_rollout: false
- blockers: []

---

## Design Document References

| Document | Purpose | Key Integration Points |
|----------|---------|----------------------|
| phase0-architecture.md | System overview | Understanding existing structure |
| phase0-competitive.md | Competitive context | Why this matters |
| phase1-database.md | DB audit | Current schema |
| phase1-effectiveness.md | Baseline metrics | What to measure |
| phase1-acceptance.md | Acceptance signals | sent_at, was_edited fields |
| phase2-quality-scoring.md | Quality algorithm | LearningQualityScorer class |
| phase2-enhanced-prompt.md | Better extraction | Prompt templates |
| phase3-relevance.md | Relevance algorithm | Replace line 82 |
| phase3-voice.md | Voice signals | VoiceSignalExtractor class |
| phase4-acceptance.md | Acceptance learning | process_acceptance_learning() |
| phase4-outcomes.md | Outcome tracking | Win/loss correlation |
| phase5-contractor-dna.md | Cross-category | ContractorDNA service |
| phase6-confidence.md | Confidence system | PricingConfidence calculator |
| phase6-explanation.md | Explanations | PricingExplanationService |

---

## Key Code Locations (Pre-Implementation)

| File | Current State | Planned Changes |
|------|---------------|-----------------|
| backend/services/learning.py | 581 lines, core learning | Add quality gate, DNA extraction |
| backend/prompts/quote_generation.py | Line 82 bug | Replace with relevance selector |
| backend/api/share.py | Lines 213, 511 | Add acceptance learning calls |
| backend/api/quotes.py | Correction flow | Add explanation endpoints |
| backend/models/database.py | Current schema | Add new JSON fields |

---

## New Files to Create

| File | Purpose | Design Source |
|------|---------|---------------|
| backend/services/learning_quality.py | Quality scoring | phase2-quality-scoring.md |
| backend/services/learning_relevance.py | Relevance selection | phase3-relevance.md |
| backend/services/voice_signal_extractor.py | Voice signals | phase3-voice.md |
| backend/services/contractor_dna.py | Cross-category | phase5-contractor-dna.md |
| backend/services/pricing_confidence.py | Confidence calc | phase6-confidence.md |
| backend/services/pricing_explanation.py | Explanations | phase6-explanation.md |
| backend/tests/test_learning_quality.py | Quality tests | phase2 test cases |
| backend/tests/test_learning_relevance.py | Relevance tests | phase3 test cases |
| backend/tests/test_acceptance_learning.py | Acceptance tests | phase4 test cases |
| backend/tests/test_contractor_dna.py | DNA tests | phase5 test cases |
| backend/tests/test_pricing_confidence.py | Confidence tests | phase6 test cases |
| backend/tests/test_pricing_explanation.py | Explanation tests | phase6 test cases |

---

## Feature Flags

| Flag | Purpose | Default | Enable For |
|------|---------|---------|------------|
| learning_quality_scoring_enabled | Quality gate on learnings | false | Eddie first |
| learning_relevance_enabled | Smart selection vs [-7:] | false | Eddie first |
| acceptance_learning_enabled | Learn from sent quotes | false | Eddie first |
| voice_signals_enabled | Extract pricing signals | false | Eddie first |
| contractor_dna_enabled | Cross-category transfer | false | Eddie first |
| confidence_system_enabled | Multi-dim confidence | false | Eddie first |
| pricing_explanations_enabled | Show explanations | false | Eddie first |

---

## Rollback Plan

If issues in production:

1. **Immediate**: Disable all feature flags in PostHog (takes effect in ~30 seconds)
2. **If data corrupted**: Rollback migration with `railway run alembic downgrade -1`
3. **If code issue**: Revert PR with `gh pr revert <pr-number>`

---

## Implementation Plan (Phase 1 Output)

### Critical Integration Points

| File | Line | Current Code | New Code | Purpose |
|------|------|--------------|----------|---------|
| `backend/prompts/quote_generation.py` | 82 | `top_learnings = learned_adjustments[-7:]` | `top_learnings = await LearningRelevanceSelector.select(learned_adjustments, transcription, category)` | Replace naive recency with intelligent relevance |
| `backend/api/share.py` | 511 | `quote = await db.update_quote(...)` | Add call after: `await process_acceptance_learning(quote, outcome="won")` | Learn from accepted quotes |
| `backend/api/share.py` | ~580 | Quote rejection endpoint | Add call: `await process_acceptance_learning(quote, outcome="lost", reason=...)` | Learn from rejected quotes |
| `backend/services/learning.py` | 36 | `process_correction()` entry | Add quality scoring gate before processing | Filter low-quality learnings |
| `backend/api/quotes.py` | 1407-1417 | Learning loop in update_quote | Integrate DNA extraction after learning | Cross-category transfer |

### Service Implementation Order (Dependencies)

```
Phase 3 - Core (Parallel):
├── learning_quality.py (no deps)
├── learning_relevance.py (no deps)
├── voice_signal_extractor.py (no deps)
└── acceptance_learning.py (no deps)

Phase 4 - Advanced (Sequential):
├── contractor_dna.py (depends on: learning_quality, voice_signal)
├── pricing_confidence.py (depends on: learning_quality, acceptance_learning)
└── pricing_explanation.py (depends on: confidence, dna)
```

### Database Schema Additions

**PricingModel table - new JSON fields in pricing_knowledge:**
```python
{
    "categories": {
        "<category>": {
            # Existing fields
            "learned_adjustments": [...],
            "tailored_prompt": "...",
            "confidence": 0.75,
            "correction_count": 5,

            # NEW: Quality metadata per learning
            "learning_metadata": [
                {
                    "text": "learning statement",
                    "quality_score": 85,
                    "specificity": 90,
                    "actionability": 80,
                    "clarity": 85,
                    "source": "correction",  # correction | acceptance | dna_transfer
                    "created_at": "2025-01-01T00:00:00Z",
                    "outcome_boost": 0.02  # from acceptance
                }
            ],

            # NEW: Relevance scoring data
            "keyword_weights": {"demolition": 0.8, "composite": 0.9},

            # NEW: Acceptance signals
            "acceptance_rate": 0.65,
            "total_sent": 20,
            "total_accepted": 13,
            "last_acceptance_at": "2025-01-15T00:00:00Z"
        }
    },

    # NEW: Contractor DNA (global patterns)
    "dna": {
        "universal_patterns": [
            {"pattern": "Premium pricing approach", "confidence": 0.85, "tier": "universal"}
        ],
        "partial_patterns": [
            {"pattern": "Second story work +25%", "confidence": 0.70, "tier": "partial", "categories": ["deck", "roof"]}
        ],
        "bootstrap_stats": {
            "categories_analyzed": 5,
            "patterns_extracted": 12,
            "last_analysis_at": "2025-01-20T00:00:00Z"
        }
    },

    # NEW: Multi-dimensional confidence
    "confidence_dimensions": {
        "data_confidence": 0.75,      # 20% weight
        "accuracy_confidence": 0.80,  # 40% weight
        "recency_confidence": 0.85,   # 25% weight
        "coverage_confidence": 0.70   # 15% weight
    }
}
```

### API Endpoints to Add

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/quotes/{id}/explanation` | GET | Get pricing explanation | `{components: [], narrative: "...", confidence: {...}}` |
| `/api/quotes/{id}/confidence` | GET | Get confidence details | `{overall: 0.78, dimensions: {...}, calibration: {...}}` |
| `/api/contractors/dna` | GET | Get contractor DNA patterns | `{universal: [...], partial: [...], category_specific: {...}}` |
| `/api/contractors/learning-stats` | GET | Enhanced learning stats | `{quality_metrics: {...}, relevance_stats: {...}}` |

### Feature Flag Rollout Plan

**Order of enablement (Eddie-first, 48h between each):**
1. `learning_quality_scoring_enabled` - Filters garbage learnings
2. `learning_relevance_enabled` - Replaces [-7:] with smart selection
3. `voice_signals_enabled` - Extracts pricing signals from voice
4. `acceptance_learning_enabled` - Learns from sent quote outcomes
5. `contractor_dna_enabled` - Cross-category transfer
6. `confidence_system_enabled` - Multi-dimensional confidence
7. `pricing_explanations_enabled` - Shows explanations in UI

### Key Algorithm Parameters (from design docs)

**Quality Scoring (phase2-quality-scoring.md):**
- Dimensions: Specificity (25%), Actionability (35%), Clarity (25%), Anti-patterns (-15%)
- Thresholds: REJECT < 40, REVIEW 40-60, REFINE 60-70, ACCEPT > 70
- Minimum to store: 40 (everything below is logged but discarded)

**Relevance Selection (phase3-relevance.md):**
- Weights: Keyword Match (40%), Recency (30%), Specificity (20%), Foundational (10%)
- Max selections: 7 (preserves existing behavior)
- Recency decay: 30-day half-life
- Foundational keywords: ["always", "never", "all", "every", "minimum", "maximum"]

**Acceptance Learning (phase4-acceptance.md):**
- Confidence boost on acceptance: +0.05 (vs +0.02 for corrections)
- Confidence ceiling: calibrated_accuracy + 0.15
- Attribution: Last learning applied before quote sent

**Contractor DNA (phase5-contractor-dna.md):**
- Tier thresholds: Universal (≥70% categories), Partial (40-70%), Specific (<40%)
- Bootstrap confidence: 40-60% of source confidence
- Minimum categories: 3 before DNA extraction

**Confidence System (phase6-confidence.md):**
- Dimension weights: Data (20%), Accuracy (40%), Recency (25%), Coverage (15%)
- Decay half-life: 30 days
- Accuracy calculation: 1 - avg(|corrections| / original_total)

### Test Strategy

**Unit Tests (>80% coverage per file):**
- `test_learning_quality.py`: 15 test cases (scoring, thresholds, anti-patterns)
- `test_learning_relevance.py`: 12 test cases (keyword, recency, selection)
- `test_voice_signals.py`: 10 test cases (extraction, categorization)
- `test_acceptance_learning.py`: 8 test cases (boost, attribution, ceiling)
- `test_contractor_dna.py`: 12 test cases (extraction, tiers, bootstrap)
- `test_pricing_confidence.py`: 10 test cases (dimensions, decay, calibration)
- `test_pricing_explanation.py`: 8 test cases (components, narrative, UI safety)

**Integration Tests:**
- End-to-end correction flow with quality gate
- End-to-end acceptance flow with confidence boost
- DNA transfer across categories
- Explanation generation with real data

**Browser QA Scenarios:**
1. Generate quote in NEW category → verify bootstrap confidence
2. Edit quote → verify quality scoring filters low-quality
3. Send and accept quote → verify confidence boost
4. Check explanation UI → verify progressive disclosure
5. Edit in second category → verify DNA transfer

### Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Quality scoring too aggressive | Start with 40 threshold (permissive), monitor rejection rate |
| Relevance breaks existing behavior | A/B test: 50% users get new, 50% get [-7:] |
| DNA transfer wrong patterns | Require 3+ category confirmation before universal tier |
| Confidence math errors | Extensive unit tests with known expected values |
| Explanation XSS | Use `document.createElement()` not innerHTML, sanitize all |

---

## Session Log

| Date | Phase | Actions | Outcome |
|------|-------|---------|---------|
| 2025-12-25 | 0 | Created orchestrator and state file | Ready to begin |
| 2025-12-25 | 1 | Read all design docs, analyzed integration points, created implementation plan | Phase 1 COMPLETE |

---

## Blockers

(none yet)

---

## Founder Decisions Needed

| ID | Question | Options | Decision | Date |
|----|----------|---------|----------|------|
| IMPL-001 | Proceed with implementation? | Yes / No / Defer | PENDING | - |
