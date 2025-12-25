# Learning Excellence Orchestrator v3.0

## Purpose

Transform Quoted's learning system into an Anthropic showcase of human-AI collaboration. This orchestrator operates as a **multi-agent coordinator** that spawns specialized agents, synthesizes their outputs, and self-continues across sessions.

**RUN THIS IN A FRESH WINDOW** for maximum context and intelligence.

---

## Architecture

```
ORCHESTRATOR (You - Coordinator)
    │
    ├── Load State & Handoff
    │
    ├── Determine Current Phase
    │
    ├── Spawn Specialist Agents ──────────────────┐
    │       (parallel where possible)             │
    │                                             ▼
    │   ┌─────────────────────────────────────────────────────┐
    │   │  AGENT POOL (Fresh Context Each)                    │
    │   │                                                     │
    │   │  • Architecture Analyst    • Quality Designer       │
    │   │  • Competitive Intel       • Implementation Agent   │
    │   │  • Database Auditor        • QA/Testing Agent       │
    │   │  • Prompt Engineer         • Voice Signal Extractor │
    │   └─────────────────────────────────────────────────────┘
    │                                             │
    │   ◄─────── Collect Agent Outputs ───────────┘
    │
    ├── Synthesize & Update State
    │
    ├── Check Continuation Conditions
    │       • Context > 80%? → Handoff
    │       • Blocker? → Document & Report
    │       • Decision needed? → Pause
    │
    └── Continue, Handoff, or Complete
```

---

## Execution Protocol

### Step 1: Load Context

```
READ these files FIRST:
1. .claude/learning-excellence-state.md (the ledger)
2. .claude/learning-excellence-handoff.md (if exists - resume context)
3. .claude/learning-excellence-outputs/ (previous agent work)
```

Parse the state ledger to determine:
- Current phase and status
- Active blockers
- Pending decisions
- What agents have already run

### Step 2: Check Continuation Conditions

Before spawning agents, check:

```
IF handoff exists:
    → Resume from handoff context
    → Don't repeat completed work

IF pending_decisions not empty:
    → Report decisions needed
    → STOP until founder responds

IF active_blockers exist:
    → Attempt resolution OR
    → Report and suggest workarounds

IF all phases complete:
    → Generate final report
    → Archive state
```

### Step 3: Spawn Phase Agents

**CRITICAL**: Each agent runs in FRESH CONTEXT via Task tool.

Spawn agents for current phase. Collect outputs. Synthesize.

**Agent Spawning Pattern:**
```
Task tool with:
  - subagent_type: appropriate type (Explore, general-purpose, etc.)
  - prompt: Focused mission with specific output format
  - run_in_background: true (for parallel execution)
```

### Step 4: Synthesize & Update

After agents complete:
1. Read all agent outputs
2. Synthesize findings into state ledger
3. Save agent outputs to `.claude/learning-excellence-outputs/`
4. Update phase status
5. Identify any new blockers or decisions

### Step 5: Continue or Handoff

```
IF context approaching limit (you feel it getting heavy):
    → Create handoff document
    → Report: "Session ending. Run /orchestrate-learning-excellence in fresh window."
    → STOP

IF next phase ready:
    → Continue to next phase
    → Loop back to Step 3

IF phase requires founder decision:
    → Update pending_decisions in state
    → Report decision needed
    → STOP
```

---

## Phase Definitions

### Phase 0: Context Loading & Baseline

**Status Check**: Read state. If phase_0.status == "COMPLETE", skip.

**Agents to Spawn:**

#### Agent 0.1: Architecture Analyst
```xml
<agent>
  <type>Explore</type>
  <id>arch-analyst</id>
  <mission>
    Map the complete learning system data flow in Quoted.

    FILES TO READ:
    - backend/services/learning.py (FULL)
    - backend/prompts/quote_generation.py (FULL)
    - backend/services/database.py (lines 200-400)
    - backend/api/quotes.py (lines 1280-1420)
    - backend/api/share.py (FULL)

    EXTRACT:
    - Data flow from correction → learning → injection
    - Decision points where quality could degrade
    - Current prompt structures
    - Storage schema for learnings
    - Quote sending detection (sent_at, shared_at, was_edited)

    OUTPUT FORMAT:
    ## Architecture Analysis

    ### Data Flow
    [ASCII diagram]

    ### Critical Decision Points
    | Point | What Happens | Risk | Severity |

    ### Injection Logic
    - How many learnings injected: X
    - Selection method: [describe]
    - Gap identified: [if any]

    ### Acceptance Signal Status
    - sent_at field: EXISTS/MISSING
    - was_edited field: EXISTS/MISSING
    - Detection possible: YES/NO
    - Implementation needed: [describe]

    ### Quality Risks
    | Risk | Location | Severity |
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase0-architecture.md</output_file>
</agent>
```

#### Agent 0.2: Competitive Intelligence
```xml
<agent>
  <type>general-purpose</type>
  <id>comp-intel</id>
  <model>haiku</model>
  <mission>
    Research how competitors handle pricing learning for contractors.

    RESEARCH:
    - ServiceTitan Titan Intelligence
    - Jobber pricing features
    - Proposify/PandaDoc pricing intelligence
    - HoneyBook AI features
    - Academic research on AI pricing assistants

    OUTPUT FORMAT (300 words max):
    ## Competitive Analysis

    ### Industry Approaches
    | Competitor | Learning Approach | Strength | Weakness |

    ### Gaps to Exploit
    - [Gap]: [Opportunity for Quoted]

    ### Best Practices
    - [Practice]: [Why relevant]

    ### Strategic Recommendation
    [1-2 sentences on how to differentiate]
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase0-competitive.md</output_file>
</agent>
```

**Synthesis**: Merge agent outputs. Update state. Identify Phase 1 requirements.

---

### Phase 1: Reality Audit

**Status Check**: If phase_1.status == "COMPLETE", skip.

**Prerequisite**: Phase 0 complete.

**Agents to Spawn:**

#### Agent 1.1: Database Auditor
```xml
<agent>
  <type>general-purpose</type>
  <id>db-auditor</id>
  <mission>
    Audit production learning data.

    APPROACH (try in order):
    1. Check if admin API endpoint exists at /api/admin/learning-stats
    2. If not, use Railway CLI: railway run python -c "..."
    3. If Railway blocked, note blocker and provide code for admin endpoint

    DATA TO COLLECT:
    - Total learning statements count
    - Category distribution
    - Sample statements (30+)
    - Quality score distribution (apply scoring heuristic)

    QUALITY SCORING HEURISTIC:
    - Has dollar amounts ($X): +30 points
    - Has percentages (X%): +25 points
    - Has specific items (deck, tile, etc.): +30 points
    - Has action words (increase, add, charge): +20 points
    - Reasonable length (30-200 chars): +10 points
    - Generic phrases ("review", "careful"): -10 points

    OUTPUT FORMAT:
    ## Database Audit

    ### Access Status
    - Method used: [API/Railway/Blocked]
    - If blocked: [Reason and resolution needed]

    ### Data Summary
    - Total statements: X
    - Categories: X
    - Contractors with learnings: X

    ### Quality Distribution
    | Quality | Count | Percentage | Example |
    | High (70+) | X | X% | "..." |
    | Medium (40-69) | X | X% | "..." |
    | Low (20-39) | X | X% | "..." |
    | Useless (<20) | X | X% | "..." |

    ### Blockers
    [If any, with resolution suggestions]
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase1-database.md</output_file>
</agent>
```

#### Agent 1.2: Effectiveness Analyst
```xml
<agent>
  <type>Explore</type>
  <id>effectiveness-analyst</id>
  <mission>
    Analyze whether learning actually improves quote accuracy.

    ANALYZE:
    - Quote edit patterns over time (if data available)
    - Correction magnitude trends
    - Category-specific performance

    IF DATABASE ACCESS BLOCKED:
    - Analyze code paths for effectiveness signals
    - Identify what metrics WOULD show effectiveness
    - Design tracking for future measurement

    OUTPUT FORMAT:
    ## Effectiveness Analysis

    ### Current Measurement Capability
    - Can measure edit rate: YES/NO
    - Can measure adjustment magnitude: YES/NO
    - Can track improvement over time: YES/NO

    ### Inferred Effectiveness Signals
    [Based on code analysis]

    ### Metrics to Implement
    | Metric | How to Capture | Why Important |

    ### Recommendation
    [What to prioritize for effectiveness tracking]
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase1-effectiveness.md</output_file>
</agent>
```

#### Agent 1.3: Acceptance Signal Analyst
```xml
<agent>
  <type>Explore</type>
  <id>acceptance-analyst</id>
  <mission>
    Determine readiness for acceptance learning ("sent without edit").

    VERIFY:
    - Does Quote model have sent_at field?
    - Does Quote model have was_edited field?
    - Where is sent_at set? (email? link? both?)
    - Can we detect "sent_at IS NOT NULL AND was_edited = FALSE"?

    IMPLEMENTATION DESIGN:
    - Where to add acceptance learning trigger
    - What to learn from acceptance signal
    - How to weight vs. correction signal

    OUTPUT FORMAT:
    ## Acceptance Signal Analysis

    ### Data Structure Status
    - sent_at: EXISTS at [location] / MISSING
    - was_edited: EXISTS at [location] / MISSING
    - Detection query: [SQL or ORM]

    ### Current Trigger Points
    | Action | Field Updated | File:Line |

    ### Implementation Plan
    1. [Step with file:line reference]
    2. [Step]

    ### Effort Estimate
    - Hours: X
    - Risk: LOW/MEDIUM/HIGH
    - Dependencies: [list]
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase1-acceptance.md</output_file>
</agent>
```

**Synthesis**: Merge findings. Update metrics baseline. Identify blockers.

---

### Phase 2: Quality Framework Design

**Agents to Spawn:**

#### Agent 2.1: Quality Scoring Designer
```xml
<agent>
  <type>general-purpose</type>
  <id>quality-designer</id>
  <mission>
    Design a quality scoring system for learning statements.

    REQUIREMENTS:
    - Score 0-100 for each statement
    - Reject statements below threshold
    - Fast enough for real-time use

    DIMENSIONS TO SCORE:
    - Specificity (numbers, item types, conditions)
    - Actionability (can be applied to future quotes)
    - Clarity (unambiguous, single rule)
    - Relevance (appropriate for category)

    OUTPUT FORMAT:
    ## Quality Scoring Framework

    ### Scoring Algorithm
    ```python
    def score_learning_statement(statement: str, category: str) -> dict:
        # Full implementation
    ```

    ### Thresholds
    - Accept: >= X
    - Review: X-Y
    - Reject: < Y

    ### Rejection Feedback Templates
    | Issue | Feedback to Claude |

    ### Integration Point
    - Where to add: [file:line]
    - When to call: [trigger]
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase2-quality-scoring.md</output_file>
</agent>
```

#### Agent 2.2: Prompt Engineer
```xml
<agent>
  <type>general-purpose</type>
  <id>prompt-engineer</id>
  <mission>
    Redesign the quote refinement prompt for higher-quality learnings.

    READ FIRST:
    - backend/services/learning.py (current prompt)

    IMPROVEMENTS:
    - Add explicit quality criteria
    - Provide good/bad examples
    - Require structured output
    - Add self-critique step

    OUTPUT FORMAT:
    ## Enhanced Refinement Prompt

    ### Changes from Current
    | Aspect | Current | Proposed | Rationale |

    ### New Prompt
    ```
    [Full prompt text, ready to copy-paste]
    ```

    ### Expected Improvement
    - Generic statement rate: X% → Y%
    - Specificity: X% → Y%
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase2-enhanced-prompt.md</output_file>
</agent>
```

---

### Phase 3: Smart Injection System

#### Agent 3.1: Relevance Algorithm Designer
```xml
<agent>
  <type>general-purpose</type>
  <id>relevance-designer</id>
  <mission>
    Replace "last 7" with intelligent relevance-based selection.

    CURRENT PROBLEM:
    Line 82 in quote_generation.py: top_learnings = learned_adjustments[-7:]
    Takes most RECENT, not most RELEVANT.

    DESIGN:
    - Relevance scoring algorithm
    - Dynamic injection count (not fixed 7)
    - Conflict handling
    - Performance requirements (<100ms)

    OUTPUT FORMAT:
    ## Relevance-Based Injection

    ### Algorithm
    ```python
    def score_relevance(statement, job_description, category) -> float:
        # Implementation

    def select_learnings(all_learnings, job_context, max_count=10) -> list:
        # Implementation
    ```

    ### Integration
    - Replace line: [file:line]
    - New code: [snippet]

    ### Performance
    - Expected latency: Xms
    - Caching strategy: [describe]
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase3-relevance.md</output_file>
</agent>
```

#### Agent 3.2: Voice Content Extractor
```xml
<agent>
  <type>general-purpose</type>
  <id>voice-extractor</id>
  <mission>
    Design system to extract pricing signals from voice transcription.

    PRINCIPLE: Learn from WORDS, not tone. Keywords, not sentiment.

    SIGNAL TYPES:
    - Difficulty: "second story", "tight space", "easy job"
    - Relationship: "repeat customer", "referral"
    - Timeline: "rush", "ASAP", "no rush"
    - Quality: "premium", "high-end", "basic"
    - Self-corrections: "no wait, make that..."

    OUTPUT FORMAT:
    ## Voice Content Extraction

    ### Signal Patterns
    | Category | Keywords | Pricing Impact |

    ### Extraction Algorithm
    ```python
    def extract_pricing_signals(transcription: str) -> dict:
        # Implementation
    ```

    ### Learning Integration
    - How to correlate signals with pricing
    - Minimum occurrences for pattern
    - Confidence thresholds
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase3-voice.md</output_file>
</agent>
```

---

### Phase 4: Acceptance & Outcome Learning

#### Agent 4.1: Acceptance Learning Implementer
```xml
<agent>
  <type>general-purpose</type>
  <id>acceptance-impl</id>
  <mission>
    Implement learning from quotes sent without edits.

    PRINCIPLE: "Sent without edit" = vote of confidence = positive signal.

    IMPLEMENTATION:
    - Detect: sent_at IS NOT NULL AND was_edited = FALSE
    - Trigger: After quote is shared/emailed
    - Learning: Reinforce current pricing patterns

    OUTPUT FORMAT:
    ## Acceptance Learning Implementation

    ### Detection Logic
    ```python
    def is_acceptance_signal(quote: Quote) -> bool:
        # Implementation
    ```

    ### Learning Trigger
    - Add to: [file:line]
    - Code: [snippet]

    ### What to Learn
    - Don't create new statements
    - Increase confidence for category
    - Weight accepted prices in future suggestions

    ### Testing Plan
    1. [Test case]
    2. [Test case]
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase4-acceptance.md</output_file>
</agent>
```

#### Agent 4.2: Outcome Tracking Designer
```xml
<agent>
  <type>general-purpose</type>
  <id>outcome-designer</id>
  <mission>
    Design system to track quote outcomes (win/loss).

    OUTCOME SIGNALS:
    - Invoice created → WIN (high confidence)
    - 30+ days no activity → Probable LOSS (medium confidence)
    - Voice: "they went with someone else" → LOSS

    OUTPUT FORMAT:
    ## Outcome Tracking System

    ### Data Model
    ```python
    class QuoteOutcome:
        # Schema
    ```

    ### Capture Triggers
    | Trigger | Outcome | Confidence | Implementation |

    ### Learning from Outcomes
    - Win rate by category
    - Price ceiling detection
    - Negotiation patterns

    ### Privacy Considerations
    [Data retention, aggregation rules]
  </mission>
  <output_file>.claude/learning-excellence-outputs/phase4-outcomes.md</output_file>
</agent>
```

---

### Phase 5: Cross-Category Intelligence

#### Agent 5.1: Contractor DNA Extractor
Design system to identify contractor-level patterns across categories.

---

### Phase 6: Confidence & Explanation Layer

#### Agent 6.1: Confidence Scoring Designer
#### Agent 6.2: Explanation Generator

---

### Phase 7: Network Intelligence (Future)

Design only, no implementation until scale achieved.

---

## Handoff Protocol

When context is getting full OR you need to pause:

1. **Update State Ledger**
   - Mark current phase status
   - Record all agent outputs
   - Log any blockers or decisions

2. **Create Handoff Document**
   ```
   Write to .claude/learning-excellence-handoff.md:

   # Learning Excellence Handoff

   ## Quick Resume
   [2-3 sentences: where we are, what's next]

   ## Session Summary
   - Date: YYYY-MM-DD
   - Phases Completed: [list]
   - Current Phase: X
   - Context Used: ~XX%

   ## Critical Findings
   [Bullet points - most important discoveries]

   ## Active Blockers
   [What's preventing progress]

   ## Pending Decisions
   [What founder needs to decide]

   ## Next Actions
   1. [Specific action]
   2. [Specific action]

   ## How to Continue
   Run `/orchestrate-learning-excellence` in a fresh window.
   ```

3. **Report to User**
   ```
   Session complete. State saved.

   To continue: Run /orchestrate-learning-excellence in a fresh window.

   Next action: [specific]
   Blocker (if any): [describe]
   Decision needed (if any): [describe]
   ```

---

## State Ledger Format

The state file at `.claude/learning-excellence-state.md` uses this structure:

```markdown
# Learning Excellence State Ledger

## Meta
- version: 3.0
- last_updated: [ISO timestamp]
- current_phase: [0-7]
- status: [IN_PROGRESS|BLOCKED|AWAITING_DECISION|COMPLETE]

## Phases

### phase_0
- status: [NOT_STARTED|IN_PROGRESS|COMPLETE]
- started_at: [timestamp]
- completed_at: [timestamp]
- agents:
  - arch-analyst: [status] → [output_file]
  - comp-intel: [status] → [output_file]
- findings: [key points]

### phase_1
[same structure]

## Blockers
- [id]: [description] (since: [date], resolution: [options])

## Decisions
### Pending
- [id]: [question] (options: [A|B|C], asked: [date])

### Resolved
- [id]: [question] → [answer] (decided: [date])

## Metrics
| Metric | Baseline | Current | Target |
```

---

## BEGIN

1. Read `.claude/learning-excellence-state.md`
2. Read `.claude/learning-excellence-handoff.md` (if exists)
3. Determine current phase and status
4. Spawn appropriate agents
5. Synthesize outputs
6. Update state
7. Continue or handoff

**Start now.**
