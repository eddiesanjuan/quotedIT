# Backend Learning

**Last Updated**: 2025-12-02
**Purpose**: Accumulated knowledge about the Quoted backend codebase

---

## Architecture Patterns

### Database
- SQLite with aiosqlite for async operations
- Database file: `./data/quoted.db`
- Connection pooling via SQLAlchemy

### API Structure
- All routes in `backend/api/` directory
- Auth: Session-based with cookies
- Rate limiting: slowapi (5/min on expensive endpoints)
- CORS: Restricted to quoted.it.com in production

### AI Integration
- Claude Sonnet 4 for quote generation (tool calling mode)
- Claude Haiku for category detection (fast, cheap)
- OpenAI Whisper for transcription
- Structured outputs via Pydantic models

---

## Key Learnings

| Date | Learning | Context |
|------|----------|---------|
| 2025-12-01 | Tool calling eliminates JSON parsing failures | Switched from text extraction to structured outputs |
| 2025-12-01 | 3-sample confidence scoring catches hallucinations | Variance > 30% triggers clarifying questions |
| 2025-12-02 | SQLite is sufficient for single-server MVP | No need for PostgreSQL until horizontal scale |
| 2025-12-02 | Rate limiting prevents API cost abuse | 5/min on /api/quotes/generate |

---

## Common Gotchas

1. **Environment variable**: Check `ENVIRONMENT=production` for HTTPS/CORS behavior
2. **Database path**: Relative to working directory (`./data/quoted.db`)
3. **Session secrets**: Must be set in Railway environment
4. **Transcription timeout**: Whisper can be slow on long recordings

---

## Code Patterns to Follow

### Route Structure
```python
@router.post("/endpoint")
async def endpoint_name(
    request: RequestModel,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> ResponseModel:
    """Docstring explaining purpose."""
    # Implementation
    return ResponseModel(...)
```

### Error Handling
```python
from fastapi import HTTPException

if not resource:
    raise HTTPException(status_code=404, detail="Resource not found")
```

---

## Files to Know

| File | Purpose | Complexity |
|------|---------|------------|
| `backend/main.py` | App entry, middleware setup | Medium |
| `backend/services/quote_generator.py` | Core AI logic | High |
| `backend/services/learning.py` | Correction processing | Medium |
| `backend/prompts/quote_generation.py` | Prompt construction | Medium |
| `backend/api/quotes.py` | Quote CRUD endpoints | Medium |

---

## Pending Improvements

- [ ] Add Sentry for error tracking
- [ ] Add unit tests for core flows
- [ ] Add pagination to list endpoints
