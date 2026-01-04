# Quoted Audit & Innovation Report (GPT-5.2-Codex)

**Generated**: 2025-12-26  
**Repo revision**: `97803ee`  
**Prepared by**: GPT-5.2-Codex  

---

## Executive summary

Quoted’s product direction (voice → quote → learning → workflow) is strong, but current risk is dominated by **deployment and integration reality** rather than UX taste:

- **Production correctness risks**: a multi-worker web process starts an in-process scheduler, guaranteeing duplicate jobs; multiple DB engines/sessions create non-atomic flows and potential connection storms.
- **Revenue/cost risks**: a quote-generation path bypasses billing/quota, and a public health endpoint can be abused to trigger external API calls.
- **Customer conversion risks**: the deposit checkout flow is currently broken end-to-end, and contractor notifications on acceptance/rejection fail (missing email method + missing config key).

These are fixable; prioritizing P0s will rapidly stabilize the foundation and unblock shipping the “innovation roadmap”.

---

## Architecture snapshot (current)

- **Frontend**: static HTML/JS app shell (`frontend/index.html`) + marketing pages (`frontend/landing.html`, `frontend/try.html`, `frontend/help.html`) served by FastAPI templates.
- **Backend**: FastAPI app (`backend/main.py`) with routers under `/api/*`.
- **Persistence**: SQLAlchemy models (`backend/models/database.py`) with runtime migrations; multiple engine/session creation patterns exist today.
- **Background jobs**: APScheduler in-process scheduler (`backend/services/scheduler.py`) started in app lifespan.
- **Third parties**: Stripe (billing + deposit checkout), Resend (email), OpenAI/Anthropic (AI), PostHog/Sentry (analytics/monitoring).

This matters because production behavior depends on worker model: `Procfile:1` runs 4 workers.

---

## Part 1: Critical fixes (do these first)

1) **Fix dev/test import crash (SQLite engine args + import-time init)**  
   Evidence: `backend/services/database.py:27`, `backend/services/__init__.py:11`.

2) **Stop scheduler duplication across workers** (run scheduler once)  
   Evidence: `Procfile:1`, `backend/main.py:108`, `backend/services/scheduler.py:269`.

3) **Close billing bypass on clarifications quote generation**  
   Evidence: `backend/api/quotes.py:733` (missing billing check).

4) **Repair deposit checkout acceptance flow end-to-end** (and add rate limit/idempotency)  
   Evidence: `backend/api/share.py:759`, `backend/api/share.py:826`, `backend/main.py:278`, `frontend/quote-view.html:1380`.

5) **Fix follow-up + acceptance notifications** (auth context + email method + config)  
   Evidence: `backend/api/followup.py:76`, `backend/services/follow_up.py:439`, `backend/api/share.py:618`, `backend/config.py` (no `app_url`).

6) **Remove/gate contractor demo endpoints + fix route shadowing**  
   Evidence: `backend/api/contractors.py:219`, `backend/api/contractors.py:541`, `frontend/index.html:12887`.

7) **Protect `/health/full`** (auth + rate limit)  
   Evidence: `backend/main.py:208`, `backend/services/health.py:65`.

8) **Rotate and purge committed secrets**  
   Evidence (redacted): `ARCHIVE/ENGINEERING_STATE_FULL_2025-12-03.md:1984`.

---

## Release gates (how to know you’re safe to ship)

Recommended “must-pass” checks before widening traffic:
- `./venv/bin/python -c "import backend.main"` (import smoke)
- `PYTHONPATH="$PWD" ./venv/bin/pytest -q` (tests)
- `./venv/bin/pip-audit -r requirements.txt` (dependency vulnerabilities)
- Manual E2E:
  - demo quote generation
  - authenticated quote generation (text + audio)
  - shared quote view → accept → contractor notified
  - shared quote view → deposit checkout → Stripe → return to `/shared/{token}` → state updated

---

## Part 2: Polish & UX improvements (after P0 stabilization)

- Mobile nav discoverability: `frontend/index.html:6464`.
- Replace `confirm()` flows with consistent modal/toast UI: `frontend/index.html:9228`.
- Improve shared invoice error state with recovery/support: `frontend/invoice-view.html:649`.
- Reduce `innerHTML` rendering of remote strings: `frontend/index.html:13037`.

---

## Part 3: Innovation roadmap (once foundations are stable)

### Immediate (this month)
- Confidence-Guided Clarifications (ship after fixing billing pipeline)
- One-Tap Acceptance → Deposit → Schedule
- Follow-Up Autopilot v1 (after scheduler/job safety)

### Next quarter
- Win/Loss Reasons → Pricing Brain actions
- Interactive web quotes (options, good/better/best)

### Future vision
- Conversational quoting
- Photo-to-quote

Details: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/GPT-5.2-Codex_phase3-innovations.md`

---

## Part 4: Recommended next steps

1) Ship a “P0 stabilization” sprint (1–3 days) with regression tests:
   - import smoke test
   - quote generation billing parity tests
   - shared quote acceptance/deposit redirect tests
2) Unify DB session/engine usage (reduce connection + atomicity risk).
3) Move scheduler to a dedicated worker or add distributed locking.
4) Upgrade vulnerable dependencies and re-run test suite.

---

## Appendix (full outputs)

- Command analysis: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/GPT-5.2-Codex_COMMAND_ANALYSIS.md`
- Phase 1 findings: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/GPT-5.2-Codex_phase1-holes.md`
- Phase 2 findings: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/GPT-5.2-Codex_phase2-polish.md`
- Phase 3 ideas: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/GPT-5.2-Codex_phase3-innovations.md`
- Artifacts: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/artifacts/`
- UI captures: `.claude/audit-innovation-outputs-gpt-5.2-codex-2025-12-26/ui/`
