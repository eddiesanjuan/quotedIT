# LLM-as-Judge Framework for Quoted Run

**DISC-101**: Quality gate for autonomous AI operations

---

## Overview

This framework provides systematic self-evaluation for `/quoted-run` cycles. A Judge Agent evaluates outputs against a defined rubric before execution decisions are made.

## Architecture

```
Primary Agent → Output → Judge Agent → Score
                                          ↓
                        ≥4.0 → Auto-execute
                        <4.0 → Suggest only (require confirmation)
```

## Evaluation Rubric

Each criterion is scored 1-5. Final score = average of all criteria.

### 1. Strategic Alignment (1-5)

| Score | Criteria |
|-------|----------|
| 5 | Directly advances sprint goals, addresses founder priorities |
| 4 | Supports strategic direction, clear business value |
| 3 | Neutral to strategy, general improvement |
| 2 | Tangential to current focus, nice-to-have |
| 1 | Misaligned with current priorities, distraction |

### 2. Autonomy Appropriateness (1-5)

| Score | Criteria |
|-------|----------|
| 5 | Purely internal, reversible, no external comms |
| 4 | Low-risk external actions, standard patterns |
| 3 | Moderate risk, follows established precedent |
| 2 | Higher risk, novel approach, should verify |
| 1 | High risk, external-facing, requires founder approval |

### 3. Output Quality (1-5)

| Score | Criteria |
|-------|----------|
| 5 | Production-ready, follows all conventions, tested |
| 4 | High quality, minor polish needed |
| 3 | Functional, meets requirements |
| 2 | Incomplete or quality issues, needs revision |
| 1 | Significant problems, not ready |

### 4. Resource Efficiency (1-5)

| Score | Criteria |
|-------|----------|
| 5 | Minimal context usage, fast execution, reusable |
| 4 | Efficient, appropriate scope |
| 3 | Reasonable resource usage |
| 2 | Higher than necessary resource consumption |
| 1 | Wasteful, over-engineered, context-heavy |

### 5. Learning Application (1-5)

| Score | Criteria |
|-------|----------|
| 5 | Applied lessons from HANDOFF.md, avoided past mistakes |
| 4 | Referenced past context, built on prior work |
| 3 | Standard approach, no repetition of known issues |
| 2 | Partial awareness of context |
| 1 | Repeated known mistakes, ignored prior learnings |

## Judge Agent Prompt

```
You are a quality judge for Quoted autonomous AI operations.

## Your Role
Evaluate the proposed action/output against the rubric below.
You are NOT the implementer - you evaluate implementation quality.

## Rubric (score each 1-5)
1. Strategic Alignment: Does this advance current priorities?
2. Autonomy Appropriateness: Is this safe for autonomous execution?
3. Output Quality: Is the output production-ready?
4. Resource Efficiency: Was this implemented efficiently?
5. Learning Application: Did this apply lessons from past sessions?

## Context Available
- HANDOFF.md: Recent session context and lessons learned
- DISCOVERY_BACKLOG.md: Current priorities and task status
- Recent git log: What was recently deployed/changed

## Your Output
```json
{
  "scores": {
    "strategic_alignment": <1-5>,
    "autonomy_appropriateness": <1-5>,
    "output_quality": <1-5>,
    "resource_efficiency": <1-5>,
    "learning_application": <1-5>
  },
  "average": <calculated>,
  "decision": "auto-execute" | "suggest-only",
  "rationale": "<2-3 sentences explaining the decision>",
  "concerns": ["<specific concerns if any>"]
}
```

## Decision Rules
- average >= 4.0 → "auto-execute"
- average < 4.0 → "suggest-only"
- ANY score of 1 → automatic "suggest-only" regardless of average
- autonomy_appropriateness <= 2 → automatic "suggest-only"
```

## Integration Points

### In /quoted-run Workflow

Insert Judge evaluation at Phase 3 (after implementation, before commit):

```
Phase 3: Execution
├── Worker implements changes
├── [NEW] Judge Agent evaluates output
│   ├── Score >= 4.0 → Proceed to commit
│   └── Score < 4.0 → Log to DECISION_QUEUE.md for founder review
└── Commit (if approved)
```

### Logging

All judge decisions logged to `QUOTED_RUN_LIVE.md`:

```
[HH:MM:SS]   🧑‍⚖️ Judge Evaluation:
   Strategic: 4 | Autonomy: 5 | Quality: 4 | Efficiency: 4 | Learning: 3
   Average: 4.0 | Decision: auto-execute
   Rationale: Output is production-ready with no external impact...
```

## Escape Hatches

1. **Founder Override**: Eddie can override any "suggest-only" by explicit approval
2. **Emergency Bypass**: Critical fixes can bypass with logged justification
3. **Threshold Adjustment**: Threshold can be raised/lowered per session

## Metrics

Track over time:
- Average scores per category
- % auto-execute vs suggest-only
- Correlation between scores and production issues
- Categories with lowest scores (improvement opportunities)

---

*Created: 2025-12-21 | DISC-101*
