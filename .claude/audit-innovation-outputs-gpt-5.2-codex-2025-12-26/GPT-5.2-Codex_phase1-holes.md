# Phase 1: Technical Audit Findings (GPT-5.2-Codex)

**Generated**: 2025-12-26  
**Repo revision**: `97803ee`  
**Scope**: backend, data layer, deployment behaviors, security controls, and frontend resilience.

**Key artifacts**:
- API inventory: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/artifacts/api-routes.md`
- Dependency audit: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/artifacts/pip-audit-summary.md`
- Secret scan (redacted): `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/artifacts/secret-fingerprint-scan.md`
- UI screenshots: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/ui/`

---

## Severity rubric (used here)

- **P0 / CRITICAL**: Production-breaking, actively exploitable, or high-cost abuse vector. Fix before scaling traffic.
- **P1 / HIGH**: High-impact reliability/security/data integrity issue. Fix within 1–2 weeks.
- **P2 / MEDIUM**: Important hardening/polish. Fix within 1–2 months.
- **P3 / LOW**: Backlog improvements.

---

## Phase 1A — “Parallel Agents” (as executed by GPT-5.2-Codex)

### Agent 1: Auth & Security Prober — highlights
- Refresh token validation is **O(n) bcrypt checks** (DoS as tokens grow): `backend/services/auth.py:216`.
- Unauthenticated onboarding session read/continue endpoints (privacy + cost abuse): `backend/api/onboarding.py:161`, `backend/api/onboarding.py:549`, `backend/api/onboarding.py:561`.
- Public `/health/full` triggers external API calls using API keys (cost burn): `backend/main.py:208`, `backend/services/health.py:65`.
- Public testimonials endpoint can return unapproved testimonials via query param: `backend/api/testimonials.py:87`.
- Token/PII leakage risk via analytics logging full properties dict: `backend/services/analytics.py:61`.

### Agent 2: API Contract Auditor — highlights
- Route inventory found **138** API routes; **26** are public/unknown-auth; **17** public/unknown-auth have **no rate limit** (heuristics): `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/artifacts/api-routes.md`.
- Multiple “broken-by-reference” endpoints (call missing DB methods or missing config):
  - Deposit checkout uses `db.get_contractor` (missing) + `settings.app_url` (missing): `backend/api/share.py:781`, `backend/api/share.py:826`.
  - Logo fetch uses `db.get_contractor` (missing): `backend/api/contractors.py:546`.

### Agent 3: Database & Data Integrity — highlights
- Default dev/test startup **crashes** on SQLite due to invalid pool args (blocks CI/dev): `backend/services/database.py:27`, cascades via `backend/services/__init__.py:11`.
- Multiple independent DB engines + sessions across request paths (risk: connection storms, non-atomic multi-step operations):
  - `backend/services/database.py:22` (global engine)
  - `backend/services/auth.py:77` (separate engine)
  - `backend/models/database.py:925` (init_db creates yet another engine)
- Invoice numbering is non-atomic and uses count+1 (race collisions): `backend/api/invoices.py:169`, `backend/services/invoice_automation.py:49`, no uniqueness constraint: `backend/models/database.py:482`.
- Cross-tenant linkage/leak: tasks accept arbitrary `customer_id` and later fetch customer names without contractor scoping: `backend/api/tasks.py:382`, `backend/api/tasks.py:374`.

### Agent 4: Frontend Resilience — highlights
- Auth tokens stored in `localStorage` (XSS becomes account takeover): `frontend/index.html:7712`.
- Some UI renders API-returned strings via `innerHTML` without escaping (defense-in-depth XSS risk): `frontend/index.html:12983`, `frontend/index.html:13037`.
- Large monolithic app shell (`~740KB`) increases regression risk and mobile load time: `frontend/index.html` (see `wc` output).
- External scripts loaded from CDNs without SRI (supply chain risk): `frontend/index.html:4421`.

---

## System map (trust boundaries + assets)

### Primary actors
- **Contractor (authenticated)**: creates quotes/invoices, manages customers/tasks, configures templates/terms.
- **Customer (unauthenticated)**: views shared quote/invoice, accepts/rejects, may pay deposit.
- **Anonymous visitor**: marketing pages, demo mode, some public endpoints.

### High-value assets
- Contractor pricing model (“Pricing Brain”), quote history, customer PII (names/emails/addresses), invoices, payment state.
- Authentication tokens (access + refresh) and share tokens (quotes/invoices).
- Third-party API keys (OpenAI, Anthropic, Stripe, Resend).

### Trust boundaries
- Browser ↔ FastAPI API (`/api/*`)
- Public share links (`/shared/{token}`, `/invoice/{token}`)
- Background scheduler (in-process jobs)
- External APIs (Stripe, Resend, OpenAI/Anthropic)

This map is used to score severity: any issue that crosses boundaries (public → private, or job runner → duplicated side effects) is weighted toward P0/P1.

---

## P0 / CRITICAL — Fix before more users

### P0-01: Backend import/dev/test is broken by SQLite engine args + import-time engine creation
- **Evidence**:
  - `backend/services/database.py:27` passes `pool_size/max_overflow/pool_timeout` to SQLite engine (invalid).
  - `backend/services/__init__.py:11` imports `.database` at package import time, cascading failure.
  - Repro: `./venv/bin/python -c "import backend.main"` fails (also blocks `pytest` collection).
- **Impact**: blocks local dev, CI, and any SQLite-based environment; reduces velocity and increases risk of shipping regressions.
- **Fix direction**:
  - Make engine creation dialect-aware (SQLite vs Postgres) and **lazy-init** (no engine at import time).
  - Centralize engine/session in one module; avoid per-service engines.
- **Verify**:
  - `./venv/bin/python -c "import backend.main"`
  - `PYTHONPATH="$PWD" ./venv/bin/pytest -q`

### P0-02: In-process scheduler runs once per Uvicorn worker (duplicates jobs/emails/tasks)
- **Evidence**:
  - `Procfile:1` runs `uvicorn ... --workers 4` (also `railway.json:deploy.startCommand`).
  - `backend/main.py:108` calls `start_scheduler()` inside lifespan.
- **Impact**: duplicated reminders and follow-up automation; racey “check then insert/send” patterns cause spam and duplicate tasks.
- **Fix direction**:
  - Run scheduler in a **single dedicated process** (separate Railway service / Procfile worker) OR implement leader election + distributed locks.
  - Make job handlers idempotent (atomic “claim” updates, unique constraints).
- **Verify**:
  - Deploy with web workers; ensure only one scheduler instance is active.
  - Add a canary job to prove single execution.

### P0-03: Billing/quota bypass via `/api/quotes/generate-with-clarifications`
- **Evidence**:
  - Main quote generation enforces billing check + increments usage: `backend/api/quotes.py:361`, `backend/api/quotes.py:583`.
  - Clarifications path does not call BillingService at all: `backend/api/quotes.py:733`.
- **Impact**: users can generate unlimited quotes outside billing guardrails; risk of cost blowouts and inconsistent billing metrics.
- **Fix direction**:
  - Apply `BillingService.check_quote_limit` + `increment_quote_usage` to clarifications flow.
  - Ensure all quote creation paths share a single “quote generation pipeline” function.
- **Verify**:
  - Add regression test: trial-expired user gets `402` on both endpoints.

### P0-04: Deposit checkout flow is broken end-to-end (and is currently an abuse surface)
- **Evidence**:
  - Endpoint has no rate limit: `backend/api/share.py:759`.
  - Calls non-existent DB methods: `backend/api/share.py:781`, `backend/api/share.py:786`.
  - References missing config key `settings.app_url`: `backend/api/share.py:826` (no `app_url` in `backend/config.py`).
  - Redirect URLs use `/quote/{token}` but actual web route is `/shared/{token}`: `backend/api/share.py:827`, `backend/main.py:278`.
  - Frontend expects `/shared/{token}?payment=...`: `frontend/quote-view.html:1380`.
- **Impact**:
  - Customer deposit acceptance is dead-on-arrival (500s + wrong redirects).
  - Without rate limits/idempotency, attacker can spam Stripe checkout session creation.
- **Fix direction**:
  - Replace DB calls with existing `get_contractor_by_id` + `get_terms`.
  - Use `settings.frontend_url` (or add a single canonical `public_base_url`) for success/cancel URLs.
  - Add limiter + idempotency per quote (store session id; block rapid repeats).
- **Verify**:
  - E2E: accept quote with “pay deposit” → Stripe → return to `/shared/{token}` showing paid state.

### P0-05: Follow-up feature is broken (auth context + email sender mismatch)
- **Evidence**:
  - Followup API expects `user["contractor_id"]`: `backend/api/followup.py:76`, `backend/api/followup.py:141`.
  - Auth dependency returns no contractor_id: `backend/services/auth.py:484`–`524`.
  - Follow-up service calls non-existent `EmailService.send_email`: `backend/services/follow_up.py:439`.
- **Impact**: follow-up creation/status/pause/resume is runtime-broken; scheduler follow-up job will error repeatedly.
- **Fix direction**:
  - Use `Depends(get_current_contractor)` in followup API, or include contractor_id in auth user dict.
  - Replace `send_email` calls with real EmailService methods (or add a generic send method).
- **Verify**:
  - Create a follow-up sequence and process due followups without exceptions.

### P0-06: Contractor settings routes are shadowed/unreachable; settings UI will break
- **Evidence**:
  - Dynamic route defined early: `backend/api/contractors.py:219` (`GET /{contractor_id}`).
  - Static routes defined later and therefore shadowed:
    - `/logo`: `backend/api/contractors.py:541`
    - `/template-settings`: `backend/api/contractors.py:638`
    - `/suggestions`: `backend/api/contractors.py:682`
  - “Me terms” is shadowed by `/{contractor_id}/terms`: `backend/api/contractors.py:298`, `backend/api/contractors.py:339`.
  - Frontend calls the shadowed routes: `frontend/index.html:12887`, `frontend/index.html:12909`.
- **Impact**: logo upload, quote defaults, template settings, and suggestions are effectively broken; also expands public surface area unintentionally.
- **Fix direction**:
  - Remove/gate demo endpoints and/or move `/{contractor_id}` under `/id/{contractor_id}`.
  - Ensure static routes are registered before parameterized catch-alls.
- **Verify**:
  - Hit `/api/contractors/logo` and `/api/contractors/me/terms` and confirm 200 in prod.

### P0-07: Secrets are committed to the repo (must rotate + purge)
- **Evidence (redacted)**:
  - Stripe secret key present: `ARCHIVE/ENGINEERING_STATE_FULL_2025-12-03.md:1984`
  - Stripe publishable key present: `ARCHIVE/ENGINEERING_STATE_FULL_2025-12-03.md:1985`
  - Resend API key present: `ARCHIVE/ENGINEERING_STATE_FULL_2025-12-03.md:1992`
  - See redacted scan: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/artifacts/secret-fingerprint-scan.md`
- **Impact**: credential leakage risk (even “test” keys should not be in git history); increases blast radius if repo is shared.
- **Fix direction**:
  - Rotate keys immediately; remove secrets from docs; rewrite history if the repo is ever shared externally.
- **Verify**:
  - Re-run secret scan; confirm 0 matches.

### P0-08: Public `/health/full` performs external API calls (cost + abuse vector)
- **Evidence**:
  - Public endpoint: `backend/main.py:208`
  - External calls using configured API keys: `backend/services/health.py:65` onward
- **Impact**: attackers can repeatedly call `/health/full` to burn OpenAI/Anthropic/Stripe/Resend quotas and degrade service.
- **Fix direction**:
  - Protect `/health/full` behind auth/secret header and add rate limiting; keep `/health` lightweight.
- **Verify**:
  - `/health/full` returns `401` without admin secret.

### P0-09: Multiple DB engines + per-call sessions create non-atomic flows and potential connection blowouts
- **Evidence**:
  - Global engine with pooled settings: `backend/services/database.py:22`
  - Separate engine for auth dependency: `backend/services/auth.py:77`
  - `init_db()` creates yet another engine on startup: `backend/models/database.py:925`, called from `backend/main.py:104`
  - Example of cross-session work in one request path: quote generation uses `auth_db` (billing) and `get_db_service()` (quote persistence): `backend/api/quotes.py:353`, `backend/api/quotes.py:391`
- **Impact**:
  - Connection pools can multiply across workers and engines (surprising Postgres connection counts).
  - Multi-step operations are not atomic (quote created but billing usage not incremented, or vice versa).
  - Passing ORM objects between sessions can silently fail or require merges (seen in best-effort customer linking).
- **Fix direction**:
  - Centralize a single engine + AsyncSession dependency and pass it through services.
  - Make “create quote + link customer + increment usage” transactional.
- **Verify**:
  - Instrument DB connection counts in prod; confirm bounded connections with 4 workers.
  - Add regression tests around quote creation + usage increment atomicity.

### P0-10: Public “demo contractor” endpoints are reachable and unbounded (memory DoS + product confusion)
- **Evidence**:
  - In-memory contractor creation/listing are public and not rate limited: `backend/api/contractors.py:183`, `backend/api/contractors.py:467`.
  - Data is stored in module-level dicts: `backend/api/contractors.py:169`.
- **Impact**:
  - Attackers can fill process memory with repeated POSTs.
  - With 4 workers, each worker has different in-memory state (unreliable behavior).
- **Fix direction**:
  - Remove these routes from production router, or gate behind an environment flag + admin auth.
  - If needed for demo, move to `/api/demo/*` and enforce strict rate limits.

---

## P1 / HIGH — Fix within 1–2 weeks

### P1-01: Invoice numbering is concurrency-unsafe and O(n)
- **Evidence**:
  - Count+1 generation: `backend/api/invoices.py:169`, `backend/services/invoice_automation.py:49`.
  - No uniqueness on invoice_number: `backend/models/database.py:482`.
- **Impact**: duplicates under concurrency; potential invoice overwrite/ambiguity; performance degrades as invoices grow.
- **Fix direction**:
  - Add per-contractor sequence (DB-side) or unique constraint + retry.
  - Replace full load + len() with `SELECT COUNT(*)` if staying with count-based.

### P1-02: Cross-tenant data leak via tasks (customer name lookup not scoped)
- **Evidence**:
  - Task create stores arbitrary `customer_id`: `backend/api/tasks.py:382`, `backend/api/tasks.py:399`.
  - Customer name lookup not contractor-scoped: `backend/api/tasks.py:374`, `backend/api/tasks.py:375`.
- **Impact**: if IDs are guessed/leaked, attackers can associate and reveal other contractors’ customer names.
- **Fix direction**:
  - Validate customer_id belongs to current contractor before storing/returning.
  - Join on `Customer.contractor_id == contractor.id` for any lookup.

### P1-03: Refresh token rotation is O(n) bcrypt checks (scales poorly; DoS risk)
- **Evidence**: `backend/services/auth.py:216`–`233`.
- **Impact**: refresh endpoint cost increases linearly with tokens; attacker can inflate token table and degrade auth.
- **Fix direction**:
  - Store a queryable token identifier (e.g., `jti` as lookup key) and hash only the secret portion.
  - Index the lookup column; verify one bcrypt per refresh.

### P1-04: Email service has two production-breaking issues (formatting + blocking)
- **Evidence**:
  - Template uses CSS braces but code calls `.format(...)`: `backend/services/email.py:262` (will throw).
  - Many “async” email methods call `resend.Emails.send(...)` synchronously (blocks event loop): `backend/services/email.py:265`.
- **Impact**: welcome/trial emails fail or stall request handling; latency spikes under load.
- **Fix direction**:
  - Switch all template injection to `.replace('{content}', ...)` with brace-escaping as needed.
  - Run Resend calls via `run_in_executor` consistently (or use async HTTP client).

### P1-05: Public/shared invoice endpoint lacks rate limiting
- **Evidence**: `backend/api/invoices.py:941`.
- **Impact**: token brute-force attempts and amplification via expensive DB reads.
- **Fix direction**:
  - Add limiter (IP-based) and consider short-lived share tokens or additional secret component.

### P1-06: Dependency vulnerability set (16 known vulnerabilities in 8 packages)
- **Evidence**:
  - `pip-audit` output stored at `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/pip-audit.json`
  - Summary: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/artifacts/pip-audit-summary.md`
- **Impact**: known CVEs in core web stack; increased supply-chain risk.
- **Fix direction**:
  - Upgrade pinned versions; re-run tests; deploy gradually.

### P1-07: Error detail leakage via `HTTPException(detail=str(e))` (information disclosure)
- **Evidence**:
  - Example: `backend/api/share.py:755` raises `HTTPException(..., detail=str(e))`
  - Example: `backend/api/quotes.py:652` raises `HTTPException(..., detail=str(e))`
- **Impact**: internal errors (stack-adjacent info, provider errors, sometimes IDs) can leak to clients; makes exploitation easier.
- **Fix direction**: return stable error codes/messages to clients; log details server-side only.

---

## P2 / MEDIUM — Fix within 1–2 months

### P2-01: Rate limiting is proxy-IP-naive and per-process by default
- **Evidence**:
  - IP keying uses `get_remote_address`: `backend/services/rate_limiting.py:18`
  - Uvicorn start command lacks `--proxy-headers`: `Procfile:1`
- **Impact**:
  - Behind Railway proxies, many users may share an apparent IP → accidental throttling or ineffective abuse prevention.
  - With 4 workers, in-memory storage multiplies effective limit by worker count unless Redis storage is configured.
- **Fix direction**:
  - Enable proxy headers (`--proxy-headers`) or add ProxyHeadersMiddleware.
  - Configure shared rate limit storage (Redis) via `RATELIMIT_STORAGE_URL`.

### P2-02: Quote expiration is computed but not enforced on accept/reject
- **Evidence**:
  - Expiration computed for view: `backend/api/share.py:430`.
  - Accept path does not enforce expiration: `backend/api/share.py:545`.
- **Impact**: policy inconsistency; can lead to disputes (“expired but accepted”).
- **Fix direction**: enforce the same expiration rule in accept/reject/deposit paths.

### P2-03: Analytics logs may include tokens/emails in plaintext logs
- **Evidence**:
  - Logs all properties: `backend/services/analytics.py:61`
  - Call sites include share token / recipient_email: `backend/api/share.py:245`, `backend/api/share.py:326`, `backend/api/invoices.py:971`
- **Impact**: PII/token leakage via logs, especially if logs are exported to third parties.
- **Fix direction**: redact token/email fields; adopt an allowlist of event properties.

---

## P3 / LOW — Backlog

### P3-01: Large monolithic frontend bundle increases mobile load and regression risk
- **Evidence**: `frontend/index.html` is ~740KB unbundled.
- **Fix direction**: split JS/CSS, add caching headers, optionally bundle/minify.

---

## Phase 1B — User Journey Hole-Poking (friction + failure modes)

### Journey 1: Brand new user
- Domain naming inconsistency across product surfaces erodes trust (quoted.it vs quoted.it.com): `backend/config.py:19`, `backend/services/email.py:30`, `frontend/help.html:486`.
- Long industry/trade selection without search creates onboarding friction on mobile (see UI in `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/ui/try-iphone11.png` and app onboarding sections in `frontend/index.html`).

### Journey 2: Active user creating quotes
- Clarifications flow bypasses billing, producing “invisible” usage and cost risk: `backend/api/quotes.py:733`.
- Unbounded audio upload reads can crash or stall: `backend/api/quotes.py:972`, `backend/api/demo.py:184`.
- Settings-dependent flows (logo, quote defaults) fail due to backend route shadowing: `frontend/index.html:12887`.

### Journey 3: Customer receiving quote
- Acceptance emails fail (missing `send_email` + `app_url`) so contractors may never know customers acted: `backend/api/share.py:618`, `backend/api/share.py:631`.
- Deposit payment flow is broken and redirects to the wrong route: `backend/api/share.py:827`, `backend/main.py:278`.

### Journey 4: Learning & improvement loop
- Follow-up automation is currently non-functional; the promise of “follow-up engine” becomes trust-damaging if surfaced in UI.
