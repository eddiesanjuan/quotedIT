# Quoted Company State

**Last Updated**: 2025-12-01 22:30 PST
**Updated By**: CEO (AI Company Bootstrap)

---

## Current Stage

**BETA-READY**

Product is fully functional and deployed. All Phase 1 enhancements complete. Awaiting first beta users.

**Live URL**: https://web-production-0550.up.railway.app/app
**Target URL**: https://quoted.it.com (DNS configuration pending)

---

## Product Status

### Core Capabilities (All Operational)

| Feature | Status | Notes |
|---------|--------|-------|
| Voice-to-Quote Pipeline | **LIVE** | Audio → Whisper → Claude → Quote |
| Structured Outputs | **LIVE** | Tool calling + Pydantic validation |
| Confidence Sampling | **LIVE** | 3-sample variance estimation |
| Active Learning Questions | **LIVE** | Clarifying questions for low-confidence |
| Feedback System | **LIVE** | Non-destructive quote feedback API |
| Learning System | **LIVE** | Per-category weighted corrections |
| PDF Generation | **LIVE** | Professional quote PDFs |
| Onboarding Interview | **LIVE** | Adaptive pricing model setup |
| Landing Page | **LIVE** | Premium dark design, industry spinner |
| Issue Tracking API | **LIVE** | /api/issues for autonomous processing |

### Technical Architecture

- **Backend**: FastAPI + SQLite (aiosqlite)
- **AI**: Claude Sonnet 4 (quote generation) + Claude Haiku (category detection)
- **Transcription**: OpenAI Whisper
- **Deployment**: Railway (web + worker)
- **Auth**: Session-based (cookie)

---

## Active Initiatives

| Initiative | Status | Owner | Next Action |
|------------|--------|-------|-------------|
| DNS Configuration | **BLOCKED** | CTO | Needs Eddie to configure DNS records |
| Beta User Recruitment | **NOT STARTED** | CGO | Identify and recruit 10-20 contractors |
| Pricing Strategy | **NOT STARTED** | CFO | Define tiers before monetization |
| Vector Embeddings (RAG) | **BACKLOG** | Engineering | Not MVP-critical, defer to post-beta |
| Multi-Agent Quotes | **BACKLOG** | Engineering | Complex quote accuracy improvement |

---

## Key Metrics

| Metric | Current | Target (Beta) | Target (Launch) |
|--------|---------|---------------|-----------------|
| Users | 0 | 10-20 beta | 100 |
| Quotes Generated | 0 | 50 | 500 |
| Activation Rate | - | 60% | 70% |
| Quote Edit Rate | - | <30% | <20% |
| NPS | - | 40+ | 50+ |

---

## This Week's Priorities

1. **Configure DNS** - Point quoted.it.com to Railway (BLOCKED on Eddie)
2. **Recruit Beta Users** - Find 10 contractors to try the product
3. **Monitor First Usage** - Track issues, fix bugs as they arise
4. **Collect Feedback** - Learn what real contractors need

---

## Blockers & Decisions Needed

| Blocker | What's Needed | Owner | Status |
|---------|---------------|-------|--------|
| DNS Configuration | Eddie to add CNAME/A record in domain registrar | Founder | WAITING |
| Issue Persistence | In-memory storage resets on restart - needs DB migration | CTO | LOW PRIORITY |

---

## Resources & Assets

**Domain**: quoted.it.com (registered, not configured)
**Codebase**: Complete MVP with Phase 1 enhancements
**Deployment**: Railway (running)
**Brand**: Dark premium aesthetic, "quoted.it" with industry spinner

---

## Learnings & Insights

| Date | Learning | Source |
|------|----------|--------|
| 2025-12-01 | Structured outputs eliminate JSON parsing failures | Engineering |
| 2025-12-01 | Confidence sampling provides reliable uncertainty estimates | Engineering |
| 2025-12-01 | Landing page positions as "ballpark quotes, not blueprints" | Marketing |
| 2025-12-01 | Voice-first + learning = unique market position | Product |

---

## Strategic Context

**Why We Win**:
1. Voice-first matches how contractors actually work (in the field)
2. Learning system creates accuracy moat over time
3. Speed: 30-second quotes vs 30-minute spreadsheets
4. "Instant voice quote from job site" - unclaimed category

**Risks**:
1. Buildxact could add voice interface
2. Quote accuracy must be high (>85%) or trust breaks
3. Contractors may resist new tools
4. Need enough corrections to make learning meaningful

**Assumptions to Validate in Beta**:
1. Contractors will use voice input (vs typing)
2. Learning system creates measurable accuracy improvement
3. Onboarding captures enough pricing knowledge
4. Word-of-mouth drives growth in contractor communities

---

## Founder Notes

*Space for Eddie's input, direction, or context*

---

## Session Log

| Date | Duration | Focus | Outcomes |
|------|----------|-------|----------|
| 2025-12-01 | Initial | Bootstrap | Created initial state, identified Phase 1 priorities |
| 2025-12-01 | 2 hours | Audit | Full product audit, state file update, ops infrastructure |

---

## Operational Infrastructure

### State Files
- `COMPANY_STATE.md` - This file (strategic state)
- `ENGINEERING_STATE.md` - Sprints, tech debt, deployments
- `SUPPORT_QUEUE.md` - User issues and tickets
- `PRODUCT_STATE.md` - Roadmap and backlog
- `METRICS_DASHBOARD.md` - KPI tracking

### Autonomous Operations
The company can process issues via `/api/issues` endpoint:
1. Users report issues in-app
2. Issues appear in SUPPORT_QUEUE.md
3. Engineering claims and resolves
4. Updates pushed to production

**Type 1 Decisions** (Just Do): Bug fixes, docs, minor improvements
**Type 2 Decisions** (Do Then Report): Feature work within roadmap
**Type 3 Decisions** (Propose Then Do): Architecture changes, new integrations
**Type 4 Decisions** (Founder Required): Pricing, external commitments, major pivots
