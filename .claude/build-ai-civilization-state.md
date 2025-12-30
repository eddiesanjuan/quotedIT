# AI Civilization Build State

## Status

| Field | Value |
|-------|-------|
| **Current Phase** | 0 |
| **Phase Status** | READY_TO_RUN |
| **Last Updated** | 2025-12-29 |
| **Orchestrator Version** | 1.0.0 |
| **Orchestrator File** | `.claude/commands/build-ai-civilization.md` |

## Overview

The AI Civilization orchestrator is complete and ready to execute. A fresh Claude context should run `/build-ai-civilization` to begin the autonomous build process.

## What's In The Orchestrator

### Tool Reference (~200 lines)
- All Claude Code built-in tools (Read, Write, Edit, Glob, Grep, Bash, Task, etc.)
- GitHub CLI commands (issues, PRs, workflows, releases)
- Railway CLI commands (logs, variables, deployments)
- Playwright browser automation
- Chrome extension tools
- Gmail integration
- Database access via Railway

### Agent Specifications (5 agents)
1. **Support Agent**: Customer emails, tickets, FAQ, sentiment analysis
2. **Ops Agent**: Log monitoring, health checks, incident response
3. **Code Agent**: Bug fixes, simple features, PR creation (max 5 files)
4. **Growth Agent**: Content, analytics, marketing
5. **Meta Agent**: Weekly self-improvement, evolves other agents

### Constitutional AI
- 6 articles defining immutable limits
- Blast radius limits per agent
- Forbidden actions list
- Escalation requirements
- Human supremacy rules

### GitHub Workflows (9 workflows)
- `ai-civilization-loop.yml` - Main 30-minute loop
- `ai-civilization-support.yml` - Support Agent
- `ai-civilization-ops.yml` - Ops Agent (15-min health checks)
- `ai-civilization-code.yml` - Code Agent
- `ai-civilization-growth.yml` - Growth Agent
- `ai-civilization-meta.yml` - Weekly Meta Agent
- `ai-civilization-urgent.yml` - Critical event handler
- `ai-civilization-morning.yml` - 6 AM briefing
- `ai-civilization-evening.yml` - 6 PM summary

### Backend Code
- `backend/models/ai_event.py` - Event database model
- `backend/api/ai_events.py` - Event gateway router
- `backend/services/ai_dispatcher.py` - GitHub Actions dispatcher

### Phases (0-8)
| Phase | Name | Blast Radius | Auto |
|-------|------|--------------|------|
| 0 | Environment Validation | none | YES |
| 1 | Foundation Files | local | YES |
| 2 | Backend Integration | local | YES |
| 3 | GitHub Workflows | local | YES |
| 4 | Slash Commands | local | YES |
| 5 | Integration Testing | none | YES |
| 6 | Preview Deployment | preview | YES |
| 7 | Production Deployment | production | YES |
| 8 | Activation | handoff | MANUAL |

## Phase Progress

| Phase | Status | Verified | Notes |
|-------|--------|----------|-------|
| 0 | COMPLETE | YES | Environment validated |
| 1 | COMPLETE | YES | 43 files, 6 agents configured |
| 2 | COMPLETE | YES | Backend models, API, dispatcher created |
| 3 | COMPLETE | YES | 9 GitHub workflows created |
| 4 | COMPLETE | YES | 4 slash commands created |
| 5 | COMPLETE | YES | All integration tests pass |
| 6 | IN_PROGRESS | - | Preview deploy |
| 7 | NOT_STARTED | - | Production deploy |
| 8 | NOT_STARTED | - | Eddie activates |

## How to Run

```bash
# In fresh Claude context:
/build-ai-civilization
```

The orchestrator will:
1. Read state file for progress
2. Execute phases in order
3. Verify each phase
4. Auto-rollback on failure
5. Checkpoint after each phase
6. Present Phase 8 checklist to Eddie

## Revolutionary Features

- **Fresh Context Per Agent**: Each GitHub Action = new Claude instance = no context limits
- **File-Based Coordination**: Agents communicate via .ai-company/ files, not shared memory
- **Constitutional Constraints**: Hard limits that even Meta Agent cannot modify
- **Recursive Self-Improvement**: Meta Agent evolves other agents weekly
- **Multi-Agent Architecture**: 5 specialized agents, each optimal for their domain

## Rollback Points

| Phase | Rollback Command |
|-------|------------------|
| 1 | Revert .ai-company/ files |
| 2 | rm backend/api/ai_events.py backend/models/ai_event.py backend/services/ai_dispatcher.py |
| 3 | rm .github/workflows/ai-civilization-*.yml |
| 6 | gh pr close && git branch -D feature/ai-civilization |
| 7 | git revert HEAD && git push |

## Estimated Time

- Phases 0-7 (autonomous): 45-60 minutes
- Phase 8 (Eddie manual): 15 minutes
- Total: ~75 minutes to live AI Civilization

## Blockers

None - ready to execute.
