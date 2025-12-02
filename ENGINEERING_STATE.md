# Engineering State

**Last Updated**: 2025-12-01 22:35 PST
**Updated By**: CTO (AI)

---

## Current Sprint

**Sprint**: 1 (Beta Launch)
**Goal**: Stable production, DNS configured, first beta users onboarded
**Dates**: 2025-12-01 to 2025-12-08

---

## Deployment Status

| Environment | URL | Status | Version |
|-------------|-----|--------|---------|
| **Production** | https://web-production-0550.up.railway.app | RUNNING | Latest (main) |
| **Target Domain** | https://quoted.it.com | DNS NOT CONFIGURED | - |

**Railway Project**: Connected to main branch, auto-deploys on push

---

## In Progress

| Ticket | Description | Assignee | Status | Blockers |
|--------|-------------|----------|--------|----------|
| - | No active engineering tickets | - | - | - |

---

## Code Review Queue

| PR | Author | Reviewer | Status |
|----|--------|----------|--------|
| - | No open PRs | - | - |

---

## Technical Debt

| Item | Priority | Effort | Notes |
|------|----------|--------|-------|
| Issues API uses in-memory storage | LOW | 2h | Move to SQLite for persistence across restarts |
| CORS allows all origins | LOW | 1h | Restrict to quoted.it.com in production |
| No rate limiting | MEDIUM | 3h | Add before public launch |
| No error tracking (Sentry) | MEDIUM | 2h | Add before scaling |

---

## Recent Deployments

| Date | Commit | Description | Status |
|------|--------|-------------|--------|
| 2025-12-01 | 43af5c6 | Add quote history UI with editable line items | SUCCESS |
| 2025-12-01 | d050eec | Update anthropic SDK for tool calling | SUCCESS |
| 2025-12-01 | 8b91f15 | Add structured outputs, feedback, confidence | SUCCESS |

---

## Architecture Notes

### Stack
- **Backend**: FastAPI + Python 3.11
- **Database**: SQLite (aiosqlite) - single file at `./data/quoted.db`
- **AI**: Claude Sonnet 4 (quotes) + Claude Haiku (category detection)
- **Transcription**: OpenAI Whisper
- **PDF**: ReportLab
- **Hosting**: Railway (web service)

### Key Files
- `backend/main.py` - FastAPI app entry
- `backend/services/quote_generator.py` - Core quote generation
- `backend/services/learning.py` - Correction processing
- `backend/prompts/quote_generation.py` - Prompt construction (learning injection)
- `frontend/index.html` - Main app (31K tokens, vanilla JS)
- `frontend/landing.html` - Landing page

### API Endpoints
```
/api/auth/*           - Authentication
/api/quotes/*         - Quote CRUD, generation, PDF
/api/contractors/*    - Contractor profile
/api/onboarding/*     - Setup interview
/api/issues/*         - Issue reporting (autonomous processing)
```

---

## On-Call

**Primary**: Autonomous AI Engineering
**Escalation**: Eddie (Founder) for Type 3-4 decisions

---

## Incidents

| Date | Severity | Issue | Resolution | Post-mortem |
|------|----------|-------|------------|-------------|
| - | - | No incidents recorded | - | - |

---

## Known Issues

| Issue | Severity | Workaround | Fix ETA |
|-------|----------|------------|---------|
| Issues reset on Railway restart | LOW | None (in-memory storage) | Post-beta |

---

## Environment Variables

Required in Railway:
```
ANTHROPIC_API_KEY     - Claude API key
OPENAI_API_KEY        - Whisper transcription
SESSION_SECRET        - Auth session signing
```

---

## Testing

| Type | Coverage | Status |
|------|----------|--------|
| Unit Tests | 0% | NOT IMPLEMENTED |
| Integration Tests | 0% | NOT IMPLEMENTED |
| Manual Testing | 100% | Ongoing |

**Note**: MVP shipped without automated tests. Add before scaling.
