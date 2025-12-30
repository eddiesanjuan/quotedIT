# Build AI Civilization - Revolutionary Multi-Agent Orchestrator

**Version**: 1.0.0
**Codename**: Claude Civilization
**Philosophy**: Multiple Claude instances with fresh context, file-based coordination, recursive self-improvement.

---

## 🌟 WHAT MAKES THIS REVOLUTIONARY

This isn't another chatbot. This is a **Claude Civilization** - a multi-agent AI system that:

1. **Runs the entire company autonomously** (support, ops, growth, code)
2. **Fixes its own bugs** (Code Agent creates PRs)
3. **Improves itself recursively** (Meta Agent evolves other agents weekly)
4. **Never hits context limits** (each agent = fresh GitHub Action invocation)
5. **Maintains constitutional constraints** (can never go rogue)
6. **Provides full audit trail** (every decision traceable)

**Anthropic Showcase Qualities:**
- Human-AI collaboration (escalates to Eddie, never replaces judgment)
- Interpretable AI (all decisions explainable)
- Honest uncertainty (confidence scores on everything)
- Constitutional AI (hard limits on autonomy)
- Recursive self-improvement (within boundaries)

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLAUDE CIVILIZATION                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   SUPPORT    │  │     OPS      │  │    CODE      │  │   GROWTH     │ │
│  │    AGENT     │  │    AGENT     │  │   AGENT      │  │   AGENT      │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤ │
│  │ • Emails     │  │ • Logs       │  │ • Bug fixes  │  │ • Content    │ │
│  │ • Tickets    │  │ • Errors     │  │ • Features   │  │ • Marketing  │ │
│  │ • FAQ        │  │ • Health     │  │ • PRs        │  │ • Analytics  │ │
│  │ • Sentiment  │  │ • Incidents  │  │ • Tests      │  │ • Campaigns  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │                 │          │
│         └────────────┬────┴────────┬────────┴────────┬────────┘          │
│                      │             │                 │                   │
│                      ▼             ▼                 ▼                   │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    FILE-BASED STATE LAYER                          │  │
│  │  .ai-company/                                                      │  │
│  │    ├── queues/events.md     ← incoming from webhooks              │  │
│  │    ├── queues/decisions.md  ← needs Eddie's input                 │  │
│  │    ├── queues/actions.md    ← ready to execute                    │  │
│  │    ├── agents/*/inbox.md    ← per-agent work                      │  │
│  │    ├── agents/*/state.md    ← agent memory                        │  │
│  │    └── state/current.md     ← system state                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                         META AGENT                                 │  │
│  │  Weekly: Analyzes agent performance, updates prompts, evolves     │  │
│  │  Recursive improvement within constitutional bounds               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         EVENT GATEWAY                                    │
│  Backend endpoint: /api/ai-company/webhook/{source}                      │
│  Receives: Stripe, Resend, Railway logs, PostHog, manual triggers        │
│  Stores in: PostgreSQL → Triggers GitHub Actions                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 TOOL REFERENCE

The AI Civilization has access to ALL of these tools. Each GitHub Action workflow can invoke Claude Code CLI with any combination.

### Core Claude Code Tools

| Tool | Purpose | Example |
|------|---------|---------|
| **Read** | Read any file | `Read file_path=/path/to/file.py` |
| **Write** | Create/overwrite files | `Write file_path=/path content=...` |
| **Edit** | Precise string replacement | `Edit file_path=... old_string=... new_string=...` |
| **Glob** | Find files by pattern | `Glob pattern="**/*.py"` |
| **Grep** | Search file contents | `Grep pattern="error" path=backend/` |
| **Bash** | Execute shell commands | `Bash command="git status"` |
| **Task** | Spawn sub-agents | `Task subagent_type=Explore prompt="find error handlers"` |
| **TodoWrite** | Track work | `TodoWrite todos=[...]` |
| **WebFetch** | Fetch web content | `WebFetch url="https://..." prompt="summarize"` |
| **WebSearch** | Search the web | `WebSearch query="python fastapi error handling"` |
| **LSP** | Code intelligence | `LSP operation=goToDefinition filePath=... line=... character=...` |

### GitHub CLI (`gh`)

```bash
# Issues
gh issue create --title "..." --body "..."
gh issue list --state open --label bug
gh issue close <number> --comment "Fixed in PR #..."
gh issue edit <number> --add-label "priority:high"

# Pull Requests
gh pr create --title "..." --body "..." --base main --head feature-branch
gh pr list --state open
gh pr merge <number> --squash --delete-branch
gh pr review <number> --approve --body "LGTM"
gh pr checks <number>
gh pr diff <number>

# Workflows
gh workflow run <workflow>.yml
gh workflow list
gh run list --workflow <workflow>.yml
gh run view <run-id>
gh run watch <run-id>

# Repository
gh repo view --json name,description,url
gh api repos/{owner}/{repo}/commits --jq '.[0].sha'
gh secret set SECRET_NAME --body "value"  # Eddie only

# Code Search
gh search code "function_name" --repo eddiesanjuan/quotedIT

# Releases
gh release create v1.0.0 --title "Release" --notes "..."
gh release list
```

### Railway CLI

```bash
# Logs (CRITICAL for Ops Agent)
railway logs                        # Stream live logs
railway logs -n 100                 # Last 100 lines
railway logs --filter "@level:error" # Only errors
railway logs --json                 # JSON format for parsing

# Environment
railway variables                   # List all env vars
railway variables set KEY=value     # Set variable
railway variables get KEY           # Get specific var

# Deployment
railway status                      # Current deploy status
railway up                          # Manual deploy
railway open                        # Open dashboard

# Execution
railway run python script.py        # Run in production env
railway run alembic upgrade head    # Run migrations
```

### Playwright Browser Automation

```javascript
// Via mcp__plugin_playwright_playwright__* tools
// Or via Claude in Chrome extension

// Navigation
mcp__plugin_playwright_playwright__browser_navigate({ url: "https://quoted.it.com" })
mcp__plugin_playwright_playwright__browser_snapshot({})  // Get page state

// Interaction
mcp__plugin_playwright_playwright__browser_click({ element: "Submit button", ref: "ref_1" })
mcp__plugin_playwright_playwright__browser_type({ element: "Search field", ref: "ref_2", text: "query" })
mcp__plugin_playwright_playwright__browser_fill_form({ fields: [...] })

// Screenshots
mcp__plugin_playwright_playwright__browser_take_screenshot({ filename: "test.png" })

// Wait
mcp__plugin_playwright_playwright__browser_wait_for({ text: "Success" })

// Console & Network
mcp__plugin_playwright_playwright__browser_console_messages({ level: "error" })
mcp__plugin_playwright_playwright__browser_network_requests({})
```

### Chrome Extension (claude-in-chrome)

```javascript
// When browser profile is active
mcp__claude-in-chrome__tabs_context_mcp({})  // Get available tabs
mcp__claude-in-chrome__navigate({ url: "...", tabId: N })
mcp__claude-in-chrome__read_page({ tabId: N })  // Accessibility tree
mcp__claude-in-chrome__computer({ action: "screenshot", tabId: N })
mcp__claude-in-chrome__get_page_text({ tabId: N })  // Extract text
mcp__claude-in-chrome__read_console_messages({ tabId: N, pattern: "error" })
mcp__claude-in-chrome__read_network_requests({ tabId: N, urlPattern: "/api/" })
```

### Gmail Integration

```javascript
// Email operations
mcp__gmail__search_emails({ query: "from:support@" })
mcp__gmail__read_email({ messageId: "..." })
mcp__gmail__send_email({ to: [...], subject: "...", body: "..." })
mcp__gmail__draft_email({ to: [...], subject: "...", body: "..." })
mcp__gmail__modify_email({ messageId: "...", addLabelIds: ["Label_1"] })
mcp__gmail__list_email_labels({})
mcp__gmail__create_filter({ criteria: {...}, action: {...} })
```

### Database (via Railway)

```bash
# Direct SQL (use sparingly, prefer ORM)
railway run python -c "
from backend.models import *
from backend.database import SessionLocal
db = SessionLocal()
result = db.execute('SELECT COUNT(*) FROM contractors').fetchone()
print(result)
"

# Migrations
railway run alembic upgrade head
railway run alembic downgrade -1
railway run alembic current
railway run alembic history
```

### PostHog Analytics

```python
# Feature flags (backend/services/feature_flags.py)
from backend.services.feature_flags import is_feature_enabled

if is_feature_enabled("invoicing_enabled", user_id=contractor.id):
    # Feature is on for this user
    pass

# Track events
import posthog
posthog.capture(
    distinct_id=user_id,
    event="quote_generated",
    properties={"trade": "plumbing", "value": 1500}
)
```

---

## 🤖 AGENT SPECIFICATIONS

### Agent 1: Support Agent

**Purpose**: Handle customer support emails, tickets, and inquiries.

**Triggers**:
- New email to support@quoted.it.com (via Resend webhook)
- Customer reply to existing ticket
- Escalation from other agents

**Capabilities**:
- Read customer history from database
- Draft email responses
- Classify sentiment and urgency
- Escalate to Eddie for complex issues
- Auto-respond to FAQ questions

**Constitutional Limits**:
- NEVER promise features that don't exist
- NEVER share other customer data
- NEVER offer unauthorized refunds
- ALWAYS escalate legal mentions to Eddie
- MAX 10 auto-responses per day

**Files**:
```
.ai-company/agents/support/
├── AGENT.md           # Full agent specification
├── state.md           # Current workload, metrics
├── inbox.md           # Pending items to process
├── drafts.md          # Response drafts for review
└── templates/         # Response templates
```

### Agent 2: Ops Agent

**Purpose**: Monitor system health, handle incidents, manage deployments.

**Triggers**:
- Error pattern in Railway logs
- Health check failure
- Deployment complete
- Critical metric threshold

**Capabilities**:
- Read Railway logs
- Check deployment status
- Query database health
- Create incident reports
- Trigger Ops playbooks

**Constitutional Limits**:
- NEVER delete production data
- NEVER modify env vars without approval
- NEVER run destructive migrations
- ALWAYS create incident ticket for errors
- MAX blast radius: read-only unless incident

**Files**:
```
.ai-company/agents/ops/
├── AGENT.md           # Full agent specification
├── state.md           # System status, active incidents
├── alerts.md          # Pending alerts to investigate
├── incidents/         # Incident reports
└── playbooks/         # Runbook references
```

### Agent 3: Code Agent

**Purpose**: Fix bugs, implement simple features, create PRs.

**Triggers**:
- Bug report from Support or Ops
- Failing test in CI
- Code review request
- Simple feature ticket

**Capabilities**:
- Read entire codebase
- Write/Edit code files
- Create git branches and commits
- Create pull requests
- Run tests locally (via Bash)

**Constitutional Limits**:
- NEVER modify more than 5 files per PR
- NEVER touch auth, billing, or security code without approval
- NEVER merge own PRs (requires human review)
- NEVER push to main directly
- ALWAYS run tests before PR
- ALWAYS explain what changed and why

**Files**:
```
.ai-company/agents/code/
├── AGENT.md           # Full agent specification
├── state.md           # Active branches, WIP
├── queue.md           # Bug/feature queue
├── reviews/           # PR review comments
└── learnings.md       # What Code Agent has learned
```

### Agent 4: Growth Agent

**Purpose**: Marketing content, analytics insights, campaign management.

**Triggers**:
- Scheduled content calendar
- Significant metric change
- New competitor activity
- Blog post due date

**Capabilities**:
- Write marketing content
- Analyze PostHog data
- Research competitors (WebSearch)
- Draft social media posts
- Generate blog articles

**Constitutional Limits**:
- NEVER publish without Eddie approval
- NEVER make claims about competitors
- NEVER access customer PII for marketing
- NEVER automate email marketing
- ALWAYS fact-check statistics

**Files**:
```
.ai-company/agents/growth/
├── AGENT.md           # Full agent specification
├── state.md           # Campaign status, metrics
├── content-queue.md   # Content awaiting approval
├── drafts/            # Content drafts
└── analytics.md       # Latest insights
```

### Agent 5: Meta Agent

**Purpose**: Improve other agents. Recursive self-improvement within bounds.

**Triggers**:
- Weekly schedule (Sundays)
- Agent failure rate > threshold
- Eddie request for agent improvement

**Capabilities**:
- Read all agent performance logs
- Analyze decision quality
- Update agent prompts and playbooks
- Propose new capabilities
- A/B test agent variants

**Constitutional Limits**:
- CANNOT modify own Meta Agent spec
- CANNOT remove constitutional limits from other agents
- CANNOT increase agent blast radius
- MUST log all changes to audit trail
- MUST explain reasoning for all changes
- Eddie can veto any change

**Files**:
```
.ai-company/agents/meta/
├── AGENT.md           # Full agent specification
├── state.md           # Improvement cycles, metrics
├── evolution-log.md   # History of agent changes
├── proposals/         # Proposed improvements
└── experiments/       # A/B test results
```

---

## 📁 STATE FILE SPECIFICATIONS

### .ai-company/queues/events.md

```markdown
# Event Queue

## Pending Events

| ID | Source | Type | Urgency | Received | Payload |
|----|--------|------|---------|----------|---------|
| evt-001 | stripe | payment_failed | HIGH | 2025-12-29T10:00:00Z | {...} |
| evt-002 | resend | email_received | MEDIUM | 2025-12-29T10:05:00Z | {...} |

## Event Schema

- **ID**: Unique event identifier
- **Source**: stripe, resend, railway, manual, posthog
- **Type**: Event type from source
- **Urgency**: CRITICAL, HIGH, MEDIUM, LOW
- **Received**: ISO timestamp
- **Payload**: JSON payload from webhook (truncated for display)
```

### .ai-company/queues/decisions.md

```markdown
# Decision Queue

Items awaiting Eddie's input.

## Pending Decisions

### DEC-001: Refund Request from John Smith
**Urgency**: HIGH
**Submitted**: 2025-12-29T10:00:00Z
**Agent**: Support

**Context**:
Customer John Smith (john@example.com) requests refund after 3 days.
Reason: "App didn't work for my use case"
Subscription: Pro ($9/mo), 3 days into billing cycle

**Options**:
1. **Full refund** - $9 refunded, good customer relations
2. **Prorated refund** - $8.10 refunded (3/30 days used)
3. **Decline with explanation** - Policy is 7-day trial, already used

**Recommendation**: Option 1 (confidence: 0.8)
**Reasoning**: Customer value > $9, and good will prevents bad review.

**Eddie's Response**: [awaiting]

---

### DEC-002: Feature request from power user
...
```

### .ai-company/state/current.md

```markdown
# AI Civilization - Current State

## System Status

| Metric | Value | Status |
|--------|-------|--------|
| **System Health** | 99.9% | 🟢 GREEN |
| **Last Run** | 2025-12-29T10:30:00Z | ✓ |
| **Events Processed (24h)** | 47 | Normal |
| **Decisions Pending** | 3 | Needs attention |
| **Incidents Active** | 0 | 🟢 GREEN |

## Agent Status

| Agent | Status | Last Run | Queue Depth | Success Rate |
|-------|--------|----------|-------------|--------------|
| Support | IDLE | 10:00 | 2 | 95% |
| Ops | MONITORING | 10:30 | 0 | 100% |
| Code | WORKING | 10:15 | 1 | 88% |
| Growth | SCHEDULED | 09:00 | 5 | 92% |
| Meta | WEEKLY | Sun 18:00 | 0 | 100% |

## Recent Activity

- 10:30 - Ops Agent: Health check passed
- 10:15 - Code Agent: PR #45 created for bug fix
- 10:00 - Support Agent: Drafted response to customer inquiry
- 09:30 - System: Processed 12 events from overnight

## Constitution Violations (Last 7 Days)

None - all agents operating within bounds.
```

---

## 🔒 CONSTITUTION.md (Immutable Rules)

```markdown
# AI Civilization Constitution

These rules are IMMUTABLE. No agent, including Meta Agent, can modify them.

## Article I: Human Supremacy

1. Eddie's explicit instructions override all agent decisions
2. Any decision involving >$100 requires human approval
3. All agent actions are logged and auditable
4. Eddie can disable any agent instantly via feature flag

## Article II: Blast Radius Limits

| Agent | Max Files Modified | Max $ Impact | Data Access |
|-------|-------------------|--------------|-------------|
| Support | 0 (read-only) | $0 | Customer context only |
| Ops | 5 (configs only) | $0 | System logs, metrics |
| Code | 5 per PR | $0 | Full codebase |
| Growth | 10 (content only) | $100 (ads) | Analytics only |
| Meta | Agent specs only | $0 | Agent logs only |

## Article III: Forbidden Actions

NO agent may ever:
1. Delete production database records
2. Modify authentication/authorization code without review
3. Access or share customer payment information
4. Push directly to main branch
5. Disable safety features or feature flags
6. Contact customers without draft approval
7. Make legal commitments
8. Access other customers' data for any customer request
9. Modify this Constitution

## Article IV: Escalation Requirements

Must escalate to Eddie:
1. Any mention of: lawyer, legal, sue, refund, cancel
2. Customer sentiment score < -0.5
3. System error rate > 5%
4. Any security-related event
5. Spending decision > $50
6. PR modifying > 3 files
7. Any uncertainty with confidence < 0.7

## Article V: Transparency

1. All decisions must include reasoning
2. All automated responses must be identifiable as AI
3. All changes must link to triggering event
4. Weekly summary published for Eddie review

## Article VI: Amendment Process

Only Eddie can amend this Constitution by:
1. Direct git commit to CONSTITUTION.md
2. Verbal confirmation in Claude Code session
3. Amendment logged with timestamp and reasoning
```

---

## ⚡ GITHUB WORKFLOWS

### ai-civilization-loop.yml (Main Processing)

```yaml
name: AI Civilization - Main Loop
on:
  schedule:
    - cron: '0,30 6-22 * * *'  # Every 30 min, 6 AM - 10 PM ET
  workflow_dispatch:
    inputs:
      agent:
        description: 'Specific agent to run (or "all")'
        default: 'all'
        type: choice
        options:
          - all
          - support
          - ops
          - code
          - growth

env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code

      - name: Run Orchestration
        run: |
          claude --print "
          You are the AI Civilization Orchestrator.

          CURRENT TIME: $(date -u +%Y-%m-%dT%H:%M:%SZ)
          AGENT FILTER: ${{ inputs.agent || 'all' }}

          INSTRUCTIONS:
          1. Read .ai-company/state/current.md for system state
          2. Read .ai-company/queues/events.md for pending events
          3. For each agent (or specified agent):
             a. Read .ai-company/agents/{name}/inbox.md
             b. Process items following .ai-company/agents/{name}/AGENT.md
             c. Update .ai-company/agents/{name}/state.md
             d. Write outputs to appropriate queues
          4. Update .ai-company/state/current.md
          5. If any CRITICAL events: trigger ai-civilization-urgent.yml
          6. Commit changes with message: 'ai-civilization: loop $(date +%H:%M)'

          SAFETY:
          - Follow CONSTITUTION.md strictly
          - Escalate per Article IV
          - Never exceed blast radius limits

          BEGIN ORCHESTRATION.
          "

      - name: Push State Updates
        run: |
          git config --global user.name 'AI Civilization'
          git config --global user.email 'ai@quoted.it.com'
          git add .ai-company/
          git diff --staged --quiet || git commit -m "ai-civilization: loop $(date +%H:%M)"
          git push
```

### ai-civilization-support.yml (Support Agent)

```yaml
name: AI Civilization - Support Agent
on:
  repository_dispatch:
    types: [support_ticket]
  workflow_dispatch:
    inputs:
      ticket_id:
        description: 'Ticket ID to process'
        required: false

env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}

jobs:
  support:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code

      - name: Process Support Request
        run: |
          claude --print "
          You are the Quoted Support Agent.

          IDENTITY: You work for Quoted, a voice-to-quote SaaS for contractors.
          TICKET: ${{ github.event.client_payload.ticket || inputs.ticket_id || 'check inbox' }}

          INSTRUCTIONS:
          1. Read .ai-company/agents/support/AGENT.md for your full specification
          2. Read .ai-company/agents/support/inbox.md for pending items
          3. Read .ai-company/knowledge/product/FAQ.md for common answers
          4. Read .ai-company/knowledge/voice/BRAND_VOICE.md for tone

          FOR EACH ITEM:
          a. Classify: FAQ, Bug Report, Feature Request, Billing, Other
          b. Determine urgency: CRITICAL, HIGH, MEDIUM, LOW
          c. Check for escalation triggers (see CONSTITUTION Article IV)
          d. If FAQ with confidence > 0.9: Draft auto-response
          e. If complex: Add to .ai-company/queues/decisions.md
          f. Update .ai-company/agents/support/state.md

          OUTPUT:
          - Drafts go to .ai-company/agents/support/drafts.md
          - Escalations go to .ai-company/queues/decisions.md
          - Log activity in .ai-company/logs/execution/

          REMEMBER:
          - You are helpful, professional, empathetic
          - Never promise features that don't exist
          - Never share other customer information
          - Always offer to escalate if uncertain
          "

      - name: Commit Changes
        run: |
          git config --global user.name 'Support Agent'
          git config --global user.email 'support-agent@quoted.it.com'
          git add .ai-company/
          git diff --staged --quiet || git commit -m "support-agent: processed $(date +%H:%M)"
          git push
```

### ai-civilization-ops.yml (Ops Agent)

```yaml
name: AI Civilization - Ops Agent
on:
  repository_dispatch:
    types: [system_alert]
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:

env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

jobs:
  ops:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Install CLI Tools
        run: |
          npm install -g @anthropic-ai/claude-code
          npm install -g @railway/cli

      - name: Collect System Metrics
        run: |
          # Get Railway logs
          railway logs -n 50 --json > /tmp/railway-logs.json || echo "[]" > /tmp/railway-logs.json

          # Get deployment status
          railway status --json > /tmp/railway-status.json || echo "{}" > /tmp/railway-status.json

          # Health check
          curl -s https://quoted.it.com/api/health > /tmp/health.json || echo '{"status":"unknown"}' > /tmp/health.json

      - name: Run Ops Agent
        run: |
          claude --print "
          You are the Quoted Ops Agent.

          SYSTEM METRICS:
          - Railway Logs: $(cat /tmp/railway-logs.json | head -c 5000)
          - Deploy Status: $(cat /tmp/railway-status.json)
          - Health Check: $(cat /tmp/health.json)

          INSTRUCTIONS:
          1. Read .ai-company/agents/ops/AGENT.md for full specification
          2. Analyze logs for error patterns
          3. Check for:
             - Error rate > 5%
             - Response time > 2000ms
             - Failed health checks
             - Unusual traffic patterns

          IF ISSUES FOUND:
          a. Severity CRITICAL: Create incident, notify via SMS
          b. Severity HIGH: Create incident, add to decision queue
          c. Severity MEDIUM: Log for review
          d. Severity LOW: Track metrics only

          OUTPUT:
          - Update .ai-company/agents/ops/state.md
          - Create incidents in .ai-company/agents/ops/incidents/
          - Escalations to .ai-company/queues/decisions.md

          CRITICAL TRIGGERS:
          - 5xx error rate > 10% = IMMEDIATE ALERT
          - Database connection failure = IMMEDIATE ALERT
          - Payment processing error = IMMEDIATE ALERT
          "

      - name: Commit Changes
        run: |
          git config --global user.name 'Ops Agent'
          git config --global user.email 'ops-agent@quoted.it.com'
          git add .ai-company/
          git diff --staged --quiet || git commit -m "ops-agent: check $(date +%H:%M)"
          git push
```

### ai-civilization-code.yml (Code Agent)

```yaml
name: AI Civilization - Code Agent
on:
  repository_dispatch:
    types: [bug_report, feature_request]
  workflow_dispatch:
    inputs:
      task:
        description: 'Bug ID or feature description'
        required: true

env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

jobs:
  code:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Setup Environment
        run: |
          npm install -g @anthropic-ai/claude-code
          python -m venv venv
          source venv/bin/activate
          pip install -r backend/requirements.txt

      - name: Run Code Agent
        run: |
          source venv/bin/activate
          claude --print "
          You are the Quoted Code Agent.

          TASK: ${{ github.event.client_payload.task || inputs.task }}

          INSTRUCTIONS:
          1. Read .ai-company/agents/code/AGENT.md for full specification
          2. Read .ai-company/agents/code/queue.md for context
          3. Understand the bug/feature request fully
          4. Search codebase to find relevant files
          5. Plan the fix (max 5 files per PR!)
          6. Implement the fix
          7. Run tests: pytest backend/tests/
          8. If tests pass: Create branch and PR
          9. If tests fail: Debug and retry (max 3 attempts)

          CREATING PR:
          \`\`\`bash
          git checkout -b fix/\$(echo '${{ inputs.task }}' | tr ' ' '-' | head -c 30)
          git add -A
          git commit -m 'fix: ...'
          git push origin HEAD
          gh pr create --title 'Fix: ...' --body '...'
          \`\`\`

          CONSTITUTIONAL LIMITS:
          - Max 5 files modified
          - Never touch auth.py, billing.py without approval
          - Never push to main
          - Always run tests before PR
          - Link PR to original ticket

          OUTPUT:
          - Update .ai-company/agents/code/state.md
          - Log work in .ai-company/agents/code/reviews/
          "

      - name: Commit State
        run: |
          git config --global user.name 'Code Agent'
          git config --global user.email 'code-agent@quoted.it.com'
          git checkout main
          git add .ai-company/
          git diff --staged --quiet || git commit -m "code-agent: task $(date +%H:%M)"
          git push
```

### ai-civilization-meta.yml (Meta Agent - Weekly)

```yaml
name: AI Civilization - Meta Agent
on:
  schedule:
    - cron: '0 18 * * 0'  # Sundays at 6 PM
  workflow_dispatch:
    inputs:
      focus:
        description: 'Agent to focus improvement on'
        default: 'all'
        type: choice
        options:
          - all
          - support
          - ops
          - code
          - growth

env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

jobs:
  meta:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 100  # Need history for analysis

      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code

      - name: Run Meta Agent
        run: |
          claude --print "
          You are the Meta Agent - the self-improvement engine of AI Civilization.

          FOCUS: ${{ inputs.focus || 'all' }}

          WEEKLY ANALYSIS TASKS:

          1. PERFORMANCE REVIEW
             - Read .ai-company/logs/execution/ from past week
             - Calculate: success rate, avg response time, escalation rate
             - Identify: failures, timeouts, constitutional violations

          2. PATTERN ANALYSIS
             - What questions does Support struggle with?
             - What errors does Ops miss?
             - What PRs from Code get rejected?
             - What content from Growth needs most edits?

          3. IMPROVEMENT PROPOSALS
             For each agent, propose improvements:
             a. Prompt refinements (be specific)
             b. New playbook entries
             c. New templates
             d. Changed thresholds

             Write proposals to .ai-company/agents/meta/proposals/

          4. APPLY SAFE IMPROVEMENTS
             If improvement is LOW RISK (prompt wording, new FAQ):
             - Apply directly to agent files
             - Log in .ai-company/agents/meta/evolution-log.md

             If improvement is MEDIUM RISK (new capability, threshold change):
             - Add to .ai-company/queues/decisions.md for Eddie

          CONSTITUTIONAL LIMITS:
          - Cannot modify CONSTITUTION.md
          - Cannot remove safety limits from any agent
          - Cannot increase blast radius
          - Cannot modify your own Meta Agent spec
          - Must explain reasoning for all changes

          OUTPUT:
          - Update .ai-company/agents/meta/state.md
          - Write proposals to .ai-company/agents/meta/proposals/
          - Log changes to .ai-company/agents/meta/evolution-log.md
          - Create decision items for risky changes
          "

      - name: Commit Evolution
        run: |
          git config --global user.name 'Meta Agent'
          git config --global user.email 'meta-agent@quoted.it.com'
          git add .ai-company/
          git diff --staged --quiet || git commit -m "meta-agent: weekly evolution $(date +%Y-%m-%d)"
          git push
```

### ai-civilization-urgent.yml (Critical Events)

```yaml
name: AI Civilization - Urgent Handler
on:
  repository_dispatch:
    types: [critical_event]
  workflow_dispatch:
    inputs:
      event:
        description: 'Critical event description'
        required: true

env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  TWILIO_ACCOUNT_SID: ${{ secrets.TWILIO_ACCOUNT_SID }}
  TWILIO_AUTH_TOKEN: ${{ secrets.TWILIO_AUTH_TOKEN }}

jobs:
  urgent:
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - uses: actions/checkout@v4

      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code

      - name: Handle Critical Event
        run: |
          claude --print "
          CRITICAL EVENT HANDLER

          EVENT: ${{ github.event.client_payload.event || inputs.event }}

          IMMEDIATE ACTIONS:
          1. Classify severity (CRITICAL confirmed)
          2. Determine impact scope
          3. Draft immediate response
          4. Prepare rollback if applicable

          NOTIFICATION:
          Create SMS message (will be sent via Twilio):
          '[QUOTED ALERT] CRITICAL
          {brief description}
          {recommended action}
          Reply YES to acknowledge'

          OUTPUT:
          - Write to .ai-company/agents/ops/incidents/
          - Update .ai-company/queues/decisions.md (urgent flag)
          - Set SMS_MESSAGE env var for next step
          "

      - name: Send SMS Alert
        if: env.SMS_MESSAGE != ''
        run: |
          curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
            --data-urlencode "To=${{ secrets.EDDIE_PHONE_NUMBER }}" \
            --data-urlencode "From=${{ secrets.TWILIO_FROM_NUMBER }}" \
            --data-urlencode "Body=$SMS_MESSAGE" \
            -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"

      - name: Commit State
        run: |
          git config --global user.name 'Urgent Handler'
          git config --global user.email 'urgent@quoted.it.com'
          git add .ai-company/
          git diff --staged --quiet || git commit -m "URGENT: $(date +%H:%M)"
          git push
```

### ai-civilization-morning.yml (Daily Briefing)

```yaml
name: AI Civilization - Morning Briefing
on:
  schedule:
    - cron: '0 11 * * *'  # 6 AM ET (11 UTC)
  workflow_dispatch:

env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}

jobs:
  morning:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code

      - name: Generate Briefing
        run: |
          claude --print "
          MORNING BRIEFING GENERATOR

          TIME: $(date)

          GATHER DATA:
          1. Read .ai-company/state/current.md
          2. Read .ai-company/queues/decisions.md (count pending)
          3. Read .ai-company/queues/events.md (overnight events)
          4. Read .ai-company/agents/*/state.md (agent status)
          5. Get metrics: signups, quotes, revenue (from state)

          GENERATE BRIEFING:

          Subject: [Quoted] Morning Briefing - {date}

          ## Good Morning, Eddie

          ### 🎯 Top Priority
          {most urgent item or 'All clear'}

          ### 📊 Key Metrics (Last 24h)
          - New signups: X
          - Quotes generated: X
          - Revenue: \$X

          ### 📬 Decisions Needed ({count})
          {list top 3 with links}

          ### 🤖 Agent Summary
          - Support: {status}
          - Ops: {status}
          - Code: {status}
          - Growth: {status}

          ### 🔗 Quick Actions
          - Review decisions: [Link]
          - View dashboard: [Link]

          ---
          AI Civilization | Auto-generated

          OUTPUT:
          - Save briefing to .ai-company/logs/briefings/
          - Output BRIEFING_EMAIL env var with content
          "

      - name: Send Briefing Email
        run: |
          curl -X POST "https://api.resend.com/emails" \
            -H "Authorization: Bearer $RESEND_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{
              \"from\": \"AI Civilization <ai@quoted.it.com>\",
              \"to\": [\"eddie@quoted.it.com\"],
              \"subject\": \"[Quoted] Morning Briefing - $(date +%Y-%m-%d)\",
              \"html\": \"$BRIEFING_CONTENT\"
            }"
```

---

## 🚀 PHASE 0: ENVIRONMENT VALIDATION

**Blast Radius**: none
**Duration**: ~2 minutes

### Prerequisites Check

```bash
# Required tools
git --version          # Git available
python --version       # Python 3.8+
node --version         # Node 18+
gh --version           # GitHub CLI
railway --version      # Railway CLI

# Required secrets (will verify in Phase 8)
# - ANTHROPIC_API_KEY
# - GITHUB_TOKEN (default available)
# - RAILWAY_TOKEN
# - RESEND_API_KEY
# - TWILIO_ACCOUNT_SID (optional)
# - TWILIO_AUTH_TOKEN (optional)

# Git state
git status --porcelain
# Should be clean or only .ai-company/ changes
```

### Validation Steps

1. **Check existing .ai-company/ files**
   - Count: `find .ai-company -type f | wc -l`
   - Expected: 34 files exist from exploration phase
   - Action: Will update, not overwrite

2. **Verify backend structure**
   - Check: `ls backend/api/`
   - Verify: main.py, existing routers

3. **Check GitHub workflows**
   - Check: `ls .github/workflows/`
   - Note any existing ai-company workflows

4. **Verify Railway connection**
   - Check: `railway status`
   - Must be linked to quoted project

### On Success

Display:
```
╔══════════════════════════════════════════════════════════════╗
║         AI CIVILIZATION - ENVIRONMENT VALIDATED              ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ✓ Git: clean                                                ║
║  ✓ Python: 3.11                                              ║
║  ✓ Node: 20.x                                                ║
║  ✓ GitHub CLI: authenticated                                 ║
║  ✓ Railway CLI: linked                                       ║
║  ✓ Existing files: 34 (will update)                         ║
║                                                               ║
║  Ready for Phase 1: Foundation                                ║
╚══════════════════════════════════════════════════════════════╝
```

→ Proceed to Phase 1.

---

## 📁 PHASE 1: FOUNDATION FILES

**Blast Radius**: local
**Duration**: ~5 minutes

### Purpose

Update existing .ai-company/ files with complete, production-ready content.
Create any missing files.

### Files to Create/Update

The orchestrator will create each file with complete content.
See AGENT SPECIFICATIONS section above for agent content.
See STATE FILE SPECIFICATIONS section above for queue/state content.

### Key Files Content

#### .ai-company/CONSTITUTION.md
(See CONSTITUTION.md section above - copy verbatim)

#### .ai-company/agents/support/AGENT.md

```markdown
# Support Agent Specification

## Identity

You are the Quoted Support Agent. You handle customer inquiries with empathy, accuracy, and efficiency.

## Personality

- **Tone**: Friendly, professional, helpful
- **Style**: Concise but thorough
- **Values**: Customer success, honesty, quick resolution

## Capabilities

### CAN DO (Auto-Execute)
- Answer FAQ questions (confidence > 0.9)
- Acknowledge receipt of complex questions
- Classify and route tickets
- Draft responses for review
- Update customer context

### REQUIRES APPROVAL
- Send any response to customer
- Offer discounts or credits
- Promise future features
- Escalate to Eddie

### CANNOT DO (Hard Limits)
- Access other customer data
- Promise unauthorized refunds
- Make legal statements
- Share internal information

## Decision Framework

```
IF sentiment < -0.5:
  → ESCALATE to Eddie

IF keywords contain [lawyer, legal, sue, cancel]:
  → ESCALATE to Eddie

IF question matches FAQ with confidence > 0.9:
  → Draft auto-response
  → Mark for review unless repeat customer with history

IF complex or uncertain:
  → Draft response
  → Add to decision queue
  → Mark confidence level
```

## Input Format

Items in inbox.md:
```markdown
### TICKET-001
**From**: customer@email.com
**Subject**: Can't generate quote
**Body**: I tried to generate a quote but it keeps saying error...
**Received**: 2025-12-29T10:00:00Z
**Customer Context**: Pro subscriber since 2025-01, 47 quotes generated
```

## Output Format

Drafts in drafts.md:
```markdown
### RESPONSE TO TICKET-001
**Confidence**: 0.85
**Category**: Bug Report
**Urgency**: MEDIUM

**Draft**:
Hi [Name],

Thanks for reaching out! I'm sorry you're experiencing issues with quote generation.

Could you tell me:
1. What device/browser you're using?
2. The approximate time this happened?
3. Any error message you saw?

This will help us investigate and get you back to quoting quickly.

Best,
Quoted Support

**Recommendation**: Send after review
**Escalate**: No
```

## Metrics Tracked

- Response time (target: < 4 hours)
- Resolution rate (target: > 80% first response)
- Customer satisfaction (target: > 4.5/5)
- Escalation rate (target: < 20%)
```

#### .ai-company/agents/code/AGENT.md

```markdown
# Code Agent Specification

## Identity

You are the Quoted Code Agent. You fix bugs and implement simple features through pull requests.

## Capabilities

### CAN DO (Auto-Execute)
- Read any file in codebase
- Create feature branches
- Write/edit code (max 5 files per PR)
- Run tests locally
- Create pull requests
- Add inline comments

### REQUIRES APPROVAL
- Merge any PR (always requires human review)
- Modify more than 5 files
- Change database schema
- Modify security-related code

### CANNOT DO (Hard Limits)
- Push to main branch
- Modify auth.py, billing.py without explicit approval
- Delete files without approval
- Disable tests or safety checks
- Access production database directly

## Workflow

```
1. RECEIVE task (bug report, feature request)

2. UNDERSTAND
   - Read related code files
   - Understand the issue
   - Search for similar patterns
   - Check for existing tests

3. PLAN
   - List files to modify (max 5)
   - If > 5 files: break into multiple PRs
   - Identify test files needed
   - Estimate complexity

4. IMPLEMENT
   - Create branch: fix/{task-slug} or feat/{task-slug}
   - Make changes
   - Add/update tests
   - Run pytest backend/tests/

5. VERIFY
   - All tests pass?
   - No new linting errors?
   - Changes match requirements?

6. SUBMIT
   - git commit with clear message
   - git push
   - gh pr create with description
   - Link to original ticket

7. DOCUMENT
   - Update .ai-company/agents/code/state.md
   - Log activity
```

## PR Template

```markdown
## Summary
{One sentence description}

## Problem
{What was broken or missing}

## Solution
{How this PR fixes it}

## Changes
- `file1.py`: {what changed}
- `file2.py`: {what changed}

## Testing
- [x] Ran pytest
- [x] {specific test that covers this}

## Related
Fixes #{ticket_number}

---
🤖 Generated by Code Agent
```

## Safety Checks

Before every PR:
```python
# Check file count
if len(modified_files) > 5:
    raise Exception("Too many files. Split into multiple PRs.")

# Check forbidden files
forbidden = ['auth.py', 'billing.py', 'config.py']
for f in modified_files:
    if any(fb in f for fb in forbidden):
        raise Exception(f"Cannot modify {f} without approval")

# Check tests pass
result = subprocess.run(['pytest', 'backend/tests/'])
if result.returncode != 0:
    raise Exception("Tests failing. Fix before PR.")
```

## Metrics Tracked

- PRs created per week
- PR acceptance rate (target: > 80%)
- Avg PR size (target: < 100 lines)
- Test coverage impact
- Bug reintroduction rate
```

### Verification

- [ ] All agent AGENT.md files complete
- [ ] CONSTITUTION.md in place
- [ ] All state files initialized
- [ ] All queue files with correct format
- [ ] Directory structure complete

### On Success

Display: "✓ Phase 1: Foundation files complete" → Proceed to Phase 2.

---

## ⚙️ PHASE 2: BACKEND INTEGRATION

**Blast Radius**: local
**Duration**: ~10 minutes

### Purpose

Create the event gateway that receives webhooks and stores events for processing.

### Files Created

| File | Purpose |
|------|---------|
| backend/api/ai_events.py | Event gateway router |
| backend/models/ai_event.py | Event database model |
| backend/services/ai_dispatcher.py | Dispatch to GitHub Actions |

### backend/models/ai_event.py

```python
"""AI Company Event Model."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from backend.database import Base


class EventUrgency(enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AIEvent(Base):
    """Incoming event from external services."""
    __tablename__ = "ai_company_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Source information
    source = Column(String(50), nullable=False)  # stripe, resend, railway, manual
    event_type = Column(String(100), nullable=False)  # e.g., payment_failed

    # Classification
    urgency = Column(SQLEnum(EventUrgency), default=EventUrgency.MEDIUM)
    target_agent = Column(String(50), nullable=True)  # support, ops, code, growth

    # Content
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=True)
    raw_body = Column(Text, nullable=True)

    # Processing state
    received_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    processing_result = Column(JSON, nullable=True)

    # Linking
    related_event_id = Column(UUID(as_uuid=True), nullable=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "source": self.source,
            "event_type": self.event_type,
            "urgency": self.urgency.value,
            "target_agent": self.target_agent,
            "payload": self.payload,
            "received_at": self.received_at.isoformat(),
            "processed": self.processed
        }
```

### backend/api/ai_events.py

```python
"""AI Company Event Gateway."""
import os
import json
import hmac
import hashlib
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.ai_event import AIEvent, EventUrgency
from backend.services.ai_dispatcher import dispatch_to_agent


router = APIRouter(prefix="/api/ai-company", tags=["ai-company"])


def is_ai_company_enabled() -> bool:
    """Check if AI Company feature is enabled."""
    # Use PostHog for feature flag in production
    from backend.services.feature_flags import is_feature_enabled
    return is_feature_enabled("ai_company_enabled")


def verify_stripe_signature(payload: bytes, sig_header: str) -> bool:
    """Verify Stripe webhook signature."""
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret:
        return False

    try:
        import stripe
        stripe.Webhook.construct_event(payload, sig_header, secret)
        return True
    except Exception:
        return False


def classify_event(source: str, event_type: str, payload: dict) -> tuple[EventUrgency, str]:
    """Classify event urgency and target agent."""

    # Critical events
    critical_patterns = {
        "stripe": ["charge.dispute", "payment_intent.payment_failed"],
        "resend": ["email.bounced", "email.complained"],
        "railway": ["error", "crash", "down"],
    }

    for pattern in critical_patterns.get(source, []):
        if pattern in event_type.lower():
            return EventUrgency.CRITICAL, "ops" if source == "railway" else "support"

    # High priority
    high_patterns = {
        "stripe": ["subscription.deleted", "invoice.payment_failed"],
        "resend": ["email.failed"],
    }

    for pattern in high_patterns.get(source, []):
        if pattern in event_type:
            return EventUrgency.HIGH, "support"

    # Agent routing
    agent_routing = {
        "stripe": "support",
        "resend": "support",
        "railway": "ops",
        "github": "code",
        "posthog": "growth",
    }

    target = agent_routing.get(source, "ops")
    return EventUrgency.MEDIUM, target


@router.post("/webhook/{source}")
async def receive_webhook(
    source: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Receive webhooks from external services."""

    if not is_ai_company_enabled():
        raise HTTPException(status_code=404, detail="Not found")

    # Get raw body for signature verification
    body = await request.body()
    headers = dict(request.headers)

    # Verify signatures
    if source == "stripe":
        sig = headers.get("stripe-signature", "")
        if not verify_stripe_signature(body, sig):
            raise HTTPException(status_code=400, detail="Invalid signature")

    # Parse payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {"raw": body.decode("utf-8", errors="replace")}

    # Extract event type
    event_type = payload.get("type", payload.get("event", "unknown"))

    # Classify
    urgency, target_agent = classify_event(source, event_type, payload)

    # Store event
    event = AIEvent(
        source=source,
        event_type=event_type,
        urgency=urgency,
        target_agent=target_agent,
        payload=payload,
        headers=headers,
        raw_body=body.decode("utf-8", errors="replace")
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Dispatch critical events immediately
    if urgency == EventUrgency.CRITICAL:
        background_tasks.add_task(
            dispatch_to_agent,
            "urgent",
            {"event_id": str(event.id), "event": event.to_dict()}
        )

    return {
        "status": "received",
        "event_id": str(event.id),
        "urgency": urgency.value,
        "target_agent": target_agent
    }


@router.get("/events/pending")
async def get_pending_events(
    limit: int = 50,
    agent: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get pending events for processing."""

    if not is_ai_company_enabled():
        raise HTTPException(status_code=404, detail="Not found")

    query = db.query(AIEvent).filter(AIEvent.processed == False)

    if agent:
        query = query.filter(AIEvent.target_agent == agent)

    events = query.order_by(
        AIEvent.urgency.desc(),  # Critical first
        AIEvent.received_at.asc()  # Then oldest
    ).limit(limit).all()

    return {"events": [e.to_dict() for e in events]}


@router.post("/events/{event_id}/mark-processed")
async def mark_processed(
    event_id: str,
    result: dict,
    db: Session = Depends(get_db)
):
    """Mark an event as processed."""

    if not is_ai_company_enabled():
        raise HTTPException(status_code=404, detail="Not found")

    event = db.query(AIEvent).filter(AIEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.processed = True
    event.processed_at = datetime.utcnow()
    event.processing_result = result
    db.commit()

    return {"status": "marked", "event_id": event_id}


@router.get("/health")
async def health():
    """Health check for AI Company system."""
    if not is_ai_company_enabled():
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "status": "healthy",
        "feature": "ai_company",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### backend/services/ai_dispatcher.py

```python
"""Dispatch events to GitHub Actions."""
import os
import httpx
from typing import Optional


async def dispatch_to_agent(agent: str, payload: dict) -> bool:
    """Trigger a GitHub Action workflow for an agent."""

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return False

    owner = "eddiesanjuan"
    repo = "quotedIT"

    workflow_map = {
        "support": "ai-civilization-support.yml",
        "ops": "ai-civilization-ops.yml",
        "code": "ai-civilization-code.yml",
        "growth": "ai-civilization-growth.yml",
        "urgent": "ai-civilization-urgent.yml",
        "meta": "ai-civilization-meta.yml",
    }

    workflow = workflow_map.get(agent)
    if not workflow:
        return False

    url = f"https://api.github.com/repos/{owner}/{repo}/dispatches"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={
                "event_type": f"{agent}_dispatch",
                "client_payload": payload
            }
        )

        return response.status_code == 204


def dispatch_sync(agent: str, payload: dict) -> bool:
    """Synchronous version for background tasks."""
    import asyncio
    return asyncio.run(dispatch_to_agent(agent, payload))
```

### main.py Modification

```python
# Add to backend/main.py imports
from backend.api.ai_events import router as ai_events_router

# Add to router registration
app.include_router(ai_events_router)
```

### Database Migration

```bash
alembic revision --autogenerate -m "Add AI Company events table"
alembic upgrade head
```

### Verification

- [ ] `python -m py_compile backend/api/ai_events.py` passes
- [ ] `python -m py_compile backend/models/ai_event.py` passes
- [ ] `python -m py_compile backend/services/ai_dispatcher.py` passes
- [ ] `python -c "from backend.main import app"` loads
- [ ] Routes return 404 when flag disabled
- [ ] Routes work when flag enabled

### On Success

Display: "✓ Phase 2: Backend integration complete" → Proceed to Phase 3.

---

## 🔄 PHASE 3: GITHUB WORKFLOWS

**Blast Radius**: local
**Duration**: ~5 minutes

### Purpose

Create all GitHub Action workflows for the AI Civilization agents.

### Files Created

| File | Purpose |
|------|---------|
| .github/workflows/ai-civilization-loop.yml | Main orchestration loop |
| .github/workflows/ai-civilization-support.yml | Support Agent |
| .github/workflows/ai-civilization-ops.yml | Ops Agent |
| .github/workflows/ai-civilization-code.yml | Code Agent |
| .github/workflows/ai-civilization-growth.yml | Growth Agent |
| .github/workflows/ai-civilization-meta.yml | Meta Agent (weekly) |
| .github/workflows/ai-civilization-urgent.yml | Critical event handler |
| .github/workflows/ai-civilization-morning.yml | Morning briefing |
| .github/workflows/ai-civilization-evening.yml | Evening summary |

(See GITHUB WORKFLOWS section above for complete YAML content)

### Initial State: Schedules Commented

All workflows created with schedules commented out:

```yaml
on:
  workflow_dispatch:  # Manual only initially
  # schedule:
  #   - cron: '0,30 6-22 * * *'  # Enable in Phase 8
```

### Verification

- [ ] 9 workflow files created
- [ ] All YAML syntax valid: `python -c "import yaml; yaml.safe_load(open('file'))"`
- [ ] All have `workflow_dispatch` trigger
- [ ] All schedules commented out
- [ ] Required secrets documented

### On Success

Display: "✓ Phase 3: 9 GitHub workflows created (schedules disabled)" → Proceed to Phase 4.

---

## 📟 PHASE 4: SLASH COMMANDS

**Blast Radius**: local
**Duration**: ~5 minutes

### Purpose

Create Claude Code slash commands for operating the AI Civilization.

### Files Created

| File | Purpose |
|------|---------|
| .claude/commands/ai-status.md | View system status |
| .claude/commands/ai-decide.md | Process decision queue |
| .claude/commands/ai-run.md | Trigger agent runs |
| .claude/commands/ai-briefing.md | Generate briefing on demand |

### .claude/commands/ai-status.md

```markdown
# AI Civilization Status

Display the current status of the AI Civilization system.

---

## Instructions

1. Read .ai-company/state/current.md
2. Read .ai-company/queues/decisions.md (count pending)
3. Read .ai-company/queues/events.md (count pending)
4. Read each agent's state.md

5. Display formatted status:

```
╔══════════════════════════════════════════════════════════════╗
║                   AI CIVILIZATION STATUS                      ║
╠══════════════════════════════════════════════════════════════╣

## System Health: {GREEN/YELLOW/RED}

## Pending Items
- Decisions awaiting Eddie: {count}
- Events in queue: {count}
- Active incidents: {count}

## Agent Status
| Agent   | Status     | Last Run | Queue | Success |
|---------|------------|----------|-------|---------|
| Support | {status}   | {time}   | {n}   | {%}     |
| Ops     | {status}   | {time}   | {n}   | {%}     |
| Code    | {status}   | {time}   | {n}   | {%}     |
| Growth  | {status}   | {time}   | {n}   | {%}     |
| Meta    | {status}   | {time}   | {n}   | {%}     |

## Recent Activity
{last 5 entries from logs}

## Quick Actions
- /ai-decide     Process pending decisions
- /ai-run        Trigger agent run
- /ai-briefing   Generate briefing

╚══════════════════════════════════════════════════════════════╝
```
```

### .claude/commands/ai-decide.md

```markdown
# AI Civilization - Decision Queue

Process pending decisions that require Eddie's input.

---

## Instructions

1. Read .ai-company/queues/decisions.md
2. For each pending decision:
   a. Display the decision context
   b. Show options with AI recommendation
   c. Ask Eddie for decision
   d. Record decision and reasoning
   e. Move to completed queue
3. Update state files

## Decision Display Format

```
╔══════════════════════════════════════════════════════════════╗
║  DECISION {N} of {total}: {title}                            ║
╠══════════════════════════════════════════════════════════════╣

**Urgency**: {CRITICAL/HIGH/MEDIUM/LOW}
**From**: {agent}
**Submitted**: {timestamp}

### Context
{full context}

### Options
1. {option 1} - {impact}
2. {option 2} - {impact}
3. {option 3} - {impact}

### AI Recommendation
{recommendation} (confidence: {0.X})
**Reasoning**: {reasoning}

### Your Decision
Enter number (1-N), or type custom response:
╚══════════════════════════════════════════════════════════════╝
```

## After Decision

1. Log decision to .ai-company/logs/decisions/{date}.md
2. Move item to .ai-company/queues/completed.md
3. Notify originating agent if needed
4. Update metrics
```

### .claude/commands/ai-run.md

```markdown
# AI Civilization - Trigger Agent Run

Manually trigger an agent workflow.

---

## Arguments

- `agent`: Which agent to run (support, ops, code, growth, meta, all)
- `task`: Optional specific task for the agent

## Usage

```
/ai-run support           # Run support agent
/ai-run ops               # Run ops agent
/ai-run code fix BUG-001  # Run code agent on specific bug
/ai-run all               # Run main loop
```

## Instructions

1. Parse arguments
2. Validate agent name
3. Trigger GitHub Action:
   ```bash
   gh workflow run ai-civilization-{agent}.yml
   ```
4. Display status:
   ```bash
   gh run list --workflow ai-civilization-{agent}.yml --limit 1
   ```
5. Offer to watch:
   ```bash
   gh run watch
   ```
```

### Verification

- [ ] 4 command files created
- [ ] Valid markdown syntax
- [ ] Commands reference correct files
- [ ] Clear usage instructions

### On Success

Display: "✓ Phase 4: 4 slash commands created" → Proceed to Phase 5.

---

## 🧪 PHASE 5: INTEGRATION TESTING

**Blast Radius**: none
**Duration**: ~5 minutes

### Purpose

Verify all components work together before deployment.

### Test Suite

```
╔══════════════════════════════════════════════════════════════╗
║              PHASE 5: INTEGRATION TESTING                     ║
╠══════════════════════════════════════════════════════════════╣

1. Foundation Tests
   □ All .ai-company/ files exist
   □ CONSTITUTION.md valid
   □ All 5 agent specs complete
   □ All state files initialized
   □ All queue files formatted correctly

2. Backend Tests
   □ Python syntax valid (all new files)
   □ App loads without errors
   □ Routes registered
   □ Feature flag blocks when disabled
   □ Event classification works
   □ Dispatcher module loads

3. Workflow Tests
   □ All 9 workflow files exist
   □ YAML syntax valid
   □ Required env vars documented
   □ Schedules disabled (commented)
   □ workflow_dispatch triggers present

4. Command Tests
   □ All 4 command files exist
   □ Valid markdown
   □ Correct file references

5. Cross-Reference Tests
   □ Agent specs reference correct playbooks
   □ Workflows reference correct agent files
   □ Commands reference correct state files
   □ Constitution rules are complete

╚══════════════════════════════════════════════════════════════╝
```

### Execution

Run each test category, display results:

```
Foundation Tests:
  ✓ Directory structure complete (50+ files)
  ✓ CONSTITUTION.md valid (6 articles)
  ✓ Agent specifications complete (5/5)
  ✓ State files initialized
  ✓ Queue files formatted

Backend Tests:
  ✓ Python syntax valid (3 new files)
  ✓ App loads successfully
  ✓ Routes registered (4 routes)
  ✓ Feature flag working
  ✓ Event classification working
  ✓ Dispatcher loads

Workflow Tests:
  ✓ All workflows exist (9/9)
  ✓ YAML syntax valid
  ✓ Schedules disabled
  ✓ Manual triggers present

Command Tests:
  ✓ Commands exist (4/4)
  ✓ Valid markdown
  ✓ References valid

Cross-Reference Tests:
  ✓ Agent → Playbook references valid
  ✓ Workflow → Agent references valid
  ✓ Command → State references valid
  ✓ Constitution complete

═══════════════════════════════════════════════════════════════
  ALL TESTS PASSED: 20/20
═══════════════════════════════════════════════════════════════
```

### On Failure

Any test fails → Report which tests failed, EXIT.

### On Success

Display: "✓ Phase 5: All 20 tests passed" → Proceed to Phase 6.

---

## 🚀 PHASE 6: PREVIEW DEPLOYMENT

**Blast Radius**: preview
**Duration**: ~10 minutes

### Purpose

Deploy to Railway preview for testing before production.

### Execution Steps

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/ai-civilization
   git add .
   git commit -m "feat: AI Civilization multi-agent system

   - Add event gateway backend
   - Add 5 agent specifications
   - Add 9 GitHub workflows
   - Add slash commands
   - Add constitutional AI framework

   🤖 Generated with Claude Code"
   git push origin feature/ai-civilization
   ```

2. **Create Pull Request**
   ```bash
   gh pr create \
     --title "feat: AI Civilization - Revolutionary Multi-Agent System" \
     --body "## Summary

   Introduces AI Civilization - a multi-agent autonomous system for running Quoted.

   ### What This Adds
   - **Event Gateway**: Receives webhooks from Stripe, Resend, Railway
   - **5 Agents**: Support, Ops, Code, Growth, Meta (self-improvement)
   - **Constitutional AI**: Hard limits on agent autonomy
   - **File-based Coordination**: Agents communicate via .ai-company/
   - **GitHub Actions**: Each agent runs as separate workflow

   ### Architecture
   \`\`\`
   Webhooks → Event Gateway → Database → GitHub Actions → Agents
                                              ↓
                                    .ai-company/ files
                                              ↓
                                    Decisions → Eddie
   \`\`\`

   ### Safety
   - Feature flag: \`ai_company_enabled\` (default: false)
   - Constitutional limits on all agents
   - Human approval for all significant actions
   - Full audit trail

   ### Anthropic Showcase Ready
   - Interpretable AI (all decisions explainable)
   - Human-AI collaboration (escalation, not replacement)
   - Constitutional constraints
   - Recursive self-improvement (Meta Agent)

   ## Test Plan
   - [ ] Preview deployment healthy
   - [ ] Feature flag blocks routes when disabled
   - [ ] Feature flag enables routes when enabled
   - [ ] Webhook endpoint receives test event
   - [ ] GitHub workflow can be triggered manually

   ---
   🤖 Generated with Claude Code"
   ```

3. **Wait for Preview Deploy**
   - Railway auto-deploys PR
   - Get preview URL

4. **Test Preview**
   ```bash
   # App loads
   curl -s https://preview-url/api/health

   # AI routes blocked (flag off)
   curl -s https://preview-url/api/ai-company/health
   # Expected: 404

   # Enable flag in Railway preview
   railway variables set ai_company_enabled=true -e preview

   # AI routes work
   curl -s https://preview-url/api/ai-company/health
   # Expected: {"status": "healthy"}

   # Test webhook
   curl -X POST https://preview-url/api/ai-company/webhook/test \
     -H "Content-Type: application/json" \
     -d '{"type": "test_event", "data": {"test": true}}'
   ```

### Verification

- [ ] PR created
- [ ] Preview deployed
- [ ] App loads normally
- [ ] Existing features work
- [ ] AI routes return 404 (flag off)
- [ ] AI routes work (flag on)
- [ ] Test event stored in database

### On Failure

```bash
gh pr close feature/ai-civilization
git branch -D feature/ai-civilization
git push origin --delete feature/ai-civilization
```
Report failure, EXIT.

### On Success

Display: "✓ Phase 6: Preview deployed and verified" → Proceed to Phase 7.

---

## 🌐 PHASE 7: PRODUCTION DEPLOYMENT

**Blast Radius**: production
**Duration**: ~10 minutes

### Purpose

Merge to main, deploy to production, verify everything works.
Feature flag keeps AI routes disabled - this is dormant code.

### Why This Is Safe

The feature flag `ai_company_enabled=false` means:
- New routes return 404
- No new functionality active
- Existing Quoted features unaffected
- Deploying dormant code

The real activation is Phase 8.

### Execution Steps

1. **Merge to Main**
   ```bash
   gh pr merge feature/ai-civilization --squash \
     -m "feat: AI Civilization multi-agent system (flag disabled)"
   ```

2. **Wait for Production Deploy**
   - Railway auto-deploys on merge
   - Monitor: `railway logs`
   - Wait: ~2-3 minutes

3. **Run Database Migration**
   ```bash
   railway run alembic upgrade head
   ```

4. **Verify Migration**
   ```bash
   railway run python -c "
   from backend.database import engine
   from sqlalchemy import inspect
   tables = inspect(engine).get_table_names()
   assert 'ai_company_events' in tables
   print('✓ Migration successful')
   "
   ```

### Post-Deploy Verification

**Core Quoted Functionality** (must all pass):
```bash
# Landing page
curl -s -o /dev/null -w "%{http_code}" https://quoted.it.com
# Expected: 200

# API health
curl -s https://quoted.it.com/api/health
# Expected: {"status": "healthy"}

# Auth endpoint
curl -s -o /dev/null -w "%{http_code}" https://quoted.it.com/api/auth/check
# Expected: 401 (endpoint works, just not authed)
```

**AI Routes Blocked** (must all return 404):
```bash
curl -s -o /dev/null -w "%{http_code}" https://quoted.it.com/api/ai-company/health
# Expected: 404

curl -s -o /dev/null -w "%{http_code}" -X POST https://quoted.it.com/api/ai-company/webhook/stripe
# Expected: 404
```

**No Regressions**:
- [ ] Demo page generates quotes
- [ ] Login flow works
- [ ] Dashboard loads
- [ ] No errors in Railway logs (last 5 min)

### On Failure

```bash
# Immediate rollback
git revert HEAD
git push origin main
```

### On Success

```
✓ Phase 7: Production deployed successfully

Verified:
  ✓ Core Quoted: Landing, API, Auth, Quotes - all working
  ✓ AI Company routes: Correctly returning 404 (flag disabled)
  ✓ Database: Migration applied, ai_company_events table exists
  ✓ No regressions detected

The AI Civilization code is now in production but dormant.
Proceed to Phase 8 for activation.
```

→ Proceed to Phase 8.

---

## ⚡ PHASE 8: ACTIVATION (HANDOFF)

### Why This Is a Handoff (Not Approval)

Claude cannot log into:
- GitHub Settings (for secrets)
- Stripe Dashboard (for webhooks)
- Resend Dashboard (for webhooks)
- Railway Dashboard (for feature flag)

This is the checklist for things only Eddie can configure.

---

### 🎯 YOUR ACTIVATION CHECKLIST

**Time Required**: ~15 minutes

#### Step 1: GitHub Secrets (github.com → Settings → Secrets)

Navigate to: `https://github.com/eddiesanjuan/quotedIT/settings/secrets/actions`

Add these repository secrets:
```
ANTHROPIC_API_KEY      = [your Anthropic API key]
RAILWAY_TOKEN          = [from railway.app → Account → Tokens]
RESEND_API_KEY         = [from resend.com → API Keys]
STRIPE_WEBHOOK_SECRET  = [will get from Step 2]
TWILIO_ACCOUNT_SID     = [optional, from twilio.com]
TWILIO_AUTH_TOKEN      = [optional, from twilio.com]
TWILIO_FROM_NUMBER     = [optional, your Twilio number]
EDDIE_PHONE_NUMBER     = [optional, your phone for SMS alerts]
```

#### Step 2: Stripe Webhook (stripe.com → Developers → Webhooks)

Navigate to: `https://dashboard.stripe.com/webhooks`

Create new endpoint:
```
Endpoint URL:  https://quoted.it.com/api/ai-company/webhook/stripe
Description:   AI Civilization Event Gateway

Events to send:
  ☑️ customer.subscription.created
  ☑️ customer.subscription.deleted
  ☑️ invoice.payment_failed
  ☑️ charge.dispute.created
  ☑️ charge.refunded
```

Copy the **Signing secret** (starts with `whsec_`) → Add to GitHub Secrets as `STRIPE_WEBHOOK_SECRET`

#### Step 3: Resend Webhook (resend.com → Webhooks)

Navigate to: `https://resend.com/webhooks`

Create new webhook:
```
Endpoint URL:  https://quoted.it.com/api/ai-company/webhook/resend

Events:
  ☑️ email.sent
  ☑️ email.delivered
  ☑️ email.bounced
  ☑️ email.complained
  ☑️ email.opened
  ☑️ email.clicked
```

#### Step 4: Enable Feature Flag (PostHog)

Navigate to: `https://app.posthog.com` → Feature Flags

Find or create `ai_company_enabled`:
- Set to `true` for your user first
- Test workflows manually
- Then set to `true` for all users

#### Step 5: Enable Workflow Schedules

Edit each workflow file to uncomment the schedule:

```yaml
# Change this:
on:
  workflow_dispatch:
  # schedule:
  #   - cron: '0,30 6-22 * * *'

# To this:
on:
  workflow_dispatch:
  schedule:
    - cron: '0,30 6-22 * * *'
```

Commit and push.

#### Step 6: First Test Run

```bash
# Trigger main loop manually
gh workflow run ai-civilization-loop.yml

# Watch execution
gh run watch

# Check results
cat .ai-company/state/current.md
cat .ai-company/logs/execution/$(date +%Y-%m-%d).md
```

#### Step 7: Verify Everything

1. Send a test email to support@quoted.it.com
2. Wait 30 minutes for next loop
3. Check .ai-company/agents/support/inbox.md
4. Verify Support Agent processed it

---

### 🎉 AI CIVILIZATION IS LIVE

```
╔══════════════════════════════════════════════════════════════╗
║           🌟 AI CIVILIZATION IS NOW RUNNING 🌟                ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  What's Active:                                               ║
║  • Event Gateway receiving webhooks                          ║
║  • Main loop every 30 minutes (6 AM - 10 PM)                 ║
║  • Support Agent processing inquiries                        ║
║  • Ops Agent monitoring system health                        ║
║  • Code Agent ready for bug assignments                      ║
║  • Growth Agent tracking content calendar                    ║
║  • Meta Agent improving weekly                               ║
║                                                               ║
║  Your Daily Routine:                                          ║
║  • Morning: Review briefing email (6 AM)                     ║
║  • As needed: /ai-decide to process queue                    ║
║  • Anytime: /ai-status for overview                          ║
║  • SMS alerts for critical events                            ║
║                                                               ║
║  First 48 Hours:                                              ║
║  • Watch GitHub Actions for successful runs                  ║
║  • Check .ai-company/logs/ for activity                      ║
║  • Review decision queue daily                               ║
║  • Tune thresholds if needed                                 ║
║                                                               ║
║  Emergency Shutdown:                                          ║
║  1. PostHog: Disable ai_company_enabled flag                 ║
║  2. GitHub: Comment out workflow schedules                   ║
║                                                               ║
║  Revolutionary. Showcase-ready. LIVE.                        ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 🔄 STATE FILE FORMAT

### .claude/build-ai-civilization-state.md

```markdown
# AI Civilization Build State

## Status

| Field | Value |
|-------|-------|
| **Current Phase** | 0 |
| **Phase Status** | NOT_STARTED |
| **Last Updated** | 2025-12-29 |
| **Orchestrator Version** | 1.0.0 |

## Phase Progress

| Phase | Status | Verified | Notes |
|-------|--------|----------|-------|
| 0 | NOT_STARTED | - | |
| 1 | NOT_STARTED | - | |
| 2 | NOT_STARTED | - | |
| 3 | NOT_STARTED | - | |
| 4 | NOT_STARTED | - | |
| 5 | NOT_STARTED | - | |
| 6 | NOT_STARTED | - | |
| 7 | NOT_STARTED | - | |
| 8 | NOT_STARTED | - | |

## Rollback Points

| Phase | Rollback Command |
|-------|------------------|
| 1 | Update .ai-company/ files to previous state |
| 2 | rm backend/api/ai_events.py backend/models/ai_event.py backend/services/ai_dispatcher.py |
| 3 | rm .github/workflows/ai-civilization-*.yml |
| 6 | gh pr close && git branch -D feature/ai-civilization |
| 7 | git revert HEAD && git push |

## Blockers

None.

## Notes

Ready to begin.
```

---

## 🚀 EXECUTION

To run this orchestrator:

```bash
/build-ai-civilization
```

The orchestrator will:
1. Read this command file
2. Check state file for current progress
3. Execute phases in order
4. Verify each phase before proceeding
5. Auto-rollback on failures
6. Checkpoint state after each phase
7. Hand off to Eddie for Phase 8 activation

**Estimated Total Time**: 45-60 minutes (Phases 0-7 autonomous)

**Eddie's Time**: ~15 minutes (Phase 8 configuration)

---

## 📊 SUCCESS CRITERIA

Before declaring the civilization live:

### Operational
- [ ] Events processed within 30 min
- [ ] Critical events trigger immediate response
- [ ] Decision queue functional
- [ ] Morning/evening briefings generated
- [ ] All 5 agents running successfully

### Safety
- [ ] Feature flag works (can disable instantly)
- [ ] Constitutional limits enforced
- [ ] Escalations working
- [ ] No impact on existing Quoted features
- [ ] Full audit trail

### Anthropic Showcase Ready
- [ ] Human-AI collaboration demonstrated
- [ ] Interpretable decisions (all explainable)
- [ ] Honest uncertainty (confidence scores)
- [ ] Constitutional AI in action
- [ ] Recursive self-improvement (Meta Agent)
- [ ] File-based coordination (novel approach)
- [ ] Multi-agent fresh context (solves context limits)

---

**This is revolutionary. This is the future of AI-powered companies. Let's build it. 🚀**
