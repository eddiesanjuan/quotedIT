# Safety Net Architecture for Autonomous Operations

**DISC-106**: Defense-in-depth for AI autonomous systems

---

## Overview

Autonomous AI systems need multiple layers of protection. No single safeguard is sufficient. This architecture implements five independent layers that work together to prevent runaway behavior, catch errors early, and maintain human control.

## The Five Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 5: ANOMALY DETECTION                  │
│  Pattern matching | Drift detection | Statistical outliers      │
├─────────────────────────────────────────────────────────────────┤
│                     LAYER 4: HUMAN OVERRIDE                     │
│  EMERGENCY_STOP file | /ai-stop command | Manual halt           │
├─────────────────────────────────────────────────────────────────┤
│                     LAYER 3: VERSION HISTORY                    │
│  Git commits | State snapshots | Rollback capability            │
├─────────────────────────────────────────────────────────────────┤
│                     LAYER 2: THRESHOLD SCORES                   │
│  LLM-Judge scoring | Risk classification | Confidence gates     │
├─────────────────────────────────────────────────────────────────┤
│                     LAYER 1: COOLDOWNS & RATE LIMITS            │
│  Self-dispatch cooldown | API budget | Iteration limits         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Cooldowns & Rate Limits

### Purpose

Prevent runaway loops, excessive resource consumption, and burst activity that could indicate errors.

### Implementation

#### Self-Dispatch Cooldown

```python
# In agent state file
LAST_DISPATCH_TIME: datetime
MIN_COOLDOWN_SECONDS: 60

def can_dispatch() -> bool:
    elapsed = (datetime.now() - LAST_DISPATCH_TIME).total_seconds()
    return elapsed >= MIN_COOLDOWN_SECONDS
```

#### API Budget Limits

| Scope | Limit | Action on Exceed |
|-------|-------|------------------|
| Per dispatch chain | $5 | Halt chain, log |
| Daily total | $50 | Block all agents, alert |
| Per agent session | $10 | Pause agent, require approval |

#### Iteration Limits

From Constitution Article IX:

| Agent | Max Iterations | Rationale |
|-------|----------------|-----------|
| Discovery | 3 | Three specialists, synthesis |
| Support | 5 | Bounded by inbox size |
| Ops | 10 | May need multiple health checks |
| Code | 3 | Each PR is a discrete unit |
| Growth | 5 | Content batches |
| Meta | 2 | Weekly analysis is bounded |
| Finance | 3 | Sync is deterministic |
| Loop | 5 | Event queue processing |

### Enforcement

```bash
# Check iteration count before proceeding
ITERATION_FILE=".ai-company/agents/${AGENT}/iteration.md"
CURRENT=$(cat $ITERATION_FILE 2>/dev/null || echo "0")
MAX_ITERATIONS="${MAX_ITERATIONS:-3}"

if [ "$CURRENT" -ge "$MAX_ITERATIONS" ]; then
    echo "HALT: Maximum iterations ($MAX_ITERATIONS) reached"
    echo "Reason: Safety Layer 1 - iteration limit exceeded"
    exit 1
fi

# Increment iteration count
echo "$((CURRENT + 1))" > $ITERATION_FILE
```

---

## Layer 2: Threshold Scores

### Purpose

Quality gates that block low-confidence or high-risk actions from autonomous execution.

### Implementation

Integrates with DISC-101 (LLM-as-Judge Framework):

```python
@dataclass
class SafetyScore:
    strategic_alignment: float  # 1-5
    autonomy_appropriateness: float  # 1-5
    output_quality: float  # 1-5
    resource_efficiency: float  # 1-5
    learning_application: float  # 1-5

    @property
    def average(self) -> float:
        return sum([
            self.strategic_alignment,
            self.autonomy_appropriateness,
            self.output_quality,
            self.resource_efficiency,
            self.learning_application
        ]) / 5

    def is_safe_for_autonomous(self) -> bool:
        """Check if action is safe for autonomous execution."""
        # Average must be >= 4.0
        if self.average < 4.0:
            return False
        # No individual score can be 1 (critical failure)
        if min(self.strategic_alignment, self.autonomy_appropriateness,
               self.output_quality, self.resource_efficiency,
               self.learning_application) <= 1:
            return False
        # Autonomy appropriateness must be > 2
        if self.autonomy_appropriateness <= 2:
            return False
        return True
```

### Risk Classification

From DISC-102 (Suggestions vs Updates Framework):

| Risk Level | Examples | Policy |
|------------|----------|--------|
| **LOW** | Internal analysis, drafts, DB reads | Auto-execute |
| **MEDIUM** | Content updates, comms to known contacts | Execute + log |
| **HIGH** | External comms, financial, publishing | Suggest only |
| **PROHIBITED** | Security changes, credentials | Block + alert |

### Confidence Gates

```python
def check_confidence_gate(confidence: float, action_type: str) -> tuple[bool, str]:
    """Check if action passes confidence gate."""
    thresholds = {
        "low_risk": 0.5,
        "medium_risk": 0.7,
        "high_risk": 0.9,
    }

    threshold = thresholds.get(action_type, 0.7)

    if confidence >= threshold:
        return True, f"Passed: {confidence:.0%} >= {threshold:.0%}"
    else:
        return False, f"Failed: {confidence:.0%} < {threshold:.0%} (escalate to human)"
```

---

## Layer 3: Version History

### Purpose

Maintain complete audit trail and enable rollback at any point.

### Implementation

#### Git as Version Control

Every significant action results in a git commit:

```bash
# State file changes
git add .ai-company/
git commit -m "state: [agent] [action] [timestamp]"

# Code changes
git add .
git commit -m "feat: [ticket] [description]"
```

#### State Snapshots

```bash
# Daily snapshot of all state files
SNAPSHOT_DIR=".ai-company/snapshots/$(date +%Y-%m-%d)"
mkdir -p "$SNAPSHOT_DIR"
cp -r .ai-company/state/ "$SNAPSHOT_DIR/"
cp -r .ai-company/agents/*/state.md "$SNAPSHOT_DIR/"
```

#### Rollback Procedure

```bash
# 1. Identify the commit to roll back to
git log --oneline -20

# 2. For state file rollback (soft)
git checkout <commit> -- .ai-company/

# 3. For code rollback (creates revert commit)
git revert <commit>

# 4. For complete rollback (hard, use with caution)
git reset --hard <commit>
```

### Retention Policy

| Type | Retention | Storage |
|------|-----------|---------|
| Git commits | Permanent | `.git/` |
| Daily snapshots | 30 days | `.ai-company/snapshots/` |
| Weekly archives | 1 year | External backup |
| Audit logs | Permanent | `.ai-company/logs/` |

---

## Layer 4: Human Override

### Purpose

Immediate human control over autonomous operations. Emergency stop capability.

### Implementation

#### Emergency Stop File

```bash
# Create emergency stop
touch .ai-company/EMERGENCY_STOP

# All agents check for this file before any action
if [ -f ".ai-company/EMERGENCY_STOP" ]; then
    echo "HALT: Emergency stop active"
    echo "Remove .ai-company/EMERGENCY_STOP to resume"
    exit 0
fi
```

#### /ai-stop Command

Triggers immediate halt of all autonomous operations:

```bash
# .claude/commands/ai-stop.md
# Create emergency stop file
touch .ai-company/EMERGENCY_STOP

# Record stop reason
echo "Stopped by: $USER" >> .ai-company/EMERGENCY_STOP
echo "Time: $(date -Iseconds)" >> .ai-company/EMERGENCY_STOP
echo "Reason: $1" >> .ai-company/EMERGENCY_STOP

# Kill any running workflows (GitHub Actions)
gh run list --workflow=ai-company --status=in_progress --json databaseId \
    | jq '.[].databaseId' \
    | xargs -I {} gh run cancel {}

echo "All autonomous operations halted"
```

#### AI_COMPANY_ENABLED Flag

```bash
# Environment variable check
if [ "${AI_COMPANY_ENABLED:-true}" = "false" ]; then
    echo "HALT: AI Company is disabled (AI_COMPANY_ENABLED=false)"
    exit 0
fi
```

#### Manual Override Points

Agents must check for human decisions before proceeding:

```python
def check_human_override(decision_queue_path: str) -> Optional[str]:
    """Check if human has overridden a pending decision."""
    with open(decision_queue_path, 'r') as f:
        content = f.read()

    # Look for APPROVED or REJECTED markers
    if "STATUS: APPROVED" in content:
        return "approved"
    elif "STATUS: REJECTED" in content:
        return "rejected"
    elif "STATUS: DEFERRED" in content:
        return "deferred"
    return None  # No decision yet
```

---

## Layer 5: Anomaly Detection

### Purpose

Detect unusual patterns that might indicate errors, runaway behavior, or compromised operations.

### Implementation

#### Pattern Matching

```python
class AnomalyDetector:
    """Detect anomalies in agent behavior."""

    def __init__(self):
        self.baselines = self._load_baselines()

    def check_for_anomalies(self, agent: str, metrics: dict) -> list[str]:
        """Check current metrics against baselines."""
        anomalies = []

        # Check iteration velocity
        if metrics.get("iterations_per_hour", 0) > self.baselines["max_iterations_per_hour"]:
            anomalies.append(f"High iteration velocity: {metrics['iterations_per_hour']}/hr")

        # Check API cost
        if metrics.get("api_cost_last_hour", 0) > self.baselines["max_cost_per_hour"]:
            anomalies.append(f"High API cost: ${metrics['api_cost_last_hour']:.2f}/hr")

        # Check file change velocity
        if metrics.get("files_changed_per_commit", 0) > self.baselines["max_files_per_commit"]:
            anomalies.append(f"Many file changes: {metrics['files_changed_per_commit']} files")

        # Check error rate
        if metrics.get("error_rate", 0) > self.baselines["max_error_rate"]:
            anomalies.append(f"High error rate: {metrics['error_rate']:.1%}")

        return anomalies
```

#### Drift Detection

```python
def detect_behavioral_drift(agent: str, recent_actions: list[dict]) -> Optional[str]:
    """Detect if agent behavior is drifting from expected patterns."""

    # Check for repeated similar actions (potential loop)
    action_types = [a["type"] for a in recent_actions[-10:]]
    if len(set(action_types)) == 1 and len(action_types) >= 5:
        return f"Potential loop detected: same action repeated {len(action_types)} times"

    # Check for escalating resource usage
    costs = [a.get("cost", 0) for a in recent_actions[-10:]]
    if len(costs) >= 5 and all(costs[i] < costs[i+1] for i in range(len(costs)-1)):
        return "Escalating resource usage detected"

    # Check for unusual time patterns
    timestamps = [a["timestamp"] for a in recent_actions[-10:]]
    if len(timestamps) >= 5:
        intervals = [(timestamps[i+1] - timestamps[i]).total_seconds()
                    for i in range(len(timestamps)-1)]
        if max(intervals) < 5:  # All within 5 seconds
            return "Unusually rapid actions detected"

    return None
```

#### Statistical Outliers

```python
def is_statistical_outlier(value: float, historical: list[float], threshold: float = 3.0) -> bool:
    """Check if value is a statistical outlier (>3 standard deviations)."""
    if len(historical) < 10:
        return False  # Not enough data

    mean = sum(historical) / len(historical)
    variance = sum((x - mean) ** 2 for x in historical) / len(historical)
    std_dev = variance ** 0.5

    if std_dev == 0:
        return value != mean

    z_score = abs(value - mean) / std_dev
    return z_score > threshold
```

#### Anomaly Response

```python
def respond_to_anomaly(anomaly_type: str, severity: str, details: str):
    """Respond to detected anomaly."""

    if severity == "CRITICAL":
        # Halt all operations
        create_emergency_stop(reason=f"Anomaly detected: {anomaly_type}")
        send_alert(channel="sms", message=f"CRITICAL: {details}")

    elif severity == "HIGH":
        # Pause affected agent
        pause_agent(agent=anomaly_type)
        send_alert(channel="email", message=f"HIGH: {details}")
        escalate_to_decision_queue(anomaly_type, details)

    elif severity == "MEDIUM":
        # Log and continue with monitoring
        log_anomaly(anomaly_type, details)
        send_alert(channel="slack", message=f"MEDIUM: {details}")

    else:  # LOW
        # Log only
        log_anomaly(anomaly_type, details)
```

---

## Integration Points

### In /quoted-run Workflow

```
BEFORE EACH ITERATION:
├── Check Layer 4: Emergency stop file?
├── Check Layer 4: AI_COMPANY_ENABLED?
├── Check Layer 1: Within iteration limit?
├── Check Layer 1: Cooldown elapsed?
└── Check Layer 1: Within API budget?

BEFORE EACH ACTION:
├── Check Layer 2: Action risk classification
├── Check Layer 2: Confidence gate
├── Check Layer 5: Anomaly detection
└── If all pass → Execute action

AFTER EACH ACTION:
├── Layer 3: Commit state to git
├── Layer 5: Update metrics for anomaly detection
└── Layer 1: Update iteration counter

ON ERROR:
├── Layer 3: Rollback to last known good state
├── Layer 5: Log error for pattern analysis
└── Layer 4: Escalate if repeated errors
```

### Safety Check Function

```bash
#!/bin/bash
# safety_check.sh - Run before any autonomous action

set -e

AGENT="${1:-unknown}"
ACTION="${2:-unknown}"

# Layer 4: Emergency stop
if [ -f ".ai-company/EMERGENCY_STOP" ]; then
    echo "BLOCKED: Emergency stop is active"
    exit 1
fi

# Layer 4: Enabled flag
if [ "${AI_COMPANY_ENABLED:-true}" = "false" ]; then
    echo "BLOCKED: AI Company is disabled"
    exit 1
fi

# Layer 1: Iteration limit
ITERATION_FILE=".ai-company/agents/${AGENT}/iteration.md"
ITERATION=$(cat "$ITERATION_FILE" 2>/dev/null || echo "0")
MAX="${MAX_ITERATIONS:-5}"
if [ "$ITERATION" -ge "$MAX" ]; then
    echo "BLOCKED: Iteration limit reached ($ITERATION >= $MAX)"
    exit 1
fi

# Layer 1: Cooldown
LAST_RUN_FILE=".ai-company/agents/${AGENT}/last_run"
if [ -f "$LAST_RUN_FILE" ]; then
    LAST_RUN=$(cat "$LAST_RUN_FILE")
    NOW=$(date +%s)
    ELAPSED=$((NOW - LAST_RUN))
    COOLDOWN="${COOLDOWN_SECONDS:-60}"
    if [ "$ELAPSED" -lt "$COOLDOWN" ]; then
        echo "BLOCKED: Cooldown not elapsed (${ELAPSED}s < ${COOLDOWN}s)"
        exit 1
    fi
fi

# All checks passed
echo "PASSED: All safety checks passed for $AGENT:$ACTION"
date +%s > "$LAST_RUN_FILE"
exit 0
```

---

## Monitoring Dashboard

### Metrics to Track

| Metric | Layer | Alert Threshold |
|--------|-------|-----------------|
| Iterations per hour | 1 | > 20 |
| API cost per hour | 1 | > $5 |
| Time since last human check | 4 | > 24 hours |
| Error rate (last 100 actions) | 5 | > 5% |
| Files changed per commit | 5 | > 10 |
| Repeated action count | 5 | > 5 same action |

### Daily Health Report

```markdown
## Safety Net Daily Report - [DATE]

### Layer 1: Cooldowns & Limits
- Total iterations today: X
- API cost today: $X.XX
- Budget remaining: $X.XX (XX%)

### Layer 2: Threshold Scores
- Actions auto-executed: X
- Actions escalated: X
- Average confidence: X.X%

### Layer 3: Version History
- Commits today: X
- Rollbacks today: X
- State snapshots: OK/MISSING

### Layer 4: Human Override
- Emergency stops: X
- Manual interventions: X
- Decision queue items: X

### Layer 5: Anomaly Detection
- Anomalies detected: X
- Severity breakdown: CRITICAL(X) HIGH(X) MEDIUM(X) LOW(X)
- Patterns observed: [list]

### Overall Health: GREEN/YELLOW/RED
```

---

## Testing the Safety Net

### Unit Tests

```python
def test_iteration_limit():
    """Test that iteration limit blocks execution."""
    set_iteration_count(5)
    result = safety_check("code", "implement")
    assert result.blocked
    assert "iteration limit" in result.reason

def test_emergency_stop():
    """Test that emergency stop halts all operations."""
    create_emergency_stop()
    result = safety_check("any", "any")
    assert result.blocked
    assert "emergency stop" in result.reason

def test_anomaly_detection():
    """Test that anomalies are detected."""
    # Simulate rapid repeated actions
    for _ in range(10):
        log_action("same_action", cost=0.01)
    anomalies = detect_anomalies()
    assert len(anomalies) > 0
    assert "loop" in anomalies[0].lower()
```

### Integration Tests

1. **Runaway Loop Test**: Trigger max iterations, verify halt
2. **Budget Exhaustion Test**: Simulate high API cost, verify block
3. **Emergency Stop Test**: Create stop file, verify all agents halt
4. **Rollback Test**: Make bad change, verify rollback works
5. **Anomaly Response Test**: Generate anomaly, verify alert sent

---

*Created: 2026-01-05 | DISC-106*
