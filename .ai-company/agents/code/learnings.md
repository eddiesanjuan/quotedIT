# Code Agent Learnings

Knowledge accumulated by the Code Agent about the Quoted codebase.

## Architecture Patterns

### Backend Structure
- FastAPI router pattern in `backend/api/`
- Services in `backend/services/`
- Models in `backend/models/`
- Config in `backend/config.py`

### Key Files
| File | Purpose | Notes |
|------|---------|-------|
| backend/main.py | App entry point | Router registration here |
| backend/api/quotes.py | Quote generation | Core business logic |
| backend/services/claude_service.py | AI integration | Claude API calls |
| backend/services/pdf_service.py | PDF generation | ReportLab |

## Common Patterns

### Adding New API Endpoint
1. Create router in `backend/api/newroute.py`
2. Register in `backend/main.py`
3. Add tests in `backend/tests/test_newroute.py`

### Database Changes
1. Create model in `backend/models/`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Apply: `alembic upgrade head`

## Gotchas

- PDF service uses WeasyPrint - CSS must be inline
- Claude API has rate limits - handle gracefully
- PostHog tracking is essential for new features

## Successful Fixes

| Date | Issue | Fix | Lessons |
|------|-------|-----|---------|
| - | - | - | Agent learning will populate this |

## Failed Attempts

| Date | Issue | Attempt | Why Failed |
|------|-------|---------|------------|
| - | - | - | Agent learning will populate this |
