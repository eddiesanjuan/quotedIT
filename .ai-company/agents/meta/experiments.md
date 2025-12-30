# Meta Agent Experiments

A/B tests and controlled experiments for agent improvements.

## Experiment Framework

All experiments follow these principles:
1. **Hypothesis-driven**: Clear prediction of outcome
2. **Measurable**: Defined success metrics
3. **Time-boxed**: 1-2 week duration
4. **Reversible**: Easy rollback if issues
5. **Controlled**: Compare against baseline

## Experiment Template

```markdown
### EXP-XXX: [Descriptive Title]

**Status**: PROPOSED | RUNNING | COMPLETED | ABORTED

**Hypothesis**:
If we [change], then [outcome], as measured by [metric].

**Agent**: [target agent]
**Duration**: [start] to [end]
**Sample Size**: [minimum N events]

**Control (A)**: [current behavior]
**Variant (B)**: [proposed change]

**Success Criteria**:
- Primary: [metric improves by X%]
- Secondary: [no regression in Y]
- Guard: [abort if Z happens]

**Results**:
| Metric | Control | Variant | Delta | Significant? |
|--------|---------|---------|-------|--------------|
| [metric] | [value] | [value] | [%] | [yes/no] |

**Conclusion**:
[What we learned, what to do next]

**Follow-up**:
[Actions taken based on results]
```

---

## Active Experiments

_No active experiments yet. System starting._

---

## Completed Experiments

_Experiments that have concluded with results._

---

## Experiment Ideas Backlog

Ideas for future experiments, to be prioritized.

| ID | Agent | Idea | Expected Impact | Priority |
|----|-------|------|-----------------|----------|
| - | Support | Vary acknowledgment email tone | +5% satisfaction? | Medium |
| - | Ops | Adjust alert threshold sensitivity | -20% false positives? | High |
| - | Code | Require test coverage for all PRs | +quality, -velocity? | Medium |
| - | Growth | A/B test email subject lines | +10% open rate? | Low |

---

## Learnings

Key insights from past experiments.

_Will be populated as experiments complete._
