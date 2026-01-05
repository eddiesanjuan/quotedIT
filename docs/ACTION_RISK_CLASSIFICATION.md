# Action Risk Classification Framework

**DISC-102**: Suggestions vs Updates - Risk-based execution policy for autonomous actions

---

## Overview

Not all AI actions are equal. Some are safe to execute automatically, others need logging, still others require human approval, and some should never be done autonomously. This framework classifies actions by risk level and defines the appropriate execution policy for each.

## Core Principle

```
The RISK of an action = IMPACT if wrong x REVERSIBILITY difficulty
```

- High impact + Hard to reverse = HIGH RISK
- Low impact + Easy to reverse = LOW RISK

---

## Risk Classification Levels

### Level 0: PROHIBITED

**Definition**: Actions that should NEVER be taken autonomously, regardless of confidence.

**Policy**: Block + Alert founder immediately

**Examples**:
- Security changes (auth, credentials, secrets)
- Accessing Eddie's personal accounts
- Making legal commitments
- Sharing customer PII externally
- Deleting customer data
- Modifying the Constitution
- Bypassing security controls
- Any irreversible action without explicit approval

**Implementation**:
```python
PROHIBITED_PATTERNS = [
    r"(password|secret|credential|api_key|token).*=",
    r"rm\s+-rf\s+/",
    r"DELETE\s+FROM.*WHERE.*1\s*=\s*1",
    r"git\s+push.*--force",
    r"DROP\s+(TABLE|DATABASE)",
]

def is_prohibited(action: str) -> bool:
    for pattern in PROHIBITED_PATTERNS:
        if re.search(pattern, action, re.IGNORECASE):
            return True
    return False
```

---

### Level 1: HIGH RISK (Suggest Only)

**Definition**: Actions with significant external impact or that are difficult to reverse.

**Policy**: Queue for human approval. AI provides recommendation, human decides.

**Examples**:
- External communications (emails to customers, social posts)
- Financial transactions (refunds, discounts, invoices > $100)
- Publishing content (blog posts, marketing materials)
- Deployments to production (merging PRs)
- Database schema changes
- Third-party API integrations
- Pricing changes
- Partnership discussions

**Implementation**:
```python
def handle_high_risk(action: Action, recommendation: str, confidence: float):
    """Queue high-risk action for human approval."""
    escalation = {
        "id": generate_id(),
        "action": action.describe(),
        "recommendation": recommendation,
        "confidence": confidence,
        "risk_level": "HIGH",
        "reasoning": action.reasoning,
        "alternatives": action.alternatives,
        "time_sensitivity": action.deadline,
    }

    append_to_decision_queue(escalation)
    notify_founder(escalation, channel="email")

    return {
        "status": "queued",
        "message": "Action queued for human approval",
        "escalation_id": escalation["id"],
    }
```

---

### Level 2: MEDIUM RISK (Execute + Log)

**Definition**: Actions with moderate impact that follow established patterns.

**Policy**: Execute autonomously but log for review. Can be rolled back if issues arise.

**Examples**:
- Content updates to existing pages (not new content)
- Communications to known contacts (follow-up emails)
- Creating PRs (not merging)
- Running tests
- Updating internal documentation
- Standard analytics queries
- Task creation and updates
- Quote generation (the core product function)

**Implementation**:
```python
def handle_medium_risk(action: Action, confidence: float):
    """Execute medium-risk action with logging."""
    if confidence < 0.7:
        # Downgrade to HIGH RISK if confidence is low
        return handle_high_risk(action, action.recommendation, confidence)

    log_entry = {
        "id": generate_id(),
        "timestamp": datetime.now().isoformat(),
        "action": action.describe(),
        "confidence": confidence,
        "risk_level": "MEDIUM",
        "agent": action.agent,
    }

    # Execute the action
    try:
        result = action.execute()
        log_entry["outcome"] = "success"
        log_entry["result"] = result
    except Exception as e:
        log_entry["outcome"] = "failure"
        log_entry["error"] = str(e)
        # Escalate failures
        handle_high_risk(action, f"Action failed: {e}", 0.0)

    append_to_audit_log(log_entry)
    return result
```

---

### Level 3: LOW RISK (Auto-Execute)

**Definition**: Internal actions with minimal impact that are easily reversible.

**Policy**: Execute immediately. Minimal logging required.

**Examples**:
- Internal analysis and research
- Creating drafts (not sending/publishing)
- Database reads
- Reading files
- Generating reports
- Creating internal tickets
- Updating state files
- Running diagnostics

**Implementation**:
```python
def handle_low_risk(action: Action):
    """Execute low-risk action immediately."""
    # Minimal logging
    log_action(action.describe(), level="DEBUG")

    # Execute directly
    return action.execute()
```

---

## Classification Matrix

| Category | LOW RISK | MEDIUM RISK | HIGH RISK | PROHIBITED |
|----------|----------|-------------|-----------|------------|
| **Data** | Read | Update existing | Create new | Delete |
| **Comms** | Draft | Known contacts | New contacts | Impersonation |
| **Code** | Read/analyze | Create PR | Merge PR | Force push |
| **Finance** | Report | Track | Invoice >$100 | Refund |
| **Content** | Draft | Update existing | Publish new | External |
| **Security** | - | - | - | Any change |

---

## Action Classification Algorithm

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class RiskLevel(Enum):
    PROHIBITED = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3

@dataclass
class ClassificationResult:
    risk_level: RiskLevel
    reason: str
    confidence_threshold: float  # Min confidence for autonomous execution
    policy: str

def classify_action(action: dict) -> ClassificationResult:
    """Classify an action by risk level."""

    action_type = action.get("type", "unknown")
    target = action.get("target", "unknown")
    scope = action.get("scope", "internal")
    reversible = action.get("reversible", True)

    # Check PROHIBITED first
    if is_prohibited(action.get("description", "")):
        return ClassificationResult(
            risk_level=RiskLevel.PROHIBITED,
            reason="Matches prohibited pattern",
            confidence_threshold=float('inf'),  # Never auto-execute
            policy="block_and_alert"
        )

    # Check for external scope
    if scope == "external":
        if action_type in ["communicate", "publish", "transact"]:
            return ClassificationResult(
                risk_level=RiskLevel.HIGH,
                reason="External-facing action",
                confidence_threshold=0.95,
                policy="suggest_only"
            )

    # Check for irreversibility
    if not reversible:
        return ClassificationResult(
            risk_level=RiskLevel.HIGH,
            reason="Irreversible action",
            confidence_threshold=0.95,
            policy="suggest_only"
        )

    # Check for financial impact
    financial_impact = action.get("financial_impact", 0)
    if financial_impact > 100:
        return ClassificationResult(
            risk_level=RiskLevel.HIGH,
            reason=f"Financial impact ${financial_impact}",
            confidence_threshold=0.95,
            policy="suggest_only"
        )

    # Check for code changes
    if action_type == "code":
        if target == "merge":
            return ClassificationResult(
                risk_level=RiskLevel.HIGH,
                reason="Merging to production",
                confidence_threshold=0.95,
                policy="suggest_only"
            )
        elif target == "pr":
            return ClassificationResult(
                risk_level=RiskLevel.MEDIUM,
                reason="Creating PR (not merging)",
                confidence_threshold=0.7,
                policy="execute_and_log"
            )

    # Default classifications by action type
    type_classifications = {
        "read": RiskLevel.LOW,
        "analyze": RiskLevel.LOW,
        "draft": RiskLevel.LOW,
        "internal_update": RiskLevel.LOW,
        "create_internal": RiskLevel.MEDIUM,
        "update_external": RiskLevel.MEDIUM,
        "communicate_known": RiskLevel.MEDIUM,
        "create_external": RiskLevel.HIGH,
        "communicate_new": RiskLevel.HIGH,
        "transact": RiskLevel.HIGH,
    }

    level = type_classifications.get(action_type, RiskLevel.MEDIUM)

    return ClassificationResult(
        risk_level=level,
        reason=f"Default for action type: {action_type}",
        confidence_threshold=0.5 if level == RiskLevel.LOW else 0.7,
        policy={
            RiskLevel.LOW: "auto_execute",
            RiskLevel.MEDIUM: "execute_and_log",
            RiskLevel.HIGH: "suggest_only",
        }[level]
    )
```

---

## Integration with Autonomous Workflow

### Pre-Action Check

```python
def can_execute_autonomously(action: dict, confidence: float) -> tuple[bool, str]:
    """Check if action can be executed autonomously."""

    classification = classify_action(action)

    # PROHIBITED never executes
    if classification.risk_level == RiskLevel.PROHIBITED:
        return False, f"PROHIBITED: {classification.reason}"

    # Check confidence threshold
    if confidence < classification.confidence_threshold:
        return False, (
            f"Confidence {confidence:.0%} below threshold "
            f"{classification.confidence_threshold:.0%} for {classification.risk_level.name}"
        )

    # LOW and MEDIUM with sufficient confidence can proceed
    if classification.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
        return True, f"OK: {classification.policy}"

    # HIGH always requires approval
    return False, f"HIGH RISK: Requires human approval - {classification.reason}"
```

### In /quoted-run Workflow

```
Phase 3: Execution
├── For each planned action:
│   ├── Classify action risk level
│   ├── Check confidence vs threshold
│   │
│   ├── If PROHIBITED:
│   │   └── Log and skip (alert founder)
│   │
│   ├── If HIGH RISK or low confidence:
│   │   ├── Generate recommendation
│   │   ├── Queue to DECISION_QUEUE.md
│   │   └── Continue to next action
│   │
│   ├── If MEDIUM RISK:
│   │   ├── Execute action
│   │   ├── Log to audit trail
│   │   └── Continue to next action
│   │
│   └── If LOW RISK:
│       ├── Execute action
│       └── Continue to next action
```

---

## Decision Queue Format

When HIGH RISK actions are queued:

```markdown
## DECISION: [ID]

**Urgency**: HIGH | NORMAL
**Agent**: [agent name]
**Timestamp**: [ISO 8601]

### Action Requested
[Description of what the AI wants to do]

### Risk Classification
Level: HIGH
Reason: [why classified as high risk]
Confidence: [X]%

### AI Recommendation
[What the AI recommends doing]

### Alternatives Considered
1. [Alternative A] - [pros/cons]
2. [Alternative B] - [pros/cons]

### Time Sensitivity
[When decision needed, consequences of delay]

### Decision
- [ ] APPROVE - Execute as recommended
- [ ] REJECT - Do not execute
- [ ] MODIFY - [Custom instructions]

---
```

---

## Confidence Thresholds by Risk Level

| Risk Level | Min Confidence | Rationale |
|------------|----------------|-----------|
| PROHIBITED | N/A | Never auto-execute |
| HIGH | 95% | Very high bar for external/irreversible |
| MEDIUM | 70% | Standard confidence for routine actions |
| LOW | 50% | Minimal bar for internal/reversible |

---

## Override Mechanism

Founders can adjust classifications:

```yaml
# .ai-company/config/risk_overrides.yaml

overrides:
  # Upgrade risk level
  - pattern: "email.*customer"
    level: HIGH
    reason: "All customer emails require approval"

  # Downgrade risk level (use sparingly)
  - pattern: "update.*faq"
    level: LOW
    reason: "FAQ updates are low risk"

  # Add to PROHIBITED
  - pattern: "delete.*production"
    level: PROHIBITED
    reason: "Never delete production data"
```

---

## Audit Trail

All classifications are logged:

```json
{
  "timestamp": "2026-01-05T08:00:00Z",
  "action_id": "act_123",
  "action_type": "communicate",
  "target": "customer",
  "classification": {
    "risk_level": "HIGH",
    "reason": "External-facing action",
    "confidence_threshold": 0.95
  },
  "agent_confidence": 0.82,
  "decision": "queued_for_approval",
  "escalation_id": "esc_456"
}
```

---

## Summary

| Risk Level | Policy | Confidence Required | Examples |
|------------|--------|---------------------|----------|
| **PROHIBITED** | Block + Alert | N/A | Security, PII, legal |
| **HIGH** | Suggest Only | 95% | External comms, finance, deploy |
| **MEDIUM** | Execute + Log | 70% | PRs, known contacts, updates |
| **LOW** | Auto-Execute | 50% | Read, analyze, draft |

---

*Created: 2026-01-05 | DISC-102*
