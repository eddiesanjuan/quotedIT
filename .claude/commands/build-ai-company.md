# Build AI Company - Autonomous Orchestrator

**Version**: 3.0
**Philosophy**: Execute autonomously, verify continuously, gate only at production.

---

## Safety Architecture

This orchestrator executes autonomously with built-in safety:

```
┌─────────────────────────────────────────────────────────────────┐
│ AUTONOMOUS EXECUTION (Phases 0-6)                                │
│ • Self-verifying: Each phase validates its own work             │
│ • Auto-rollback: Failed verification triggers automatic revert  │
│ • Progress streaming: Real-time status without interaction      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ FEATURE FLAG = SAFETY NET                                        │
│ • AI_COMPANY_ENABLED=false by default                           │
│ • Code in production but routes return 404                      │
│ • Instant kill switch if anything goes wrong                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 8 = PHYSICAL HANDOFF (not approval)                        │
│ • Claude can't log into Stripe/Resend/GitHub                    │
│ • Eddie configures external webhooks manually                   │
│ • Eddie enables feature flag when ready                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ CRASH RECOVERY                                                   │
│ • State checkpointed after every step                           │
│ • Resume from exact failure point with --continue               │
│ • Idempotent operations (safe to re-run)                        │
└─────────────────────────────────────────────────────────────────┘
```

**The Deal**: I build and deploy everything autonomously (Phases 0-7). Phase 8 is a handoff - you configure external webhooks and flip the feature flag when ready. If anything breaks, feature flag kills it instantly.

---

## Commands

```bash
# Status & Planning
/build-ai-company --status              # Show current state
/build-ai-company --plan                # Show full plan without executing
/build-ai-company --plan --phase=N      # Show plan for specific phase

# Execution
/build-ai-company                       # Interactive mode (recommended)
/build-ai-company --continue            # Resume from last checkpoint
/build-ai-company --phase=N             # Start/resume specific phase

# Safety Controls
/build-ai-company --dry-run             # Validate everything, create nothing
/build-ai-company --max-blast=local     # Limit to local changes only
/build-ai-company --max-blast=preview   # Allow preview deploys, not production

# Recovery
/build-ai-company --rollback            # Revert last phase
/build-ai-company --rollback --phase=N  # Revert specific phase
/build-ai-company --reset               # Start fresh (with confirmation)
```

---

## Entry Point Logic

```
START
  │
  ├─> Read state file: .claude/build-ai-company-state.md
  │
  ├─> Parse command arguments
  │
  ├─> Is --status?
  │     └─> Display current phase, progress, blockers → EXIT
  │
  ├─> Is --plan?
  │     └─> Generate and display full plan → EXIT
  │
  ├─> Is --rollback?
  │     └─> Execute rollback procedure → EXIT
  │
  ├─> Validate prerequisites:
  │     □ Git working directory clean (or only .ai-company/ changes)?
  │     □ Required tools available (git, python)?
  │     □ No blocking issues in state?
  │
  ├─> Prerequisites failed?
  │     └─> Display issues, suggest fixes → EXIT with error
  │
  ├─> Determine next phase from state
  │
  │   ╔════════════════════════════════════════════════════════════╗
  │   ║  AUTONOMOUS EXECUTION (Phases 0-7)                         ║
  │   ╠════════════════════════════════════════════════════════════╣
  │   ║                                                            ║
  │   ║  WHILE current_phase <= 7:                                 ║
  │   ║    │                                                       ║
  │   ║    ├─> Display: "Phase {N}: {Name}..."                     ║
  │   ║    │                                                       ║
  │   ║    ├─> Execute phase steps                                 ║
  │   ║    │                                                       ║
  │   ║    ├─> Run verification checks                             ║
  │   ║    │                                                       ║
  │   ║    ├─> Verification passed?                                ║
  │   ║    │     ├─> YES: Update state, continue to next phase     ║
  │   ║    │     └─> NO:  Auto-rollback, report failure → EXIT     ║
  │   ║    │                                                       ║
  │   ║    └─> Checkpoint state                                    ║
  │   ║                                                            ║
  │   ║  Phase 7 includes:                                         ║
  │   ║    • Merge to main                                         ║
  │   ║    • Wait for Railway deploy                               ║
  │   ║    • Extensive post-deploy verification                    ║
  │   ║    • Feature flag keeps routes disabled                    ║
  │   ║                                                            ║
  │   ╚════════════════════════════════════════════════════════════╝
  │
  ├─> Phases 0-7 complete (code in production, flag OFF)
  │
  │   ╔════════════════════════════════════════════════════════════╗
  │   ║  HANDOFF (Phase 8) - Not an approval gate                  ║
  │   ╠════════════════════════════════════════════════════════════╣
  │   ║                                                            ║
  │   ║  Claude cannot log into external services.                 ║
  │   ║  Display checklist for Eddie:                              ║
  │   ║    • GitHub secrets                                        ║
  │   ║    • Stripe webhook                                        ║
  │   ║    • Resend webhook                                        ║
  │   ║    • Enable feature flag                                   ║
  │   ║  Enable feature flag and workflow schedules                ║
  │   ║  Run first test cycle                                      ║
  │   ║  Display: "AI Company is LIVE"                             ║
  │   ║                                                            ║
  │   ╚════════════════════════════════════════════════════════════╝
  │
  └─> EXIT (BUILD COMPLETE)
```

---

## Blast Radius Definitions

| Level | Meaning | Examples | Reversibility |
|-------|---------|----------|---------------|
| **none** | No external effect | Reading files, planning | N/A |
| **local** | Files in repo only | Creating .ai-company/, configs | Delete files |
| **preview** | Railway preview deploy | Preview URL testing | Delete preview |
| **production** | Live site changes | Main deploy, webhook config | Feature flags, rollback |

---

## Phase Structure (Template)

Every phase follows this structure:

```markdown
## Phase N: [Name]

### Blast Radius: [none | local | preview | production]

### Prerequisites
- [ ] Phase N-1 complete
- [ ] [Specific requirements]

### Plan
[Detailed description of what this phase will do]

### Files Created/Modified
| File | Action | Purpose |
|------|--------|---------|
| path/to/file | CREATE | Why |
| path/to/file | MODIFY | What changes |

### Execution Steps
1. [Step 1]
2. [Step 2]
...

### Verification
- [ ] Automated: [Test 1]
- [ ] Automated: [Test 2]
- [ ] Manual: [Review point if needed]

### Rollback Procedure
[How to undo this phase completely]

### Human Gate
[YES/NO - Does this phase require explicit human approval before next?]
```

---

## PHASE 0: Validate & Prepare [AUTONOMOUS]

### Blast Radius: none

### Purpose
Validate the environment and prepare for the build. Creates nothing, modifies nothing.

### Execution Steps

1. **Validate Git State**
   ```bash
   git status --porcelain
   # Must be empty or only .ai-company/ files
   ```
   - If dirty with other files: FAIL with message

2. **Check for Existing AI Company Files**
   ```bash
   ls -la .ai-company/ 2>/dev/null
   ```
   - If exists: Note "Existing files found, will validate/update in Phase 1"
   - If not exists: Note "Clean slate, will create in Phase 1"

3. **Verify Required Tools**
   - Git available: `git --version`
   - Python available: `python --version`
   - Network connectivity: Can reach github.com

4. **Display Build Plan**
   ```
   ╔══════════════════════════════════════════════════════════════╗
   ║          AI COMPANY BUILD - AUTONOMOUS MODE                   ║
   ╠══════════════════════════════════════════════════════════════╣
   ║                                                               ║
   ║  Phases 0-6: Autonomous (I build, I verify)                  ║
   ║  Phase 7:    Production Gate (you approve once)              ║
   ║  Phase 8:    Handoff (you configure webhooks, I finish)      ║
   ║                                                               ║
   ║  Starting autonomous execution...                            ║
   ╚══════════════════════════════════════════════════════════════╝
   ```

### Verification
- [ ] Git status clean (or only .ai-company/)
- [ ] Required tools available
- [ ] Network connectivity confirmed

### On Failure
Report what's wrong, suggest fix, EXIT.

### On Success
Proceed immediately to Phase 1.

---

## PHASE 1: Foundation [AUTONOMOUS]

### Blast Radius: local

### Purpose
Create the complete .ai-company/ directory structure and all foundational files.

### Prerequisites
- [ ] Phase 0 complete

### Files Created

```
.ai-company/                              # 28 files total
├── CONSTITUTION.md                       # AI governance rules
├── README.md                             # System documentation
├── state/
│   ├── current.md                        # Operational state
│   └── metrics.md                        # Business metrics
├── queues/
│   ├── events.md                         # Incoming events
│   ├── decisions.md                      # Awaiting human input
│   ├── actions.md                        # Ready to execute
│   └── completed.md                      # Archive
├── agents/
│   ├── support/
│   │   ├── AGENT.md                      # Agent specification
│   │   ├── state.md                      # Agent state
│   │   ├── inbox.md                      # Items to process
│   │   └── drafts.md                     # Response drafts
│   ├── ops/
│   │   ├── AGENT.md
│   │   ├── state.md
│   │   ├── alerts.md
│   │   └── fixes.md
│   ├── growth/
│   │   ├── AGENT.md
│   │   ├── state.md
│   │   └── content-queue.md
│   └── finance/
│       ├── AGENT.md
│       ├── state.md
│       └── reports.md
├── knowledge/
│   ├── product/
│   │   ├── PRODUCT_OVERVIEW.md
│   │   └── FAQ.md
│   ├── playbooks/
│   │   ├── support-playbook.md
│   │   ├── incident-playbook.md
│   │   ├── growth-playbook.md
│   │   └── finance-playbook.md
│   ├── voice/
│   │   └── BRAND_VOICE.md
│   └── customers/
│       └── CUSTOMER_TEMPLATE.md
├── config/
│   ├── settings.md
│   ├── escalation.md
│   ├── schedules.md
│   └── integrations.md
└── logs/
    ├── execution/                        # Daily execution logs
    ├── decisions/                        # Human decision logs
    └── audit/                            # Full audit trail
```

### Execution Steps

1. **Create Directory Structure**
   ```bash
   mkdir -p .ai-company/{state,queues,logs/{execution,decisions,audit},config}
   mkdir -p .ai-company/agents/{support,ops,growth,finance}
   mkdir -p .ai-company/knowledge/{product,playbooks,voice,customers}
   ```

2. **Create Each File**
   - For each file: Check if exists
   - If exists and matches expected content: Skip with note
   - If exists but differs: Ask user (overwrite/skip/view diff)
   - If not exists: Create with verified content

3. **Validate All Files Created**
   ```bash
   # Count files
   find .ai-company -type f | wc -l
   # Should be 28
   ```

### Verification
- [ ] Directory structure exists: `ls -la .ai-company/`
- [ ] File count correct: 28 files
- [ ] CONSTITUTION.md valid: Contains "Article I"
- [ ] All agent specs exist: 4 AGENT.md files
- [ ] All playbooks exist: 4 playbook files
- [ ] Config files exist: 4 config files

### On Failure
```bash
rm -rf .ai-company/
```
Report failure, EXIT.

### On Success
Display: "✓ Phase 1: 28 files created" → Proceed to Phase 2.

---

## PHASE 2: Event Gateway (Backend) [AUTONOMOUS]

### Blast Radius: local

### Purpose
Add the webhook receiver API to the backend. This receives events from Stripe, Resend, etc.

### Prerequisites
- [ ] Phase 1 complete

### Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| backend/api/ai_events.py | CREATE | Event gateway API routes |
| backend/models/ai_event.py | CREATE | Event database model |
| backend/main.py | MODIFY | Register new router |

### Safety Notes

- **New files only**: `ai_events.py` is new, doesn't touch existing routes
- **Feature flag wrapped**: All routes check `AI_COMPANY_ENABLED` env var (default: false)
- **Separate table**: Uses new table `ai_company_events`, doesn't modify existing schema

### Execution Steps

1. **Create Event Model**
   - New file: backend/models/ai_event.py
   - Define AIEvent model with fields:
     - id, source, event_type, urgency, payload, headers
     - received_at, processed, processed_at, processing_result

2. **Create Event Gateway API**
   - New file: backend/api/ai_events.py
   - Routes (all behind feature flag):
     - POST /api/ai-company/webhook/{source}
     - GET /api/ai-company/events/pending
     - POST /api/ai-company/events/mark-processed
   - Feature flag check at router level

3. **Register Router in main.py**
   - Add import
   - Add router inclusion (conditional on feature flag)

4. **Create Database Migration**
   - Generate Alembic migration for new table
   - Migration is additive-only (new table, no modifications)

### Verification
- [ ] Syntax valid: `python -m py_compile backend/api/ai_events.py`
- [ ] Model syntax valid: `python -m py_compile backend/models/ai_event.py`
- [ ] Main.py still loads: `python -c "from backend.main import app"`
- [ ] Routes registered (when flag enabled)
- [ ] Feature flag works (routes return 404 when disabled)

### On Failure
```bash
rm backend/api/ai_events.py backend/models/ai_event.py
git checkout backend/main.py
```
Report failure, EXIT.

### On Success
Display: "✓ Phase 2: Backend event gateway created" → Proceed to Phase 3.

---

## PHASE 3: GitHub Workflows [AUTONOMOUS]

### Blast Radius: local

### Purpose
Create GitHub Actions workflow files. Schedules disabled until Phase 8.

### Prerequisites
- [ ] Phase 2 complete

### Files Created

| File | Purpose |
|------|---------|
| .github/workflows/ai-company-loop.yml | Main processing loop (every 30 min) |
| .github/workflows/ai-company-morning.yml | Morning briefing (6 AM) |
| .github/workflows/ai-company-evening.yml | Evening summary (6 PM) |
| .github/workflows/ai-company-weekly.yml | Weekly review (Sunday 6 PM) |
| .github/workflows/ai-company-urgent.yml | Critical event handler |

### Safety: Workflows Disabled

All workflows are created with `workflow_dispatch` only trigger initially.
Scheduled triggers (`cron`) are commented out.
This means workflows exist but won't run until manually enabled.

```yaml
# Initial state - disabled
on:
  workflow_dispatch:  # Manual trigger only
  # schedule:         # DISABLED until Phase 8
  #   - cron: '0,30 * * * *'
```

### Execution Steps

1. **Create Each Workflow File**
   - ai-company-loop.yml (main loop)
   - ai-company-morning.yml (morning briefing)
   - ai-company-evening.yml (evening summary)
   - ai-company-weekly.yml (weekly review)
   - ai-company-urgent.yml (urgent handler)

2. **Verify YAML Syntax**
   ```bash
   # Validate each workflow
   for f in .github/workflows/ai-company-*.yml; do
     python -c "import yaml; yaml.safe_load(open('$f'))"
   done
   ```

### Verification
- [ ] 5 workflow files created
- [ ] All YAML syntax valid
- [ ] All workflows have `workflow_dispatch` trigger
- [ ] All scheduled triggers are commented out
- [ ] No workflows will auto-run

### On Failure
```bash
rm .github/workflows/ai-company-*.yml
```
Report failure, EXIT.

### On Success
Display: "✓ Phase 3: 5 workflow files created (schedules disabled)" → Proceed to Phase 4.

---

## PHASE 4: Slash Commands [AUTONOMOUS]

### Blast Radius: local

### Purpose
Create the Claude Code slash commands that operate the AI Company.

### Prerequisites
- [ ] Phase 3 complete

### Files Created

| File | Purpose |
|------|---------|
| .claude/commands/ai-company.md | Main runtime command |
| .claude/commands/ai-company-decide.md | Decision queue interface |
| .claude/commands/ai-company-status.md | Status display |

### Execution Steps

1. **Create Main Command**
   - .claude/commands/ai-company.md
   - Handles: /ai-company, /ai-company run, /ai-company briefing

2. **Create Decision Command**
   - .claude/commands/ai-company-decide.md
   - Interactive decision queue processor

3. **Create Status Command**
   - .claude/commands/ai-company-status.md
   - Displays current system state

### Verification
- [ ] 3 command files created
- [ ] Commands are valid markdown
- [ ] No syntax errors in command definitions

### On Failure
```bash
rm .claude/commands/ai-company*.md
```
Report failure, EXIT.

### On Success
Display: "✓ Phase 4: 3 slash commands created" → Proceed to Phase 5.

---

## PHASE 5: Integration Testing [AUTONOMOUS]

### Blast Radius: none

### Purpose
Verify all components work together before deployment.

### Prerequisites
- [ ] Phases 1-4 complete

### Tests

1. **Foundation Tests**
   - [ ] All 28 .ai-company/ files exist
   - [ ] CONSTITUTION.md is valid
   - [ ] All agent specs are complete
   - [ ] Config files have required fields

2. **Backend Tests**
   - [ ] Python syntax valid for all new files
   - [ ] App loads without errors
   - [ ] Routes registered correctly
   - [ ] Feature flag blocks routes when disabled

3. **Workflow Tests**
   - [ ] All 5 workflow files exist
   - [ ] YAML syntax valid
   - [ ] Required env vars documented
   - [ ] Scheduled triggers disabled

4. **Command Tests**
   - [ ] All 3 command files exist
   - [ ] Commands reference correct files
   - [ ] No broken file paths

5. **Integration Tests**
   - [ ] State file format correct
   - [ ] Queue file format correct
   - [ ] Agent specs reference correct playbooks

### Execution

```
╔══════════════════════════════════════════════════════════════╗
║              PHASE 5: INTEGRATION TESTING                     ║
╠══════════════════════════════════════════════════════════════╣

Running tests...

Foundation Tests:
  ✓ Directory structure complete (28/28 files)
  ✓ CONSTITUTION.md valid
  ✓ Agent specifications complete
  ✓ Config files valid

Backend Tests:
  ✓ Python syntax valid
  ✓ App loads successfully
  ✓ Routes registered (3 routes)
  ✓ Feature flag working

Workflow Tests:
  ✓ All workflows exist (5/5)
  ✓ YAML syntax valid
  ✓ Scheduled triggers disabled

Command Tests:
  ✓ Commands exist (3/3)
  ✓ No broken references

Integration Tests:
  ✓ State format valid
  ✓ Queue format valid
  ✓ Cross-references valid

═══════════════════════════════════════════════════════════════
  ALL TESTS PASSED: 15/15
═══════════════════════════════════════════════════════════════
╚══════════════════════════════════════════════════════════════╝
```

### On Failure
Any test fails → Report which tests failed, EXIT.

### On Success
Display: "✓ Phase 5: All 15 tests passed" → Proceed to Phase 6.

---

## PHASE 6: Preview Deployment [AUTONOMOUS]

### Blast Radius: preview

### Purpose
Deploy to Railway preview environment for testing before production.

### Prerequisites
- [ ] Phase 5 tests passed

### Execution Steps

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/ai-company-v1
   git add .ai-company/ backend/api/ai_events.py backend/models/ai_event.py
   git add .github/workflows/ai-company-*.yml
   git add .claude/commands/ai-company*.md
   git commit -m "feat: AI Company infrastructure (Phase 1-4)"
   git push origin feature/ai-company-v1
   ```

2. **Create Pull Request**
   ```bash
   gh pr create --title "feat: AI Company infrastructure" \
     --body "Adds AI Company autonomous operations system..."
   ```

3. **Railway Auto-Deploys Preview**
   - Wait for preview URL
   - Should be: feature-ai-company-v1.quoted.it.com or similar

4. **Test Preview Environment**
   - [ ] App loads normally
   - [ ] Existing features work (quote generation, etc.)
   - [ ] New routes exist but return 404 (feature flag off)
   - [ ] No console errors

5. **Enable Feature Flag in Preview**
   - Set AI_COMPANY_ENABLED=true in preview env
   - Test new routes respond

6. **Test Event Gateway**
   ```bash
   # Test webhook endpoint
   curl -X POST https://preview-url/api/ai-company/webhook/test \
     -H "Content-Type: application/json" \
     -d '{"test": true}'

   # Should return: {"status": "received", "event_id": "...", "urgency": "normal"}
   ```

### Verification
- [ ] PR created and preview deployed
- [ ] App loads in preview
- [ ] Existing features work
- [ ] New routes work when flag enabled
- [ ] No regressions detected

### On Failure
```bash
gh pr close feature/ai-company-v1
git branch -D feature/ai-company-v1
git push origin --delete feature/ai-company-v1
```
Report what failed, EXIT.

### On Success
Display: "✓ Phase 6: Preview deployed and verified" → Proceed to Phase 7.

---

## PHASE 7: Production Deployment [AUTONOMOUS]

### Blast Radius: production

### Purpose
Merge to main, deploy to production, and verify everything works. Feature flag keeps new routes disabled - this is dormant code until Phase 8 activation.

### Why This Is Safe to Auto-Deploy

The feature flag `AI_COMPANY_ENABLED=false` means:
- New routes return 404 (not exposed)
- No new functionality active
- Existing Quoted features unaffected
- Essentially deploying dormant code

The real "go live" is Phase 8 when Eddie enables the flag.

### Execution Steps

1. **Merge to Main**
   ```bash
   gh pr merge --squash -m "feat: AI Company infrastructure (flag disabled)"
   ```

2. **Wait for Production Deploy**
   - Railway auto-deploys on merge
   - Wait for deploy to complete (~2-3 minutes)
   - Monitor Railway logs for errors

3. **Run Database Migration**
   ```bash
   railway run alembic upgrade head
   ```

4. **Verify Migration**
   - Table ai_company_events exists
   - No migration errors

### Post-Deploy Verification (Extensive)

**Core Quoted Functionality** (must all pass):
```bash
# Landing page loads
curl -s -o /dev/null -w "%{http_code}" https://quoted.it.com
# Expected: 200

# API health
curl -s https://quoted.it.com/api/health
# Expected: {"status": "healthy"}

# Auth endpoints respond
curl -s -o /dev/null -w "%{http_code}" https://quoted.it.com/api/auth/check
# Expected: 401 (unauthorized, but endpoint works)

# Quote generation endpoint exists
curl -s -o /dev/null -w "%{http_code}" -X POST https://quoted.it.com/api/quotes/generate
# Expected: 401 or 422 (auth required or validation error, but endpoint works)
```

**AI Company Routes Disabled** (must all return 404):
```bash
# Event gateway blocked
curl -s -o /dev/null -w "%{http_code}" https://quoted.it.com/api/ai-company/events/pending
# Expected: 404

# Webhook endpoints blocked
curl -s -o /dev/null -w "%{http_code}" -X POST https://quoted.it.com/api/ai-company/webhook/stripe
# Expected: 404

curl -s -o /dev/null -w "%{http_code}" -X POST https://quoted.it.com/api/ai-company/webhook/resend
# Expected: 404
```

**No Regressions** (spot check key flows):
- [ ] Demo page generates quotes
- [ ] Login flow works
- [ ] Dashboard loads for logged-in users
- [ ] No new errors in Railway logs (last 5 minutes)

### On Failure

Any verification fails → Report which check failed, do NOT proceed to Phase 8.

If core Quoted functionality broken:
```bash
# Immediate rollback
git revert HEAD
git push origin main
```

### On Success

Display summary:
```
✓ Phase 7: Production deployed successfully

Verified:
  ✓ Core Quoted: Landing, API, Auth, Quotes - all working
  ✓ AI Company routes: Correctly returning 404 (flag disabled)
  ✓ Database: Migration applied, tables exist
  ✓ No regressions detected

The AI Company code is now in production but dormant.
Proceed to Phase 8 for activation handoff.
```

→ Proceed to Phase 8.

### On Failure
```bash
# Feature flag already off, no user impact
# If migration failed:
railway run alembic downgrade -1
# If severe:
git revert HEAD && git push origin main
```
Report failure, EXIT.

### On Success
Display: "✓ Phase 7: Production deployed (feature flag OFF)" → Proceed to Phase 8.

---

## PHASE 8: Activation [HANDOFF]

### Why This Is a Handoff (Not an Approval)

Claude can't log into Stripe, Resend, or GitHub settings pages. This isn't asking permission - it's providing the checklist for things only Eddie can configure in external dashboards.

---

### 🎯 YOUR ACTIVATION CHECKLIST

**Time Required**: ~10 minutes

#### 1. GitHub Secrets (github.com → Settings → Secrets)

Add these repository secrets:
```
ANTHROPIC_API_KEY      = [your key]
RESEND_API_KEY         = [your key]
STRIPE_SECRET_KEY      = [read-only key]
POSTHOG_API_KEY        = [your key]
```

#### 2. Stripe Webhook (stripe.com/dashboard → Webhooks)

```
Endpoint:  https://quoted.it.com/api/ai-company/webhook/stripe
Events:    customer.*, invoice.*, charge.*, subscription.*
```

#### 3. Resend Webhook (resend.com → Webhooks)

```
Endpoint:  https://quoted.it.com/api/ai-company/webhook/resend
Events:    email.*
```

#### 4. Enable Feature Flag (Railway dashboard or CLI)

```bash
railway variables set AI_COMPANY_ENABLED=true
```

#### 5. Test It

```bash
# Verify routes work
curl https://quoted.it.com/api/ai-company/events/pending

# Trigger first run
gh workflow run ai-company-loop.yml
gh run watch
```

---

### What Happens Next

Once you complete the checklist above:
- Workflows run every 30 minutes (6 AM - 10 PM)
- Morning briefing at 6:00 AM
- Evening summary at 6:00 PM
- Critical events trigger SMS alerts

**The AI Company is live. 🚀**

### Rollback Procedure

**Immediate shutdown:**
```bash
# Disable feature flag
railway variables set AI_COMPANY_ENABLED=false

# Disable workflows (comment out schedules)
# Commit and push
```

### Human Gate: N/A (End of build)

```
╔══════════════════════════════════════════════════════════════╗
║             🎉 AI COMPANY BUILD COMPLETE 🎉                   ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  The AI Company is now LIVE and processing.                  ║
║                                                               ║
║  What's Running:                                              ║
║  • Event Gateway receiving webhooks                          ║
║  • Main loop every 30 minutes                                ║
║  • Morning briefing at 6 AM                                  ║
║  • Evening summary at 6 PM                                   ║
║  • Weekly review on Sundays                                  ║
║                                                               ║
║  Your Daily Routine:                                          ║
║  • Morning: Run /ai-company decide (5-10 min)                ║
║  • Check /ai-company status anytime                          ║
║  • SMS alerts for critical events                            ║
║                                                               ║
║  Monitor First 24 Hours:                                      ║
║  • Watch GitHub Actions for successful runs                  ║
║  • Check .ai-company/logs/execution/ for activity            ║
║  • Verify events being processed                             ║
║                                                               ║
║  Emergency Shutdown:                                          ║
║  railway variables set AI_COMPANY_ENABLED=false              ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## State File Format

The orchestrator tracks progress in `.claude/build-ai-company-state.md`:

```markdown
# Build AI Company - Orchestration State

## Current Status

| Field | Value |
|-------|-------|
| **Current Phase** | 3 |
| **Phase Status** | IN_PROGRESS |
| **Last Checkpoint** | Phase 3, Step 2 |
| **Last Updated** | 2025-12-29T15:30:00Z |
| **Blast Radius Used** | local |

## Phase Progress

| Phase | Status | Verified | Notes |
|-------|--------|----------|-------|
| 0 | COMPLETE | ✓ | User confirmed |
| 1 | COMPLETE | ✓ | 28 files created |
| 2 | COMPLETE | ✓ | Backend routes added |
| 3 | IN_PROGRESS | - | Step 2 of 5 |
| 4 | NOT_STARTED | - | |
| 5 | NOT_STARTED | - | |
| 6 | NOT_STARTED | - | |
| 7 | NOT_STARTED | - | |
| 8 | NOT_STARTED | - | |

## Checkpoint Details

### Phase 3 Checkpoint
- Step completed: 2 (created ai-company-morning.yml)
- Next step: 3 (create ai-company-evening.yml)
- Files created this phase: 2

## Rollback Points

| Phase | Rollback Command |
|-------|------------------|
| 1 | rm -rf .ai-company/ |
| 2 | git checkout backend/main.py && rm backend/api/ai_events.py backend/models/ai_event.py |
| 3 | rm .github/workflows/ai-company-*.yml |

## Blockers

None

## Notes

- Phase 2 required user approval for backend changes
- All tests passing as of Phase 3
```

---

## Crash Recovery

If the orchestrator crashes or context is lost:

1. **Read State File**
   ```bash
   cat .claude/build-ai-company-state.md
   ```

2. **Resume from Checkpoint**
   ```bash
   /build-ai-company --continue
   ```

3. **The orchestrator will:**
   - Read current phase and step
   - Verify completed work still valid
   - Continue from exact checkpoint
   - Not duplicate completed work

4. **If state is corrupted:**
   ```bash
   /build-ai-company --status
   # Shows actual file state vs recorded state
   # Offers to reconcile
   ```

---

## Edge Case Handling

### Atomic State Updates

State file updates follow write-verify pattern:
```
1. Write state to .claude/build-ai-company-state.md.tmp
2. Verify tmp file is valid markdown
3. Atomically move: mv state.md.tmp state.md
4. Never leave partial writes
```

### Step-Level Recovery

Each phase tracks completed steps in state file:
```markdown
### Phase 3 Checkpoint
- Steps completed: [1, 2]
- Next step: 3
- Artifacts created: ["ai-company-loop.yml", "ai-company-morning.yml"]
```

On crash, resume from next incomplete step, not phase start.

### Deployment Timeouts

```yaml
deploy_timeouts:
  railway_preview: 300  # 5 min
  railway_production: 300  # 5 min
  workflow_run: 600  # 10 min

on_timeout:
  - Log timeout in state
  - Ask user: retry, skip, or abort
  - Never assume success without verification
```

### Idempotency Guarantee

Every operation checks before executing:
```
Before creating file:
  - Does file exist?
  - Does content match expected?
  - If yes to both: skip with note
  - If exists but differs: ask user

Before running command:
  - Check if effect already achieved
  - E.g., migration: check if table exists
  - Feature flag: check current value first
```

---

## Success Criteria

Before declaring the build complete:

### Operational
- [ ] Events processed within 30 min
- [ ] Critical events trigger immediate response
- [ ] Decision queue functional
- [ ] Morning/evening briefings generated

### Safety
- [ ] Feature flag works (can disable instantly)
- [ ] No impact on existing features
- [ ] All changes auditable in git
- [ ] Rollback procedures tested

### Quality
- [ ] All verification tests pass
- [ ] No console errors
- [ ] No unexpected behavior
- [ ] Documentation complete

### Anthropic Showcase Ready
- [ ] Constitutional AI framework in place
- [ ] Human-in-loop working
- [ ] Full audit trail
- [ ] Explainable decisions
