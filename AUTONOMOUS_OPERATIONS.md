# Autonomous Operations Guide

**Last Updated**: 2025-12-01 22:50 PST
**Purpose**: Enable Quoted, Inc. (AI Company) to operate autonomously without founder intervention

---

## How This Company Runs

Quoted, Inc. is an AI-native company. When Eddie starts a session, the company activates and can:

1. **Read state files** to understand current status
2. **Process issues** from users via the API
3. **Fix bugs and ship features** within decision authority
4. **Update state files** to maintain continuity
5. **Spawn worker agents** for parallel execution

---

## Session Start Protocol

When a session begins:

1. **CEO Activates First**
   - Read all state files (COMPANY_STATE.md, ENGINEERING_STATE.md, SUPPORT_QUEUE.md, PRODUCT_STATE.md, METRICS_DASHBOARD.md)
   - Check `/api/issues/new` for pending issues
   - Identify highest priority work

2. **Brief Founder** (if present)
   - Current status summary
   - Key decisions needed
   - Recommended focus

3. **Execute Work**
   - Process issues and bugs (Type 1-2)
   - Propose larger changes (Type 3)
   - Request decisions (Type 4)

4. **Update State Files**
   - Document what was done
   - Update metrics
   - Set next priorities

---

## Decision Authority Matrix

| Level | Can Decide Autonomously | Must Ask Eddie |
|-------|------------------------|----------------|
| **Type 1** | Bug fixes, documentation, minor UI tweaks | - |
| **Type 2** | Feature work within roadmap, process improvements | Report after |
| **Type 3** | Architecture changes, new integrations | Propose first |
| **Type 4** | Pricing, external commitments, major pivots | Always ask |

### Examples

**Type 1 (Just Do It)**:
- Fix a CSS bug
- Update documentation
- Add error handling
- Improve prompts

**Type 2 (Do, Then Report)**:
- Implement backlog feature
- Add API endpoint
- Refactor code
- Add monitoring

**Type 3 (Propose, Then Do)**:
- Add new database table
- Integrate third-party service
- Change authentication system
- Major UI redesign

**Type 4 (Founder Decision)**:
- Set pricing tiers
- Sign up for paid services
- Commit to customer timelines
- Change product positioning

---

## Issue Processing Workflow

### How Users Report Issues

1. **In-App**: Report button in UI (TBD)
2. **API**: `POST /api/issues` with issue details
3. **Manual**: Eddie adds to SUPPORT_QUEUE.md

### How Company Processes Issues

```
1. Check for new issues
   GET /api/issues/new

2. Claim an issue (prevents duplicate work)
   POST /api/issues/{id}/claim

3. Analyze the issue
   - Read relevant code
   - Reproduce if possible
   - Determine fix approach

4. Fix and test
   - Make code changes
   - Verify fix works
   - Check for regressions

5. Update issue status
   PATCH /api/issues/{id}
   {
     "status": "resolved",
     "agent_analysis": "Root cause was...",
     "agent_solution": "Fixed by...",
     "files_modified": ["backend/api/quotes.py"]
   }

6. Commit and deploy
   git add . && git commit -m "Fix: ..." && git push
   (Railway auto-deploys on push to main)

7. Update SUPPORT_QUEUE.md
   Move issue from Active to Resolved
```

### Issue Statuses

| Status | Meaning |
|--------|---------|
| `new` | Reported, not yet claimed |
| `queued` | Claimed, waiting to be worked |
| `in_progress` | Actively being fixed |
| `resolved` | Fix deployed |
| `wont_fix` | Decided not to fix (with reason) |

---

## Spawning Worker Agents

For parallel work, spawn specialized agents via the Task tool:

### Backend Engineer
```
subagent_type: "general-purpose"
prompt: |
  You are a Backend Engineer at Quoted. You write Python/FastAPI code.

  Standards:
  - Type hints on all functions
  - Docstrings for public methods
  - Error handling with proper HTTP codes
  - Follow existing patterns in codebase

  Task: [specific implementation task]

  Read relevant files first. Implement. Test. Return summary.
```

### Frontend Engineer
```
subagent_type: "general-purpose"
prompt: |
  You are a Frontend Engineer at Quoted. You write HTML/CSS/JavaScript.

  Standards:
  - Mobile-first responsive design
  - Accessible (WCAG 2.1 AA)
  - Clean, semantic HTML
  - Use existing design patterns

  Task: [specific implementation task]
```

### QA Engineer
```
subagent_type: "general-purpose"
prompt: |
  You are a QA Engineer at Quoted. You break things before users do.

  Approach:
  - Test happy path and edge cases
  - Mobile and desktop
  - Error conditions

  Task: [specific QA task]
```

---

## State File Maintenance

### Update Frequency

| File | Update When |
|------|-------------|
| COMPANY_STATE.md | Strategic changes, weekly at minimum |
| ENGINEERING_STATE.md | Every deployment, every sprint |
| SUPPORT_QUEUE.md | Every ticket change |
| PRODUCT_STATE.md | Feature decisions, roadmap changes |
| METRICS_DASHBOARD.md | Weekly, or when data available |

### State File Rules

1. **Keep under 500 lines** - Archive old content if needed
2. **Use consistent formatting** - Follow existing structure
3. **Include timestamps** - Always update "Last Updated"
4. **Be specific** - "Fixed login bug" not "Made improvements"

---

## Git Workflow

### Commit Convention
```
<type>: <description>

Types:
- Fix: Bug fix
- Add: New feature
- Update: Improvement to existing
- Refactor: Code cleanup
- Docs: Documentation
```

### Deployment
- Push to `main` triggers Railway auto-deploy
- No staging environment (MVP)
- Rollback: Revert commit and push

---

## Monitoring & Alerts

### What to Check
- Railway dashboard for deployment status
- Error logs in Railway
- `/api/issues/new` for user reports

### When to Alert Eddie
- Production is down
- Critical security issue
- Data loss risk
- Type 4 decisions needed

---

## Constraints

### What the Company Cannot Do
- Access external systems without credentials
- Make financial commitments
- Sign contracts
- Push to production without testing
- Compromise on security

### What the Company Must Do
- Maintain accurate state files
- Test before deploying
- Document all changes
- Protect user data
- Escalate blockers

---

## Bootstrapping a Session

When Eddie says "start" or "what's the status":

```
1. Read all 5 state files
2. Check /api/issues/new for pending issues
3. Summarize:
   - Current stage (BETA-READY)
   - Active blockers
   - Pending issues
   - Recommended priorities
4. Ask: "What would you like to focus on?"
```

---

## Common Scenarios

### Scenario: User reports bug
1. Check SUPPORT_QUEUE.md or /api/issues/new
2. Claim issue
3. Reproduce → Diagnose → Fix → Test → Deploy
4. Update issue and SUPPORT_QUEUE.md
5. Brief founder in session summary

### Scenario: Eddie wants new feature
1. Assess scope (Type 1-4)
2. If Type 1-2: Implement directly
3. If Type 3: Propose approach, get approval
4. If Type 4: Document decision needed
5. Update PRODUCT_STATE.md backlog

### Scenario: Production is down
1. Check Railway dashboard
2. Check recent commits
3. Rollback if needed
4. Alert Eddie immediately
5. Document in ENGINEERING_STATE.md incidents

### Scenario: No specific task from Eddie
1. Check for open issues
2. Work on highest-priority backlog item
3. Improve documentation
4. Technical debt cleanup
5. Propose improvements

---

## Contact Points

| Role | When to Engage |
|------|----------------|
| **Eddie (Founder)** | Type 4 decisions, critical issues, strategic direction |
| **CEO (AI)** | Cross-functional coordination, priorities |
| **CTO (AI)** | Technical decisions, architecture |
| **CPO (AI)** | Product decisions, roadmap |
| **Engineering (AI)** | Implementation, bug fixes |
| **Support (AI)** | User issues, documentation |
