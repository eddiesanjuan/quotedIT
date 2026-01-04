# Orchestrate AI Company

Build and deploy a fully autonomous AI-operated company system for Quoted, Inc.

**Philosophy**: Claude Code IS the runtime. No external frameworks. Files ARE the database. Git IS the audit trail.

## Quick Start

```bash
/ai-company                      # Run the AI company (main loop)
/ai-company status               # Check current state
/ai-company decide               # Process decision queue
/ai-company briefing             # Generate morning briefing
/ai-company --agent=support      # Run specific agent only
/ai-company --setup              # First-time setup
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     EDDIE'S MAC (Runtime)                        │
│                                                                  │
│  Claude Code                                                     │
│  └── Company Brain (this orchestrator)                           │
│      ├── Support Agent (Task)                                    │
│      ├── Ops Agent (Task)                                        │
│      ├── Growth Agent (Task)                                     │
│      └── Finance Agent (Task)                                    │
│                                                                  │
│  State Directory: quoted/.ai-company/                            │
│  └── All state persisted in markdown/JSON files                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Git sync, API calls, webhooks
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CLOUD (Minimal)                              │
│                                                                  │
│  Railway: Quoted app + Event Collector endpoint                  │
│  Resend: Email (in/out)                                          │
│  Stripe: Billing                                                 │
│  PostHog: Analytics                                              │
│  Twilio: Urgent notifications                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Phase Structure

| Phase | Name | Focus | Agents |
|-------|------|-------|--------|
| 0 | Setup | Directory structure, constitution, config | 1 |
| 1 | Event Collector | Railway endpoint for webhook ingestion | 2 |
| 2 | Support Agent | Customer communication handling | 3 |
| 3 | Ops Agent | System monitoring and fixes | 3 |
| 4 | Growth Agent | Content and campaigns | 2 |
| 5 | Finance Agent | Revenue tracking and reporting | 2 |
| 6 | Decision Queue | Human-in-loop interface | 2 |
| 7 | Operating Rhythm | Scheduled execution (launchd) | 2 |
| 8 | Integration Testing | Full system validation | 2 |
| 9 | Production Launch | Go live with monitoring | 2 |

**Total: 21 agents across 10 phases**

---

## Tool Arsenal

### Claude Code Native
- Task tool: Spawn specialist agents
- Bash: Execute any command
- Read/Write/Edit: State management
- Glob/Grep: File search
- WebFetch: API calls

### External APIs
```bash
# Railway
railway logs -n 100                    # View logs
railway variables                      # Check env vars
railway status                         # Deployment status

# GitHub
gh pr create                           # Create PR
gh pr merge                            # Merge PR

# Stripe (via curl)
curl https://api.stripe.com/v1/customers

# Resend (via curl)
curl https://api.resend.com/emails

# PostHog (via curl)
curl https://app.posthog.com/api/projects/{id}/events
```

### Notification
```bash
# Twilio SMS for urgent
curl -X POST https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json
```

---

## Phase 0: Setup

**Agent Count**: 1
**Priority**: CRITICAL
**Dependencies**: None

### Agent 0A: Initialize AI Company Infrastructure

**Target**: Create directory structure and foundational files

TASK: Set up the AI company infrastructure from scratch.

PROCEDURE:

1. Create directory structure:
```bash
mkdir -p quoted/.ai-company/{state,queues,agents/{support,ops,growth,finance},knowledge/{customers,product,playbooks},logs/{execution,decisions,audit},config}
```

2. Create CONSTITUTION.md (the rules AI must follow)

3. Create state/current.md (operational state)

4. Create queues/decisions.md (for Eddie)

5. Create queues/events.jsonl (incoming events)

6. Create config/boundaries.md (autonomy rules)

7. Create config/voice.md (brand voice guide)

8. Create agent state files for each agent

9. Create knowledge/playbooks/ with common scenarios

10. Initialize git tracking for audit trail

VERIFICATION:
- All directories exist
- All foundational files created
- Git tracking initialized
- Constitution committed

---

## Phase 1: Event Collector

**Agent Count**: 2
**Priority**: CRITICAL
**Dependencies**: Phase 0 complete

### Agent 1A: Create Event Collector Endpoint

**Target**: `backend/api/events.py`

TASK: Create minimal endpoint to receive webhooks and store events.

IMPLEMENTATION:
```python
# backend/api/events.py
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
import json
import hmac
import hashlib

router = APIRouter(prefix="/api/events", tags=["events"])

# Event storage (in production, use PostgreSQL)
# For now, append to a JSONL file that Claude Code can read

@router.post("/webhook/{source}")
async def receive_webhook(source: str, request: Request):
    """
    Receive webhooks from various sources and store for Claude Code processing.
    Sources: stripe, resend, posthog, custom
    """
    body = await request.body()
    headers = dict(request.headers)

    # Validate webhook signature based on source
    if source == "stripe":
        # Stripe signature validation
        signature = headers.get("stripe-signature", "")
        # TODO: Validate with STRIPE_WEBHOOK_SECRET
        pass
    elif source == "resend":
        # Resend signature validation
        pass

    # Parse payload
    try:
        payload = json.loads(body)
    except:
        payload = {"raw": body.decode()}

    # Classify urgency
    urgency = classify_urgency(source, payload)

    # Create event record
    event = {
        "id": f"{source}_{datetime.utcnow().timestamp()}",
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "urgency": urgency,
        "payload": payload,
        "processed": False
    }

    # Store event (append to JSONL for Claude Code to read)
    # In production: INSERT INTO events
    # For now: store in memory/file

    # If critical, send notification
    if urgency == "critical":
        await send_urgent_notification(event)

    return {"status": "received", "event_id": event["id"]}


@router.get("/pending")
async def get_pending_events():
    """Get unprocessed events for Claude Code to fetch."""
    # Return events where processed = False
    # In production: SELECT * FROM events WHERE processed = false ORDER BY timestamp
    pass


@router.post("/mark-processed/{event_id}")
async def mark_processed(event_id: str):
    """Mark event as processed by Claude Code."""
    # UPDATE events SET processed = true WHERE id = event_id
    pass


def classify_urgency(source: str, payload: dict) -> str:
    """Classify event urgency based on source and content."""
    # Critical: Refund, chargeback, security, angry customer
    # High: Payment failure, bug report, feature request
    # Normal: General inquiry, analytics update
    # Low: Marketing, informational

    if source == "stripe":
        event_type = payload.get("type", "")
        if event_type in ["charge.dispute.created", "charge.refunded"]:
            return "critical"
        if event_type in ["invoice.payment_failed"]:
            return "high"
        return "normal"

    if source == "resend":
        # Check for angry keywords
        subject = payload.get("subject", "").lower()
        body = payload.get("body", "").lower()
        if any(word in subject + body for word in ["lawyer", "legal", "sue", "refund"]):
            return "critical"
        if any(word in subject + body for word in ["bug", "broken", "not working"]):
            return "high"
        return "normal"

    return "normal"


async def send_urgent_notification(event: dict):
    """Send push notification for critical events."""
    # Use Twilio to send SMS
    # TODO: Implement with TWILIO_SID, TWILIO_AUTH, TWILIO_PHONE
    pass
```

VERIFICATION:
```bash
# Test webhook endpoint
curl -X POST "http://localhost:8000/api/events/webhook/test" \
  -H "Content-Type: application/json" \
  -d '{"type": "test_event", "data": {}}'
# Expected: {"status": "received", "event_id": "..."}
```

### Agent 1B: Wire Webhook Sources

**Target**: External service configurations

TASK: Configure Stripe, Resend, PostHog to send webhooks to collector.

PROCEDURE:

1. Stripe Webhooks:
   - Go to Stripe Dashboard > Developers > Webhooks
   - Add endpoint: `https://quoted.it.com/api/events/webhook/stripe`
   - Select events: charge.*, customer.*, invoice.*
   - Copy signing secret to Railway env

2. Resend Webhooks:
   - Configure inbound email webhook
   - Forward to: `https://quoted.it.com/api/events/webhook/resend`

3. PostHog (optional):
   - Actions > Webhooks for specific events

4. Add environment variables to Railway:
```bash
railway variables set STRIPE_WEBHOOK_SECRET=whsec_xxx
railway variables set RESEND_WEBHOOK_SECRET=xxx
railway variables set TWILIO_SID=xxx
railway variables set TWILIO_AUTH=xxx
railway variables set TWILIO_PHONE=+1xxx
railway variables set EDDIE_PHONE=+1xxx
```

VERIFICATION:
- Each webhook configured
- Test events received
- Urgent events trigger notification

---

## Phase 2: Support Agent

**Agent Count**: 3
**Priority**: HIGH
**Dependencies**: Phase 1 complete

### Agent 2A: Support Agent Core

**Target**: `.ai-company/agents/support/AGENT.md`

TASK: Create the Support Agent specification and processing logic.

IMPLEMENTATION:
```markdown
# Support Agent

## Identity
I am the Support Agent for Quoted, Inc. I handle customer communications
with empathy and efficiency, within constitutional bounds.

## Inputs
- Customer emails (from events queue, source=resend)
- In-app feedback
- App store reviews

## Processing Loop

For each support event:

1. CLASSIFY
   - Type: question | bug_report | feature_request | complaint | praise | spam
   - Urgency: critical | high | normal | low
   - Sentiment: -1.0 to 1.0
   - Requires: autonomous | approval | escalation

2. CHECK KNOWLEDGE BASE
   - Search playbooks for similar situations
   - Check customer history
   - Look for existing tickets

3. DETERMINE ACTION
   - If autonomous + high confidence: Draft and queue for auto-send
   - If needs approval: Draft response, add to decision queue
   - If escalation: Create escalation with full context

4. EXECUTE OR QUEUE
   - Autonomous: Add to actions queue with draft response
   - Approval: Add to decisions queue with recommendation
   - Escalation: Add to decisions queue with CRITICAL flag

## Response Templates

### FAQ Responses (Autonomous)
- How do I create a quote? → [Link to help article]
- How do I upload my logo? → [Step-by-step]
- What payment methods? → [List]
- How to cancel? → [Process]

### Needs Approval
- Refund requests (any amount)
- Custom pricing
- Angry customers
- Feature commitments

### Escalation Triggers
- Mentions lawyer/legal
- Sentiment < -0.5
- Confidence < 70%
- Involves money > $50

## Output Format
```json
{
  "item_id": "...",
  "classification": {...},
  "action": "autonomous|approval|escalation",
  "response_draft": "...",
  "confidence": 0.85,
  "reasoning": "..."
}
```
```

### Agent 2B: Support Knowledge Base

**Target**: `.ai-company/knowledge/playbooks/support/`

TASK: Create support playbooks for common scenarios.

FILES TO CREATE:
- `faq-responses.md` - Standard FAQ with approved responses
- `refund-policy.md` - When to approve/deny refunds
- `bug-triage.md` - How to classify and respond to bugs
- `angry-customer.md` - De-escalation techniques
- `tone-guide.md` - Brand voice for support

### Agent 2C: Support Integration

**Target**: Main orchestrator integration

TASK: Wire support agent into the main company brain loop.

IMPLEMENTATION:
- Add support agent spawning to main loop
- Create support event filter
- Route support outputs to appropriate queues

---

## Phase 3: Ops Agent

**Agent Count**: 3
**Priority**: HIGH
**Dependencies**: Phase 1 complete

### Agent 3A: Ops Agent Core

**Target**: `.ai-company/agents/ops/AGENT.md`

TASK: Create the Ops Agent specification.

IMPLEMENTATION:
```markdown
# Ops Agent

## Identity
I am the Operations Agent for Quoted, Inc. I monitor systems, detect issues,
and maintain reliability.

## Inputs
- Railway logs (polled)
- Error events
- Performance metrics
- Deployment status

## Processing Loop

1. FETCH LOGS
   ```bash
   railway logs -n 500 --filter "@level:error OR @level:warn"
   ```

2. ANALYZE
   - Group errors by type
   - Identify patterns
   - Assess severity
   - Check if known issue

3. FOR EACH ISSUE
   - If auto-fixable: Generate fix, create PR, queue for deploy approval
   - If needs investigation: Create detailed ticket
   - If critical: Escalate immediately

4. GENERATE REPORT
   - System health status
   - Issues detected
   - Fixes prepared
   - Recommendations

## Severity Classification

CRITICAL (immediate escalation):
- Auth/billing errors
- Database connection failures
- Security-related errors
- Error rate > 5%

HIGH (queue for review):
- API errors affecting users
- Performance degradation
- Failed deployments

NORMAL (log and monitor):
- Non-critical warnings
- Temporary issues that resolved

## Fix Generation Rules

Can auto-generate fixes for:
- Simple null checks
- Missing error handling
- Typos in strings
- Simple logic fixes

Must escalate for:
- Auth/billing code
- Database schema
- Security-related
- Complex logic changes

## Output Format
```json
{
  "health_status": "healthy|degraded|critical",
  "errors_found": [...],
  "fixes_generated": [...],
  "escalations": [...],
  "metrics": {...}
}
```
```

### Agent 3B: Monitoring Integration

**Target**: Railway log fetching and parsing

TASK: Create robust log monitoring system.

### Agent 3C: Fix Generation Pipeline

**Target**: Automated PR creation for simple fixes

TASK: Create pipeline that generates fixes and PRs.

---

## Phase 4: Growth Agent

**Agent Count**: 2
**Priority**: MEDIUM
**Dependencies**: Phase 0 complete

### Agent 4A: Growth Agent Core

**Target**: `.ai-company/agents/growth/AGENT.md`

TASK: Create the Growth Agent specification.

IMPLEMENTATION:
```markdown
# Growth Agent

## Identity
I am the Growth Agent for Quoted, Inc. I drive sustainable growth through
content, campaigns, and optimization.

## Capabilities

### Content Generation
- Blog posts (SEO-optimized)
- Social media posts
- Email campaigns
- In-app messages

### Analytics
- Track conversion funnels
- Monitor user engagement
- Identify growth opportunities
- Competitor monitoring

## Content Pipeline

1. IDEATION
   - Analyze trending topics
   - Check competitor content
   - Review user questions
   - Consider SEO opportunities

2. DRAFTING
   - Create outline
   - Write draft
   - Optimize for SEO
   - Add CTAs

3. QUEUE FOR APPROVAL
   - All content requires Eddie approval
   - Include: Word count, SEO score, confidence

## Campaign Management

Email Campaigns:
- Onboarding sequence (automated once approved)
- Engagement campaigns
- Win-back campaigns

Social Media:
- Twitter: Industry tips, product updates
- LinkedIn: Professional content, case studies

## Output Format
```json
{
  "content_created": [...],
  "campaigns_prepared": [...],
  "metrics_summary": {...},
  "recommendations": [...]
}
```
```

### Agent 4B: Content Templates

**Target**: `.ai-company/knowledge/playbooks/growth/`

TASK: Create content templates and guidelines.

---

## Phase 5: Finance Agent

**Agent Count**: 2
**Priority**: MEDIUM
**Dependencies**: Phase 1 complete

### Agent 5A: Finance Agent Core

**Target**: `.ai-company/agents/finance/AGENT.md`

TASK: Create the Finance Agent specification.

### Agent 5B: Financial Reporting

**Target**: Automated financial reports

TASK: Create daily/weekly/monthly financial report generation.

---

## Phase 6: Decision Queue

**Agent Count**: 2
**Priority**: CRITICAL
**Dependencies**: Phases 2-5 complete

### Agent 6A: Decision Queue System

**Target**: `.ai-company/queues/decisions.md`

TASK: Create the decision queue format and processing logic.

IMPLEMENTATION:
```markdown
# Decision Queue

## Format

Each decision entry:
```yaml
- id: DEC-001
  timestamp: 2025-01-01T10:00:00Z
  urgency: critical|high|normal|low
  category: support|ops|growth|finance
  title: Short description
  context:
    customer: (if applicable)
    data: (relevant info)
    history: (past interactions)
  ai_analysis: What AI determined
  ai_recommendation: What AI suggests
  ai_confidence: 0-100
  options:
    - id: a
      label: Option description
      action: What happens if selected
    - id: b
      label: Alternative
      action: What happens
  status: pending|approved|denied|deferred
  decision: (filled when Eddie decides)
  decided_at: (timestamp)
```

## Processing

1. READ queue from file
2. PRESENT to Eddie in priority order
3. RECORD decision with timestamp
4. MOVE to execution queue or archive

## CLI Interface

```bash
/ai-company decide
```

Shows each pending decision, collects input, records outcome.
```

### Agent 6B: Decision Execution

**Target**: Execute approved decisions

TASK: Create the execution pipeline that acts on Eddie's decisions.

---

## Phase 7: Operating Rhythm

**Agent Count**: 2
**Priority**: HIGH
**Dependencies**: Phase 6 complete

### Agent 7A: Scheduled Execution (launchd)

**Target**: macOS launchd configuration

TASK: Create scheduled execution for the AI company.

IMPLEMENTATION:

Create `~/Library/LaunchAgents/com.quoted.ai-company.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.quoted.ai-company</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant/quoted && /usr/local/bin/claude --headless --command "/ai-company" >> ~/.ai-company-logs/run.log 2>&1</string>
    </array>

    <key>StartInterval</key>
    <integer>1800</integer> <!-- Every 30 minutes -->

    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/eddiesanjuan/.ai-company-logs/stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/eddiesanjuan/.ai-company-logs/stderr.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

Load the agent:
```bash
mkdir -p ~/.ai-company-logs
launchctl load ~/Library/LaunchAgents/com.quoted.ai-company.plist
```

### Agent 7B: Morning Briefing Generator

**Target**: Daily briefing at 6 AM

TASK: Create comprehensive morning briefing generation.

Create separate launchd for morning briefing:
```xml
<!-- com.quoted.ai-company.morning.plist -->
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>6</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

---

## Phase 8: Integration Testing

**Agent Count**: 2
**Priority**: CRITICAL
**Dependencies**: Phases 0-7 complete

### Agent 8A: End-to-End Flow Testing

**Target**: Full system validation

TASK: Test complete event → processing → decision → execution flow.

TEST SCENARIOS:
1. Support email arrives → classified → response drafted → queued for approval
2. Stripe refund event → classified as critical → notification sent → queued
3. Error spike in logs → detected → fix generated → PR created → queued
4. Eddie approves decisions → executed → logged → state updated

### Agent 8B: Failure Mode Testing

**Target**: Error handling and recovery

TASK: Test system resilience.

TEST SCENARIOS:
1. Network failure during processing → graceful recovery
2. Invalid event format → logged and skipped
3. Agent timeout → retry with backoff
4. State file corruption → recovery from git

---

## Phase 9: Production Launch

**Agent Count**: 2
**Priority**: CRITICAL
**Dependencies**: Phase 8 complete

### Agent 9A: Production Deployment

**Target**: Deploy event collector, enable webhooks

TASK: Go live with the AI company system.

PROCEDURE:
1. Deploy event collector to Railway
2. Enable all webhooks
3. Load launchd agents
4. Monitor first 24 hours

### Agent 9B: Monitoring & Alerting

**Target**: Production monitoring

TASK: Set up monitoring for the AI company itself.

MONITOR:
- launchd agent running
- Event processing rate
- Decision queue depth
- Execution success rate
- Error rates

---

## Main Loop: /ai-company

When invoked, the Company Brain executes:

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPANY BRAIN MAIN LOOP                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LOAD STATE                                                   │
│     - Read .ai-company/state/current.md                         │
│     - Read .ai-company/queues/events.jsonl                      │
│     - Read .ai-company/queues/decisions.md                      │
│                                                                  │
│  2. FETCH NEW EVENTS                                             │
│     - Poll Railway: GET /api/events/pending                     │
│     - Mark fetched events as processed                          │
│     - Append to local events queue                              │
│                                                                  │
│  3. ROUTE EVENTS TO AGENTS                                       │
│     - Support events → Support Agent (Task)                     │
│     - Ops events → Ops Agent (Task)                             │
│     - Growth events → Growth Agent (Task)                       │
│     - Finance events → Finance Agent (Task)                     │
│     - Run agents in parallel where possible                     │
│                                                                  │
│  4. COLLECT AGENT OUTPUTS                                        │
│     - Autonomous actions → Action queue                         │
│     - Approval needed → Decision queue                          │
│     - Escalations → Decision queue (CRITICAL)                   │
│                                                                  │
│  5. EXECUTE AUTONOMOUS ACTIONS                                   │
│     - Process action queue                                       │
│     - Log each action with reasoning                            │
│     - Update metrics                                             │
│                                                                  │
│  6. CHECK FOR EDDIE'S DECISIONS                                  │
│     - Read decisions marked as approved/denied                  │
│     - Execute approved decisions                                 │
│     - Archive completed decisions                                │
│                                                                  │
│  7. UPDATE STATE                                                 │
│     - Update .ai-company/state/current.md                       │
│     - Update metrics                                             │
│     - Commit changes to git                                      │
│                                                                  │
│  8. SEND NOTIFICATIONS                                           │
│     - If critical items in queue: SMS Eddie                     │
│     - If daily briefing time: Send summary email                │
│                                                                  │
│  9. LOG AND EXIT                                                 │
│     - Write to execution log                                     │
│     - Update last-run timestamp                                  │
│     - Exit cleanly                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Decision Interface: /ai-company decide

Interactive decision processing:

```
/ai-company decide

1. Load pending decisions from queue
2. Sort by urgency (critical first)
3. For each decision:
   a. Display context clearly
   b. Show AI recommendation and confidence
   c. Present options
   d. Collect Eddie's choice
   e. Record decision with timestamp
4. After all decisions:
   a. Summarize decisions made
   b. Queue approved items for execution
   c. Archive decided items
5. Optionally trigger immediate execution
```

---

## State Files Reference

### state/current.md
```markdown
# AI Company State

Last Updated: 2025-01-01T10:00:00Z
Last Run: 2025-01-01T09:30:00Z

## Status
- System: OPERATIONAL
- Decision Queue: 3 pending
- Action Queue: 0 pending

## Metrics (Today)
- Events Processed: 47
- Autonomous Actions: 12
- Decisions Made: 3
- Errors: 0

## Agent Status
- Support: HEALTHY (last run: 9:30)
- Ops: HEALTHY (last run: 9:30)
- Growth: HEALTHY (last run: 9:00)
- Finance: HEALTHY (last run: 6:00)
```

### queues/decisions.md
```markdown
# Decision Queue

## Pending

### DEC-2025-001 [CRITICAL]
**Category**: Support - Refund
**Customer**: John Smith (john@example.com)
**Request**: "App doesn't work on my phone"

**Context**:
- Subscribed: 14 days ago ($9/mo)
- Usage: 0 quotes created
- Previous support: None

**AI Analysis**: User likely had mobile compatibility issue. Never successfully used product.

**AI Recommendation**: Approve refund + offer technical help
**Confidence**: 87%

**Options**:
- [a] Approve refund + offer help
- [b] Approve refund only
- [c] Deny + explain mobile requirements
- [d] Handle manually

---

### DEC-2025-002 [NORMAL]
...
```

---

## Rollback Procedures

### System Not Running
```bash
# Check launchd status
launchctl list | grep ai-company

# Reload if needed
launchctl unload ~/Library/LaunchAgents/com.quoted.ai-company.plist
launchctl load ~/Library/LaunchAgents/com.quoted.ai-company.plist
```

### State Corruption
```bash
# Restore from git
cd quoted/.ai-company
git checkout HEAD~1 -- state/
```

### Event Collector Down
- Events buffer in external services
- Manual poll when restored
- No data loss, just delayed processing

---

## Success Metrics

### Operational
- [ ] Events processed within 30 min of arrival
- [ ] Critical events notified within 5 min
- [ ] Decision queue depth < 10 at any time
- [ ] System uptime > 99%

### Efficiency
- [ ] 80%+ support tickets handled autonomously
- [ ] Average decision time < 2 minutes
- [ ] Zero missed critical events

### Quality
- [ ] Customer satisfaction maintained
- [ ] Error rate unchanged or improved
- [ ] No unauthorized actions

### Anthropic Showcase
- [ ] Full audit trail in git
- [ ] Every action logged with reasoning
- [ ] Constitutional compliance verified
- [ ] Human-in-loop functioning smoothly

---

## The Anthropic Showcase Story

This system demonstrates:

1. **Responsible AI Autonomy**
   - Clear boundaries (constitutional rules)
   - Human oversight (decision queue)
   - Transparent operations (full logging)

2. **Human-AI Collaboration**
   - AI handles volume (95% of tasks)
   - Human provides judgment (5% key decisions)
   - Clear handoff protocol

3. **Constitutional AI in Practice**
   - Explicit rules AI follows
   - Reasoning logged for every decision
   - Escalation when uncertain

4. **Economic Value**
   - One person + AI = full company operations
   - Minimal infrastructure cost
   - Scalable model

5. **Technical Excellence**
   - Native Claude Code runtime
   - File-based state (simple, auditable)
   - Git as audit trail
   - No external frameworks

**The story**: "We built a SaaS company that runs almost entirely on Claude. The AI handles customer support, monitors systems, generates content, and tracks finances. The human founder spends 10 minutes a day making key decisions. Everything else is autonomous, auditable, and aligned with responsible AI principles."
