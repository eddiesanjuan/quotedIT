# Phase 1: Technical Audit Findings (GPT-5.2-Codex)

**Date**: 2025-12-25  
**Scope**: backend, database layer, deployment/infra behaviors, frontend resilience, and core user journeys  
**Note**: Findings below are *re-validated against the current repo state* (some prior AI outputs contained false positives).

---

## Severity rubric (used here)

- **CRITICAL (P0)**: Actively exploitable, data-loss risk, or production-breaking; fix before scaling traffic.
- **HIGH (P1)**: Exploitable or high-impact reliability issue; fix within 1–2 weeks.
- **MEDIUM (P2)**: Important hardening/polish; fix within 1–2 months.
- **LOW (P3)**: Backlog / nice-to-have.

---

## CRITICAL (P0) — Fix before scaling users

### P0-01: App import/start fails on SQLite due to invalid engine args (blocks local dev + tests)
- **Evidence**:
  - `backend/services/database.py:27` creates an engine with `pool_size`, `max_overflow`, `pool_timeout` which are invalid for `sqlite+aiosqlite`.
  - Importing the app currently crashes: `./venv/bin/python -c "import backend.main"` → `TypeError: Invalid argument(s) 'pool_size','max_overflow','pool_timeout' ... SQLiteDialect_aiosqlite/NullPool/Engine`.
- **Why this matters**:
  - Breaks local development, CI, and any environment using SQLite (or any “quick start” default).
  - Prevents importing `backend.main`, which blocks tooling (tests, scripts, docs generation) that rely on importability.
- **Fix direction**:
  - Configure engine kwargs conditionally by dialect (SQLite vs Postgres), or move engine creation into a function that applies safe defaults per DB.
  - Avoid creating engines at import-time; lazy-init after config load.

### P0-02: In-process scheduler runs once per Uvicorn worker (duplicate emails/tasks, racey side effects)
- **Evidence**:
  - `Procfile:1` runs `uvicorn ... --workers 4`
  - `backend/main.py:109` starts scheduler in lifespan for every worker process
  - Scheduler creates tasks and sends reminder emails: `backend/services/scheduler.py:213` onward
- **Impact**:
  - Multiple workers ⇒ multiple schedulers ⇒ duplicate reminders and follow-up tasks.
  - Any “send email then mark as sent” flow will spam when multiple workers query the same “pending” rows concurrently.
- **Fix direction**:
  - Move scheduler to a single dedicated process (separate worker dyno) or implement leader election / distributed locking.
  - Make job handlers idempotent (DB-level “claim” updates, unique constraints, transactional guards).

### P0-03: Public/demo contractor endpoints ship in production router (data exposure + behavior conflicts)
- **Evidence**:
  - Unauthenticated endpoints backed by in-memory dicts:
    - `backend/api/contractors.py:183` (`POST /api/contractors/`) creates contractors without auth (in memory)
    - `backend/api/contractors.py:219` (`GET /api/contractors/{contractor_id}`) exposes contractor data without auth (in memory)
    - `backend/api/contractors.py:405` (`GET /api/contractors/{contractor_id}/accuracy`) is unauthenticated
    - `backend/api/contractors.py:467` (`GET /api/contractors/`) lists all demo contractors unauthenticated
- **Why this matters**:
  - “Demo scaffolding” endpoints are reachable because `backend/main.py` includes the contractors router in production.
  - They also create routing-footguns: the generic `/{contractor_id}` route can shadow future static GET routes (e.g., `/logo`) depending on router matching order.
- **Fix direction**:
  - Remove demo endpoints from production builds, or gate them behind an admin auth / environment flag.
  - Ensure static routes (e.g., `/logo`) are not shadowed by parameterized routes.

### P0-04: Onboarding session read/continue endpoints are unauthenticated and unthrottled (privacy + cost abuse)
- **Evidence**:
  - `backend/api/onboarding.py:161` (`POST /api/onboarding/{session_id}/continue`) has no auth dependency
  - `backend/api/onboarding.py:549` (`GET /api/onboarding/{session_id}`) has no auth dependency
  - `backend/api/onboarding.py:561` (`GET /api/onboarding/{session_id}/messages`) has no auth dependency
- **Impact**:
  - If a session_id leaks (logs, referer, screenshots, support tickets), an attacker can read the full onboarding conversation (often contains business pricing/IP).
  - “Continue” endpoints can be spammed to drive LLM costs.
- **Fix direction**:
  - Require auth when a session is linked to a contractor, and/or require an unguessable session secret separate from the public session_id.
  - Add rate limiting to onboarding endpoints (especially `/continue`).

### P0-05: Rate limiting is process-local and likely proxy-IP-naive (security control is weaker than it appears)
- **Evidence**:
  - Rate limiters are built with SlowAPI and `get_remote_address`: `backend/services/rate_limiting.py:142`–`164`
  - App runs multiple workers: `Procfile:1`
  - No shared rate limit backend is configured (SlowAPI defaults to in-memory per process).
- **Impact**:
  - With `--workers 4`, an attacker can effectively multiply allowed attempts (limits apply per worker process).
  - Behind a proxy/load balancer, `get_remote_address` may resolve to the proxy IP instead of the real client (limits become either useless or overly aggressive).
- **Fix direction**:
  - Use a shared rate limit store (Redis) and a trusted client IP extraction strategy (`X-Forwarded-For` with a known proxy chain).
  - Standardize on one limiter instance/config across modules (avoid per-file limiters unless intentional).

---

## HIGH (P1) — Fix within 1–2 weeks

### P1-01: Invoice numbering is race-prone and O(n) (duplicate invoice numbers at scale)
- **Evidence**:
  - `backend/api/invoices.py:161` uses `select(Invoice)... scalars().all()` then `len(...)` to compute next invoice number.
  - `backend/models/database.py:468` invoice_number is indexed but not unique.
- **Impact**:
  - Two concurrent invoice creations can generate the same invoice number.
  - Selecting *all* invoices to count is slow with growth.
- **Fix direction**:
  - Use a DB sequence or atomic “counter row” per contractor in a transaction.
  - Enforce uniqueness at least on (`contractor_id`, `invoice_number`) if invoice numbers are contractor-scoped.

### P1-02: Testimonials endpoint can return unapproved submissions to anyone (privacy leak)
- **Evidence**:
  - `backend/api/testimonials.py:87` is public and allows `approved_only=false` which returns all testimonials.
- **Impact**:
  - Unapproved testimonials can contain names, companies, or sensitive text.
- **Fix direction**:
  - Require admin auth for non-approved retrieval, or split into `/admin/testimonials`.

### P1-03: Task create allows arbitrary `customer_id` and later returns customer names without contractor scoping (cross-tenant data leak)
- **Evidence**:
  - `backend/api/tasks.py:382` stores `customer_id=request.customer_id` without verifying ownership
  - `backend/api/tasks.py:260` and `backend/api/tasks.py:410` fetch customer names without contractor filtering
- **Impact**:
  - If an attacker learns/guesses another contractor’s customer ID, they can attach it to their tasks and receive the customer name (at minimum).
- **Fix direction**:
  - Validate `customer_id` belongs to the current contractor before storing/returning.

### P1-04: Audio upload endpoints read entire files without explicit size limits (DoS risk)
- **Evidence**:
  - `backend/api/quotes.py:781` reads uploaded audio into memory; no explicit max size checks.
- **Impact**:
  - Large uploads can consume memory/CPU and impact availability.
- **Fix direction**:
  - Enforce max upload size at app + reverse proxy level; add server-side checks (reject large files early).

### P1-05: Known vulnerable dependency set (16 vulns across 8 packages)
- **Evidence**:
  - `./venv/bin/pip-audit -r requirements.txt` reports vulnerabilities in `fastapi`, `python-multipart`, `weasyprint`, `python-jose`, `jinja2`, `starlette`, `urllib3`, `ecdsa`.
  - Versions pinned in `requirements.txt:5`–`44`.
- **Impact**:
  - Supply-chain risk and known CVEs/GSAs in core web framework and templating stack.
- **Fix direction**:
  - Upgrade to suggested fixed versions (pay attention to transitive constraints between FastAPI/Starlette).

---

## MEDIUM (P2) — Fix within 1–2 months

### P2-01: Browser auth tokens stored in localStorage + no CSP hardening (increases impact of any XSS)
- **Evidence**:
  - `frontend/index.html:7013`–`7015` stores `quoted_token` and `quoted_refresh_token` in `localStorage`.
- **Impact**:
  - Any XSS becomes account takeover (token exfiltration).
- **Fix direction**:
  - Consider HttpOnly cookies + CSRF defense, or add strong CSP + Trusted Types approach if staying with tokens.

### P2-02: Template grid uses `innerHTML` with API-provided strings (defense-in-depth XSS gap)
- **Evidence**:
  - `frontend/index.html:12077`–`12094` sets `card.innerHTML` with `${template.name}` and `${template.description}`.
- **Impact**:
  - If template metadata becomes user-editable (or compromised), XSS becomes possible.
- **Fix direction**:
  - Use `textContent` and createElement-based rendering for any string originating outside the page.

### P2-03: Frontend network resilience is inconsistent (no timeouts, partial retry logic)
- **Evidence**:
  - `frontend/index.html:7066` implements `authenticatedFetch`, but many calls use raw `fetch` with manual headers and no timeout.
- **Impact**:
  - Hung requests can hang UI states; expired token flows behave inconsistently across features.
- **Fix direction**:
  - Standardize API calls through one wrapper with timeout + retry (idempotent only) + unified error parsing.

### P2-04: “Alert/confirm” still used for user-facing errors and confirmations (UX + accessibility)
- **Evidence**:
  - `frontend/index.html:8725`, `frontend/index.html:11240`, `frontend/index.html:14510` (and others) use `alert()`/`confirm()`.
- **Impact**:
  - Poor mobile UX, inconsistent design language, and limited accessibility control.
- **Fix direction**:
  - Replace with existing toast/notification system + modal confirmations.

---

## LOW (P3) — Backlog

### P3-01: Large monolithic frontend payload
- **Evidence**:
  - `frontend/index.html` is ~652KB (`wc -c`), mixing markup + CSS + JS.
- **Impact**:
  - Slower mobile load, harder caching, and higher regression risk for edits.
- **Fix direction**:
  - Split JS/CSS assets, enable caching headers, consider bundling/minification.

---

## User journey friction points (what a real contractor/customer will feel)

### Journey 1: Brand new user (landing → signup → onboarding)
- Voice-first promise is strong, but onboarding is sensitive to:
  - trade selection errors surfaced via alerts (jarring)
  - long-running steps without explicit timeout/retry
  - a “continue onboarding session” endpoint that is unauthenticated (security posture mismatch with “business pricing interview”)

### Journey 2: Active user creating a quote (record → transcribe → generate → edit)
- Strength: multiple voice entry points, transcription preview, autosave scaffolding.
- Fragility:
  - no explicit upload size ceiling communicated
  - network hangs can stall loading UI (no AbortController timeouts)
  - token refresh is not consistently used by all fetch calls

### Journey 3: Customer receiving a quote (shared link → accept/reject)
- Quote-view is implemented carefully with `textContent` for line items.
- Remaining gaps:
  - error flows use `alert()` rather than designed UI
  - “expiration” and “status” flows depend heavily on backend correctness; needs strong idempotency and auditing

### Journey 4: Learning & improvement loop (pricing brain)
- Strong concept foundation, but the loop benefits from:
  - clearer “what changed because of my edits?”
  - win/loss outcomes to learn from (not only edits)

