# Escalation Configuration

## Escalation Matrix

### By Severity

| Level | Response Time | Notification Method | Approval Required |
|-------|---------------|--------------------|--------------------|
| **CRITICAL** | 5 minutes | SMS + Email | Pre-authorized actions OK |
| **HIGH** | 30 minutes | Email | Yes |
| **MEDIUM** | 4 hours | Morning briefing | Yes |
| **LOW** | 24 hours | Morning briefing | Yes |

### By Domain

```yaml
support:
  escalation_triggers:
    - sentiment_below: -0.5
    - keywords: ["lawyer", "legal", "sue", "attorney", "BBB", "complaint"]
    - keywords: ["refund", "money back", "cancel"]
    - multiple_contacts: 3  # Same customer 3+ times
    - response_time_exceeded: true
    - confidence_below: 0.5

  escalation_actions:
    critical:
      - notify_sms
      - create_high_priority_decision
      - pause_auto_responses
    high:
      - notify_email
      - create_decision
      - flag_for_review

ops:
  escalation_triggers:
    - error_rate_above: 0.05  # 5%
    - response_time_above_ms: 2000
    - system_down: true
    - payment_system_error: true
    - data_integrity_concern: true
    - security_event: any

  escalation_actions:
    critical:
      - notify_sms
      - create_incident
      - prepare_rollback
      - notify_affected_users_draft
    high:
      - notify_email
      - create_ticket
      - gather_diagnostics

growth:
  escalation_triggers:
    - content_compliance_issue: true
    - brand_reputation_mention: true
    - competitor_mention: true
    - viral_content: true

  escalation_actions:
    high:
      - pause_scheduled_content
      - notify_email
      - create_decision

finance:
  escalation_triggers:
    - dispute_filed: true
    - revenue_drop_percent: 20
    - churn_spike: 2.0  # 2x normal
    - fraud_detected: true
    - refund_request: any  # All refunds escalate

  escalation_actions:
    critical:
      - notify_sms
      - freeze_auto_actions
      - create_urgent_decision
    high:
      - notify_email
      - create_decision
```

## Keyword Triggers

### Immediate Escalation (CRITICAL)

```yaml
critical_keywords:
  legal:
    - "lawyer"
    - "attorney"
    - "legal action"
    - "sue"
    - "lawsuit"
    - "court"

  regulatory:
    - "BBB"
    - "Better Business Bureau"
    - "FTC"
    - "attorney general"
    - "class action"

  media:
    - "reporter"
    - "journalist"
    - "news"
    - "going viral"
    - "Twitter thread"

  security:
    - "hacked"
    - "breach"
    - "stolen"
    - "compromised"
    - "unauthorized access"
```

### High Priority Keywords

```yaml
high_priority_keywords:
  churn_risk:
    - "cancel"
    - "refund"
    - "money back"
    - "not worth it"
    - "switching to"
    - "competitor"

  frustration:
    - "frustrated"
    - "angry"
    - "unacceptable"
    - "ridiculous"
    - "terrible"
    - "worst"

  urgency:
    - "urgent"
    - "emergency"
    - "ASAP"
    - "immediately"
    - "critical"
```

## Notification Chains

### Critical Incident

```
1. Immediate SMS to Eddie
2. Email with full details
3. Create decision queue item
4. Prepare response drafts
5. Pause related automations
6. Log in incident tracker
```

### High Priority

```
1. Email notification
2. Create decision queue item
3. Add to morning briefing (if not addressed)
4. Follow up in 4 hours if no response
```

### Medium Priority

```
1. Add to decision queue
2. Include in morning briefing
3. Auto-deprioritize after 48 hours if no new information
```

### Low Priority

```
1. Log for weekly review
2. Batch with similar items
3. Auto-archive after 7 days if unaddressed
```

## Override Rules

### Can Skip Escalation

```yaml
skip_escalation_if:
  - known_test_user: true
  - duplicate_within_minutes: 5
  - already_escalated: true
  - customer_marked_resolved: true
```

### Must Always Escalate

```yaml
always_escalate:
  - security_mention: true
  - legal_mention: true
  - dispute_filed: true
  - any_refund_request: true
  - system_wide_outage: true
```

## Escalation Cooldowns

```yaml
cooldowns:
  # Prevent spam
  same_customer_hours: 4
  same_issue_type_hours: 1
  same_keyword_minutes: 30

  # Exception: Critical always notify
  critical_override_cooldowns: true
```

## Escalation Format

### SMS Format

```
[QUOTED ALERT] [LEVEL]
[Brief description]
[Action needed]
Reply YES to acknowledge
```

### Email Subject Format

```
[Quoted] [LEVEL] - [Brief description]
```

### Decision Queue Format

```markdown
## [ID] [LEVEL] - [Title]

**Urgency**: [CRITICAL/HIGH/MEDIUM/LOW]
**Escalated**: [timestamp]
**Source**: [agent]
**Trigger**: [what caused escalation]

### Context
[Relevant details]

### Options
1. [Option A] - [impact]
2. [Option B] - [impact]

### Recommendation
[AI recommendation with confidence]

### Quick Response
Reply with number (1-N) or custom response
```
